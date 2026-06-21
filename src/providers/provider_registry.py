"""
ProviderRegistry - Phase 20.1

Registers, instantiates, and manages AI providers in the Council.
"""

import logging
from typing import Dict, List, Type, Optional, Any
from src.providers.base_provider import BaseProvider, ProviderConfig
from src.providers.groq_client import GroqClient
from src.providers.gemini_client import GeminiClient
from src.providers.claude_client import ClaudeClient
from src.providers.deepseek_client import DeepSeekClient
from src.providers.openrouter_client import OpenRouterClient
from src.providers.cerebras_client import CerebrasClient

logger = logging.getLogger("aithera.provider_registry")


class ProviderRegistry:
    """Registry for managing Council model providers.
    
    Responsibilities:
    - Register providers (classes)
    - Instantiate providers (on demand or on init)
    - Enable/disable providers
    - Return active providers
    - Validate provider names
    """

    # Mapping of default provider names to their client classes
    _DEFAULT_PROVIDERS: Dict[str, Type[BaseProvider]] = {
        "groq": GroqClient,
        "gemini": GeminiClient,
        "claude": ClaudeClient,
        "deepseek": DeepSeekClient,
        "openrouter": OpenRouterClient,
        "cerebras": CerebrasClient,
    }

    def __init__(self) -> None:
        """Initialize the ProviderRegistry and register default providers."""
        self._providers: Dict[str, BaseProvider] = {}
        self._provider_classes: Dict[str, Type[BaseProvider]] = dict(self._DEFAULT_PROVIDERS)
        
        # Instantiate default providers
        for name, cls in self._provider_classes.items():
            try:
                self._providers[name] = cls()
            except Exception as e:
                logger.warning("Failed to initialize default provider '%s': %s", name, e)

    def validate_name(self, name: str) -> str:
        """Validate provider name and return its standardized lowercase form.
        
        Args:
            name: Name of the provider.
            
        Returns:
            str: Standardized lowercase name.
            
        Raises:
            ValueError: If the provider is unknown.
        """
        if not name:
            raise ValueError("Provider name cannot be empty.")
        
        std_name = name.strip().lower()
        if std_name not in self._provider_classes:
            raise ValueError(
                f"Unknown provider: '{name}'. Supported providers: "
                f"{', '.join(self._provider_classes.keys())}"
            )
        return std_name

    def register_provider(
        self, 
        name: str, 
        provider_class: Type[BaseProvider], 
        config: Optional[ProviderConfig] = None
    ) -> None:
        """Register a new provider class and optionally instantiate it with config.
        
        Args:
            name: Unique identifier for the provider.
            provider_class: The class inheriting from BaseProvider.
            config: Optional config to instantiate the provider with.
        """
        if not name or not name.strip():
            raise ValueError("Provider name cannot be empty.")
        if not issubclass(provider_class, BaseProvider):
            raise TypeError("Provider class must inherit from BaseProvider.")
            
        std_name = name.strip().lower()
        self._provider_classes[std_name] = provider_class
        
        # Instantiate immediately
        self._providers[std_name] = provider_class(config)
        logger.info("Registered provider '%s'", std_name)

    def get_provider(self, name: str) -> BaseProvider:
        """Retrieve the instantiated provider by name.
        
        Args:
            name: Name of the provider.
            
        Returns:
            BaseProvider: The instantiated provider instance.
            
        Raises:
            ValueError: If the provider is unknown.
        """
        std_name = self.validate_name(name)
        if std_name not in self._providers:
            # Lazy instantiation fallback
            cls = self._provider_classes[std_name]
            self._providers[std_name] = cls()
        return self._providers[std_name]

    def enable_provider(self, name: str) -> None:
        """Enable a provider by name.
        
        Args:
            name: Name of the provider.
            
        Raises:
            ValueError: If the provider is unknown.
        """
        provider = self.get_provider(name)
        provider.config.enabled = True
        logger.info("Enabled provider '%s'", name)

    def disable_provider(self, name: str) -> None:
        """Disable a provider by name.
        
        Args:
            name: Name of the provider.
            
        Raises:
            ValueError: If the provider is unknown.
        """
        provider = self.get_provider(name)
        provider.config.enabled = False
        logger.info("Disabled provider '%s'", name)

    def get_all_providers(self) -> Dict[str, BaseProvider]:
        """Return all registered provider instances.
        
        Returns:
            Dict[str, BaseProvider]: Dictionary mapping provider names to instances.
        """
        # Ensure all registered classes are instantiated
        for name in self._provider_classes:
            if name not in self._providers:
                self._providers[name] = self._provider_classes[name]()
        return dict(self._providers)

    def get_active_providers(self) -> Dict[str, BaseProvider]:
        """Return all active (enabled) provider instances.
        
        Returns:
            Dict[str, BaseProvider]: Dictionary mapping active provider names to instances.
        """
        all_providers = self.get_all_providers()
        return {name: prov for name, prov in all_providers.items() if prov.is_enabled()}
