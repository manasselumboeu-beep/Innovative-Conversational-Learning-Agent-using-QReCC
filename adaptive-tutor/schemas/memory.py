import re
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

CONCEPT_ID_PATTERN = re.compile(r"^[a-z][a-z_]{2,40}$")


class Fact(BaseModel):
    id: str
    turn: int
    confidence: float
    summary: Optional[str] = None

    @field_validator("id")
    @classmethod
    def validate_concept_id(cls, v):
        if not CONCEPT_ID_PATTERN.match(v):
            raise ValueError(
                f"concept id '{v}' must match ^[a-z][a-z_]{{2,40}}$"
            )
        return v

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v

    @field_validator("turn")
    @classmethod
    def validate_turn(cls, v):
        if v < 0:
            raise ValueError("turn must be non-negative")
        return v


class MemoryUpdate(BaseModel):
    new_facts: list[Fact]

    @field_validator("new_facts")
    @classmethod
    def max_five_facts(cls, v):
        if len(v) > 5:
            raise ValueError("Cannot add more than 5 new facts per turn")
        return v


class TurnRecord(BaseModel):
    question: str
    rewritten: str
    answer: str
    had_comprehension_check: bool
    confusion_type: str = "none"


class LearnerState(BaseModel):
    known_facts: list[Fact] = []
    confusion_count_last_5: int = 0
    current_style: str = "standard"
    turn_history: list[TurnRecord] = []
    proficiency_estimate: float = 0.5

    @field_validator("confusion_count_last_5")
    @classmethod
    def validate_confusion_count(cls, v):
        if not 0 <= v <= 5:
            raise ValueError("confusion_count_last_5 must be between 0 and 5")
        return v

    @field_validator("proficiency_estimate")
    @classmethod
    def validate_proficiency(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("proficiency_estimate must be between 0.0 and 1.0")
        return v

    @model_validator(mode="after")
    def validate_style(self):
        valid_styles = {"foundation", "standard", "expert"}
        if self.current_style not in valid_styles:
            raise ValueError(f"current_style must be one of {valid_styles}")
        return self
