import pytest
import time
from src.providers.provider_health import ProviderHealth, ProviderHealthTracker
from src.config.settings import settings

def test_provider_health_metrics():
    health = ProviderHealth("test_provider")
    
    # Simulate success
    health.record_success(response_time=1.5)
    assert health.total_requests == 1
    assert health.successful_requests == 1
    assert health.average_response_time == 1.5
    assert health.success_rate == 1.0
    
    # Simulate failure
    health.record_failure(is_timeout=True, retries=2)
    assert health.total_requests == 2
    assert health.failed_requests == 1
    assert health.timeout_count == 1
    assert health.retry_count == 2
    assert health.consecutive_failures == 1
    assert health.success_rate == 0.5
    
def test_provider_ranking_score():
    health = ProviderHealth("test_provider")
    
    # New provider should start at 50
    assert health.get_score() == 50.0
    
    # Excellent provider
    for _ in range(10):
        health.record_success(0.5)
    
    score = health.get_score()
    # 80 for success + 20 for speed - 0 for failures = 100
    assert score == 100.0
    
    # Terrible provider
    health.reset()
    for _ in range(3):
        health.record_failure()
    score = health.get_score()
    # 0 for success + 0 for speed (avg latency 0) - 30 for failures = -30 -> max(0, -30) -> 0
    assert score == 0.0
    
def test_provider_temporary_disablement():
    tracker = ProviderHealthTracker()
    tracker.reset()
    
    settings.HEALTH_MAX_CONSECUTIVE_FAILURES = 3
    
    # 3 failures should disable
    tracker.record_failure("test1")
    tracker.record_failure("test1")
    tracker.record_failure("test1")
    
    h = tracker.get_provider_health("test1")
    assert h.consecutive_failures == 3
    assert h.disabled_until is not None
    assert h.disabled_until > time.time()
    
def test_provider_rankings_sorting():
    tracker = ProviderHealthTracker()
    tracker.reset()
    
    # Fast reliable provider
    for _ in range(5):
        tracker.record_success("fast", 0.5)
        
    # Slow reliable provider
    for _ in range(5):
        tracker.record_success("slow", 10.0)
        
    # Failing provider
    for _ in range(5):
        tracker.record_failure("failing")
        
    rankings = tracker.get_provider_rankings()
    
    assert len(rankings) == 3
    assert rankings[0]["provider_name"] == "fast"
    assert rankings[1]["provider_name"] == "slow"
    assert rankings[2]["provider_name"] == "failing"
