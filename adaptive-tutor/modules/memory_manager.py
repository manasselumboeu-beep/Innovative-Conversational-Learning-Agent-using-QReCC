"""
Module 1 — Lightweight Browser-State Memory.
Extracts new facts from completed answers via optional HF call.
"""

import re
import json
import logging

from schemas.memory import LearnerState, MemoryUpdate, Fact, TurnRecord
from schemas.confusion import ConfusionSignal
from validators.logic_gates import gate_memory_update
from modules.skill_loader import load_meta_skill

logger = logging.getLogger(__name__)


def update_state_after_turn(
    state: LearnerState,
    question: str,
    rewritten: str,
    answer: str,
    confusion: ConfusionSignal,
    had_comprehension_check: bool,
    new_proficiency: float,
    new_style: str,
) -> LearnerState:
    """
    Synchronously update learner state — no HF call needed.
    Memory extraction (HF call) is handled separately / async.
    """
    # Update confusion count (rolling window of 5)
    if confusion.confused:
        new_confusion_count = min(5, state.confusion_count_last_5 + 1)
    else:
        new_confusion_count = max(0, state.confusion_count_last_5 - 1)

    # Add turn record
    new_turn = TurnRecord(
        question=question,
        rewritten=rewritten,
        answer=answer,
        had_comprehension_check=had_comprehension_check,
        confusion_type=confusion.type,
    )

    updated_history = state.turn_history + [new_turn]
    # Keep last 10 turns in state to bound request size
    if len(updated_history) > 10:
        updated_history = updated_history[-10:]

    return LearnerState(
        known_facts=state.known_facts,
        confusion_count_last_5=new_confusion_count,
        current_style=new_style,
        turn_history=updated_history,
        proficiency_estimate=new_proficiency,
    )


def extract_facts(
    answer: str,
    turn_number: int,
    state: LearnerState,
    hf_client,
) -> list[Fact]:
    """HF call #3 — extract new facts from the completed answer."""
    skill = load_meta_skill("memory_extraction")
    existing_ids = ", ".join(f.id for f in state.known_facts) if state.known_facts else "none"

    prompt = (
        f"{skill}\n\n"
        f"Turn number: {turn_number}\n"
        f"Already in known_facts (do not re-extract): {existing_ids}\n\n"
        f"Tutor's answer:\n{answer}\n\n"
        "Return ONLY the JSON object."
    )

    try:
        raw = hf_client.generate(prompt, max_tokens=400, temperature=0.0)
        data = _extract_json(raw)
        update = MemoryUpdate(**data)
        update = gate_memory_update(update, state.known_facts)
        return update.new_facts
    except Exception as exc:
        logger.warning("memory extraction failed: %s", exc)
        return []


def merge_facts(existing: list[Fact], new_facts: list[Fact]) -> list[Fact]:
    """Merge new facts into existing, deduplicating by id."""
    existing_ids = {f.id for f in existing}
    merged = list(existing)
    for f in new_facts:
        if f.id not in existing_ids:
            merged.append(f)
            existing_ids.add(f.id)
    return merged


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"```(?:json)?", "", text).strip("` \n")
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
