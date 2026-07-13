import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Database configuration and reusable engine creation.

# Project repository root and expected .env path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOTENV_PATH = os.path.join(REPO_ROOT, ".env")

# If the project .env is missing, raise a clear error instructing the developer how
# to create it (do not commit real credentials). This makes startup failures
# explicit and tells users to copy the provided .env.example into place.
if not os.path.exists(DOTENV_PATH):
    raise RuntimeError(
        "Required .env file not found at: {path}\n"
        "Create it by copying the provided .env.example in the project root and filling in values.\n\n"
        "Example (from project root):\n"
        "  copy .env.example .env            (Windows)\n"
        "  cp .env.example .env              (Linux / macOS)\n\n"
        "Expected environment variables in .env:\n"
        "  DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES\n"
    ).format(path=DOTENV_PATH)

# Load environment variables from project root .env, overriding existing values so
# the local .env takes precedence during development and migrations.
load_dotenv(dotenv_path=DOTENV_PATH, override=True)


def get_database_url() -> str:
    """Return the database URL from environment variables.

    Looks for `DATABASE_URL` in the environment (loaded via python-dotenv).
    Raises a clear RuntimeError if not found.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set.\n"
            f"Expected .env at: {DOTENV_PATH}\n"
            "Create it by copying .env.example and setting `DATABASE_URL` accordingly."
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
