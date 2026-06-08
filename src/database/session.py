from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from .connection import engine

# Session management for database interactions and FastAPI dependency.

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after use."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Provide a context manager for database session scope."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
