from __future__ import annotations
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from ..database.base import Base


class CouncilResponse(Base):
    """A single council member's response to a prompt request.

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
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship back to the prompt request
    request: Mapped["PromptRequest"] = relationship("PromptRequest", back_populates="council_responses")
