from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict

from src.optimizer.prompt_variants import PromptVariant
from src.optimizer.learning_path import LearningPath
from src.optimizer.recommendation_engine import Recommendation

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


class GeneratePromptRequest(BaseModel):
    """Input schema for the full AI generation pipeline."""
    
    topic: str = Field(..., min_length=1, example="Photosynthesis overview")
    learning_style: str = Field(..., min_length=1, example="visual")
    difficulty: str = Field(..., min_length=1, example="beginner")
    bloom_level: Optional[str] = Field("understand", example="understand")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Optional flags for controlling generation (e.g., skip_variants)"
    )


class GeneratePromptResponse(BaseModel):
    """Complete response returned by the /generate endpoint."""
    
    optimized_prompt: Optional[str] = None
    consensus_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
    agreement_score: Optional[float] = None
    provider_contributions: Optional[Dict[str, List[str]]] = None
    educational_metrics: Optional[Dict[str, Any]] = None
    explainability_metrics: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Recommendation]] = None
    learning_path: Optional[LearningPath] = None
    prompt_variants: Optional[List[PromptVariant]] = None

    model_config = ConfigDict(from_attributes=True)
