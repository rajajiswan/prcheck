from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class StaleResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    days_since_update: Optional[int] = None
    is_stale: bool = False

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_stale(
    updated_at: str,
    stale_days: int = 30,
    warn_days: int = 14,
    require_fresh: bool = False,
) -> StaleResult:
    """Check whether a PR has gone stale based on its last-updated timestamp.

    Args:
        updated_at: ISO-8601 timestamp string from the GitHub API.
        stale_days: Number of days without activity before a PR is stale.
        warn_days: Number of days without activity before a warning is issued.
        require_fresh: If True, a stale PR causes a hard failure instead of a warning.
    """
    result = StaleResult()

    try:
        updated_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        result.fail(f"Could not parse updated_at timestamp: {exc}")
        return result

    now = datetime.now(tz=timezone.utc)
    delta = now - updated_dt
    days = delta.days
    result.days_since_update = days

    if days >= stale_days:
        result.is_stale = True
        message = (
            f"PR has not been updated in {days} day(s) "
            f"(stale threshold: {stale_days} day(s))."
        )
        if require_fresh:
            result.fail(message)
        else:
            result.warn(message)
    elif days >= warn_days:
        result.warn(
            f"PR has not been updated in {days} day(s). "
            f"It will be considered stale after {stale_days} day(s)."
        )

    return result
