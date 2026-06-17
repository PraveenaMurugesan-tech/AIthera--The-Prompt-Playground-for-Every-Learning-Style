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
        self.last_success_timestamp: Optional[float] = None

    def record_success(self, response_time: float = 0.0) -> None:
        """Record a successful request and update metrics.
        
        Args:
            response_time: The execution duration in seconds.
        """
        self.total_requests += 1
        self.successful_requests += 1
        self.last_success_timestamp = time.time()
        
        # Calculate new average response time
        prev_success_count = self.successful_requests - 1
        self.average_response_time = (
            (self.average_response_time * prev_success_count + response_time)
            / self.successful_requests
        )
        
        # Update success rate
        self.success_rate = self.successful_requests / self.total_requests

    def record_failure(self) -> None:
        """Record a failed request and update metrics."""
        self.total_requests += 1
        self.failed_requests += 1
        
        # Update success rate
        self.success_rate = self.successful_requests / self.total_requests

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
            "last_success_timestamp": self.last_success_timestamp,
        }

    def reset(self) -> None:
        """Reset all health metrics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.success_rate = 0.0
        self.average_response_time = 0.0
        self.last_success_timestamp = None


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

    def record_failure(self, provider_name: str) -> None:
        """Record a failure for a provider.
        
        Args:
            provider_name: The name of the provider.
        """
        tracker = self.get_provider_health(provider_name)
        tracker.record_failure()

    def get_health_report(self) -> Dict[str, Dict[str, Any]]:
        """Generate a complete health report for all tracked providers.
        
        Returns:
            Dict[str, Dict[str, Any]]: Map of provider name to health metrics.
        """
        return {name: tracker.get_health_report() for name, tracker in self._trackers.items()}

    def reset(self) -> None:
        """Reset all trackers."""
        for tracker in self._trackers.values():
            tracker.reset()
        logger.info("All provider health metrics reset.")
