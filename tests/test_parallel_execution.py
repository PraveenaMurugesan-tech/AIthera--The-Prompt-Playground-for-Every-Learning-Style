import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.council.council_executor import CouncilExecutor, CouncilExecutionError
from src.models.prompt_request import PromptRequest
from src.models.council_response import CouncilResponse, ResponseMetadata
from src.providers.provider_registry import ProviderRegistry
from src.providers.base_provider import BaseProvider, ProviderConfig

pytestmark = pytest.mark.anyio


class MockProvider(BaseProvider):
    """Mock Provider class to verify execution."""
    async def generate_response(self, *args, **kwargs):
        pass


@pytest.fixture
def mock_registry():
    registry = ProviderRegistry()
    # Clear defaults to register only mock providers
    registry._providers.clear()
    registry._provider_classes.clear()
    return registry


async def test_parallel_execution_success(mock_registry):
    """Verify that multiple providers execute simultaneously and responses are collected."""
    # Create mock providers with real configs and valid models
    config1 = ProviderConfig(provider_name="Groq", role="creator", model_name="llama-3.3-70b-versatile", enabled=True)
    config2 = ProviderConfig(provider_name="Gemini", role="refiner", model_name="gemini-1.5-pro", enabled=True)
    
    p1 = MockProvider(config1)
    p2 = MockProvider(config2)
    
    # Mock return responses with approved model strings
    res1 = CouncilResponse(
        provider="Groq",  # We can still pass it but it won't be a schema property
        role="creator",
        model="llama-3.3-70b-versatile",
        prompt="Groq prompt",
        reasoning="reasoning",
        strengths=["strength"],
        metadata=ResponseMetadata(tokens_used=10, response_time=0.1)
    )
    res2 = CouncilResponse(
        provider="Gemini",
        role="refiner",
        model="gemini-1.5-pro",
        prompt="Gemini prompt",
        reasoning="reasoning",
        strengths=["strength"],
        metadata=ResponseMetadata(tokens_used=15, response_time=0.2)
    )
    
    # We will simulate parallel delay to ensure concurrency.
    p1_started = asyncio.Event()
    p2_started = asyncio.Event()
    
    async def p1_gen(*args, **kwargs):
        p1_started.set()
        await p2_started.wait()  # Wait for p2 to start to prove concurrency
        return res1
        
    async def p2_gen(*args, **kwargs):
        p2_started.set()
        await p1_started.wait()  # Wait for p1 to start to prove concurrency
        return res2
        
    p1.generate_response = AsyncMock(side_effect=p1_gen)
    p2.generate_response = AsyncMock(side_effect=p2_gen)
    
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
    
    assert len(responses) == 2
    assert responses[0].model == "llama-3.3-70b-versatile"
    assert responses[1].model == "gemini-1.5-pro"
    assert executor.health_tracker.get_provider_health("Groq").successful_requests == 1
    assert executor.health_tracker.get_provider_health("Gemini").successful_requests == 1
