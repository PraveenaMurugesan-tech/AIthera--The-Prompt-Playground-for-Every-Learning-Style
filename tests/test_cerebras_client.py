import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.providers.cerebras_client import (
    CerebrasClient,
    CerebrasConfigError,
    CerebrasAuthError,
    CerebrasRateLimitError,
    CerebrasTransientError,
    CerebrasNonTransientError,
    CerebrasError,
)
from src.providers.base_provider import ProviderConfig
from openai import AuthenticationError, APIConnectionError, RateLimitError, APITimeoutError, APIStatusError

import httpx
# Use AnyIO test marker for async tests
pytestmark = pytest.mark.anyio

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("CEREBRAS_API_KEY", "test-key")
    monkeypatch.setenv("CEREBRAS_MODEL", "llama-4-scout-17b-16e-instruct")
    monkeypatch.setenv("CEREBRAS_TIMEOUT", "10")

@pytest.fixture
def client(mock_env):
    return CerebrasClient()

async def test_successful_response(client):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "id": "test-id",
        "choices": [{"message": {"content": "Hello from Cerebras", "role": "assistant"}}],
        "model": "llama-4-scout-17b-16e-instruct"
    }

    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        response = await client.generate_response(prompt="Hello")

        assert response["choices"][0]["message"]["content"] == "Hello from Cerebras"
        assert "response_time" in response
        mock_instance.chat.completions.create.assert_called_once()

async def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("CEREBRAS_API_KEY", raising=False)
    client = CerebrasClient()
    with pytest.raises(CerebrasConfigError):
        await client.generate_response(prompt="Hello")

async def test_authentication_failure(client):
    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        
        mock_request = httpx.Request("POST", "https://api.cerebras.ai/v1")
        mock_response = httpx.Response(401, request=mock_request)
        err = AuthenticationError("Auth failed", response=mock_response, body=None)
        mock_instance.chat.completions.create = AsyncMock(side_effect=err)

        with pytest.raises(CerebrasAuthError):
            await client.generate_response(prompt="Hello")

async def test_rate_limit_handling(client):
    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        
        mock_request = httpx.Request("POST", "https://api.cerebras.ai/v1")
        mock_response = httpx.Response(429, request=mock_request)
        err = RateLimitError("Rate limited", response=mock_response, body=None)
        mock_instance.chat.completions.create = AsyncMock(side_effect=err)

        with pytest.raises(CerebrasRateLimitError):
            await client.generate_response(prompt="Hello")

async def test_timeout_handling(client):
    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        
        mock_instance.chat.completions.create = AsyncMock(side_effect=APITimeoutError(MagicMock()))

        with pytest.raises(CerebrasTransientError):
            await client.generate_response(prompt="Hello")

async def test_retry_behavior(client):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "id": "test-id",
        "choices": [{"message": {"content": "Hello", "role": "assistant"}}],
        "model": "llama-4-scout-17b-16e-instruct"
    }

    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        
        # Fail first time, succeed second time
        mock_instance.chat.completions.create = AsyncMock(side_effect=[
            APIConnectionError(request=MagicMock()),
            mock_response
        ])

        response = await client.generate_response(prompt="Hello")
        assert response["choices"][0]["message"]["content"] == "Hello"
        assert mock_instance.chat.completions.create.call_count == 2

async def test_unexpected_provider_error(client):
    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(side_effect=Exception("Unknown Error"))

        with pytest.raises(CerebrasError):
            await client.generate_response(prompt="Hello")

async def test_server_error_transient(client):
    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_request = httpx.Request("POST", "https://api.cerebras.ai/v1")
        mock_response = httpx.Response(500, request=mock_request)
        err = APIStatusError("Server error", response=mock_response, body=None)
        mock_instance.chat.completions.create = AsyncMock(side_effect=err)

        with pytest.raises(CerebrasTransientError):
            await client.generate_response(prompt="Hello")

async def test_client_error_non_transient(client):
    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_request = httpx.Request("POST", "https://api.cerebras.ai/v1")
        mock_response = httpx.Response(400, request=mock_request)
        err = APIStatusError("Bad request", response=mock_response, body=None)
        mock_instance.chat.completions.create = AsyncMock(side_effect=err)

        with pytest.raises(CerebrasNonTransientError):
            await client.generate_response(prompt="Hello")

async def test_serialization_compatibility(client):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "id": "test-id",
        "choices": [{"message": {"content": "{\"prompt\":\"Test\",\"reasoning\":\"R\",\"strengths\":[\"S\"]}", "role": "assistant"}}],
        "model": "llama-4-scout-17b-16e-instruct",
        "usage": {"total_tokens": 100}
    }

    with patch("src.providers.cerebras_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        response = await client.generate_response(prompt="Hello")

        # ResponseNormalizer expects dictionary keys like choices[0].message.content, model, and usage
        assert "choices" in response
        assert "model" in response
        assert "usage" in response
        assert response["usage"]["total_tokens"] == 100
