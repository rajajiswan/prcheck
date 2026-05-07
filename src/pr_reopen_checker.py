from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReopenResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reopen_count: int = 0
    last_closed_at: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_reopen(
    reopen_count: int,
    last_closed_at: Optional[str],
    max_reopens: int = 2,
    warn_on_reopen: bool = True,
    fail_on_exceed: bool = True,
) -> ReopenResult:
    """Check whether a PR has been reopened too many times.

    Args:
        reopen_count: Number of times the PR has been reopened.
        last_closed_at: ISO timestamp of when the PR was last closed, or None.
        max_reopens: Maximum number of allowed reopens before failing.
        warn_on_reopen: Emit a warning whenever the PR has been reopened at all.
        fail_on_exceed: Fail when reopen_count exceeds max_reopens.

    Returns:
        ReopenResult with pass/fail state and any messages.
    """
    result = ReopenResult(reopen_count=reopen_count, last_closed_at=last_closed_at)

    if reopen_count > 0 and warn_on_reopen:
        result.warn(
            f"PR has been reopened {reopen_count} time(s). "
            "Consider addressing the root cause before merging."
        )

    if fail_on_exceed and reopen_count > max_reopens:
        result.fail(
            f"PR has been reopened {reopen_count} time(s), "
            f"exceeding the maximum of {max_reopens}."
        )

    return result
