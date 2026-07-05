import os
import logging
import time
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError, APIStatusError
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception

from src.models.council_response import CouncilResponse
from .base_provider import BaseProvider, ProviderConfig

# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger("aithera.sambanova_client")


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class SambaNovaError(Exception):
    """Base exception for SambaNova provider errors."""
    pass


class SambaNovaConfigError(SambaNovaError):
    """Exception raised when SambaNova configuration is invalid or missing."""
    pass


class SambaNovaAuthError(SambaNovaError):
    """Exception raised when SambaNova authentication fails."""
    pass


class SambaNovaRateLimitError(SambaNovaError):
    """Exception raised when SambaNova rate limits are exceeded."""
    pass


class SambaNovaTransientError(SambaNovaError):
    """Exception raised when SambaNova transient error retries are exhausted."""
    pass


class SambaNovaNonTransientError(SambaNovaError):
    """Exception raised for non-transient SambaNova errors."""
    pass


# ============================================================================
# SAMBANOVA CLIENT PROVIDER
# ============================================================================

class SambaNovaClient(BaseProvider):
    """Council provider interface client for SambaNova models."""

    PROVIDER_NAME = "SambaNova"
    DEFAULT_MODEL = "Meta-Llama-3.3-70B-Instruct"
    DEFAULT_ROLE = "creator"
    BASE_URL = "https://api.sambanova.ai/v1"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        """Initialize the SambaNova client with configuration, falling back to defaults if not provided."""
        env_model = os.getenv("SAMBANOVA_MODEL", self.DEFAULT_MODEL)
        if config is None:
            config = ProviderConfig(
                provider_name=self.PROVIDER_NAME,
                role=self.DEFAULT_ROLE,
                model_name=env_model,
                enabled=True,
            )
        super().__init__(config)

        # Load API key and timeout from environment
        self.api_key = os.getenv("SAMBANOVA_API_KEY")
        try:
            self.timeout = float(os.getenv("SAMBANOVA_TIMEOUT", "30"))
        except (ValueError, TypeError):
            self.timeout = 30.0

    def validate_config(self) -> None:
        """Validate that SambaNova client has required configuration."""
        if not self.api_key or not self.api_key.strip():
            raise SambaNovaConfigError("SambaNova API key is missing or empty.")

    def _build_prompt_from_template(
        self,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str
    ) -> str:
        """Load prompt template from prompts/gpt_teacher.txt and substitute variables."""
        from pathlib import Path

        # Resolve template file path
        root_dir = Path(__file__).parent.parent.parent
        template_path = root_dir / "prompts" / "gpt_teacher.txt"

        if not template_path.exists():
            logger.warning("Prompt template not found at %s. Using default format.", template_path)
            return (
                f"Create an educational prompt.\n"
                f"Topic: {topic}\n"
                f"Objective: {objective}\n"
                f"Learning Style: {learning_style}\n"
                f"Difficulty: {difficulty}\n"
                f"Education Level: {education_level}\n"
                f"Output Length: {output_length}"
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
                output_length=output_length
            )
        except Exception as e:
            logger.error("Failed to load/format prompt template: %s", str(e))
            raise SambaNovaError(f"Failed to build prompt from template: {str(e)}") from e

    async def generate_response(
        self,
        topic: str = "",
        objective: Optional[str] = None,
        learning_style: Optional[str] = None,
        difficulty: Optional[str] = None,
        education_level: Optional[str] = None,
        output_length: Optional[str] = None,
        prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate a prompt response using SambaNova.

        Accepts either:
        - A single `prompt` string (positional or keyword argument).
        - Educational parameters (topic, objective, etc.) from which the prompt is resolved.

        Returns:
            Dict[str, Any]: The raw OpenAI API-compatible response dictionary.
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
                output_length=output_length or ""
            )

        if not resolved_prompt or not resolved_prompt.strip():
            raise ValueError("Resolved prompt cannot be empty.")

        model = self.get_model_name()
        logger.info("Request start - Provider: SambaNova, Model: %s", model)

        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.BASE_URL,
            timeout=self.timeout
        )

        # Retry logic with tenacity
        def is_transient_error(exception: Exception) -> bool:
            if isinstance(exception, (APIConnectionError, APITimeoutError, RateLimitError)):
                return True
            if isinstance(exception, APIStatusError):
                return exception.status_code >= 500
            return False

        start_time = time.time()

        try:
            # Stagger request slightly to avoid immediate rate limit spikes when called concurrently
            import asyncio
            await asyncio.sleep(1.5)
            
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(4),
                wait=wait_exponential(multiplier=5, min=5, max=20),
                retry=retry_if_exception(is_transient_error),
                reraise=True
            ):
                with attempt:
                    attempt_num = attempt.retry_state.attempt_number
                    logger.info("=== SambaNova Request ===")
                    logger.info("Endpoint: %s/chat/completions", self.BASE_URL)
                    logger.info("Model: %s", model)
                    logger.info("Timeout: %s", self.timeout)
                    logger.info("Retry Number: %d/5", attempt_num)
                    
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": resolved_prompt}],
                    )
                    
                    # Try to extract request ID if available
                    request_id = response.id if hasattr(response, 'id') else 'unknown'
                    logger.info("Request ID: %s", request_id)
                    
                    duration = time.time() - start_time
                    logger.info("Request completed successfully in %.2f seconds", duration)

                    # Return raw response as Python dictionary
                    raw_response = response.model_dump()

                    # Add response_time so ResponseNormalizer can extract it
                    raw_response["response_time"] = duration
                    return raw_response

        except AuthenticationError as e:
            logger.error("Authentication failed: %s", str(e))
            raise SambaNovaAuthError(f"SambaNova Authentication failed: {str(e)}") from e
        except RateLimitError as e:
            logger.error("Rate limit error encountered: %s", str(e))
            raise SambaNovaRateLimitError(f"SambaNova rate limit error: {str(e)}") from e
        except (APIConnectionError, APITimeoutError) as e:
            logger.error("Transient error encountered: %s", str(e))
            raise SambaNovaTransientError(f"SambaNova transient error: {str(e)}") from e
        except APIStatusError as e:
            logger.error("API error status code %d: %s", e.status_code, str(e))
            if e.status_code >= 500:
                raise SambaNovaTransientError(f"SambaNova server error: {str(e)}") from e
            else:
                raise SambaNovaNonTransientError(f"SambaNova non-transient API error: {str(e)}") from e
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise SambaNovaError(f"Unexpected SambaNova provider error: {str(e)}") from e
