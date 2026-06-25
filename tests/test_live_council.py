import pytest
from unittest.mock import MagicMock, AsyncMock
from src.council.live_council import LiveCouncil, LiveCouncilError
from src.council.council_executor import CouncilExecutor, CouncilExecutionError
from src.models.prompt_request import PromptRequest
from src.models.council_response import CouncilResponse, ResponseMetadata
from src.models.consensus_result import ConsensusResult
from src.scoring.prompt_scorer import ResponseScore
from src.providers.provider_registry import ProviderRegistry
from src.providers.base_provider import BaseProvider, ProviderConfig

pytestmark = pytest.mark.anyio


class MockProvider(BaseProvider):
    """Mock Provider class to verify live council workflow."""
    async def generate_response(self, *args, **kwargs):
        pass


@pytest.fixture
def mock_registry():
    registry = ProviderRegistry()
    registry._providers.clear()
    registry._provider_classes.clear()
    return registry


async def test_live_council_success(mock_registry):
    """Verify that the Live Council executes successfully end-to-end when all providers succeed."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    config2 = ProviderConfig(provider_name="Gemini", role="refiner", model_name="gemini-1.5-pro", enabled=True)
    
    p1 = MockProvider(config1)
    p2 = MockProvider(config2)
    
    # Provider 1 response
    res1 = CouncilResponse(
        role="creator",
        model="llama-3.3-70b-versatile",
        prompt="Explain photosynthesis by drawing a leaf layout diagram showing stomata.",
        reasoning="Visual metaphor helps visual learners see layout.",
        strengths=["Strong visual diagram reference"],
        metadata=ResponseMetadata(tokens_used=100, response_time=0.1)
    )
    # Provider 2 response
    res2 = CouncilResponse(
        role="refiner",
        model="gemini-1.5-pro",
        prompt="Draw a flowchart of photosynthesis showing leaf cell structure and chloroplasts.",
        reasoning="Flowchart structure maps concepts.",
        strengths=["Clear concept flow mapping"],
        metadata=ResponseMetadata(tokens_used=120, response_time=0.15)
    )
    
    p1.generate_response = AsyncMock(return_value=res1)
    p2.generate_response = AsyncMock(return_value=res2)
    
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    mock_registry.register_provider("gemini", MockProvider)
    mock_registry._providers["gemini"] = p2
    
    live_council = LiveCouncil(provider_registry=mock_registry)
    
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand leaf structure and reactions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    request.id = 42
    
    result = await live_council.execute(request)
    
    # Verify output keys and structures
    assert "responses" in result
    assert "consensus" in result
    assert "score" in result
    assert "explanation" in result
    assert "contributors" in result
    
    # Verify responses
    assert len(result["responses"]) == 2
    
    # Verify consensus
    consensus = result["consensus"]
    assert isinstance(consensus, ConsensusResult)
    assert consensus.request_id == 42
    assert "flowchart" in consensus.final_prompt or "diagram" in consensus.final_prompt
    
    # Verify score
    score = result["score"]
    assert isinstance(score, ResponseScore)
    assert score.overall_score > 0.0
    
    # Verify explanation
    explanation = result["explanation"]
    assert "provider_explanation" in explanation
    assert "consensus_explanation" in explanation
    assert "learning_style_explanation" in explanation
    assert "score_explanation" in explanation
    assert "summary" in explanation
    
    # Verify contributors
    assert "groq" in result["contributors"]
    assert "gemini" in result["contributors"]
    
    # Verify health metrics
    health_tracker = live_council.council_executor.health_tracker
    assert health_tracker.get_provider_health("Groq").successful_requests == 1
    assert health_tracker.get_provider_health("Gemini").successful_requests == 1


async def test_live_council_failover(mock_registry):
    """Verify that if one provider fails, the Live Council still succeeds using failover."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    config2 = ProviderConfig(provider_name="Gemini", role="refiner", model_name="gemini-1.5-pro", enabled=True)
    
    p1 = MockProvider(config1)
    p2 = MockProvider(config2)
    
    # Groq fails, Gemini succeeds
    p1.generate_response = AsyncMock(side_effect=RuntimeError("Groq offline"))
    
    res2 = CouncilResponse(
        role="refiner",
        model="gemini-1.5-pro",
        prompt="Draw a flowchart of photosynthesis showing leaf cell structure and chloroplasts.",
        reasoning="Flowchart structure maps concepts.",
        strengths=["Clear concept flow mapping"],
        metadata=ResponseMetadata(tokens_used=120, response_time=0.15)
    )
    p2.generate_response = AsyncMock(return_value=res2)
    
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    mock_registry.register_provider("gemini", MockProvider)
    mock_registry._providers["gemini"] = p2
    
    live_council = LiveCouncil(provider_registry=mock_registry)
    
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand leaf structure and reactions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    request.id = 43
    
    result = await live_council.execute(request)
    
    assert len(result["responses"]) == 1
    assert result["responses"][0].model == "gemini-1.5-pro"
    assert "gemini" in result["contributors"]
    assert "groq" not in result["contributors"]
    
    # Health metrics verified
    health_tracker = live_council.council_executor.health_tracker
    assert health_tracker.get_provider_health("Groq").failed_requests == 1
    assert health_tracker.get_provider_health("Gemini").successful_requests == 1


async def test_live_council_all_fail(mock_registry):
    """Verify that LiveCouncilError is raised if all providers fail."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    
    p1 = MockProvider(config1)
    p1.generate_response = AsyncMock(side_effect=RuntimeError("Groq offline"))
    
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    
    live_council = LiveCouncil(provider_registry=mock_registry)
    
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand leaf structure",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    with pytest.raises(LiveCouncilError, match="Live Council execution failed"):
        await live_council.execute(request)


async def test_live_council_consensus_score_propagation(mock_registry):
    """Verify that consensus_score correctly reflects the winning prompt's score."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    p1 = MockProvider(config1)
    
    res1 = CouncilResponse(
        role="creator",
        model="llama-3.3-70b-versatile",
        prompt="Explain photosynthesis clearly.",
        reasoning="Simple clear explanation.",
        strengths=["Clarity"],
        metadata=ResponseMetadata(tokens_used=100, response_time=0.1)
    )
    p1.generate_response = AsyncMock(return_value=res1)
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    
    live_council = LiveCouncil(provider_registry=mock_registry)
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand leaf structure and reactions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    request.id = 100
    
    result = await live_council.execute(request)
    
    consensus = result["consensus"]
    score = result["score"]
    
    assert len(result["responses"]) > 0
    assert consensus is not None
    assert consensus.quality_score > 0.0
    assert consensus.quality_score == score.overall_score

