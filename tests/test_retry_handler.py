"""Tests for src/retry_handler.py."""
from __future__ import annotations

import pytest

from src.retry_handler import RetryExhausted, with_retry


# ---------------------------------------------------------------------------
# RetryExhausted
# ---------------------------------------------------------------------------


class TestRetryExhausted:
    def test_stores_attempts_and_last_error(self):
        err = ValueError("boom")
        exc = RetryExhausted(3, err)
        assert exc.attempts == 3
        assert exc.last_error is err

    def test_str_contains_attempt_count(self):
        exc = RetryExhausted(2, RuntimeError("oops"))
        assert "2" in str(exc)
        assert "oops" in str(exc)


# ---------------------------------------------------------------------------
# with_retry — success paths
# ---------------------------------------------------------------------------


def test_returns_value_on_first_success():
    result = with_retry(lambda: 42, retries=3, backoff=0)
    assert result == 42


def test_succeeds_after_transient_failures(mocker):
    mocker.patch("src.retry_handler.time.sleep")  # don't actually sleep
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"

    result = with_retry(flaky, retries=3, backoff=0.1, retryable=(ConnectionError,))
    assert result == "ok"
    assert calls["n"] == 3


# ---------------------------------------------------------------------------
# with_retry — exhaustion
# ---------------------------------------------------------------------------


def test_raises_retry_exhausted_after_all_attempts(mocker):
    mocker.patch("src.retry_handler.time.sleep")
    attempts = {"n": 0}

    def always_fails():
        attempts["n"] += 1
        raise TimeoutError("slow")

    with pytest.raises(RetryExhausted) as exc_info:
        with_retry(always_fails, retries=3, backoff=0.1, retryable=(TimeoutError,))

    assert exc_info.value.attempts == 3
    assert attempts["n"] == 3


def test_non_retryable_exception_propagates_immediately(mocker):
    mocker.patch("src.retry_handler.time.sleep")
    calls = {"n": 0}

    def raises_value_error():
        calls["n"] += 1
        raise ValueError("not retryable")

    with pytest.raises(ValueError, match="not retryable"):
        with_retry(
            raises_value_error,
            retries=5,
            backoff=0,
            retryable=(ConnectionError,),
        )

    assert calls["n"] == 1  # only called once


# ---------------------------------------------------------------------------
# with_retry — validation
# ---------------------------------------------------------------------------


def test_raises_value_error_for_zero_retries():
    with pytest.raises(ValueError, match="retries must be >= 1"):
        with_retry(lambda: None, retries=0)


def test_sleep_called_between_attempts(mocker):
    sleep_mock = mocker.patch("src.retry_handler.time.sleep")
    n = {"i": 0}

    def two_failures():
        n["i"] += 1
        if n["i"] <= 2:
            raise OSError("retry me")
        return "done"

    with_retry(two_failures, retries=3, backoff=1.5, retryable=(OSError,))
    assert sleep_mock.call_count == 2
    sleep_mock.assert_called_with(1.5)
