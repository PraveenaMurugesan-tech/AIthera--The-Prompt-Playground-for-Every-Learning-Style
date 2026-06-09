from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from src.database.base import Base


class User(Base):
    """SQLAlchemy ORM model for application users.

    The model uses SQLAlchemy 2.0 style declarative base and is ready
    to be included in Alembic autogenerate by importing this module
    from migration environment when needed.
    """

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(150), unique=True, nullable=False, index=True)
    email: str = Column(String(320), unique=True, nullable=False, index=True)
    hashed_password: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
