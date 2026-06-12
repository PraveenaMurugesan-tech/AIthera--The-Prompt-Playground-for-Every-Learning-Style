from __future__ import annotations
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class Explanation(Base):
    """Explanation produced for a prompt request.

    Responsibilities:
    - Store human-readable explanation or rationale for the final prompt
    - One-to-one relationship with PromptRequest
    """

    __tablename__ = "explanations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("prompt_requests.id"), nullable=False, unique=True)

    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # One-to-one back to the request
    request: Mapped["PromptRequest"] = relationship("PromptRequest", back_populates="explanation")
