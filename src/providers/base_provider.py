from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from src.models.council_response import CouncilResponse

class ProviderInitializationError(Exception):
    """Exception raised when a provider fails to initialize."""
    pass

class ProviderConfig(BaseModel):
    """Configuration schema for individual AI providers in the Council."""

    provider_name: str = Field(
        ...,
        description="The unique name identifying the AI provider (e.g. OpenAI, Claude, Gemini, DeepSeek)",
    )
    role: str = Field(
        ...,
        description="The role assigned to this provider in the council (e.g. creator, validator, refiner, critic)",
    )
    model_name: str = Field(
        ...,
        description="The specific provider model version or API identifier (e.g. gpt-4o, claude-3-5-sonnet)",
    )
    enabled: bool = Field(
        True,
        description="Flags whether this provider is active and should participate in prompt generation",
    )

    def get_provider_name(self) -> str:
        """Helper method to retrieve the provider name."""
        return self.provider_name

    def get_role(self) -> str:
        """Helper method to retrieve the assigned role."""
        return self.role

    def get_model_name(self) -> str:
        """Helper method to retrieve the model name."""
        return self.model_name


class BaseProvider(ABC):
    """Abstract Base Class representing a council model provider interface."""

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the provider with configuration.

        Args:
            config: The ProviderConfig instance containing provider details.
        """
        self.config = config

    def get_provider_name(self) -> str:
        """Retrieve the provider name."""
        return self.config.get_provider_name()

    def get_role(self) -> str:
        """Retrieve the council role assigned to this provider."""
        return self.config.get_role()

    def get_model_name(self) -> str:
        """Retrieve the specific model name used by this provider."""
        return self.config.get_model_name()

    def is_enabled(self) -> bool:
        """Check if this provider is currently enabled."""
        return self.config.enabled
        
    def validate_api_key(self, env_var: str) -> str:
        """Validates that an API key is present in the environment."""
        import os
        key = os.getenv(env_var)
        if not key or not key.strip():
            raise ProviderInitializationError(f"{self.get_provider_name()} provider requires the {env_var} environment variable.")
        return key.strip()

    @abstractmethod
    async def generate_response(
        self,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str,
    ) -> CouncilResponse:
        """Generate a standardized CouncilResponse based on the educational parameters.

        Args:
            topic: The topic of study.
            objective: The pedagogical objective or goal.
            learning_style: Targeted learning style (e.g. visual, verbal, active).
            difficulty: targeted difficulty level (e.g. beginner, intermediate, advanced).
            education_level: targeted grade level or learning stage.
            output_length: requested target length of the response.

        Returns:
            CouncilResponse: Standardized response object containing the prompt, reasoning, scores, and metadata.
        """
        pass
