from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

# Example JSON representation of a CouncilResponse
EXAMPLE_JSON = """{
  "model": "gpt-4o",
  "role": "creator",
  "prompt": "Create an interactive lesson about photosynthesis for a visual learner...",
  "reasoning": "Designed with visually structured headings and structured steps...",
  "strengths": [
    "Strong visual metaphors",
    "Structured progression of concepts",
    "Clear active learning tasks"
  ],
  "metadata": {
    "tokens_used": 850,
    "response_time": 1.45,
    "provider_version": "gpt-4o-2024-05-13"
  },
  "score": {
    "clarity": 0.95,
    "structure": 0.90,
    "personalization": 0.88,
    "educational_effectiveness": 0.92,
    "depth": 0.80,
    "overall_score": 0.9035
  }
}"""


class ResponseMetadata(BaseModel):
    """Metadata detailing execution and resource usage statistics for a council response."""

    tokens_used: Optional[int] = Field(
        None,
        description="Total number of tokens consumed by the provider during generation",
        ge=0,
    )
    response_time: Optional[float] = Field(
        None,
        description="Time taken by the provider to generate the response in seconds",
        ge=0.0,
    )
    provider_version: Optional[str] = Field(
        None,
        description="Version string of the specific provider model used",
    )


class ResponseScore(BaseModel):
    """Quality metrics evaluated for a council response."""

    clarity: Optional[float] = Field(
        None,
        description="Clarity and readability score of the prompt, normalized from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    structure: Optional[float] = Field(
        None,
        description="Structural and formatting quality score of the prompt, normalized from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    personalization: Optional[float] = Field(
        None,
        description="Adaptation and alignment score to learning styles and profile, normalized from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    depth: Optional[float] = Field(
        None,
        description="Conceptual depth and richness score of the prompt, normalized from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    educational_effectiveness: Optional[float] = Field(
        None,
        description="Pedagogical and learning outcomes alignment score, normalized from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    overall_score: Optional[float] = Field(
        None,
        description="Weighted overall quality score, normalized from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )

    def calculate_overall_score(self) -> float:
        """Calculate and update the overall score using weighted category scores.

        Formula:
            overall_score = (clarity * 0.25) +
                            (structure * 0.20) +
                            (personalization * 0.20) +
                            (educational_effectiveness * 0.25) +
                            (depth * 0.10)

        If a category score is None, it is treated as 0.0.
        Updates the `overall_score` attribute and returns the calculated value.
        """
        c = self.clarity or 0.0
        s = self.structure or 0.0
        p = self.personalization or 0.0
        e = self.educational_effectiveness or 0.0
        d = self.depth or 0.0

        overall = (c * 0.25) + (s * 0.20) + (p * 0.20) + (e * 0.25) + (d * 0.10)
        overall = round(overall, 4)
        self.overall_score = overall
        return overall


class CouncilResponse(BaseModel):
    """Standardized response schema returned by each AI provider in the AI Council."""

    model: str = Field(
        ...,
        description="The AI provider model name (e.g. gpt-4o, claude-3-5-sonnet, gemini-1.5-pro, deepseek-chat)",
    )
    role: str = Field(
        ...,
        description="The specific role assigned to the council member (e.g., creator, validator, refiner)",
    )
    prompt: str = Field(
        ...,
        description="The generated prompt text returned by the model",
    )
    reasoning: str = Field(
        ...,
        description="The internal reasoning/rationale provided by the model explaining its response",
    )
    strengths: List[str] = Field(
        ...,
        description="List of key pedagogical or structural strengths identified in the response",
    )
    metadata: Optional[ResponseMetadata] = Field(
        default_factory=ResponseMetadata,
        description="Execution statistics and model version details",
    )
    score: Optional[ResponseScore] = Field(
        default_factory=ResponseScore,
        description="Evaluated quality scores for the response across core dimensions",
    )

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate that the model name belongs to one of the approved council providers."""
        v_lower = v.lower()
        valid_providers = ["gpt", "claude", "gemini", "deepseek"]
        if not any(provider in v_lower for provider in valid_providers):
            raise ValueError(
                f"Model '{v}' must be associated with one of the approved council providers: "
                f"{', '.join(valid_providers)}"
            )
        return v

    @field_validator("role", "prompt", "reasoning")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        """Validate that textual fields are non-empty and contain content."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return v

    @field_validator("strengths")
    @classmethod
    def validate_strengths(cls, v: List[str]) -> List[str]:
        """Validate that strengths contains at least one strength and all strengths are non-empty."""
        if not v:
            raise ValueError("Strengths list cannot be empty.")
        for strength in v:
            if not strength or not strength.strip():
                raise ValueError("Strengths must be non-empty strings.")
        return v

    def calculate_overall_score(self) -> float:
        """Calculate and update the overall score of the response.

        Delegates calculation to the nested ResponseScore model. If the score
        model is not initialized, it initializes it first.
        """
        if self.score is None:
            self.score = ResponseScore()
        return self.score.calculate_overall_score()

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """Convert the council response instance to a clean Python dictionary.

        Supports both Pydantic v1 (using `.dict()`) and v2 (using `.model_dump()`)
        for backward compatibility.
        """
        if hasattr(self, "model_dump"):
            return self.model_dump(**kwargs)
        return self.dict(**kwargs)

    model_config = {
        "json_schema_extra": {
            "example": {
                "model": "gpt-4o",
                "role": "creator",
                "prompt": "Create an interactive lesson about photosynthesis for a visual learner...",
                "reasoning": "Designed with visually structured headings and structured steps...",
                "strengths": [
                    "Strong visual metaphors",
                    "Structured progression of concepts",
                    "Clear active learning tasks"
                ],
                "metadata": {
                    "tokens_used": 850,
                    "response_time": 1.45,
                    "provider_version": "gpt-4o-2024-05-13"
                },
                "score": {
                    "clarity": 0.95,
                    "structure": 0.90,
                    "personalization": 0.88,
                    "educational_effectiveness": 0.92,
                    "depth": 0.80,
                    "overall_score": 0.9035
                }
            }
        }
    }


# ==============================================================================
# Database ORM Model
# ==============================================================================

class CouncilResponseDB(Base):
    """A single council member's response to a prompt request stored in the database.

    Responsibilities:
    - Store the generated prompt, reasoning and metadata from a model/role
    - Belongs to a PromptRequest (many responses per request)
    """

    __tablename__ = "council_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("prompt_requests.id"), nullable=False, index=True)

    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship back to the prompt request
    request: Mapped["PromptRequest"] = relationship("PromptRequest", back_populates="council_responses")
