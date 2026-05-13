"""
Module 3 — Adaptive Teaching Behaviour.
Deterministic proficiency estimation + SKILL.md injection.
No LLM call for style selection.
"""

import re
import logging

from schemas.memory import LearnerState
from schemas.style import StyleSelection
from schemas.confusion import ConfusionSignal
from validators.logic_gates import gate_style_selection, gate_proficiency_change
from modules.skill_loader import (
    load_index,
    load_explanation_skill,
    load_interaction_skill,
)

logger = logging.getLogger(__name__)


def _readability_score(text: str) -> float:
    """Rough vocabulary complexity: fraction of words > 8 chars."""
    words = re.findall(r"\b[a-zA-Z]+\b", text)
    if not words:
        return 0.0
    long_words = sum(1 for w in words if len(w) > 8)
    return long_words / len(words)


def estimate_proficiency(state: LearnerState, question: str) -> float:
    """Deterministic proficiency estimation — zero LLM cost."""
    current = state.proficiency_estimate

    # Confusion strongly pulls proficiency down
    if state.confusion_count_last_5 > 0:
        adjustment = -0.1 * state.confusion_count_last_5
    else:
        # Three+ stable turns → slight upward drift
        stable_turns = sum(
            1 for t in state.turn_history[-3:] if t.confusion_type == "none"
        )
        adjustment = 0.05 * stable_turns

    # Vocabulary complexity of the question shifts estimate
    vocab_score = _readability_score(question)
    adjustment += (vocab_score - 0.15) * 0.1

    # Early turns: stay near default
    if len(state.turn_history) < 2:
        return 0.5

    new_estimate = current + adjustment
    return gate_proficiency_change(new_estimate, current)


def select_style(
    proficiency: float,
    state: LearnerState,
    confusion: ConfusionSignal,
) -> StyleSelection:
    """Select teaching style based on proficiency and confusion signal."""
    # Confusion always forces foundation
    if confusion.confused:
        raw = StyleSelection(
            style="foundation",
            reason="confusion_detected",
            skill_path="explanation/foundation/SKILL.md",
        )
    elif proficiency < 0.4 or state.confusion_count_last_5 > 0:
        raw = StyleSelection(
            style="foundation",
            reason="low_proficiency",
            skill_path="explanation/foundation/SKILL.md",
        )
    elif proficiency > 0.75:
        raw = StyleSelection(
            style="expert",
            reason="high_proficiency",
            skill_path="explanation/expert/SKILL.md",
        )
    else:
        raw = StyleSelection(
            style="standard",
            reason="default",
            skill_path="explanation/standard/SKILL.md",
        )

    return gate_style_selection(raw, state)


def build_system_prompt(
    style: StyleSelection,
    confusion: ConfusionSignal,
    state: LearnerState,
    inject_comprehension_check: bool,
) -> str:
    """Assemble the full system prompt by layering SKILL.md files."""
    parts = [load_index()]

    # If confusion was detected, prepend confusion-handling skill
    if confusion.confused:
        parts.append(load_interaction_skill("handle_confusion"))

    # Explanation style skill
    parts.append(load_explanation_skill(style.style))

    # Inject recent conversation history for context
    if state.turn_history:
        history_parts = []
        for turn in state.turn_history[-3:]:
            history_parts.append(f"Student: {turn.question}")
            history_parts.append(f"Tutor: {turn.answer}")
        
        parts.append(
            f"\n## Recent Conversation\n"
            f"Use this context to resolve pronouns and avoid repeating yourself:\n" + 
            "\n".join(history_parts)
        )

    # Inject known facts to prevent repetition
    if state.known_facts:
        fact_summaries = "\n".join(
            f"- {f.id}: {f.summary or '(known)'}" for f in state.known_facts
        )
        parts.append(
            f"\n## Already Known by Student\n"
            f"Do not re-explain these concepts — the student already knows them:\n{fact_summaries}"
        )

    # Comprehension check injection
    if inject_comprehension_check:
        parts.append(load_interaction_skill("comprehension_check"))

    return "\n\n---\n\n".join(p for p in parts if p)
