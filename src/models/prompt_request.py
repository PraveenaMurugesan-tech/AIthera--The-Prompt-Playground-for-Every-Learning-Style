from __future__ import annotations

from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class PromptRequest(Base):
    """User-created prompt request."""

    __tablename__ = "prompt_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    learning_style: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)

    generated_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="prompt_requests",
    )

    council_responses: Mapped[List["CouncilResponseDB"]] = relationship(
        "CouncilResponseDB",
        back_populates="request",
        cascade="all, delete-orphan",
    )

    consensus_result: Mapped[Optional["ConsensusResult"]] = relationship(
        "ConsensusResult",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan",
    )

    explanation: Mapped[Optional["Explanation"]] = relationship(
        "Explanation",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan",
    )