import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
from groq import (
    AsyncGroq,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    BadRequestError
)

from src.providers.groq_client import (
    GroqClient,
    GroqConfigError,
    GroqAuthError,
    GroqTransientError,
    GroqNonTransientError,
    GroqProviderError
)

# Use AnyIO test marker for async tests
pytestmark = pytest.mark.anyio


# ==============================================================================
# Helper Factories
# ==============================================================================

def make_mock_chat_completion(content: str, model: str = "llama-3.3-70b-versatile", total_tokens: int = 100):
    """Create a mock ChatCompletion object from Groq SDK."""
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": total_tokens - 10,
            "total_tokens": total_tokens
        }
    }
    return mock_response


# ==============================================================================
# Test Cases
# ==============================================================================

@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_success_prompt(mock_async_groq):
    """Verify that a successful response with direct prompt is handled correctly."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_response = make_mock_chat_completion(
        content='{"prompt": "Groq prompt", "reasoning": "Groq reasoning", "strengths": ["Visual"]}'
    )
    mock_client.chat.completions.create.return_value = mock_response
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(prompt="Hello, world")
    
    assert res["model"] == "llama-3.3-70b-versatile"
    assert "choices" in res
    assert res["choices"][0]["message"]["content"] == '{"prompt": "Groq prompt", "reasoning": "Groq reasoning", "strengths": ["Visual"]}'
    assert res["usage"]["total_tokens"] == 100
    assert "response_time" in res
    
    # Assert API was called with the prompt
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args["model"] == "llama-3.3-70b-versatile"
    assert call_args["messages"] == [{"role": "user", "content": "Hello, world"}]


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_success_educational(mock_async_groq):
    """Verify that educational parameters are formatted using the template correctly."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_response = make_mock_chat_completion('{"prompt": "Edu prompt"}')
    mock_client.chat.completions.create.return_value = mock_response
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(
        topic="Math",
        objective="Fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    assert res["choices"][0]["message"]["content"] == '{"prompt": "Edu prompt"}'
    mock_client.chat.completions.create.assert_called_once()
    
    call_args = mock_client.chat.completions.create.call_args[1]
    prompt_content = call_args["messages"][0]["content"]
    # Verify that the variables are present in the formatted prompt
    assert "Topic: Math" in prompt_content
    assert "Objective: Fractions" in prompt_content
    assert "Learning Style: visual" in prompt_content


async def test_groq_client_missing_api_key():
    """Verify that a config error is raised when the API key is missing."""
    client = GroqClient()
    client.api_key = ""
    
    with pytest.raises(GroqConfigError, match="Groq API key is missing or empty"):
        await client.generate_response(prompt="Hello")


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_auth_failure(mock_async_groq):
    """Verify that authentication errors are mapped to GroqAuthError and not retried."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.groq.com")
    mock_response = httpx.Response(401, request=mock_request)
    mock_client.chat.completions.create.side_effect = AuthenticationError(
        message="Invalid API Key",
        response=mock_response,
        body=None
    )
    
    client = GroqClient()
    client.api_key = "invalid-key"
    
    with pytest.raises(GroqAuthError, match="Groq Authentication failed"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.chat.completions.create.call_count == 1


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_rate_limit_failure(mock_async_groq):
    """Verify that rate limit errors are retried up to 3 times before raising GroqTransientError."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.groq.com")
    mock_response = httpx.Response(429, request=mock_request)
    mock_client.chat.completions.create.side_effect = RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body=None
    )
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GroqTransientError, match="Groq transient error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.chat.completions.create.call_count == 3


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_timeout_failure(mock_async_groq):
    """Verify that timeouts are retried up to 3 times before raising GroqTransientError."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.groq.com")
    mock_client.chat.completions.create.side_effect = APITimeoutError(
        request=mock_request
    )
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GroqTransientError, match="Groq transient error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.chat.completions.create.call_count == 3


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_retry_then_success(mock_async_groq):
    """Verify that a transient failure followed by success works on the second try."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.groq.com")
    mock_response = make_mock_chat_completion('{"prompt": "Success"}')
    mock_client.chat.completions.create.side_effect = [
        APIConnectionError(message="Connection failed", request=mock_request),
        mock_response
    ]
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(prompt="Hello")
    assert res["choices"][0]["message"]["content"] == '{"prompt": "Success"}'
    assert mock_client.chat.completions.create.call_count == 2


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_non_transient_error(mock_async_groq):
    """Verify that a bad request (400) is treated as non-transient and not retried."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.groq.com")
    mock_response = httpx.Response(400, request=mock_request)
    mock_client.chat.completions.create.side_effect = BadRequestError(
        message="Bad Request",
        response=mock_response,
        body=None
    )
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GroqNonTransientError, match="Groq non-transient API error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.chat.completions.create.call_count == 1


@patch("src.providers.groq_client.AsyncGroq")
async def test_groq_client_unexpected_error(mock_async_groq):
    """Verify that unexpected Python exceptions are mapped to GroqProviderError and not retried."""
    mock_client = AsyncMock()
    mock_async_groq.return_value = mock_client
    
    mock_client.chat.completions.create.side_effect = ValueError("Some local python error")
    
    client = GroqClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(GroqProviderError, match="Unexpected Groq provider error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.chat.completions.create.call_count == 1
