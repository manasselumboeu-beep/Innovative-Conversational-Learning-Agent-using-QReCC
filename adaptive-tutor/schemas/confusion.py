from typing import Literal, Optional
from pydantic import BaseModel, model_validator


class ConfusionSignal(BaseModel):
    confused: bool
    type: Literal["repetition", "vague", "contradiction", "scope", "none"]
    trigger_turn: Optional[int] = None
    evidence_phrase: Optional[str] = None

    @model_validator(mode="after")
    def validate_consistency(self):
        if self.confused:
            if self.trigger_turn is None:
                raise ValueError("trigger_turn is required when confused is True")
            if self.type == "none":
                raise ValueError("type cannot be 'none' when confused is True")
        else:
            if self.type != "none":
                raise ValueError("type must be 'none' when confused is False")
        return self
