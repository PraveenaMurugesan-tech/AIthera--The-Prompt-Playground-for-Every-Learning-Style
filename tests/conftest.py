import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Ensure test DB is clean and tables are created before tests
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    repo_root = Path(__file__).resolve().parents[1]
    db_path = repo_root / "test.db"

    # Remove any previous test database
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass

    # Import app and database objects (will create engine from .env)
    from src.database.connection import engine
    from src.database.base import Base

    # Create all tables (initial setup)
    Base.metadata.create_all(bind=engine)

    yield

    # Teardown: dispose engine and remove test.db
    try:
        engine.dispose()
    except Exception:
        pass
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass

@pytest.fixture(autouse=True)
def clean_db():
    from src.database.connection import engine
    from src.database.base import Base
    
    # Drop and recreate all tables for perfect test isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield


@pytest.fixture
def client():
    from src.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def get_auth_token(client):
    """Register a test user and return a bearer token string."""
    email = "test@example.com"
    password = "password123"

    # Register user
    resp = client.post("/auth/register", json={"email": email, "password": password})
    assert resp.status_code in (201, 400)

    # Login to get token
    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token

    return token


@pytest.fixture
def auth_client(client, get_auth_token):
    token = get_auth_token
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
