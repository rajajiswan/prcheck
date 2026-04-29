"""Retry handler for transient GitHub API failures."""
from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")

DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 2.0  # seconds


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"Operation failed after {attempts} attempt(s): {last_error}"
        )


def with_retry(
    func: Callable[[], T],
    *,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    retryable: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Call *func* up to *retries* times, sleeping *backoff* seconds between
    attempts.  Only exceptions that are instances of *retryable* trigger a
    retry; all others propagate immediately.

    Args:
        func: Zero-argument callable to execute.
        retries: Maximum number of attempts (must be >= 1).
        backoff: Seconds to wait between attempts.
        retryable: Tuple of exception types that should trigger a retry.

    Returns:
        The return value of *func* on success.

    Raises:
        RetryExhausted: When all attempts are exhausted.
        Exception: Any non-retryable exception raised by *func*.
    """
    if retries < 1:
        raise ValueError(f"retries must be >= 1, got {retries}")

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except retryable as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(backoff)
        except Exception:
            raise

    raise RetryExhausted(retries, last_error)  # type: ignore[arg-type]
