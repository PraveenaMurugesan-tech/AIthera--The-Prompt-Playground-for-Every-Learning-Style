import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.providers.sambanova_client import (
    SambaNovaClient,
    SambaNovaConfigError,
    SambaNovaAuthError,
    SambaNovaTransientError,
    SambaNovaNonTransientError,
    SambaNovaRateLimitError
)
from src.providers.base_provider import ProviderConfig
from openai import AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError, APIStatusError


@pytest.fixture
def mock_env():
    with patch("os.getenv") as mock_getenv:
        def getenv_side_effect(key, default=None):
            env_vars = {
                "SAMBANOVA_API_KEY": "test-key-123",
                "SAMBANOVA_MODEL": "Meta-Llama-3.3-70B-Instruct",
                "SAMBANOVA_TIMEOUT": "10"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        yield mock_getenv


@pytest.fixture
def client(mock_env):
    return SambaNovaClient()


@pytest.mark.anyio
async def test_generate_response_success(client):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "id": "test-id",
        "choices": [{"message": {"content": "SambaNova test output"}}],
        "model": "Meta-Llama-3.3-70B-Instruct",
        "usage": {"total_tokens": 42}
    }

    with patch("src.providers.sambanova_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        # Disable retries delay for tests
        with patch("src.providers.sambanova_client.wait_exponential", return_value=MagicMock()):
            response = await client.generate_response(prompt="Hello SambaNova")

        assert response["choices"][0]["message"]["content"] == "SambaNova test output"
        assert "response_time" in response
        mock_instance.chat.completions.create.assert_called_once()


def test_missing_api_key():
    with patch("os.getenv") as mock_getenv:
        def getenv_side_effect(key, default=None):
            if key == "SAMBANOVA_API_KEY":
                return None
            return default
        mock_getenv.side_effect = getenv_side_effect
        client = SambaNovaClient()
        with pytest.raises(SambaNovaConfigError):
            client.validate_config()


@pytest.mark.anyio
async def test_authentication_error(client):
    with patch("src.providers.sambanova_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=AuthenticationError(
                message="Invalid API Key",
                response=MagicMock(status_code=401),
                body=None
            )
        )

        with pytest.raises(SambaNovaAuthError):
            await client.generate_response(prompt="Test")


@pytest.mark.anyio
async def test_rate_limit_error(client):
    with patch("src.providers.sambanova_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=RateLimitError(
                message="Too many requests",
                response=MagicMock(status_code=429),
                body=None
            )
        )

        # Mock retries to fail quickly
        with patch("tenacity.wait_exponential", return_value=MagicMock()):
            with pytest.raises(SambaNovaRateLimitError):
                await client.generate_response(prompt="Test")


@pytest.mark.anyio
async def test_timeout_error(client):
    with patch("src.providers.sambanova_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APITimeoutError(request=MagicMock())
        )

        with pytest.raises(SambaNovaTransientError):
            await client.generate_response(prompt="Test")


@pytest.mark.anyio
async def test_api_status_error_500(client):
    with patch("src.providers.sambanova_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APIStatusError(
                message="Server Error",
                response=MagicMock(status_code=500),
                body=None
            )
        )

        with pytest.raises(SambaNovaTransientError):
            await client.generate_response(prompt="Test")


@pytest.mark.anyio
async def test_api_status_error_400(client):
    with patch("src.providers.sambanova_client.AsyncOpenAI") as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APIStatusError(
                message="Bad Request",
                response=MagicMock(status_code=400),
                body=None
            )
        )

        with pytest.raises(SambaNovaNonTransientError):
            await client.generate_response(prompt="Test")


@pytest.mark.anyio
async def test_empty_prompt(client):
    with pytest.raises(ValueError, match="Resolved prompt cannot be empty."):
        await client.generate_response(prompt="   ")
