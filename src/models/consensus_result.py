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
            "response_metadata": self.response_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
