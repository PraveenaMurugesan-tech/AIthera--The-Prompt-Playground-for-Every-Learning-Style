from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.user import User
from .security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Return a user by email or None if not found."""

    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalars().first()


def create_user(db: Session, email: str, password: str) -> User:
    """Create a new user with a hashed password."""

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Optional[User]:
    """Authenticate a user by email and password."""

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user