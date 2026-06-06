from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Label = Literal["human", "bot", "human_imitating_bot", "bot_imitating_human"]

LABELS: tuple[Label, ...] = (
    "human",
    "bot",
    "human_imitating_bot",
    "bot_imitating_human",
)


class ParticipantLabel(str, Enum):
    human = "human"
    bot = "bot"
    human_imitating_bot = "human_imitating_bot"
    bot_imitating_human = "bot_imitating_human"


class ClassificationResult(BaseModel):
    username: str
    label: Label
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    cues: list[str] = Field(default_factory=list)
    low_evidence: bool = False
    mode: str = "hybrid"

    @field_validator("label", mode="before")
    @classmethod
    def normalize_label(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower().replace(" ", "_").replace("-", "_")
        return v


class ThreadAnalysis(BaseModel):
    participants: list[ClassificationResult]
    dead_internet_index: float
    label_counts: dict[str, int]
