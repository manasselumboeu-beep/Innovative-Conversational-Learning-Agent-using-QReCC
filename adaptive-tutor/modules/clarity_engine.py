"""
Module 2 — Proactive Question Clarity Engine.
Three-way classification: self_contained / resolvable / confusion_indicating.
"""

import re
import json
import logging

from schemas.classification import QuestionClassification
from schemas.memory import TurnRecord
from validators.logic_gates import gate_classification
from modules.skill_loader import load_meta_skill

logger = logging.getLogger(__name__)


def classify_question(
    question: str,
    turn_history: list[TurnRecord],
    hf_client,
) -> QuestionClassification:
    """Classify the question and optionally rewrite or request clarification."""
    skill = load_meta_skill("question_classification")

    history_text = "\n".join(
        f"Turn {i}: Q: {t.question} | A: {t.answer[:200]}"
        for i, t in enumerate(turn_history[-4:])
    ) if turn_history else "No prior turns."

    # Build recent topics for clarification options
    recent_topics = []
    for t in reversed(turn_history[-2:]):
        recent_topics.append(t.rewritten or t.question)

    clarification_hint = ""
    if len(recent_topics) >= 2:
        clarification_hint = (
            f"\nRecent topics for clarification options: "
            f"'{recent_topics[0]}' or '{recent_topics[1]}'"
        )

    prompt = (
        f"{skill}\n\n"
        f"Conversation history:\n{history_text}{clarification_hint}\n\n"
        f"Student's current question: {question}\n\n"
        "Return ONLY the JSON object."
    )

    raw = hf_client.generate(prompt, max_tokens=300, temperature=0.0)
    try:
        data = _extract_json(raw)
        classification = QuestionClassification(**data)
        classification = gate_classification(classification, question)
        return classification
    except Exception as exc:
        logger.warning("clarity LLM parse failed: %s — treating as self_contained", exc)
        return QuestionClassification(
            question_type="self_contained",
            needs_rewrite=False,
            needs_clarification=False,
        )


def get_working_question(classification: QuestionClassification, original: str) -> str:
    """Return the question to send to generation, after rewriting if needed."""
    if classification.needs_rewrite and classification.rewritten_question:
        return classification.rewritten_question
    return original


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"```(?:json)?", "", text).strip("` \n")
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
