from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, delete as sa_delete

from src.models.prompt_request import PromptRequest


import datetime

def create_prompt_request(
    db: Session, user_id: int, topic: str, learning_style: str, difficulty: str, bloom_level: str = "understand"
) -> PromptRequest:
    """Create and persist a new PromptRequest, avoiding duplicates within 10 seconds."""
    
    stmt = (
        select(PromptRequest)
        .where(PromptRequest.user_id == user_id)
        .where(PromptRequest.topic == topic)
        .where(PromptRequest.learning_style == learning_style)
        .where(PromptRequest.difficulty == difficulty)
        .where(PromptRequest.bloom_level == bloom_level)
        .order_by(PromptRequest.id.desc())
    )
    recent = db.execute(stmt).scalars().first()
    
    if recent and recent.created_at:
        now = datetime.datetime.now(datetime.timezone.utc)
        created_at = recent.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=datetime.timezone.utc)
            
        if (now - created_at).total_seconds() < 10:
            return recent

    request = PromptRequest(
        user_id=user_id,
        topic=topic,
        learning_style=learning_style,
        difficulty=difficulty,
        bloom_level=bloom_level,
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


def get_prompt_request_owner(db: Session, request_id: int) -> Optional[int]:
    """Return the `user_id` owner for a PromptRequest id, or None if not found.

    This performs a lightweight query selecting only the `user_id` column to avoid
    loading the full ORM object and any related collections which could trigger
    lazy-loads against missing tables.
    """

    stmt = select(PromptRequest.user_id).where(PromptRequest.id == request_id)
    row = db.execute(stmt).first()
    if not row:
        return None
    return int(row[0])


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

    stmt = sa_delete(PromptRequest).where(PromptRequest.id == request_id)
    result = db.execute(stmt)
    db.commit()

    return (result.rowcount or 0) > 0


def clear_user_prompt_requests(db: Session, user_id: int) -> int:
    """Delete all PromptRequests for a user."""
    
    stmt = sa_delete(PromptRequest).where(PromptRequest.user_id == user_id)
    result = db.execute(stmt)
    db.commit()
    
    return result.rowcount or 0


def generate_and_save_prompt(db: Session, request_id: int, generated_prompt: str) -> Optional[PromptRequest]:
    """Convenience helper to save a generated prompt to a PromptRequest.

    Returns the updated PromptRequest or `None` if not found.
    """

    return update_generated_prompt(db=db, request_id=request_id, generated_prompt=generated_prompt)
