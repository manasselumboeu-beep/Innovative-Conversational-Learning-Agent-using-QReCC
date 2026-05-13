
import pytest
from api.pipeline import _classify_heuristic
from modules.adaptive_teacher import build_system_prompt
from schemas.memory import LearnerState, TurnRecord
from schemas.style import StyleSelection
from schemas.confusion import ConfusionSignal

def test_what_does_it_do_heuristic():
    history = [
        TurnRecord(
            question="i mean in calculus",
            rewritten="i mean in calculus",
            answer="A derivative measures how fast something is changing...",
            had_comprehension_check=False
        )
    ]
    question = "what does it do"
    classification = _classify_heuristic(question, history)
    
    assert classification.question_type == "resolvable"
    assert classification.needs_rewrite is True
    assert "referring to i mean in calculus" in classification.rewritten_question

def test_history_in_system_prompt():
    state = LearnerState(
        turn_history=[
            TurnRecord(
                question="What is a derivative?",
                rewritten="What is a derivative?",
                answer="It measures rate of change.",
                had_comprehension_check=False
            )
        ]
    )
    style = StyleSelection(style="standard", reason="default", skill_path="explanation/standard/SKILL.md")
    confusion = ConfusionSignal(confused=False, type="none")
    
    prompt = build_system_prompt(style, confusion, state, False)
    
    assert "## Recent Conversation" in prompt
    assert "Student: What is a derivative?" in prompt
    assert "Tutor: It measures rate of change." in prompt

def test_how_does_it_work_heuristic():
    history = [TurnRecord(question="Tell me about gravity", rewritten="Tell me about gravity", answer="Gravity is...", had_comprehension_check=False)]
    question = "how does it work"
    classification = _classify_heuristic(question, history)
    
    assert classification.question_type == "resolvable"
    assert classification.needs_rewrite is True
    assert "referring to Tell me about gravity" in classification.rewritten_question
