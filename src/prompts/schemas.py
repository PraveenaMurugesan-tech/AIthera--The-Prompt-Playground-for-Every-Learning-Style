from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PromptRequestCreate(BaseModel):
    """Input schema for creating a prompt request."""

    topic: str = Field(..., min_length=1, example="Photosynthesis overview")
    learning_style: str = Field(..., min_length=1, example="visual")
    difficulty: str = Field(..., min_length=1, example="beginner")

    model_config = ConfigDict(from_attributes=True)


class PromptRequestResponse(BaseModel):
    """Representation of a persisted PromptRequest returned by the API."""

    id: int
    user_id: int
    topic: str
    learning_style: str
    difficulty: str
    generated_prompt: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
