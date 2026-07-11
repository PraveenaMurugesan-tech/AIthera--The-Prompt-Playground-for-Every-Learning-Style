import hashlib
import json
import logging
import time
from typing import Optional, Dict, Any, Tuple

from src.config.settings import settings
from src.models.prompt_request import PromptRequest

logger = logging.getLogger("aithera.council_cache")

class CouncilCache:
    """Intelligent response cache for AI Council requests."""

    def __init__(self) -> None:
        """Initialize the cache with settings."""
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self.hits = 0
        self.misses = 0

    def _generate_key(self, request: PromptRequest) -> str:
        """Generate a deterministic cache key based on request parameters.
        
        Args:
            request: The PromptRequest to hash.
            
        Returns:
            str: The generated cache key.
        """
        # Include all relevant parameters that define a unique request
        key_data = {
            "topic": str(request.topic).lower().strip(),
            "learning_style": str(request.learning_style).lower().strip(),
            "difficulty": str(request.difficulty).lower().strip(),
            "objective": str(request.objective).lower().strip(),
            "output_length": str(request.output_length).lower().strip(),
            "education_level": str(request.education_level).lower().strip()
        }
        
        # Create a stable JSON string and hash it
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def get(self, request: PromptRequest) -> Optional[Any]:
        """Retrieve a cached response if valid and enabled.
        
        Args:
            request: The PromptRequest to look up.
            
        Returns:
            Optional[Any]: The cached result, or None if miss/disabled/expired.
        """
        if not settings.CACHE_ENABLED:
            return None
            
        key = self._generate_key(request)
        cached_item = self._cache.get(key)
        
        if cached_item:
            timestamp, data = cached_item
            if time.time() - timestamp <= settings.CACHE_TTL_SECONDS:
                self.hits += 1
                logger.info(f"Cache hit for topic '{request.topic}' (Key: {key[:8]}...)")
                return data
            else:
                # Expired
                del self._cache[key]
                
        self.misses += 1
        logger.debug(f"Cache miss for topic '{request.topic}'")
        return None

    def set(self, request: PromptRequest, result: Any) -> None:
        """Store a response in the cache.
        
        Args:
            request: The PromptRequest to use for the key.
            result: The result to cache.
        """
        if not settings.CACHE_ENABLED:
            return
            
        key = self._generate_key(request)
        self._cache[key] = (time.time(), result)
        logger.info(f"Cached response for topic '{request.topic}' (Key: {key[:8]}...)")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics.
        
        Returns:
            Dict[str, Any]: Dictionary of cache hits, misses, size, and hit ratio.
        """
        total = self.hits + self.misses
        hit_ratio = (self.hits / total) if total > 0 else 0.0
        
        return {
            "enabled": settings.CACHE_ENABLED,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_ratio": hit_ratio,
            "size": len(self._cache)
        }

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared manually.")

    def cleanup_expired(self) -> int:
        """Remove expired entries from the cache.
        
        Returns:
            int: Number of entries removed.
        """
        now = time.time()
        expired_keys = [
            k for k, (timestamp, _) in self._cache.items() 
            if now - timestamp > settings.CACHE_TTL_SECONDS
        ]
        
        for k in expired_keys:
            del self._cache[k]
            
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries.")
            
        return len(expired_keys)

# Global cache instance
council_cache = CouncilCache()
