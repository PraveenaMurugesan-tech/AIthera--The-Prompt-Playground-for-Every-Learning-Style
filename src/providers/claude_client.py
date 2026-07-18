import os
import logging
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from anthropic import AsyncAnthropic, APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError, APIStatusError
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception

from src.models.council_response import CouncilResponse
from .base_provider import BaseProvider, ProviderConfig

# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger("aithera.claude_client")


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ClaudeProviderError(Exception):
    """Base exception for Claude provider errors."""
    pass


class ClaudeConfigError(ClaudeProviderError):
    """Exception raised when Claude configuration is invalid or missing."""
    pass


class ClaudeAuthError(ClaudeProviderError):
    """Exception raised when Claude authentication fails."""
    pass


class ClaudeTransientError(ClaudeProviderError):
    """Exception raised when Claude transient error retries are exhausted."""
    pass


class ClaudeNonTransientError(ClaudeProviderError):
    """Exception raised for non-transient Claude errors."""
    pass


# ============================================================================
# CLAUDE CLIENT PROVIDER
# ============================================================================

class ClaudeClient(BaseProvider):
    """Council provider interface client for Anthropic models (e.g. Claude)."""

    PROVIDER_NAME = "Claude"
    DEFAULT_MODEL = "claude-3-5-sonnet"
    DEFAULT_ROLE = "validator"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        """Initialize the Claude client with configuration, falling back to defaults if not provided."""
        env_model = os.getenv("CLAUDE_MODEL", self.DEFAULT_MODEL)
        if config is None:
            config = ProviderConfig(
                provider_name=self.PROVIDER_NAME,
                role=self.DEFAULT_ROLE,
                model_name=env_model,
                enabled=True,
            )
        super().__init__(config)

        # Load API key and timeout from environment
        self.api_key = self.validate_api_key("CLAUDE_API_KEY")
        try:
            self.timeout = float(os.getenv("CLAUDE_TIMEOUT", "30"))
        except (ValueError, TypeError):
            self.timeout = 30.0

    def validate_config(self) -> None:
        """Validate that Claude client has required configuration."""
        if not self.api_key or not self.api_key.strip():
            raise ClaudeConfigError("Claude API key is missing or empty.")

    def _build_prompt_from_template(
        self,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str,
        bloom_level: str = 'understand'
    ) -> str:
        """Load prompt template from prompts/claude_reasoning.txt and substitute variables."""
        from pathlib import Path

        # Resolve template file path
        root_dir = Path(__file__).parent.parent.parent
        template_path = root_dir / "prompts" / "claude_reasoning.txt"

        if not template_path.exists():
            logger.warning("Prompt template not found at %s. Using default format.", template_path)
            return (
                f"Create an educational prompt.\\n"
                f"Topic: {topic}\\n"
                f"Objective: {objective}\\n"
                f"Learning Style: {learning_style}\\n"
                f"Difficulty: {difficulty}\\n"
                f"Education Level: {education_level}\\n"
                f"Output Length: {output_length}\n" \
                f"Bloom's Level: {bloom_level}"
            )

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            return template_content.format(
                topic=topic,
                objective=objective,
                learning_style=learning_style,
                difficulty=difficulty,
                education_level=education_level,
                output_length=output_length,
                bloom_level=bloom_level
            )
        except Exception as e:
            logger.error("Failed to load/format prompt template: %s", str(e))
            raise ClaudeProviderError(f"Failed to build prompt from template: {str(e)}") from e

    async def generate_response(
        self,
        topic: str = "",
        objective: Optional[str] = None,
        learning_style: Optional[str] = None,
        difficulty: Optional[str] = None,
        education_level: Optional[str] = None,
        output_length: Optional[str] = None,
        bloom_level: Optional[str] = None,
        prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate a prompt response using Claude.

        Accepts either:
        - A single `prompt` string (positional or keyword argument).
        - Educational parameters (topic, objective, etc.) from which the prompt is resolved.

        Returns:
            Dict[str, Any]: The raw Anthropic API response dictionary.
        """
        self.validate_config()

        # Resolve the prompt string
        resolved_prompt = ""
        if prompt is not None:
            resolved_prompt = prompt
        elif not objective and topic and not learning_style:
            # If only one positional parameter is passed, treat it as the prompt
            resolved_prompt = topic
        else:
            # Build prompt from template using the educational fields
            resolved_prompt = self._build_prompt_from_template(
                topic=topic,
                objective=objective or "",
                learning_style=learning_style or "",
                difficulty=difficulty or "",
                education_level=education_level or "",
                output_length=output_length or "",
                bloom_level=bloom_level or "understand"
            )

        if not resolved_prompt or not resolved_prompt.strip():
            raise ValueError("Resolved prompt cannot be empty.")

        model = self.get_model_name()
        logger.info("Request start - Provider: Claude, Model: %s", model)

        if not getattr(self, '_client', None):
            self._client = AsyncAnthropic(api_key=self.api_key, timeout=self.timeout)

        # Retry logic with tenacity
        def is_transient_error(exception: Exception) -> bool:
            if isinstance(exception, (APIConnectionError, APITimeoutError, RateLimitError)):
                return True
            if isinstance(exception, APIStatusError):
                return exception.status_code >= 500
            return False

        start_time = time.time()

        try:
            # We use AsyncRetrying to perform retries asynchronously
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=5),
                retry=retry_if_exception(is_transient_error),
                reraise=True
            ):
                with attempt:
                    attempt_num = attempt.retry_state.attempt_number
                    logger.info("Sending Claude API request (attempt %d/3)...", attempt_num)
                    response = await self._client.messages.create(
                        model=model,
                        max_tokens=4096,
                        messages=[{"role": "user", "content": resolved_prompt}],
                    )
                    duration = time.time() - start_time
                    logger.info("Request completed successfully in %.2f seconds", duration)

                    # Return raw response as Python dictionary
                    # Claude's response.model_dump() usually provides what we need
                    raw_response = response.model_dump()

                    # Add response_time so ResponseNormalizer can extract it
                    raw_response["response_time"] = duration
                    return raw_response

        except AuthenticationError as e:
            logger.error("Authentication failed: %s", str(e))
            raise ClaudeAuthError(f"Claude Authentication failed: {str(e)}") from e
        except (APIConnectionError, APITimeoutError, RateLimitError) as e:
            logger.error("Transient error encountered: %s", str(e))
            raise ClaudeTransientError(f"Claude transient error: {str(e)}") from e
        except APIStatusError as e:
            logger.error("API error status code %d: %s", e.status_code, str(e))
            if e.status_code >= 500:
                raise ClaudeTransientError(f"Claude server error: {str(e)}") from e
            else:
                raise ClaudeNonTransientError(f"Claude non-transient API error: {str(e)}") from e
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise ClaudeProviderError(f"Unexpected Claude provider error: {str(e)}") from e
