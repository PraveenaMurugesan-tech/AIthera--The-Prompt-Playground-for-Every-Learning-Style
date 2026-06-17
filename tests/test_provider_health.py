import pytest
import time
from src.providers.provider_health import ProviderHealth, ProviderHealthTracker


def test_provider_health_initial_state():
    """Verify that a newly initialized ProviderHealth starts with zeroed metrics."""
    health = ProviderHealth("groq")
    assert health.provider_name == "groq"
    assert health.total_requests == 0
    assert health.successful_requests == 0
    assert health.failed_requests == 0
    assert health.success_rate == 0.0
    assert health.average_response_time == 0.0
    assert health.last_success_timestamp is None


def test_provider_health_record_success():
    """Verify metrics update correctly on success."""
    health = ProviderHealth("groq")
    
    health.record_success(response_time=1.5)
    assert health.total_requests == 1
    assert health.successful_requests == 1
    assert health.failed_requests == 0
    assert health.success_rate == 1.0
    assert health.average_response_time == 1.5
    assert health.last_success_timestamp is not None
    
    # Record another success with different response time
    last_ts = health.last_success_timestamp
    time.sleep(0.01) # ensure timestamp updates
    health.record_success(response_time=2.5)
    assert health.total_requests == 2
    assert health.successful_requests == 2
    assert health.average_response_time == 2.0  # (1.5 + 2.5) / 2
    assert health.last_success_timestamp > last_ts


def test_provider_health_record_failure():
    """Verify metrics update correctly on failure."""
    health = ProviderHealth("gemini")
    
    health.record_failure()
    assert health.total_requests == 1
    assert health.successful_requests == 0
    assert health.failed_requests == 1
    assert health.success_rate == 0.0
    assert health.average_response_time == 0.0
    assert health.last_success_timestamp is None


def test_provider_health_mixed_requests():
    """Verify success rate is computed accurately with mixed success/failure."""
    health = ProviderHealth("claude")
    
    health.record_success(1.0)
    health.record_failure()
    health.record_success(2.0)
    health.record_failure()
    
    assert health.total_requests == 4
    assert health.successful_requests == 2
    assert health.failed_requests == 2
    assert health.success_rate == 0.5
    assert health.average_response_time == 1.5  # (1.0 + 2.0) / 2


def test_provider_health_report():
    """Verify health report generation returns correct keys and values."""
    health = ProviderHealth("deepseek")
    health.record_success(0.5)
    
    report = health.get_health_report()
    assert report["provider_name"] == "deepseek"
    assert report["total_requests"] == 1
    assert report["successful_requests"] == 1
    assert report["failed_requests"] == 0
    assert report["success_rate"] == 1.0
    assert report["average_response_time"] == 0.5
    assert report["last_success_timestamp"] is not None


def test_provider_health_reset():
    """Verify reset functionality sets all metrics back to initial state."""
    health = ProviderHealth("groq")
    health.record_success(1.0)
    health.record_failure()
    
    health.reset()
    assert health.total_requests == 0
    assert health.successful_requests == 0
    assert health.failed_requests == 0
    assert health.success_rate == 0.0
    assert health.average_response_time == 0.0
    assert health.last_success_timestamp is None


def test_provider_health_tracker():
    """Verify ProviderHealthTracker coordinates health metrics for multiple providers."""
    tracker = ProviderHealthTracker()
    
    tracker.record_success("groq", response_time=1.0)
    tracker.record_failure("gemini")
    
    report = tracker.get_health_report()
    assert "groq" in report
    assert "gemini" in report
    
    assert report["groq"]["successful_requests"] == 1
    assert report["gemini"]["failed_requests"] == 1
    
    # Verify reset clears all
    tracker.reset()
    report_after_reset = tracker.get_health_report()
    assert report_after_reset["groq"]["total_requests"] == 0
    assert report_after_reset["gemini"]["total_requests"] == 0
