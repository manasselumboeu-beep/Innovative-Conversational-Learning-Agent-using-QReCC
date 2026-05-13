from typing import Optional
from pydantic import BaseModel, field_validator


class TutorResponse(BaseModel):
    answer_text: str
    cited_facts: list[str] = []
    has_comprehension_check: bool = False
    confusion_handled: bool = False
    style_used: str = "standard"
    debug_info: Optional[dict] = None

    @field_validator("answer_text")
    @classmethod
    def answer_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("answer_text cannot be empty")
        return v.strip()
