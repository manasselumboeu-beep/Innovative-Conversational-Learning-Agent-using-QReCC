"""
Deterministic pedagogical business rules — pure Python, zero LLM cost.
Each gate raises ValueError with a descriptive message on violation.
"""

from schemas.confusion import ConfusionSignal
from schemas.classification import QuestionClassification
from schemas.memory import LearnerState, MemoryUpdate
from schemas.style import StyleSelection


STYLE_LEVELS = {"foundation": 0, "standard": 1, "expert": 2}


def gate_style_selection(
    selection: StyleSelection, current_state: LearnerState
) -> StyleSelection:
    """
    - Expert is blocked when confusion_count_last_5 > 0.
    - Style cannot rise more than one level per turn.
    """
    current_level = STYLE_LEVELS.get(current_state.current_style, 1)
    proposed_level = STYLE_LEVELS.get(selection.style, 1)

    if selection.style == "expert" and current_state.confusion_count_last_5 > 0:
        # Clamp to standard instead of raising — silent correction
        return StyleSelection(
            style="standard",
            reason="confusion_detected",
            skill_path=selection.skill_path.replace("expert", "standard"),
        )

    if proposed_level - current_level > 1:
        # Cap the rise to exactly one level
        capped_level = current_level + 1
        capped_style = [k for k, v in STYLE_LEVELS.items() if v == capped_level][0]
        return StyleSelection(
            style=capped_style,
            reason=selection.reason,
            skill_path=selection.skill_path.replace(selection.style, capped_style),
        )

    return selection


def gate_proficiency_change(new_estimate: float, current_estimate: float) -> float:
    """Proficiency estimate cannot change by more than 0.2 per turn."""
    delta = new_estimate - current_estimate
    if abs(delta) > 0.2:
        clamped = current_estimate + (0.2 if delta > 0 else -0.2)
        return round(max(0.0, min(1.0, clamped)), 4)
    return round(max(0.0, min(1.0, new_estimate)), 4)


def gate_confusion_signal(
    signal: ConfusionSignal, turn_history_len: int
) -> ConfusionSignal:
    """
    - trigger_turn must be a valid index in turn_history.
    - evidence_phrase should exist (enforced at schema level; here we validate index).
    """
    if signal.confused and signal.trigger_turn is not None:
        if signal.trigger_turn < 0 or signal.trigger_turn >= turn_history_len:
            # Clamp to the most recent valid turn instead of hard-failing
            signal = signal.model_copy(
                update={"trigger_turn": max(0, turn_history_len - 1)}
            )
    return signal


def gate_classification(
    classification: QuestionClassification, question: str
) -> QuestionClassification:
    """
    A self_contained classification on a question beginning with
    'it', 'that', 'they', 'this' is downgraded to resolvable.
    """
    pronoun_starters = {"it", "that", "they", "this", "he", "she", "its", "their"}
    first_word = question.strip().split()[0].lower().rstrip("'s") if question.strip() else ""

    if (
        classification.question_type == "self_contained"
        and first_word in pronoun_starters
    ):
        return QuestionClassification(
            question_type="resolvable",
            needs_rewrite=True,
            needs_clarification=False,
            # Use existing rewrite if available, else keep original for clarity engine to rewrite
            rewritten_question=classification.rewritten_question or question,
        )
    return classification


def gate_memory_update(
    update: MemoryUpdate, existing_facts: list
) -> MemoryUpdate:
    """
    - Max 5 new facts per turn (enforced by schema too; belt-and-suspenders).
    - No duplicate fact IDs.
    """
    existing_ids = {f.id for f in existing_facts}
    deduped = [f for f in update.new_facts if f.id not in existing_ids]
    capped = deduped[:5]
    return MemoryUpdate(new_facts=capped)


def gate_comprehension_check(turn_history: list) -> bool:
    """Return True if a comprehension check is appropriate this turn.
    Rules: max one check per 3-turn window; not if last 3 turns had one.
    """
    if len(turn_history) < 3:
        return False
    last_three = turn_history[-3:]
    if any(t.had_comprehension_check for t in last_three):
        return False
    return True


def gate_cited_facts(cited_ids: list[str], known_ids: set[str]) -> list[str]:
    """A cited fact ID must exist in known_facts; remove unknown citations."""
    return [fid for fid in cited_ids if fid in known_ids]
