import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pydantic import ValidationError

from schemas.confusion import ConfusionSignal
from schemas.classification import QuestionClassification
from schemas.memory import Fact, MemoryUpdate, LearnerState, TurnRecord
from schemas.style import StyleSelection
from schemas.response import TutorResponse


# ── ConfusionSignal ───────────────────────────────────────────────────────────

class TestConfusionSignal:
    def test_valid_not_confused(self):
        s = ConfusionSignal(confused=False, type="none")
        assert not s.confused

    def test_valid_confused(self):
        s = ConfusionSignal(confused=True, type="vague", trigger_turn=0)
        assert s.confused

    def test_confused_requires_trigger_turn(self):
        with pytest.raises(ValidationError):
            ConfusionSignal(confused=True, type="vague")

    def test_type_none_must_be_not_confused(self):
        with pytest.raises(ValidationError):
            ConfusionSignal(confused=True, type="none", trigger_turn=0)

    def test_type_not_none_requires_confused(self):
        with pytest.raises(ValidationError):
            ConfusionSignal(confused=False, type="repetition")

    def test_all_valid_types(self):
        for t in ["repetition", "vague", "contradiction", "scope"]:
            s = ConfusionSignal(confused=True, type=t, trigger_turn=1)
            assert s.type == t


# ── QuestionClassification ────────────────────────────────────────────────────

class TestQuestionClassification:
    def test_self_contained(self):
        qc = QuestionClassification(
            question_type="self_contained",
            needs_rewrite=False,
            needs_clarification=False,
        )
        assert qc.question_type == "self_contained"

    def test_resolvable_requires_rewritten(self):
        with pytest.raises(ValidationError):
            QuestionClassification(
                question_type="resolvable",
                needs_rewrite=True,
                needs_clarification=False,
                rewritten_question=None,
            )

    def test_clarification_requires_prompt(self):
        with pytest.raises(ValidationError):
            QuestionClassification(
                question_type="resolvable",
                needs_rewrite=False,
                needs_clarification=True,
                clarification_prompt=None,
            )

    def test_clarification_and_confusion_mutually_exclusive(self):
        with pytest.raises(ValidationError):
            QuestionClassification(
                question_type="confusion_indicating",
                needs_rewrite=False,
                needs_clarification=True,
                clarification_prompt="Are you asking about X or Y?",
            )


# ── Fact and MemoryUpdate ─────────────────────────────────────────────────────

class TestFact:
    def test_valid_fact(self):
        f = Fact(id="photosynthesis_overview", turn=2, confidence=0.9)
        assert f.id == "photosynthesis_overview"

    def test_invalid_concept_id_uppercase(self):
        with pytest.raises(ValidationError):
            Fact(id="PhotoSynthesis", turn=1, confidence=0.8)

    def test_invalid_concept_id_too_short(self):
        with pytest.raises(ValidationError):
            Fact(id="ab", turn=1, confidence=0.8)

    def test_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            Fact(id="test_fact", turn=1, confidence=1.5)

    def test_negative_turn_rejected(self):
        with pytest.raises(ValidationError):
            Fact(id="test_fact", turn=-1, confidence=0.9)


_TEST_IDS = ["fact_alpha", "fact_beta", "fact_gamma", "fact_delta", "fact_epsilon", "fact_zeta"]


class TestMemoryUpdate:
    def test_max_five_facts(self):
        facts = [Fact(id=_TEST_IDS[i], turn=1, confidence=0.8) for i in range(6)]
        with pytest.raises(ValidationError):
            MemoryUpdate(new_facts=facts)

    def test_five_facts_ok(self):
        facts = [Fact(id=_TEST_IDS[i], turn=1, confidence=0.8) for i in range(5)]
        m = MemoryUpdate(new_facts=facts)
        assert len(m.new_facts) == 5


# ── LearnerState ──────────────────────────────────────────────────────────────

class TestLearnerState:
    def test_defaults(self):
        s = LearnerState()
        assert s.current_style == "standard"
        assert s.confusion_count_last_5 == 0

    def test_invalid_style(self):
        with pytest.raises(ValidationError):
            LearnerState(current_style="intermediate")

    def test_confusion_count_out_of_range(self):
        with pytest.raises(ValidationError):
            LearnerState(confusion_count_last_5=6)

    def test_proficiency_out_of_range(self):
        with pytest.raises(ValidationError):
            LearnerState(proficiency_estimate=1.5)


# ── StyleSelection ────────────────────────────────────────────────────────────

class TestStyleSelection:
    def test_valid(self):
        s = StyleSelection(
            style="foundation",
            reason="confusion_detected",
            skill_path="skills/explanation/foundation/SKILL.md",
        )
        assert s.style == "foundation"

    def test_invalid_style(self):
        with pytest.raises(ValidationError):
            StyleSelection(style="beginner", reason="default", skill_path="x")

    def test_invalid_reason(self):
        with pytest.raises(ValidationError):
            StyleSelection(style="standard", reason="unknown_reason", skill_path="x")


# ── TutorResponse ─────────────────────────────────────────────────────────────

class TestTutorResponse:
    def test_valid(self):
        r = TutorResponse(answer_text="Great question! Here is the answer.")
        assert r.has_comprehension_check is False

    def test_empty_answer_rejected(self):
        with pytest.raises(ValidationError):
            TutorResponse(answer_text="")

    def test_whitespace_answer_rejected(self):
        with pytest.raises(ValidationError):
            TutorResponse(answer_text="   ")
