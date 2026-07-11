import pytest
import time
from unittest.mock import patch, MagicMock
from src.council.council_cache import CouncilCache
from src.models.prompt_request import PromptRequest

@pytest.fixture
def cache():
    c = CouncilCache()
    c.clear()
    return c

@pytest.fixture
def request_mock():
    req = PromptRequest(
        user_id=1,
        topic="Testing Caching",
        learning_style="Visual",
        difficulty="Beginner",
        objective="Understand Caching",
        output_length="Short",
        education_level="High School"
    )
    return req

def test_generate_key_is_deterministic(cache, request_mock):
    key1 = cache._generate_key(request_mock)
    key2 = cache._generate_key(request_mock)
    assert key1 == key2

def test_cache_set_and_get(cache, request_mock):
    mock_result = {"status": "success"}
    cache.set(request_mock, mock_result)
    
    result = cache.get(request_mock)
    assert result == mock_result
    assert cache.hits == 1
    assert cache.misses == 0

def test_cache_miss(cache, request_mock):
    result = cache.get(request_mock)
    assert result is None
    assert cache.hits == 0
    assert cache.misses == 1

@patch("src.council.council_cache.settings")
def test_cache_ttl_expiration(mock_settings, cache, request_mock):
    mock_settings.CACHE_ENABLED = True
    mock_settings.CACHE_TTL_SECONDS = 0.1
    
    mock_result = {"status": "success"}
    cache.set(request_mock, mock_result)
    
    time.sleep(0.2) # Wait for TTL to expire
    
    result = cache.get(request_mock)
    assert result is None
    assert cache.hits == 0
    assert cache.misses == 1

def test_cache_clear(cache, request_mock):
    cache.set(request_mock, {"a": 1})
    cache.clear()
    
    result = cache.get(request_mock)
    assert result is None
    assert cache.misses == 1
    
def test_cleanup_expired(cache, request_mock):
    # Set one normal
    cache.set(request_mock, {"status": "success"})
    
    # Set one expired by modifying timestamp
    key2 = "expired_key"
    cache._cache[key2] = (time.time() - 4000, {"status": "old"})
    
    removed = cache.cleanup_expired()
    assert removed == 1
    assert key2 not in cache._cache
