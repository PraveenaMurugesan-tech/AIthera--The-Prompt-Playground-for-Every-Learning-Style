import os
from dataclasses import dataclass

@dataclass
class CouncilSettings:
    """Centralized configuration for the AI Council."""
    
    # Caching
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # Provider Settings
    PROVIDER_TIMEOUT_DEFAULT: float = float(os.getenv("PROVIDER_TIMEOUT_DEFAULT", "60.0"))
    PROVIDER_RETRY_LIMIT: int = int(os.getenv("PROVIDER_RETRY_LIMIT", "3"))
    MAX_PARALLEL_PROVIDERS: int = int(os.getenv("MAX_PARALLEL_PROVIDERS", "10"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Health Monitoring
    HEALTH_MAX_CONSECUTIVE_FAILURES: int = int(os.getenv("HEALTH_MAX_CONSECUTIVE_FAILURES", "3"))
    HEALTH_RECOVERY_INTERVAL: float = float(os.getenv("HEALTH_RECOVERY_INTERVAL", "60.0"))

settings = CouncilSettings()
