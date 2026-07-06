from __future__ import annotations
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Float, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from ..database.base import Base


class ConsensusResult(Base):
    """Final consensus outcome for a prompt request.

    Responsibilities:
    - Store the final prompt and an overall quality score
    - One-to-one relationship with PromptRequest
    """

    __tablename__ = "consensus_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("prompt_requests.id"), nullable=False, unique=True, index=True)

    final_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)

    consensus_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    combined_strengths: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    contributors: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    response_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    winner_provider: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    winner_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    agreement_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    learning_style_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_consensus_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    common_concepts: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    unique_contributions: Mapped[Optional[Dict[str, list[str]]]] = mapped_column(JSON, nullable=True)
    providers_used: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    failed_providers: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # One-to-one back to the request
    request: Mapped["PromptRequest"] = relationship("PromptRequest", back_populates="consensus_result", uselist=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert the consensus result instance to a clean Python dictionary.

        For serialization compatibility.
        """
        return {
            "id": self.id,
            "request_id": self.request_id,
            "final_prompt": self.final_prompt,
            "consensus_reasoning": self.consensus_reasoning,
            "combined_strengths": self.combined_strengths,
            "quality_score": self.quality_score,
            "contributors": self.contributors,
            "response_count": self.response_count,
            "winner_provider": self.winner_provider,
            "winner_model": self.winner_model,
            "prompt_score": self.prompt_score,
            "agreement_score": self.agreement_score,
            "learning_style_score": self.learning_style_score,
            "completeness_score": self.completeness_score,
            "overall_consensus_score": self.overall_consensus_score,
            "common_concepts": self.common_concepts,
            "unique_contributions": self.unique_contributions,
            "providers_used": self.providers_used,
            "failed_providers": self.failed_providers,
            "response_metadata": self.response_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
