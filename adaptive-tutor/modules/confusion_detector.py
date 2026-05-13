"""
Module 6 — Confusion Detector.
Layer 1: deterministic rules (ROUGE-L, keyword match, regex) — zero HF calls.
Layer 2: constrained LLM classification — only when Layer 1 is inconclusive.
"""

import re
import json
import logging
from typing import Optional

from rouge_score import rouge_scorer

from schemas.confusion import ConfusionSignal
from schemas.memory import TurnRecord
from validators.logic_gates import gate_confusion_signal
from modules.skill_loader import load_meta_skill

logger = logging.getLogger(__name__)

_scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)

_VAGUE_PATTERN = re.compile(
    r"\b(what do you mean|can you explain|explain again|don't understand|"
    r"confused|i'm confused|don't get it|not sure i|what\?|huh\?|"
    r"could you clarify|what does that mean|say that again)\b",
    re.IGNORECASE,
)

_CONTRADICTION_PATTERN = re.compile(
    r"\b(but you said|but didn't you|you told me|i thought you said|"
    r"isn't it actually|but isn't|but you mentioned)\b",
    re.IGNORECASE,
)

_REPETITION_THRESHOLD = 0.7


def _rouge_l(a: str, b: str) -> float:
    return _scorer.score(a, b)["rougeL"].fmeasure


def detect_confusion_rules(
    question: str, turn_history: list[TurnRecord]
) -> Optional[ConfusionSignal]:
    """Layer 1: deterministic rule-based detection. Returns None if inconclusive."""

    # Check for repetition via ROUGE-L first
    # Skip for very short questions to avoid false positives on 'yes', 'no', etc.
    if turn_history and len(question) >= 15 and len(question.split()) >= 3:
        for idx, turn in enumerate(turn_history):
            score = _rouge_l(question, turn.question)
            if score >= _REPETITION_THRESHOLD:
                return ConfusionSignal(
                    confused=True,
                    type="repetition",
                    trigger_turn=idx,
                    evidence_phrase=question[:80],
                )

    # Check for vague confusion signal
    if _VAGUE_PATTERN.search(question):
        trigger = max(0, len(turn_history) - 1)
        return ConfusionSignal(
            confused=True,
            type="vague",
            trigger_turn=trigger,
            evidence_phrase=_extract_match(_VAGUE_PATTERN, question),
        )

    # Check for contradiction signal
    if _CONTRADICTION_PATTERN.search(question):
        trigger = max(0, len(turn_history) - 1)
        return ConfusionSignal(
            confused=True,
            type="contradiction",
            trigger_turn=trigger,
            evidence_phrase=_extract_match(_CONTRADICTION_PATTERN, question),
        )

    # Inconclusive — return None to trigger Layer 2
    return None


def _extract_match(pattern: re.Pattern, text: str) -> str:
    m = pattern.search(text)
    return m.group(0) if m else text[:40]


def detect_confusion_llm(
    question: str,
    turn_history: list[TurnRecord],
    hf_client,
) -> ConfusionSignal:
    """Layer 2: constrained LLM classification (only when rules are inconclusive)."""
    skill = load_meta_skill("confusion_classification")
    history_text = "\n".join(
        f"Turn {i}: Q: {t.question} | A: {t.answer[:200]}"
        for i, t in enumerate(turn_history[-5:])
    )
    prompt = (
        f"{skill}\n\n"
        f"Conversation history (last {len(turn_history[-5:])} turns):\n{history_text}\n\n"
        f"Student's current question: {question}\n\n"
        "Return ONLY the JSON object."
    )

    try:
        raw = hf_client.generate(prompt, max_tokens=200, temperature=0.0)
        data = _extract_json(raw)

        signal = ConfusionSignal(**data)
        signal = gate_confusion_signal(signal, len(turn_history))
        return signal
    except Exception as exc:
        logger.warning("confusion LLM parse failed: %s — defaulting to none", exc)
        return ConfusionSignal(confused=False, type="none")


def detect(
    question: str,
    turn_history: list[TurnRecord],
    hf_client=None,
) -> ConfusionSignal:
    """Main entry point. Layer 1 first; Layer 2 only if needed."""
    if not turn_history:
        return ConfusionSignal(confused=False, type="none")

    result = detect_confusion_rules(question, turn_history)
    if result is not None:
        return gate_confusion_signal(result, len(turn_history))

    if hf_client is not None:
        return detect_confusion_llm(question, turn_history, hf_client)

    return ConfusionSignal(confused=False, type="none")


def _extract_json(text: str) -> dict:
    text = text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = re.sub(r"```(?:json)?", "", text).strip("` \n")
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
