"""
Core pipeline orchestrator — 5-step turn processing.
Called by server.py (FastAPI) and turn.py (Vercel).
"""

import re
import json
import logging
import asyncio
from typing import AsyncIterator

from schemas.memory import LearnerState, TurnRecord
from schemas.confusion import ConfusionSignal
from schemas.classification import QuestionClassification
from modules.confusion_detector import detect as detect_confusion
from modules.clarity_engine import get_working_question
from modules.adaptive_teacher import estimate_proficiency, select_style, build_system_prompt
from modules.memory_manager import update_state_after_turn, extract_facts, merge_facts
from validators.logic_gates import gate_comprehension_check, gate_classification
from validators.regex_patterns import check_blocklist
from api.hf_client import HFClient, FALLBACK_RESPONSE

logger = logging.getLogger(__name__)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def run_pipeline(
    question: str,
    state: LearnerState,
    hf_client: HFClient,
) -> AsyncIterator[str]:
    """Full 5-step pipeline — yields SSE events."""

    # ── Step 1: Module 6 — Confusion Detection (rule layer only, zero HF cost) ─
    # Layer 2 (LLM) is intentionally skipped in the prototype: the rule layer
    # handles repetition, vague, and contradiction reliably, and LLM Layer 2
    # would add ~20s latency on every turn.
    confusion = detect_confusion(question, state.turn_history, hf_client=None)

    yield _sse("confusion", {
        "confused": confusion.confused,
        "type": confusion.type,
    })

    # ── Step 2: Module 2 — Question Classifier (heuristic, zero HF cost) ──────
    # Use deterministic heuristics instead of an LLM call.
    # The LLM classifier is reserved for the full system where latency budget allows.
    from schemas.classification import QuestionClassification
    classification = _classify_heuristic(question, state.turn_history)

    # If clarification needed, return that and stop
    if classification.needs_clarification and classification.clarification_prompt:
        is_clean, _ = check_blocklist(classification.clarification_prompt)
        clarification_text = (
            classification.clarification_prompt if is_clean else FALLBACK_RESPONSE
        )
        yield _sse("token", {"text": clarification_text})
        yield _sse("classification", {"type": "needs_clarification"})
        # Return a lightweight state update (no answer to extract facts from)
        updated_state = update_state_after_turn(
            state=state,
            question=question,
            rewritten=question,
            answer=clarification_text,
            confusion=ConfusionSignal(confused=False, type="none"),
            had_comprehension_check=False,
            new_proficiency=state.proficiency_estimate,
            new_style=state.current_style,
        )
        yield _sse("state", updated_state.model_dump())
        yield _sse("done", {})
        return

    working_question = get_working_question(classification, question)

    yield _sse("classification", {
        "type": classification.question_type,
        "rewritten": working_question if classification.needs_rewrite else None,
    })

    # ── Step 3: Module 3 — Style Selection ───────────────────────────────────
    new_proficiency = estimate_proficiency(state, question)
    style = select_style(new_proficiency, state, confusion)
    inject_check = gate_comprehension_check(state.turn_history)

    system_prompt = build_system_prompt(
        style=style,
        confusion=confusion,
        state=state,
        inject_comprehension_check=inject_check,
    )

    yield _sse("style", {"style": style.style, "reason": style.reason})

    # ── Step 4: Answer Generation (streamed) ─────────────────────────────────
    full_answer = ""
    try:
        for token in hf_client.stream(system_prompt, working_question, max_tokens=600):
            full_answer += token
            yield _sse("token", {"text": token})
    except Exception as exc:
        logger.error("Stream generation failed: %s", exc)
        yield _sse("token", {"text": FALLBACK_RESPONSE})
        full_answer = FALLBACK_RESPONSE

    # Layer 2: regex blocklist on output
    is_clean, matched = check_blocklist(full_answer)
    if not is_clean:
        logger.warning("Output blocked — pattern: %s", matched)
        yield _sse("token", {"text": "\n\n[Response filtered. Please rephrase your question.]"})
        full_answer = FALLBACK_RESPONSE

    # ── Step 5: Memory Update (async — does not block stream completion) ──────
    updated_state = update_state_after_turn(
        state=state,
        question=question,
        rewritten=working_question,
        answer=full_answer,
        confusion=confusion,
        had_comprehension_check=inject_check,
        new_proficiency=new_proficiency,
        new_style=style.style,
    )

    # Send state and done immediately — don't block on memory extraction
    yield _sse("state", updated_state.model_dump())
    yield _sse("done", {})

    # Fire memory extraction truly async after response is complete
    # Result is silently dropped — facts appear on the next turn's state
    asyncio.get_event_loop().run_in_executor(
        None, _extract_and_log, full_answer, len(updated_state.turn_history), state, hf_client
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

_PRONOUN_STARTERS = re.compile(
    r"^(?:is|does|can|was|were|has|what about|what|how|why)\s+(?:(?:is|does|can|was|were|has|about)\s+)?(it|that|they|this|he|she|its|their|those|these|them|him|her)\b|"
    r"^(it|that|they|this|he|she|its|their|those|these|them|him|her)\b",
    re.IGNORECASE,
)
_ELLIPSIS_PHRASES = re.compile(
    r"^(and|but|so|what about|how about|tell me more|can you|why|when|where|who)\b",
    re.IGNORECASE,
)


def _classify_heuristic(
    question: str, turn_history: list[TurnRecord]
) -> QuestionClassification:
    """
    Deterministic question classifier — zero HF cost.
    Handles ~90% of cases correctly for the prototype.
    """
    q = question.strip()

    if not turn_history:
        return QuestionClassification(
            question_type="self_contained",
            needs_rewrite=False,
            needs_clarification=False,
        )

    # Short question with pronoun → resolvable
    if _PRONOUN_STARTERS.match(q):
        last = turn_history[-1]
        reference = last.rewritten or last.question
        rewritten = f"{q.rstrip('?')} (referring to {reference})?"
        if rewritten:
            rewritten = rewritten[0].upper() + rewritten[1:]
        classification = QuestionClassification(
            question_type="resolvable",
            needs_rewrite=True,
            needs_clarification=False,
            rewritten_question=rewritten,
        )
        return gate_classification(classification, q)

    # Short affirmative/negative responses ("yes", "no") → resolvable
    if q.lower().rstrip('?!. ') in ("yes", "no", "yep", "nope", "sure", "correct", "got it") and len(turn_history) > 0:
        last = turn_history[-1]
        reference = last.rewritten or last.question
        rewritten = f"{q.capitalize()} in response to: {reference}"
        return QuestionClassification(
            question_type="resolvable",
            needs_rewrite=True,
            needs_clarification=False,
            rewritten_question=rewritten,
        )

    # Ellipsis / follow-up phrases → resolvable
    if _ELLIPSIS_PHRASES.match(q) and len(q.split()) < 8:
        classification = QuestionClassification(
            question_type="resolvable",
            needs_rewrite=True,
            needs_clarification=False,
            rewritten_question=q,
        )
        return gate_classification(classification, q)

    return QuestionClassification(
        question_type="self_contained",
        needs_rewrite=False,
        needs_clarification=False,
    )


def _extract_and_log(
    answer: str, turn_number: int, state: LearnerState, hf_client: HFClient
) -> None:
    """Background memory extraction — errors are logged, never raised."""
    try:
        extract_facts(answer, turn_number, state, hf_client)
    except Exception as exc:
        logger.debug("Background memory extraction skipped: %s", exc)
