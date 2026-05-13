from typing import Literal, Optional
from pydantic import BaseModel, model_validator


class QuestionClassification(BaseModel):
    question_type: Literal["self_contained", "resolvable", "confusion_indicating"]
    needs_rewrite: bool
    needs_clarification: bool
    rewritten_question: Optional[str] = None
    clarification_prompt: Optional[str] = None

    @model_validator(mode="after")
    def check_mutual_exclusion(self):
        if self.needs_clarification and self.question_type == "confusion_indicating":
            raise ValueError(
                "needs_clarification and confusion_indicating cannot both be true"
            )
        if self.needs_rewrite and self.rewritten_question is None:
            raise ValueError("rewritten_question required when needs_rewrite is True")
        if self.needs_clarification and self.clarification_prompt is None:
            raise ValueError(
                "clarification_prompt required when needs_clarification is True"
            )
        return self
