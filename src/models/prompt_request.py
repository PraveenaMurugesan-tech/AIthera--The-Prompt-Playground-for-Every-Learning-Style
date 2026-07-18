from __future__ import annotations

from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class PromptRequest(Base):
    """User-created prompt request."""

    __tablename__ = "prompt_requests"

    def __init__(self, **kwargs):
        # Pop out fields that aren't database columns in the current schema
        self._objective = kwargs.pop("objective", None)
        self._education_level = kwargs.pop("education_level", None)
        self._output_length = kwargs.pop("output_length", None)
        self._bloom_level = kwargs.pop("bloom_level", None)
        self._status = kwargs.pop("status", "pending")
        super().__init__(**kwargs)

    @property
    def bloom_level(self):
        return getattr(self, "_bloom_level", None) or "understand"

    @bloom_level.setter
    def bloom_level(self, value):
        self._bloom_level = value

    @property
    def objective(self):
        return getattr(self, "_objective", None) or f"Learn {self.topic}"

    @objective.setter
    def objective(self, value):
        self._objective = value

    @property
    def education_level(self):
        return getattr(self, "_education_level", None) or self.difficulty

    @education_level.setter
    def education_level(self, value):
        self._education_level = value

    @property
    def output_length(self):
        return getattr(self, "_output_length", None) or "moderate"

    @output_length.setter
    def output_length(self, value):
        self._output_length = value

    @property
    def status(self):
        return getattr(self, "_status", None) or "pending"

    @status.setter
    def status(self, value):
        self._status = value

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    learning_style: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)

    generated_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
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