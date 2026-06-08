import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv, dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import url as sa_url
import logging
from typing import Optional

# --------------------------------------------------
# Project root setup
# --------------------------------------------------

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# --------------------------------------------------
# Alembic config
# --------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------------------------------------------------
# Load .env
# --------------------------------------------------

DOTENV_PATH = os.path.join(REPO_ROOT, ".env")

# Override existing environment variables
# Load .env into the process env (override existing), then also read values directly
load_dotenv(dotenv_path=DOTENV_PATH, override=True)

# Gather pre/post environment values for diagnostics
pre_env_value = os.environ.get("DATABASE_URL")

# Read .env file values explicitly and prefer them if present (robust across shells)
dotenv_vals = dotenv_values(DOTENV_PATH) or {}
env_file_value = dotenv_vals.get("DATABASE_URL")

# If .env defines DATABASE_URL, prefer it and set into os.environ
if env_file_value:
    os.environ["DATABASE_URL"] = env_file_value
database_url: Optional[str] = os.getenv("DATABASE_URL")

print("\n====================")
print("DATABASE_URL =", database_url)

post_env_value = database_url

# Mask password for safe logging
def _mask_url(u: str | None) -> str:
    if not u:
        return "<none>"
    try:
        p = sa_url.make_url(u)
        if p.password:
            p = p._replace(password="***")
        return str(p)
    except Exception:
        return "<invalid-database-url>"

masked_pre = _mask_url(pre_env_value)
masked_file = _mask_url(env_file_value)
masked_post = _mask_url(post_env_value)

logging.getLogger("alembic.env").info("Using DATABASE_URL from %s", DOTENV_PATH)
logging.getLogger("alembic.env").info("DATABASE_URL pre-env: %s", masked_pre)
logging.getLogger("alembic.env").info("DATABASE_URL from .env file: %s", masked_file)
logging.getLogger("alembic.env").info("DATABASE_URL effective: %s", masked_post)
print(f"[alembic.env] DATABASE_URL effective={masked_post}")

if not database_url:
    raise RuntimeError(
        f"DATABASE_URL not found. Expected a .env file at: {DOTENV_PATH}\n"
        f"Create the file with an entry like:\n"
        f"DATABASE_URL=mysql+pymysql://root:password@localhost:3306/aithera"
    )

# Force Alembic to use the URL from .env
config.set_main_option("sqlalchemy.url", database_url)

# --------------------------------------------------
# Import metadata
# --------------------------------------------------

from src.database.base import Base

target_metadata = Base.metadata

# --------------------------------------------------
# Offline migrations
# --------------------------------------------------

def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        as_sql=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# --------------------------------------------------
# Online migrations
# --------------------------------------------------

def run_migrations_online() -> None:
    engine = create_engine(
        database_url,
        future=True,
        pool_pre_ping=True,
    )
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    except OperationalError as exc:  # pragma: no cover - DB runtime
        try:
            parsed = sa_url.make_url(database_url)
            if parsed.password:
                parsed = parsed._replace(password="***")
            human_url = str(parsed)
        except Exception:
            human_url = "<invalid-database-url>"

        # If the command requested autogenerate, we cannot proceed without a live DB
        is_autogenerate = any("--autogenerate" in a or "autogenerate" in a for a in sys.argv)
        if is_autogenerate:
            raise RuntimeError(
                "Database connection failed and autogenerate requires a running database.\n"
                "Start your MySQL server (or update DATABASE_URL) and retry, or run the revision without `--autogenerate`.\n"
                "Original error: " + str(exc)
            ) from exc

        logging.getLogger("alembic.env").warning(
            "Could not connect to the database (%s). Falling back to offline mode. Error: %s",
            human_url,
            exc,
        )
        print(f"[alembic.env] Could not connect to DB: {human_url}. Falling back to offline mode.")
        # Fall back to offline migrations for non-autogenerate commands
        run_migrations_offline()
        return

# --------------------------------------------------
# Execute
# --------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()