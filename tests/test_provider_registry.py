import pytest
from src.providers.provider_registry import ProviderRegistry
from src.providers.base_provider import BaseProvider, ProviderConfig
from src.providers.groq_client import GroqClient
from src.providers.gemini_client import GeminiClient
from src.providers.claude_client import ClaudeClient
from src.providers.deepseek_client import DeepSeekClient


class DummyProvider(BaseProvider):
    """Dummy provider for testing registration."""
    async def generate_response(self, *args, **kwargs):
        pass


def test_provider_registry_default_providers():
    """Verify that default providers are registered and instantiated."""
    registry = ProviderRegistry()
    
    # Check that default providers exist in all providers
    all_providers = registry.get_all_providers()
    assert "groq" in all_providers
    assert "gemini" in all_providers
    assert "claude" in all_providers
    assert "deepseek" in all_providers
    
    # Verify correct classes
    assert isinstance(registry.get_provider("groq"), GroqClient)
    assert isinstance(registry.get_provider("gemini"), GeminiClient)
    assert isinstance(registry.get_provider("claude"), ClaudeClient)
    assert isinstance(registry.get_provider("deepseek"), DeepSeekClient)


def test_provider_registry_case_insensitive():
    """Verify that provider retrieval is case-insensitive."""
    registry = ProviderRegistry()
    
    p1 = registry.get_provider("Groq")
    p2 = registry.get_provider("groq")
    p3 = registry.get_provider("GROQ")
    
    assert p1 is p2 is p3


def test_provider_registry_unknown_provider():
    """Verify that retrieving an unknown provider raises ValueError."""
    registry = ProviderRegistry()
    
    with pytest.raises(ValueError, match="Unknown provider: 'unknown'"):
        registry.get_provider("unknown")


def test_provider_registry_register_custom_provider():
    """Verify that custom providers can be registered and retrieved."""
    registry = ProviderRegistry()
    
    config = ProviderConfig(
        provider_name="dummy",
        role="tester",
        model_name="dummy-v1",
        enabled=True
    )
    
    registry.register_provider("dummy", DummyProvider, config)
    
    provider = registry.get_provider("dummy")
    assert isinstance(provider, DummyProvider)
    assert provider.get_provider_name() == "dummy"
    assert provider.get_role() == "tester"
    assert provider.get_model_name() == "dummy-v1"
    
    all_providers = registry.get_all_providers()
    assert "dummy" in all_providers


def test_provider_registry_enable_disable():
    """Verify that providers can be enabled and disabled, and filtering works."""
    registry = ProviderRegistry()
    
    # All defaults should be enabled initially
    active = registry.get_active_providers()
    assert "groq" in active
    assert "gemini" in active
    
    registry.disable_provider("groq")
    assert not registry.get_provider("groq").is_enabled()
    
    active = registry.get_active_providers()
    assert "groq" not in active
    assert "gemini" in active
    
    registry.enable_provider("groq")
    assert registry.get_provider("groq").is_enabled()
    
    active = registry.get_active_providers()
    assert "groq" in active


def test_provider_registry_invalid_registration():
    """Verify registry raises errors for invalid inputs during registration."""
    registry = ProviderRegistry()
    
    with pytest.raises(ValueError, match="Provider name cannot be empty"):
        registry.register_provider("", DummyProvider)
        
    with pytest.raises(TypeError, match="Provider class must inherit from BaseProvider"):
        registry.register_provider("invalid", object)  # type: ignore
