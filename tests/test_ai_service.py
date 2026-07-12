import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.ai_service import AIService
from src.models.prompt_request import PromptRequest

def test_ai_service_generate_prompt():
    mock_council = MagicMock()
    # Execute is an async method
    mock_council.execute = AsyncMock(return_value={"responses": [], "consensus": MagicMock()})
    
    service = AIService(live_council=mock_council)
    request = PromptRequest(
        topic="Test",
        learning_style="visual",
        difficulty="beginner",
        education_level="beginner",
        output_length="medium",
        objective="Test"
    )
    
    result = asyncio.run(service.generate_prompt(request))
    assert "responses" in result
    mock_council.execute.assert_called_once()

def test_ai_service_sync_methods():
    service = AIService()
    
    # Test optimization
    prompt = "Please explain."
    optimized = service.optimize_prompt(prompt)
    assert "Please" not in optimized
    
    # Test validation
    score = service.validate_prompt(prompt)
    assert score.overall_score >= 0
    
    # Test difficulty
    adapted = service.adapt_difficulty(prompt, "beginner")
    assert "BEGINNER" in adapted
    
    # Test variants
    variants = service.generate_prompt_variants("Math")
    assert len(variants) > 0

def test_ai_service_learning_path():
    mock_council = MagicMock()
    mock_consensus = MagicMock()
    mock_consensus.final_prompt = '{"topic": "Python", "target_audience": "Beginner", "prerequisites": [], "milestones": [], "practice_tasks": [], "projects": [], "recommended_resources": [], "estimated_total_hours": 10.0, "difficulty_progression": "linear"}'
    mock_council.execute = AsyncMock(return_value={"consensus": mock_consensus})
    
    service = AIService(live_council=mock_council)
    path = asyncio.run(service.generate_learning_path("Python", "beginner"))
    
    assert path is not None
    assert path.topic == "Python"
