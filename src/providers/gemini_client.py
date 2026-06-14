import os
import logging
import time
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

import google.generativeai as genai
from google.api_core.exceptions import (
    GoogleAPICallError,
    Unauthenticated,
    PermissionDenied,
    DeadlineExceeded,
    ServiceUnavailable,
    ResourceExhausted,
)
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception

from src.models.council_response import CouncilResponse
from .base_provider import BaseProvider, ProviderConfig

# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger("aithera.gemini_client")


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class GeminiProviderError(Exception):
    """Base exception for Gemini provider errors."""
    pass


class GeminiConfigError(GeminiProviderError):
    """Exception raised when Gemini configuration is invalid or missing."""
    pass


class GeminiAuthError(GeminiProviderError):
    """Exception raised when Gemini authentication fails."""
    pass


class GeminiTransientError(GeminiProviderError):
    """Exception raised when Gemini transient error retries are exhausted."""
    pass


class GeminiNonTransientError(GeminiProviderError):
    """Exception raised for non-transient Gemini errors."""
    pass


# ============================================================================
# GEMINI CLIENT PROVIDER
# ============================================================================

class GeminiClient(BaseProvider):
    """Council provider interface client for Google models (e.g. Gemini)."""

    PROVIDER_NAME = "Gemini"
    DEFAULT_MODEL = "gemini-2.5-flash"
    DEFAULT_ROLE = "refiner"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        """Initialize the Gemini client with configuration, falling back to defaults if not provided."""
        env_model = os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)
        if config is None:
            config = ProviderConfig(
                provider_name=self.PROVIDER_NAME,
                role=self.DEFAULT_ROLE,
                model_name=env_model,
                enabled=True,
            )
        else:
            # Override model name from environment if defined
            env_model = os.getenv("GEMINI_MODEL")
            if env_model:
                config.model_name = env_model

        super().__init__(config)

        # Load API key and timeout from environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        try:
            self.timeout = float(os.getenv("GEMINI_TIMEOUT", "30"))
        except (ValueError, TypeError):
            self.timeout = 30.0

        if self.api_key and self.api_key.strip():
            genai.configure(api_key=self.api_key)

    def validate_config(self) -> None:
        """Validate that Gemini client has required configuration."""
        if not self.api_key or not self.api_key.strip():
            raise GeminiConfigError("Gemini API key is missing or empty.")

    def _build_prompt_from_template(
        self,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str
    ) -> str:
        """Load prompt template from prompts/gemini_visual.txt and substitute variables."""
        from pathlib import Path

        # Resolve template file path
        root_dir = Path(__file__).parent.parent.parent
        template_path = root_dir / "prompts" / "gemini_visual.txt"

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
            raise GeminiProviderError(f"Failed to build prompt from template: {str(e)}") from e

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
        """Generate a prompt response using Gemini.

        Accepts either:
        - A single `prompt` string (positional or keyword argument).
        - Educational parameters (topic, objective, etc.) from which the prompt is resolved.

        Returns:
            Dict[str, Any]: The raw Gemini API response dictionary format.
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

        model_name = self.get_model_name()
        logger.info("Request start - Provider: Gemini, Model: %s", model_name)

        # Re-configure on request in case API key environment changed
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(model_name)

        # Retry logic with tenacity
        def is_transient_error(exception: Exception) -> bool:
            if isinstance(exception, (DeadlineExceeded, ServiceUnavailable, ResourceExhausted, asyncio.TimeoutError)):
                return True
            if isinstance(exception, GoogleAPICallError):
                # Status codes: 408 (Timeout), 429 (Rate Limit / ResourceExhausted), 5xx (Server errors)
                if exception.code in (408, 429) or (exception.code and exception.code >= 500):
                    return True
            return False

        start_time = time.time()

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=5),
                retry=retry_if_exception(is_transient_error),
                reraise=True
            ):
                with attempt:
                    attempt_num = attempt.retry_state.attempt_number
                    logger.info("Sending Gemini API request (attempt %d/3)...", attempt_num)
                    
                    # Call async generation with timeout
                    response = await model.generate_content_async(
                        resolved_prompt,
                        request_options={"timeout": self.timeout}
                    )
                    
                    duration = time.time() - start_time
                    logger.info("Request completed successfully in %.2f seconds", duration)

                    # Extract generated text and token count
                    generated_text = response.text
                    total_tokens = 0
                    if hasattr(response, "usage_metadata") and response.usage_metadata:
                        total_tokens = getattr(response.usage_metadata, "total_token_count", 0)

                    # Return formatted dictionary satisfying both Gemini features and ResponseNormalizer candidate structure
                    return {
                        "provider": "gemini",
                        "model": model_name,
                        "content": generated_text,
                        "metadata": {
                            "tokens_used": total_tokens,
                            "response_time": duration,
                            "provider_version": model_name
                        },
                        "candidates": [
                            {
                                "content": {
                                    "parts": [
                                        {"text": generated_text}
                                    ]
                                }
                            }
                        ],
                        "usageMetadata": {
                            "totalTokenCount": total_tokens
                        },
                        "modelVersion": model_name,
                        "response_time": duration
                    }

        except (Unauthenticated, PermissionDenied) as e:
            logger.error("Authentication failed: %s", str(e))
            raise GeminiAuthError(f"Gemini Authentication failed: {str(e)}") from e
        except GoogleAPICallError as e:
            if e.code in (401, 403):
                logger.error("Authentication failed: %s", str(e))
                raise GeminiAuthError(f"Gemini Authentication failed: {str(e)}") from e
            elif e.code in (408, 429) or (e.code and e.code >= 500):
                logger.error("Transient error encountered: %s", str(e))
                raise GeminiTransientError(f"Gemini transient error: {str(e)}") from e
            else:
                logger.error("Non-transient error: %s", str(e))
                raise GeminiNonTransientError(f"Gemini non-transient API error: {str(e)}") from e
        except (DeadlineExceeded, ServiceUnavailable, ResourceExhausted, asyncio.TimeoutError) as e:
            logger.error("Transient error encountered: %s", str(e))
            raise GeminiTransientError(f"Gemini transient error: {str(e)}") from e
        except Exception as e:
            logger.error("Unexpected error occurred: %s", str(e))
            raise GeminiProviderError(f"Unexpected Gemini provider error: {str(e)}") from e
