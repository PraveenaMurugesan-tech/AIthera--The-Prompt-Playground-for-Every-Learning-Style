from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.prompt_request import PromptRequest


def create_prompt_request(
    db: Session, user_id: int, topic: str, learning_style: str, difficulty: str
) -> PromptRequest:
    """Create and persist a new PromptRequest."""

    request = PromptRequest(
        user_id=user_id,
        topic=topic,
        learning_style=learning_style,
        difficulty=difficulty,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def get_prompt_request(db: Session, request_id: int) -> Optional[PromptRequest]:
    """Return a PromptRequest by id or None if not found."""

    stmt = select(PromptRequest).where(PromptRequest.id == request_id)
    return db.execute(stmt).scalars().first()


def get_user_prompt_requests(db: Session, user_id: int) -> List[PromptRequest]:
    """Return all PromptRequest rows for a user ordered by newest first."""

    stmt = (
        select(PromptRequest)
        .where(PromptRequest.user_id == user_id)
        .order_by(PromptRequest.created_at.desc())
    )

    return db.execute(stmt).scalars().all()


def update_generated_prompt(db: Session, request_id: int, generated_prompt: str) -> Optional[PromptRequest]:
    """Update the `generated_prompt` field for a PromptRequest."""

    request = get_prompt_request(db, request_id)

    if not request:
        return None

    request.generated_prompt = generated_prompt

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def delete_prompt_request(db: Session, request_id: int) -> bool:
    """Delete a PromptRequest by id. Returns True if deleted, False if not found."""

    request = get_prompt_request(db, request_id)

    if not request:
        return False

    db.delete(request)
    db.commit()

    return True
