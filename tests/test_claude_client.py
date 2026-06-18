import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
from anthropic import (
    AsyncAnthropic,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    APIStatusError
)

from src.providers.claude_client import (
    ClaudeClient,
    ClaudeConfigError,
    ClaudeAuthError,
    ClaudeTransientError,
    ClaudeNonTransientError,
    ClaudeProviderError
)

# Use AnyIO test marker for async tests
pytestmark = pytest.mark.anyio


# ==============================================================================
# Helper Factories
# ==============================================================================

def make_mock_message(content: str, model: str = "claude-3-5-sonnet", input_tokens: int = 10, output_tokens: int = 90):
    """Create a mock Message object from Anthropic SDK."""
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "id": "msg-test",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [
            {
                "type": "text",
                "text": content
            }
        ],
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    }
    return mock_response


# ==============================================================================
# Test Cases
# ==============================================================================

@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_success_prompt(mock_async_anthropic, monkeypatch):
    """Verify that a successful response with direct prompt is handled correctly."""
    monkeypatch.setenv("CLAUDE_MODEL", "claude-3-5-sonnet")
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_response = make_mock_message(
        content='{"prompt": "Claude prompt", "reasoning": "Claude reasoning", "strengths": ["Clear"]}'
    )
    mock_client.messages.create.return_value = mock_response
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(prompt="Hello, world")
    
    assert res["model"] == "claude-3-5-sonnet"
    assert "content" in res
    assert res["content"][0]["text"] == '{"prompt": "Claude prompt", "reasoning": "Claude reasoning", "strengths": ["Clear"]}'
    assert res["usage"]["input_tokens"] == 10
    assert res["usage"]["output_tokens"] == 90
    assert "response_time" in res
    
    # Assert API was called with the prompt
    mock_client.messages.create.assert_called_once()
    call_args = mock_client.messages.create.call_args[1]
    assert call_args["model"] == "claude-3-5-sonnet"
    assert call_args["messages"] == [{"role": "user", "content": "Hello, world"}]


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_success_educational(mock_async_anthropic):
    """Verify that educational parameters are formatted using the template correctly."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_response = make_mock_message('{"prompt": "Edu prompt"}')
    mock_client.messages.create.return_value = mock_response
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(
        topic="Math",
        objective="Fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    
    assert res["content"][0]["text"] == '{"prompt": "Edu prompt"}'
    mock_client.messages.create.assert_called_once()
    
    call_args = mock_client.messages.create.call_args[1]
    prompt_content = call_args["messages"][0]["content"]
    # Verify that the variables are present in the formatted prompt
    assert "Topic: Math" in prompt_content
    assert "Objective: Fractions" in prompt_content
    assert "Learning Style: visual" in prompt_content


async def test_claude_client_missing_api_key():
    """Verify that a config error is raised when the API key is missing."""
    client = ClaudeClient()
    client.api_key = ""
    
    with pytest.raises(ClaudeConfigError, match="Claude API key is missing or empty"):
        await client.generate_response(prompt="Hello")


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_auth_failure(mock_async_anthropic):
    """Verify that authentication errors are mapped to ClaudeAuthError and not retried."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.anthropic.com")
    mock_response = httpx.Response(401, request=mock_request)
    mock_client.messages.create.side_effect = AuthenticationError(
        message="Invalid API Key",
        response=mock_response,
        body=None
    )
    
    client = ClaudeClient()
    client.api_key = "invalid-key"
    
    with pytest.raises(ClaudeAuthError, match="Claude Authentication failed"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.messages.create.call_count == 1


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_rate_limit_failure(mock_async_anthropic):
    """Verify that rate limit errors are retried up to 3 times before raising ClaudeTransientError."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.anthropic.com")
    mock_response = httpx.Response(429, request=mock_request)
    mock_client.messages.create.side_effect = RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body=None
    )
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(ClaudeTransientError, match="Claude transient error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.messages.create.call_count == 3


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_timeout_failure(mock_async_anthropic):
    """Verify that timeouts are retried up to 3 times before raising ClaudeTransientError."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.anthropic.com")
    mock_client.messages.create.side_effect = APITimeoutError(
        request=mock_request
    )
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(ClaudeTransientError, match="Claude transient error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.messages.create.call_count == 3


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_retry_then_success(mock_async_anthropic):
    """Verify that a transient failure followed by success works on the second try."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.anthropic.com")
    mock_response = make_mock_message('{"prompt": "Success"}')
    mock_client.messages.create.side_effect = [
        APIConnectionError(message="Connection failed", request=mock_request),
        mock_response
    ]
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    res = await client.generate_response(prompt="Hello")
    assert res["content"][0]["text"] == '{"prompt": "Success"}'
    assert mock_client.messages.create.call_count == 2


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_server_error(mock_async_anthropic):
    """Verify that a 500 status code is treated as transient and retried."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.anthropic.com")
    mock_response = httpx.Response(500, request=mock_request)
    mock_client.messages.create.side_effect = APIStatusError(
        message="Internal Server Error",
        response=mock_response,
        body=None
    )
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(ClaudeTransientError, match="Claude server error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.messages.create.call_count == 3


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_non_transient_error(mock_async_anthropic):
    """Verify that a 400 bad request is treated as non-transient and not retried."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_request = httpx.Request("POST", "https://api.anthropic.com")
    mock_response = httpx.Response(400, request=mock_request)
    mock_client.messages.create.side_effect = APIStatusError(
        message="Bad Request",
        response=mock_response,
        body=None
    )
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(ClaudeNonTransientError, match="Claude non-transient API error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.messages.create.call_count == 1


@patch("src.providers.claude_client.AsyncAnthropic")
async def test_claude_client_unexpected_error(mock_async_anthropic):
    """Verify that unexpected Python exceptions are mapped to ClaudeProviderError and not retried."""
    mock_client = AsyncMock()
    mock_async_anthropic.return_value = mock_client
    
    mock_client.messages.create.side_effect = ValueError("Some local python error")
    
    client = ClaudeClient()
    client.api_key = "test-api-key"
    
    with pytest.raises(ClaudeProviderError, match="Unexpected Claude provider error"):
        await client.generate_response(prompt="Hello")
        
    assert mock_client.messages.create.call_count == 1
