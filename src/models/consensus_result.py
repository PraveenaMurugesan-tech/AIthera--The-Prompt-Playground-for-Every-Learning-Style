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

    # Phase 2 Synthesis Fields
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    educational_structure_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    synthesized_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    synthesized_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    merged_strengths: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    unique_concepts: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    conflicting_concepts: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    provider_contributions: Mapped[Optional[Dict[str, list[str]]]] = mapped_column(JSON, nullable=True)

    # Phase 3 Fields
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diversity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    diversity_level: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coverage_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    educational_sections: Mapped[Optional[Dict[str, bool]]] = mapped_column(JSON, nullable=True)
    learning_style_verification: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    confidence_level: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Phase 4 Production Metrics
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    provider_execution_times: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    parallel_efficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cache_hit: Mapped[Optional[bool]] = mapped_column(JSON, nullable=True) # JSON allows True/False neatly or Boolean
    retry_stats: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False)

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
            "confidence_score": self.confidence_score,
            "educational_structure_score": self.educational_structure_score,
            "synthesized_prompt": self.synthesized_prompt,
            "synthesized_reasoning": self.synthesized_reasoning,
            "merged_strengths": self.merged_strengths,
            "unique_concepts": self.unique_concepts,
            "conflicting_concepts": self.conflicting_concepts,
            "provider_contributions": self.provider_contributions,
            "explanation": self.explanation,
            "diversity_score": self.diversity_score,
            "diversity_level": self.diversity_level,
            "coverage_score": self.coverage_score,
            "educational_sections": self.educational_sections,
            "learning_style_verification": self.learning_style_verification,
            "confidence_level": self.confidence_level,
            "evaluation_summary": self.evaluation_summary,
            "execution_time": self.execution_time,
            "provider_execution_times": self.provider_execution_times,
            "parallel_efficiency": self.parallel_efficiency,
            "cache_hit": self.cache_hit,
            "retry_stats": self.retry_stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
