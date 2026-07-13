import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database.session import get_db
from src.database.base import Base
from src.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_dependencies():
    # Save current overrides to prevent leakage from other test files
    old_overrides = app.dependency_overrides.copy()
    
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db
    
    yield
    
    # Restore original overrides
    app.dependency_overrides.clear()
    app.dependency_overrides.update(old_overrides)

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()

def test_register_user():
    response = client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_register_duplicate_user():
    # Register first time
    client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "testpassword123"}
    )
    # Register second time
    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success():
    # Create user
    client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "loginpassword"}
    )
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "loginuser@example.com", "password": "loginpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure():
    response = client.post(
        "/auth/login",
        data={"username": "wronguser@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_protected_endpoint(monkeypatch):
    # Mock AIService so we don't actually hit external APIs
    from src.services.ai_service import AIService
    
    async def mock_generate_prompt(*args, **kwargs):
        class MockConsensus:
            final_prompt = "Mocked Prompt"
            consensus_reasoning = "Mocked Reasoning"
            confidence_score = 95.0
            agreement_score = 0.9
            provider_contributions = {}
            educational_structure_score = 90
            diversity_score = 80
            coverage_score = 85
            explanation = "Mocked Explanation"
            evaluation_summary = "Mocked Evaluation"
        
        return {"consensus": MockConsensus()}

    async def mock_generate_learning_path(*args, **kwargs):
        return None
    
    def mock_generate_prompt_variants(*args, **kwargs):
        return None
        
    def mock_validate_prompt(*args, **kwargs):
        return 90
        
    def mock_generate_recommendations(*args, **kwargs):
        return None

    monkeypatch.setattr(AIService, "generate_prompt", mock_generate_prompt)
    monkeypatch.setattr(AIService, "generate_learning_path", mock_generate_learning_path)
    monkeypatch.setattr(AIService, "generate_prompt_variants", mock_generate_prompt_variants)
    monkeypatch.setattr(AIService, "validate_prompt", mock_validate_prompt)
    monkeypatch.setattr(AIService, "generate_recommendations", mock_generate_recommendations)

    # Register and Login
    client.post(
        "/auth/register",
        json={"email": "protected@example.com", "password": "protectedpassword"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "protected@example.com", "password": "protectedpassword"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/prompts/generate",
        json={
            "topic": "Testing",
            "learning_style": "visual",
            "difficulty": "beginner",
            "options": {"skip_variants": True, "skip_learning_path": True}
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["optimized_prompt"] == "Mocked Prompt"
