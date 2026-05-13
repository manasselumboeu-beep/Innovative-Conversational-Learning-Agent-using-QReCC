import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from schemas.confusion import ConfusionSignal
from schemas.classification import QuestionClassification
from schemas.memory import LearnerState, MemoryUpdate, Fact, TurnRecord
from schemas.style import StyleSelection
from validators.logic_gates import (
    gate_style_selection,
    gate_proficiency_change,
    gate_confusion_signal,
    gate_classification,
    gate_memory_update,
    gate_comprehension_check,
    gate_cited_facts,
)


class TestGateStyleSelection:
    def _state(self, style="standard", confusion=0):
        return LearnerState(current_style=style, confusion_count_last_5=confusion)

    def test_expert_blocked_when_confused(self):
        sel = StyleSelection(style="expert", reason="high_proficiency", skill_path="skills/explanation/expert/SKILL.md")
        state = self._state(style="standard", confusion=1)
        result = gate_style_selection(sel, state)
        assert result.style == "standard"
        assert result.reason == "confusion_detected"

    def test_max_one_level_rise(self):
        sel = StyleSelection(style="expert", reason="high_proficiency", skill_path="skills/explanation/expert/SKILL.md")
        state = self._state(style="foundation", confusion=0)
        result = gate_style_selection(sel, state)
        assert result.style == "standard"

    def test_valid_one_level_rise(self):
        sel = StyleSelection(style="standard", reason="default", skill_path="skills/explanation/standard/SKILL.md")
        state = self._state(style="foundation", confusion=0)
        result = gate_style_selection(sel, state)
        assert result.style == "standard"

    def test_same_level_passes(self):
        sel = StyleSelection(style="expert", reason="high_proficiency", skill_path="skills/explanation/expert/SKILL.md")
        state = self._state(style="expert", confusion=0)
        result = gate_style_selection(sel, state)
        assert result.style == "expert"

    def test_drop_passes(self):
        sel = StyleSelection(style="foundation", reason="confusion_detected", skill_path="skills/explanation/foundation/SKILL.md")
        state = self._state(style="expert", confusion=1)
        result = gate_style_selection(sel, state)
        assert result.style == "foundation"


class TestGateProficiencyChange:
    def test_clamps_upward(self):
        result = gate_proficiency_change(0.9, 0.5)
        assert result == 0.7

    def test_clamps_downward(self):
        result = gate_proficiency_change(0.1, 0.5)
        assert result == 0.3

    def test_small_change_passes(self):
        result = gate_proficiency_change(0.6, 0.5)
        assert result == 0.6

    def test_clamps_to_zero(self):
        result = gate_proficiency_change(-0.5, 0.1)
        assert result == 0.0

    def test_clamps_to_one(self):
        result = gate_proficiency_change(1.5, 0.9)
        assert result == 1.0


class TestGateConfusionSignal:
    def test_valid_trigger_passes(self):
        sig = ConfusionSignal(confused=True, type="vague", trigger_turn=2)
        result = gate_confusion_signal(sig, turn_history_len=3)
        assert result.trigger_turn == 2

    def test_out_of_bounds_trigger_clamped(self):
        sig = ConfusionSignal(confused=True, type="vague", trigger_turn=10)
        result = gate_confusion_signal(sig, turn_history_len=3)
        assert result.trigger_turn == 2

    def test_not_confused_passes(self):
        sig = ConfusionSignal(confused=False, type="none")
        result = gate_confusion_signal(sig, turn_history_len=5)
        assert not result.confused


class TestGateClassification:
    def test_self_contained_with_pronoun_downgraded(self):
        qc = QuestionClassification(
            question_type="self_contained",
            needs_rewrite=False,
            needs_clarification=False,
        )
        result = gate_classification(qc, "It moves through the membrane?")
        assert result.question_type == "resolvable"
        assert result.needs_rewrite is True

    def test_self_contained_no_pronoun_passes(self):
        qc = QuestionClassification(
            question_type="self_contained",
            needs_rewrite=False,
            needs_clarification=False,
        )
        result = gate_classification(qc, "What is photosynthesis?")
        assert result.question_type == "self_contained"

    def test_resolvable_unchanged(self):
        qc = QuestionClassification(
            question_type="resolvable",
            needs_rewrite=True,
            needs_clarification=False,
            rewritten_question="What does ATP do in cellular respiration?",
        )
        result = gate_classification(qc, "What does it do in respiration?")
        assert result.question_type == "resolvable"


_IDS = ["fact_alpha", "fact_beta", "fact_gamma", "fact_delta", "fact_epsilon", "fact_zeta", "fact_theta"]


class TestGateMemoryUpdate:
    def _make_fact(self, fid):
        return Fact(id=fid, turn=1, confidence=0.8)

    def test_deduplication(self):
        existing = [self._make_fact("photosynthesis_overview")]
        update = MemoryUpdate(new_facts=[self._make_fact("photosynthesis_overview"), self._make_fact("chlorophyll_role")])
        result = gate_memory_update(update, existing)
        assert len(result.new_facts) == 1
        assert result.new_facts[0].id == "chlorophyll_role"

    def test_caps_at_five(self):
        existing = []
        facts = [self._make_fact(_IDS[i]) for i in range(5)]
        update = MemoryUpdate(new_facts=facts)
        result = gate_memory_update(update, existing)
        assert len(result.new_facts) <= 5


class TestGateComprehensionCheck:
    def _turn(self, had_check=False):
        return TurnRecord(
            question="q", rewritten="q", answer="a",
            had_comprehension_check=had_check
        )

    def test_fires_after_three_clean_turns(self):
        history = [self._turn(), self._turn(), self._turn()]
        assert gate_comprehension_check(history) is True

    def test_does_not_fire_if_recent_check(self):
        history = [self._turn(), self._turn(had_check=True), self._turn()]
        assert gate_comprehension_check(history) is False

    def test_does_not_fire_on_short_history(self):
        assert gate_comprehension_check([self._turn(), self._turn()]) is False


class TestGateCitedFacts:
    def test_removes_unknown_ids(self):
        known = {"fact_aaa", "fact_bbb"}
        result = gate_cited_facts(["fact_aaa", "fact_zzz"], known)
        assert result == ["fact_aaa"]

    def test_all_known_passes(self):
        known = {"fact_aaa", "fact_bbb"}
        result = gate_cited_facts(["fact_aaa", "fact_bbb"], known)
        assert set(result) == known
