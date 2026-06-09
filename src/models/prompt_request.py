from __future__ import annotations
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class PromptRequest(Base):
    """Represents a user's prompt generation request.

    Responsibilities:
    - Store request parameters and status
    - Owns council responses (one-to-many)
    - Has a single consensus result and explanation (one-to-one)
    """

    __tablename__ = "prompt_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    objective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    learning_style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    education_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    output_length: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="pending")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="requests")

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
