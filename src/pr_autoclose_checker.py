from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class AutocloseResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    days_inactive: Optional[int] = None
    would_close: bool = False

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_autoclose(
    updated_at: str,
    is_draft: bool,
    autoclose_days: int = 30,
    warn_days: int = 21,
    skip_drafts: bool = True,
    autoclose_enabled: bool = True,
) -> AutocloseResult:
    """Check whether a PR is inactive and should be auto-closed."""
    result = AutocloseResult()

    if not autoclose_enabled:
        return result

    if skip_drafts and is_draft:
        result.warn("PR is a draft; autoclose check skipped.")
        return result

    try:
        updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        result.fail(f"Invalid updated_at timestamp: {updated_at!r}")
        return result

    now = datetime.now(tz=timezone.utc)
    delta = now - updated
    days_inactive = delta.days
    result.days_inactive = days_inactive

    if days_inactive >= autoclose_days:
        result.would_close = True
        result.fail(
            f"PR has been inactive for {days_inactive} day(s) "
            f"(threshold: {autoclose_days}). Eligible for auto-close."
        )
    elif days_inactive >= warn_days:
        result.warn(
            f"PR has been inactive for {days_inactive} day(s). "
            f"Will be eligible for auto-close in "
            f"{autoclose_days - days_inactive} day(s)."
        )

    return result
