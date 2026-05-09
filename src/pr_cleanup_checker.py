from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CleanupResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    branch_name: Optional[str] = None
    is_merged: bool = False
    is_closed: bool = False

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_cleanup(
    branch_name: str,
    state: str,
    is_merged: bool,
    protected_branches: Optional[List[str]] = None,
    warn_on_stale_closed: bool = True,
    days_closed_threshold: int = 7,
    closed_at: Optional[str] = None,
) -> CleanupResult:
    """Check whether a PR's source branch is a candidate for cleanup."""
    from datetime import datetime, timezone

    protected = set(protected_branches or ["main", "master", "develop", "staging"])
    result = CleanupResult(
        branch_name=branch_name,
        is_merged=is_merged,
        is_closed=(state == "closed"),
    )

    if branch_name in protected:
        result.fail(
            f"Branch '{branch_name}' is a protected branch and should never be deleted."
        )
        return result

    if state == "open":
        result.warn(
            f"PR is still open; branch '{branch_name}' should not be cleaned up yet."
        )
        return result

    if is_merged:
        result.warn(
            f"Branch '{branch_name}' was merged and is safe to delete."
        )
        return result

    # Closed but not merged
    if warn_on_stale_closed and closed_at:
        try:
            closed_dt = datetime.fromisoformat(closed_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_old = (now - closed_dt).days
            if days_old >= days_closed_threshold:
                result.warn(
                    f"Branch '{branch_name}' has been closed (unmerged) for "
                    f"{days_old} day(s) and may be safe to delete."
                )
        except ValueError:
            pass

    return result
