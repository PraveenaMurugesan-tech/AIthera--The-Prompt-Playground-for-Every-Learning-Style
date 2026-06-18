import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from google.genai.errors import APIError

from src.providers.gemini_client import (
    GeminiClient,
    GeminiConfigError,
    GeminiAuthError,
    GeminiTransientError,
    GeminiNonTransientError,
    GeminiProviderError,
)

# Use AnyIO test marker for async tests
pytestmark = pytest.mark.anyio


# ==============================================================================
# Helper Factories
# ==============================================================================

def make_mock_gemini_response(text: str, total_tokens: int = 120):
    """Create a mock genai response object."""
    mock_resp = MagicMock()
    mock_resp.text = text
    
    mock_usage = MagicMock()
    mock_usage.total_token_count = total_tokens
    mock_resp.usage_metadata = mock_usage
    
    return mock_resp


def make_api_error(code: int, message: str) -> APIError:
    """Create a mock APIError."""
    err = APIError(code=code, response_json={"error": {"message": message}})
    return err


# ==============================================================================
# Test Cases
# ==============================================================================

async def test_gemini_client_missing_api_key():
    """Verify that a config error is raised when the API key is missing."""
    client = GeminiClient()
    client.api_key = ""
    
    with pytest.raises(GeminiConfigError, match="Gemini API key is missing or empty"):
        await client.generate_response(prompt="Hello")


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_success_prompt(mock_client_class):
    """Verify that a successful response with direct prompt is handled correctly."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_response = make_mock_gemini_response(
        text='{"prompt": "Gemini prompt", "reasoning": "Gemini reasoning", "strengths": ["Visual"]}',
        total_tokens=150
    )
    mock_models.generate_content = AsyncMock(return_value=mock_response)
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(prompt="Hello, world")
    
    # Assert properties
    assert res["provider"] == "gemini"
    assert res["model"] == "gemini-2.5-flash"
    assert res["content"] == '{"prompt": "Gemini prompt", "reasoning": "Gemini reasoning", "strengths": ["Visual"]}'
    assert res["metadata"]["tokens_used"] == 150
    assert "response_time" in res
    
    # Assert candidate compatibility structure for ResponseNormalizer
    assert res["candidates"][0]["content"]["parts"][0]["text"] == res["content"]
    assert res["usageMetadata"]["totalTokenCount"] == 150
    
    # Assert API was called correctly
    mock_models.generate_content.assert_called_once()
    call_kwargs = mock_models.generate_content.call_args.kwargs
    assert call_kwargs["contents"] == "Hello, world"
    assert call_kwargs["model"] == "gemini-2.5-flash"


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_success_educational(mock_client_class):
    """Verify that educational parameters are formatted using the template correctly."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_response = make_mock_gemini_response('{"prompt": "Edu prompt"}')
    mock_models.generate_content = AsyncMock(return_value=mock_response)
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(
        topic="Math",
        objective="Fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    assert res["content"] == '{"prompt": "Edu prompt"}'
    mock_models.generate_content.assert_called_once()
    
    prompt_content = mock_models.generate_content.call_args.kwargs["contents"]
    # Verify template injection
    assert "Topic: Math" in prompt_content
    assert "Objective: Fractions" in prompt_content
    assert "Learning Style: visual" in prompt_content


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_model_selection(mock_client_class):
    """Verify that model name can be set via env var or dynamic config."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_models.generate_content = AsyncMock(return_value=make_mock_gemini_response("Success"))

    with patch.dict("os.environ", {"GEMINI_MODEL": "gemini-2.5-pro"}):
        client = GeminiClient()
        client.api_key = "test-api-key"
        res = await client.generate_response(prompt="Hello")
        assert res["model"] == "gemini-2.5-pro"
        
        call_kwargs = mock_models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.5-pro"


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_auth_failure(mock_client_class):
    """Verify that authentication errors are mapped to GeminiAuthError and not retried."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_models.generate_content.side_effect = make_api_error(401, "Unauthenticated")
    
    client = GeminiClient()
    client.api_key = "invalid-key"
    
    with pytest.raises(GeminiAuthError, match="Gemini Authentication failed"):
        await client.generate_response(prompt="Hello")
        
    assert mock_models.generate_content.call_count == 1


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_rate_limit_failure(mock_client_class):
    """Verify that rate limit errors are retried up to 2 times before raising GeminiTransientError."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_models.generate_content.side_effect = make_api_error(429, "Rate limit exceeded")
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GeminiTransientError, match="Gemini transient error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_models.generate_content.call_count == 2


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_timeout_failure(mock_client_class):
    """Verify that timeouts are retried up to 2 times before raising GeminiTransientError."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_models.generate_content.side_effect = make_api_error(408, "Timeout")
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GeminiTransientError, match="Gemini transient error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_models.generate_content.call_count == 2


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_retry_then_success(mock_client_class):
    """Verify that a transient failure followed by success works on the second try."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_response = make_mock_gemini_response("Success")
    
    calls = 0
    async def side_effect_fn(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise make_api_error(503, "Service Unavailable")
        return mock_response
        
    mock_models.generate_content.side_effect = side_effect_fn
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(prompt="Hello")
    assert res["content"] == "Success"
    assert mock_models.generate_content.call_count == 2


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_non_transient_error(mock_client_class):
    """Verify that invalid arguments are treated as non-transient and not retried."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_models.generate_content.side_effect = make_api_error(400, "Bad Request")
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GeminiNonTransientError, match="Gemini non-transient API error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_models.generate_content.call_count == 1


@patch("src.providers.gemini_client.genai.Client")
async def test_gemini_client_unexpected_error(mock_client_class):
    """Verify that unexpected Python exceptions are mapped to GeminiProviderError and not retried."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_models = MagicMock()
    mock_client.aio.models = mock_models
    
    mock_models.generate_content.side_effect = ValueError("Local Python error")
    
    client = GeminiClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GeminiProviderError, match="Unexpected Gemini provider error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_models.generate_content.call_count == 1
