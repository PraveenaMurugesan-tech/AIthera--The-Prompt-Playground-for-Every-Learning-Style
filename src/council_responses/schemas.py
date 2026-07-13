from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CouncilResponseCreate(BaseModel):
    request_id: int
    model: str
    role: str
    prompt: str
    reasoning: str
    strengths: List[str]
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CouncilResponseOut(BaseModel):
    id: int
    request_id: int
    model: Optional[str]
    role: Optional[str]
    prompt: Optional[str]
    reasoning: Optional[str]
    strengths: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
