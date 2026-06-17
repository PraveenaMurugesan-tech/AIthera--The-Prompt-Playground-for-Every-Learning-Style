import pytest
from unittest.mock import MagicMock, AsyncMock
from src.council.council_executor import CouncilExecutor, CouncilExecutionError
from src.models.prompt_request import PromptRequest
from src.models.council_response import CouncilResponse, ResponseMetadata
from src.providers.provider_registry import ProviderRegistry
from src.providers.base_provider import BaseProvider, ProviderConfig

pytestmark = pytest.mark.anyio


class MockProvider(BaseProvider):
    """Mock Provider class to verify failover."""
    async def generate_response(self, *args, **kwargs):
        pass


@pytest.fixture
def mock_registry():
    registry = ProviderRegistry()
    registry._providers.clear()
    registry._provider_classes.clear()
    return registry


async def test_one_provider_failure(mock_registry):
    """Verify that if one provider fails, the executor succeeds with the remaining provider."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    config2 = ProviderConfig(provider_name="Gemini", role="refiner", model_name="gemini-1.5-pro", enabled=True)
    
    p1 = MockProvider(config1)
    p2 = MockProvider(config2)
    
    # p1 fails, p2 succeeds
    p1.generate_response = AsyncMock(side_effect=RuntimeError("Groq offline"))
    
    res2 = CouncilResponse(
        role="refiner",
        model="gemini-1.5-pro",
        prompt="Gemini prompt",
        reasoning="reasoning",
        strengths=["strength"],
        metadata=ResponseMetadata(tokens_used=15, response_time=0.2)
    )
    p2.generate_response = AsyncMock(return_value=res2)
    
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    mock_registry.register_provider("gemini", MockProvider)
    mock_registry._providers["gemini"] = p2
    
    executor = CouncilExecutor(provider_registry=mock_registry)
    request = PromptRequest(
        user_id=1,
        topic="Math",
        objective="Fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    responses = await executor.execute_council(request)
    
    assert len(responses) == 1
    assert responses[0].model == "gemini-1.5-pro"
    assert "Groq" in executor.failed_providers
    assert "Gemini" in executor.successful_providers
    assert executor.health_tracker.get_provider_health("Groq").failed_requests == 1
    assert executor.health_tracker.get_provider_health("Gemini").successful_requests == 1


async def test_multiple_provider_failures(mock_registry):
    """Verify that multiple provider failures are tolerated as long as at least one succeeds."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    config2 = ProviderConfig(provider_name="Gemini", role="refiner", model_name="gemini-1.5-pro", enabled=True)
    config3 = ProviderConfig(provider_name="Claude", role="validator", model_name="claude-3-5-sonnet", enabled=True)
    
    p1 = MockProvider(config1)
    p2 = MockProvider(config2)
    p3 = MockProvider(config3)
    
    # p1 and p2 fail, p3 succeeds
    p1.generate_response = AsyncMock(side_effect=RuntimeError("Groq offline"))
    p2.generate_response = AsyncMock(return_value=None)  # Returns None
    
    res3 = CouncilResponse(
        role="validator",
        model="claude-3-5-sonnet",
        prompt="Claude prompt",
        reasoning="reasoning",
        strengths=["strength"],
        metadata=ResponseMetadata(tokens_used=15, response_time=0.2)
    )
    p3.generate_response = AsyncMock(return_value=res3)
    
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    mock_registry.register_provider("gemini", MockProvider)
    mock_registry._providers["gemini"] = p2
    mock_registry.register_provider("claude", MockProvider)
    mock_registry._providers["claude"] = p3
    
    executor = CouncilExecutor(provider_registry=mock_registry)
    request = PromptRequest(
        user_id=1,
        topic="Math",
        objective="Fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    responses = await executor.execute_council(request)
    
    assert len(responses) == 1
    assert responses[0].model == "claude-3-5-sonnet"
    assert "Groq" in executor.failed_providers
    assert "Gemini" in executor.failed_providers
    assert "Claude" in executor.successful_providers


async def test_all_providers_fail(mock_registry):
    """Verify that CouncilExecutionError is raised if all providers fail."""
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    config2 = ProviderConfig(provider_name="Gemini", role="refiner", model_name="gemini-1.5-pro", enabled=True)
    
    p1 = MockProvider(config1)
    p2 = MockProvider(config2)
    
    p1.generate_response = AsyncMock(side_effect=RuntimeError("Groq offline"))
    p2.generate_response = AsyncMock(side_effect=RuntimeError("Gemini offline"))
    
    mock_registry.register_provider("groq", MockProvider)
    mock_registry._providers["groq"] = p1
    mock_registry.register_provider("gemini", MockProvider)
    mock_registry._providers["gemini"] = p2
    
    executor = CouncilExecutor(provider_registry=mock_registry)
    request = PromptRequest(
        user_id=1,
        topic="Math",
        objective="Fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    with pytest.raises(CouncilExecutionError, match="All providers failed. Council cannot proceed."):
        await executor.execute_council(request)
        
    assert "Groq" in executor.failed_providers
    assert "Gemini" in executor.failed_providers
