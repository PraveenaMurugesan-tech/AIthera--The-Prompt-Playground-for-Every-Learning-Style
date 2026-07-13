from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.explanation import Explanation


def create_explanation(db: Session, request_id: int, content: str) -> Explanation:
    """Create an Explanation for a PromptRequest.

    If an Explanation already exists for the given request_id it will be
    returned instead of creating a duplicate (one explanation per request).
    """

    # Check for existing explanation
    existing = get_explanation_by_request(db=db, request_id=request_id)

    if existing:
        return existing

    explanation = Explanation(request_id=request_id, explanation=content)

    db.add(explanation)
    db.commit()
    db.refresh(explanation)

    return explanation


def get_explanation_by_request(db: Session, request_id: int) -> Optional[Explanation]:
    """Return the Explanation for a PromptRequest or None if not found."""

    stmt = select(Explanation).where(Explanation.request_id == request_id)
    return db.execute(stmt).scalars().first()


def delete_explanation(db: Session, explanation: Explanation) -> bool:
    """Delete the provided Explanation instance from the database."""

    if explanation is None:
        return False

    db.delete(explanation)
    db.commit()

    return True
