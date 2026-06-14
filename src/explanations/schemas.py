from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExplanationOut(BaseModel):
    """Representation of an Explanation returned by the API."""

    id: int
    request_id: int
    content: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
