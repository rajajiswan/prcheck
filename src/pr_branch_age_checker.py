"""Check how long a branch has been open relative to its base branch."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class BranchAgeResult:
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    branch_name: str = ""
    age_days: Optional[float] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_branch_age(
    branch_name: str,
    created_at: str,
    max_age_days: Optional[int] = None,
    warn_age_days: Optional[int] = None,
    now: Optional[datetime] = None,
) -> BranchAgeResult:
    """Check whether a branch exceeds configured age thresholds.

    Args:
        branch_name: The name of the branch being checked.
        created_at: ISO-8601 timestamp of when the branch/PR was created.
        max_age_days: Hard limit; exceeding this fails the check.
        warn_age_days: Soft limit; exceeding this emits a warning.
        now: Override current time (for testing).

    Returns:
        BranchAgeResult with pass/fail state and messages.
    """
    result = BranchAgeResult(branch_name=branch_name)

    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        result.fail(f"Could not parse created_at timestamp: {exc}")
        return result

    reference = now or datetime.now(timezone.utc)
    age = (reference - created).total_seconds() / 86400
    result.age_days = round(age, 2)

    if max_age_days is not None and age > max_age_days:
        result.fail(
            f"Branch '{branch_name}' is {result.age_days} days old, "
            f"exceeding the maximum of {max_age_days} days."
        )
    elif warn_age_days is not None and age > warn_age_days:
        result.warn(
            f"Branch '{branch_name}' is {result.age_days} days old, "
            f"exceeding the warning threshold of {warn_age_days} days."
        )

    return result
