"""
ProviderHealth - Phase 20.4

Tracks and monitors the health and performance of AI providers.
"""

import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger("aithera.provider_health")


class ProviderHealth:
    """Tracks health and performance metrics for a single provider."""

    def __init__(self, provider_name: str) -> None:
        """Initialize ProviderHealth metrics.
        
        Args:
            provider_name: The name of the provider.
        """
        self.provider_name = provider_name
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.success_rate = 0.0
        self.average_response_time = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        self.timeout_count = 0
        self.retry_count = 0
        self.last_success_timestamp: Optional[float] = None
        self.last_failed_timestamp: Optional[float] = None
        self.consecutive_failures = 0
        self.disabled_until: Optional[float] = None

    def record_success(self, response_time: float = 0.0) -> None:
        """Record a successful request and update metrics.
        
        Args:
            response_time: The execution duration in seconds.
        """
        self.total_requests += 1
        self.successful_requests += 1
        self.last_success_timestamp = time.time()
        self.consecutive_failures = 0
        
        # Calculate latencies
        if response_time > 0:
            self.min_latency = min(self.min_latency, response_time)
            self.max_latency = max(self.max_latency, response_time)
            
        prev_success_count = self.successful_requests - 1
        self.average_response_time = (
            (self.average_response_time * prev_success_count + response_time)
            / self.successful_requests
        )
        
        # Update success rate
        self.success_rate = self.successful_requests / self.total_requests
        self.success_rate = self.successful_requests / self.total_requests

    def record_failure(self, is_timeout: bool = False, retries: int = 0) -> None:
        """Record a failed request and update metrics."""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failed_timestamp = time.time()
        self.consecutive_failures += 1
        
        if is_timeout:
            self.timeout_count += 1
        self.retry_count += retries
        
        # Update success rate
        self.success_rate = self.successful_requests / self.total_requests
        
    def get_score(self) -> float:
        """Calculate intelligent provider ranking score (0.0 to 100.0).
        Considers success rate, latency, and recency of failure.
        """
        if self.total_requests == 0:
            return 50.0  # Neutral starting score
            
        score = self.success_rate * 80.0  # Up to 80 points for success
        
        # Up to 20 points for speed (assuming 1s is excellent, >30s is poor)
        avg_lat = self.average_response_time
        if avg_lat <= 0:
            speed_score = 0
        elif avg_lat <= 2.0:
            speed_score = 20.0
        elif avg_lat >= 30.0:
            speed_score = 0.0
        else:
            speed_score = 20.0 * (1.0 - (avg_lat - 2.0) / 28.0)
            
        score += speed_score
        
        # Penalty for consecutive failures
        score -= min(self.consecutive_failures * 10.0, 30.0)
        
        return max(0.0, min(100.0, score))

    def get_health_report(self) -> Dict[str, Any]:
        """Generate a dictionary report of this provider's health.
        
        Returns:
            Dict[str, Any]: Health metrics.
        """
        return {
            "provider_name": self.provider_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.success_rate,
            "average_response_time": self.average_response_time,
            "min_latency": self.min_latency if self.min_latency != float('inf') else 0.0,
            "max_latency": self.max_latency,
            "timeout_count": self.timeout_count,
            "retry_count": self.retry_count,
            "consecutive_failures": self.consecutive_failures,
            "last_success_timestamp": self.last_success_timestamp,
            "last_failed_timestamp": self.last_failed_timestamp,
            "score": self.get_score(),
        }

    def reset(self) -> None:
        """Reset all health metrics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.success_rate = 0.0
        self.average_response_time = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        self.timeout_count = 0
        self.retry_count = 0
        self.last_success_timestamp = None
        self.last_failed_timestamp = None
        self.consecutive_failures = 0
        self.disabled_until = None


class ProviderHealthTracker:
    """Manages health tracking for all providers in the registry."""

    def __init__(self) -> None:
        """Initialize the ProviderHealthTracker."""
        self._trackers: Dict[str, ProviderHealth] = {}

    def get_provider_health(self, provider_name: str) -> ProviderHealth:
        """Retrieve or create a ProviderHealth instance for a provider.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            ProviderHealth: The health tracker for the provider.
        """
        std_name = provider_name.strip().lower()
        if std_name not in self._trackers:
            self._trackers[std_name] = ProviderHealth(provider_name)
        return self._trackers[std_name]

    def record_success(self, provider_name: str, response_time: float = 0.0) -> None:
        """Record a success for a provider.
        
        Args:
            provider_name: The name of the provider.
            response_time: The execution duration in seconds.
        """
        tracker = self.get_provider_health(provider_name)
        tracker.record_success(response_time)

    def record_failure(self, provider_name: str, is_timeout: bool = False, retries: int = 0) -> None:
        """Record a failure for a provider.
        
        Args:
            provider_name: The name of the provider.
            is_timeout: Whether it failed due to timeout.
            retries: Number of retries attempted.
        """
        tracker = self.get_provider_health(provider_name)
        tracker.record_failure(is_timeout=is_timeout, retries=retries)
        
        # Temporary disablement logic if threshold is hit
        from src.config.settings import settings
        if tracker.consecutive_failures >= settings.HEALTH_MAX_CONSECUTIVE_FAILURES:
            tracker.disabled_until = time.time() + settings.HEALTH_RECOVERY_INTERVAL
            logger.warning(f"Provider {provider_name} temporarily disabled due to {tracker.consecutive_failures} failures.")

    def get_health_report(self) -> Dict[str, Dict[str, Any]]:
        """Generate a complete health report for all tracked providers.
        
        Returns:
            Dict[str, Dict[str, Any]]: Map of provider name to health metrics.
        """
        return {name: tracker.get_health_report() for name, tracker in self._trackers.items()}

    def get_provider_status(self, provider_name: str) -> str:
        """Get a human-readable status for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            str: "Healthy (XX%)" or "Failing".
        """
        tracker = self.get_provider_health(provider_name)
        if tracker.total_requests == 0:
            return "Healthy (100%)"
        
        pct = int(tracker.success_rate * 100)
        if pct < 50 and tracker.total_requests >= 2:
            return f"Failing ({pct}%)"
        return f"Healthy ({pct}%)"

    def get_all_provider_stats(self) -> Dict[str, str]:
        """Get formatted status for all providers.
        
        Returns:
            Dict[str, str]: Map of provider name to human-readable status.
        """
        return {name.capitalize(): self.get_provider_status(name) for name in self._trackers.keys()}

    def get_provider_rankings(self) -> list[Dict[str, Any]]:
        """Return a ranked list of providers based on intelligent scoring.
        
        Returns:
            list[Dict[str, Any]]: Sorted list of provider health reports.
        """
        reports = list(self.get_health_report().values())
        return sorted(reports, key=lambda x: x["score"], reverse=True)

    def reset(self) -> None:
        """Reset all trackers."""
        for tracker in self._trackers.values():
            tracker.reset()
        logger.info("All provider health metrics reset.")
