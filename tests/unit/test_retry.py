"""Tests for retry logic."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from vaulty.exceptions import VaultyAPIError, VaultyRateLimitError
from vaulty.retry import RetryConfig, retry_with_backoff


@pytest.mark.asyncio
async def test_retry_config_defaults():
    """Test RetryConfig default values."""
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.initial_delay == 1.0
    assert config.max_delay == 60.0
    assert config.backoff_factor == 2.0
    assert config.jitter is True


@pytest.mark.asyncio
async def test_retry_config_custom():
    """Test RetryConfig with custom values."""
    config = RetryConfig(
        max_retries=5, initial_delay=2.0, max_delay=120.0, backoff_factor=3.0, jitter=False
    )
    assert config.max_retries == 5
    assert config.initial_delay == 2.0
    assert config.max_delay == 120.0
    assert config.backoff_factor == 3.0
    assert config.jitter is False


@pytest.mark.asyncio
async def test_retry_success_first_attempt():
    """Test retry succeeds on first attempt."""
    func = AsyncMock(return_value="success")

    result = await retry_with_backoff(func)

    assert result == "success"
    assert func.call_count == 1


@pytest.mark.asyncio
async def test_retry_success_after_failures():
    """Test retry succeeds after some failures."""
    func = AsyncMock(
        side_effect=[VaultyAPIError("Error", 500), VaultyAPIError("Error", 500), "success"]
    )

    config = RetryConfig(max_retries=3, initial_delay=0.01)
    result = await retry_with_backoff(func, config)

    assert result == "success"
    assert func.call_count == 3


@pytest.mark.asyncio
async def test_retry_exhausts_retries():
    """Test retry raises exception after exhausting retries."""
    func = AsyncMock(side_effect=VaultyAPIError("Error", 500))

    config = RetryConfig(max_retries=2, initial_delay=0.01)

    with pytest.raises(VaultyAPIError):
        await retry_with_backoff(func, config)

    assert func.call_count == 3  # Initial + 2 retries


@pytest.mark.asyncio
async def test_retry_rate_limit_with_retry_after():
    """Test retry handles rate limit with Retry-After header."""
    func = AsyncMock(
        side_effect=[
            VaultyRateLimitError("Rate limit", 429, "Too many", retry_after=0.01),
            "success",
        ]
    )

    config = RetryConfig(max_retries=3, initial_delay=0.01)
    result = await retry_with_backoff(func, config)

    assert result == "success"
    assert func.call_count == 2


@pytest.mark.asyncio
async def test_retry_no_retry_on_4xx():
    """Test retry doesn't retry on 4xx errors (except rate limit)."""
    func = AsyncMock(side_effect=VaultyAPIError("Bad request", 400))

    config = RetryConfig(max_retries=3, initial_delay=0.01)

    with pytest.raises(VaultyAPIError):
        await retry_with_backoff(func, config)

    assert func.call_count == 1  # No retries for 4xx


@pytest.mark.asyncio
async def test_retry_retries_on_5xx():
    """Test retry retries on 5xx errors."""
    func = AsyncMock(side_effect=[VaultyAPIError("Server error", 500), "success"])

    config = RetryConfig(max_retries=3, initial_delay=0.01)
    result = await retry_with_backoff(func, config)

    assert result == "success"
    assert func.call_count == 2


@pytest.mark.asyncio
async def test_retry_handles_generic_exception():
    """Test retry handles generic exceptions."""
    func = AsyncMock(side_effect=[ConnectionError("Network error"), "success"])

    config = RetryConfig(max_retries=3, initial_delay=0.01)
    result = await retry_with_backoff(func, config)

    assert result == "success"
    assert func.call_count == 2


@pytest.mark.asyncio
async def test_retry_delay_calculation():
    """Test retry delay calculation with backoff."""
    func = AsyncMock(side_effect=VaultyAPIError("Error", 500))
    delays = []

    original_sleep = asyncio.sleep

    async def mock_sleep(delay):
        delays.append(delay)
        await original_sleep(0)  # Minimal delay for test speed

    config = RetryConfig(max_retries=2, initial_delay=1.0, backoff_factor=2.0, jitter=False)

    with patch("asyncio.sleep", side_effect=mock_sleep), pytest.raises(VaultyAPIError):
        await retry_with_backoff(func, config)

    # Should have delays: 1.0, 2.0 (backoff_factor * initial_delay)
    assert len(delays) == 2
    assert delays[0] == 1.0
    assert delays[1] == 2.0


@pytest.mark.asyncio
async def test_retry_respects_max_delay():
    """Test retry respects max_delay."""
    func = AsyncMock(side_effect=VaultyAPIError("Error", 500))
    delays = []

    original_sleep = asyncio.sleep

    async def mock_sleep(delay):
        delays.append(delay)
        await original_sleep(0)

    config = RetryConfig(
        max_retries=2, initial_delay=50.0, backoff_factor=2.0, max_delay=60.0, jitter=False
    )

    with patch("asyncio.sleep", side_effect=mock_sleep), pytest.raises(VaultyAPIError):
        await retry_with_backoff(func, config)

    # Second delay should be capped at max_delay (100 * 2 = 200, but max is 60)
    assert delays[1] <= 60.0
