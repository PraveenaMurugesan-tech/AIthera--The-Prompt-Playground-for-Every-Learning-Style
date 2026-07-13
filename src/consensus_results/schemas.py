from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ConsensusResultCreate(BaseModel):
    request_id: int
    final_prompt: Optional[str] = None
    quality_score: Optional[float] = None
    consensus_reasoning: Optional[str] = None
    combined_strengths: Optional[List[str]] = None
    contributors: Optional[List[str]] = None
    response_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ConsensusResultOut(BaseModel):
    id: int
    request_id: int
    final_prompt: Optional[str] = None
    quality_score: Optional[float] = None
    consensus_reasoning: Optional[str] = None
    combined_strengths: Optional[List[str]] = None
    contributors: Optional[List[str]] = None
    response_count: Optional[int] = None
    response_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
