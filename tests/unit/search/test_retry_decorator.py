"""Tests for retry decorator."""

import asyncio
from unittest.mock import patch

import pytest

from youtube_search_mcp.search.retry_decorator import async_retry


class TestAsyncRetry:
    """Tests for async_retry decorator."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Test that function succeeds on first attempt."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01)
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_func()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_success_after_retry(self):
        """Test that function succeeds after retry."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"

        result = await flaky_func()

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_failure_after_max_attempts(self):
        """Test that function fails after max attempts exhausted."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with pytest.raises(ValueError) as exc_info:
            await always_fails()

        assert "Persistent error" in str(exc_info.value)
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_custom_max_attempts(self):
        """Test custom max_attempts value."""
        call_count = 0

        @async_retry(max_attempts=5, delay=0.01, exceptions=(ValueError,))
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Error")

        with pytest.raises(ValueError):
            await always_fails()

        assert call_count == 5

    @pytest.mark.asyncio
    async def test_specific_exception_caught(self):
        """Test that only specified exceptions are caught."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        async def raises_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("Not caught")

        with pytest.raises(TypeError):
            await raises_type_error()

        # Should not retry because TypeError is not in exceptions
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_multiple_exceptions(self):
        """Test retry with multiple exception types."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01, exceptions=(ValueError, KeyError))
        async def raises_different_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First error")
            elif call_count == 2:
                raise KeyError("Second error")
            return "success"

        result = await raises_different_errors()

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test that delay increases exponentially."""
        delays = []

        @async_retry(max_attempts=4, delay=0.1, backoff=2.0, exceptions=(ValueError,))
        async def failing_func():
            raise ValueError("Error")

        original_sleep = asyncio.sleep

        async def mock_sleep(delay):
            delays.append(delay)
            await original_sleep(0.001)  # Minimal actual delay

        with patch("asyncio.sleep", mock_sleep):
            with pytest.raises(ValueError):
                await failing_func()

        # Should have delays: 0.1, 0.2, 0.4 (3 retries, no delay after last failure)
        assert len(delays) == 3
        assert delays[0] == pytest.approx(0.1)
        assert delays[1] == pytest.approx(0.2)
        assert delays[2] == pytest.approx(0.4)

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        """Test that decorator preserves function name."""

        @async_retry(max_attempts=3, delay=0.01)
        async def named_function():
            return "result"

        assert named_function.__name__ == "named_function"

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        """Test that args and kwargs are passed correctly."""

        @async_retry(max_attempts=3, delay=0.01)
        async def func_with_args(a, b, c=None):
            return (a, b, c)

        result = await func_with_args(1, 2, c=3)

        assert result == (1, 2, 3)

    @pytest.mark.asyncio
    async def test_returns_correct_value(self):
        """Test that correct return value is returned."""

        @async_retry(max_attempts=3, delay=0.01)
        async def returning_func():
            return {"key": "value", "list": [1, 2, 3]}

        result = await returning_func()

        assert result == {"key": "value", "list": [1, 2, 3]}

    @pytest.mark.asyncio
    async def test_default_exceptions(self):
        """Test default exception handling (catches all exceptions)."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01)
        async def raises_various_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("ValueError")
            elif call_count == 2:
                raise KeyError("KeyError")
            return "success"

        result = await raises_various_errors()

        assert result == "success"
        assert call_count == 3

