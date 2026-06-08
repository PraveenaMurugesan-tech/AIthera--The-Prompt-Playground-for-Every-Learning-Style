import os
from typing import Optional
import os.path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Database configuration and reusable engine creation.

# Load environment variables from project root .env if present.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOTENV_PATH = os.path.join(REPO_ROOT, ".env")
# Override existing environment variables so local .env takes precedence during dev/migrations
load_dotenv(dotenv_path=DOTENV_PATH, override=True)


def get_database_url() -> str:
    """Return the database URL from environment variables.

    Looks for `DATABASE_URL` in the environment (loaded via python-dotenv).
    Raises a clear RuntimeError if not found.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            f"DATABASE_URL environment variable is not set. Expected .env at: {DOTENV_PATH}"
        )
    return database_url


def create_engine_instance(database_url: Optional[str] = None) -> Engine:
    """Create and return a reusable SQLAlchemy engine instance.

    The function does not hardcode any dialect and supports URLs for
    PostgreSQL, MySQL (e.g. mysql+pymysql://...), and others supported by SQLAlchemy.
    """
    database_url = database_url or get_database_url()

    # Create engine with sensible production options (connection pooling enabled).
    return create_engine(
        database_url,
        pool_pre_ping=True,
        future=True,
    )


# Reusable engine instance for the application
engine: Engine = create_engine_instance()
