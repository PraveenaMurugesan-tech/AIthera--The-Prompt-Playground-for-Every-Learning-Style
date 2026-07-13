from typing import List, Optional
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.council_response import CouncilResponseDB


def create_council_response(
    db: Session,
    request_id: int,
    model: str,
    role: str,
    prompt: str,
    reasoning: str,
    strengths: list[str],
    metadata: Optional[dict] = None,
) -> CouncilResponseDB:
    """Create and persist a CouncilResponse tied to a PromptRequest."""

    strengths_json = json.dumps(strengths) if strengths is not None else None

    response = CouncilResponseDB(
        request_id=request_id,
        model=model,
        role=role,
        prompt=prompt,
        reasoning=reasoning,
        strengths=strengths_json,
        response_metadata=metadata,
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return response


def get_council_responses_by_request(db: Session, request_id: int) -> List[CouncilResponseDB]:
    """Return all CouncilResponse rows for a given PromptRequest."""

    stmt = select(CouncilResponseDB).where(CouncilResponseDB.request_id == request_id).order_by(CouncilResponseDB.created_at.desc())

    return db.execute(stmt).scalars().all()
