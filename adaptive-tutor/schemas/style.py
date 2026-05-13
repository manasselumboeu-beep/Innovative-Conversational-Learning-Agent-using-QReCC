from typing import Literal
from pydantic import BaseModel


class StyleSelection(BaseModel):
    style: Literal["foundation", "standard", "expert"]
    reason: Literal[
        "confusion_detected",
        "low_proficiency",
        "high_proficiency",
        "default",
    ]
    skill_path: str
