import pytest
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.main import app
from src.services.ai_service import AIService
from src.models.consensus_result import ConsensusResult
from src.optimizer.prompt_variants import PromptVariant, VariantStyle
from src.optimizer.learning_path import LearningPath, Milestone

client = TestClient(app)

# We need to mock the authentication and database dependencies if they are active,
# or just mock AIService.
# Let's mock the db and auth for the /generate endpoint.
from src.auth.router import get_current_user
from src.database.session import get_db
from src.prompts.router import get_ai_service

def mock_get_current_user():
    class MockUser:
        id = 1
    return MockUser()

def mock_get_db():
    yield MagicMock()

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db] = mock_get_db

@pytest.fixture
def mock_ai_service():
    service = MagicMock(spec=AIService)
    
    # Mock generate_prompt
    mock_consensus = ConsensusResult(
        final_prompt="This is an optimized prompt",
        consensus_reasoning="Consensus reasoning here",
        confidence_score=0.95,
        agreement_score=0.9,
        provider_contributions={"providerA": ["concept1"]},
        educational_structure_score=0.8,
        diversity_score=0.7,
        coverage_score=0.85,
        explanation="Explanation text",
        evaluation_summary="Good"
    )
    service.generate_prompt = AsyncMock(return_value={"consensus": mock_consensus})
    
    # Mock learning path
    mock_lp = LearningPath(
        topic="Test Topic",
        target_audience="Beginner",
        prerequisites=[],
        milestones=[Milestone(title="M1", description="desc", estimated_minutes=30, topics=[])],
        practice_tasks=[],
        projects=[],
        recommended_resources=[],
        estimated_total_hours=1.0,
        difficulty_progression="Linear"
    )
    service.generate_learning_path = AsyncMock(return_value=mock_lp)
    
    # Mock variants
    mock_variants = [
        PromptVariant(style=VariantStyle.QUICK_REVISION, title="Title", prompt_text="Prompt variant text", metadata={})
    ]
    service.generate_prompt_variants.return_value = mock_variants
    
    # Mock recommendations
    service.validate_prompt.return_value = MagicMock()
    service.generate_recommendations.return_value = []
    
    app.dependency_overrides[get_ai_service] = lambda: service
    return service

def test_generate_prompt_endpoint(mock_ai_service):
    payload = {
        "topic": "Python basics",
        "learning_style": "visual",
        "difficulty": "beginner",
        "bloom_level": "understand",
        "options": {
            "skip_variants": False,
            "skip_learning_path": False
        }
    }
    
    # Needs to mock crud.create_prompt_request to return a mock DB record
    with patch("src.prompts.router.crud.create_prompt_request") as mock_create_request:
        mock_record = MagicMock()
        mock_record.id = 1
        mock_create_request.return_value = mock_record
        
        response = client.post("/prompts/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["optimized_prompt"] == "This is an optimized prompt"
        assert data["confidence_score"] == 0.95
        assert "learning_path" in data
        assert data["learning_path"]["topic"] == "Test Topic"
        assert "prompt_variants" in data
        assert len(data["prompt_variants"]) == 1

def test_generate_prompt_timeout(mock_ai_service):
    payload = {
        "topic": "Python basics",
        "learning_style": "visual",
        "difficulty": "beginner"
    }
    
    mock_ai_service.generate_prompt.side_effect = TimeoutError()
    
    with patch("src.prompts.router.crud.create_prompt_request") as mock_create_request:
        mock_record = MagicMock()
        mock_create_request.return_value = mock_record
        
        response = client.post("/prompts/generate", json=payload)
        
        assert response.status_code == 408
        assert response.json()["detail"] == "Generation timed out"
