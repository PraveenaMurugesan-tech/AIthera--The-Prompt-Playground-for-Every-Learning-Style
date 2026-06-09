from typing import Optional
from src.models.council_response import CouncilResponse
from .base_provider import BaseProvider, ProviderConfig


class OpenAIClient(BaseProvider):
    """Council provider interface client for OpenAI models (e.g. GPT)."""

    PROVIDER_NAME = "OpenAI"
    DEFAULT_MODEL = "gpt-4o"
    DEFAULT_ROLE = "creator"

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        """Initialize the OpenAI client with configuration, falling back to defaults if not provided."""
        if config is None:
            config = ProviderConfig(
                provider_name=self.PROVIDER_NAME,
                role=self.DEFAULT_ROLE,
                model_name=self.DEFAULT_MODEL,
                enabled=True,
            )
        super().__init__(config)

    async def generate_response(
        self,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str,
    ) -> CouncilResponse:
        """Generate a prompt response using OpenAI.

        Note:
            This is a placeholder implementation. The actual API connection is not yet implemented.

        Raises:
            NotImplementedError: Real API integration is not yet implemented.
        """
        raise NotImplementedError(
            f"API integration for {self.get_provider_name()} ({self.get_model_name()}) "
            f"is not yet implemented."
        )
