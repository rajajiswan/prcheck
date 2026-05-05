"""Check that a PR has at least one requested reviewer assigned."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ReviewerResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_reviewers(
    requested_reviewers: List[str],
    *,
    require_reviewer: bool = True,
    min_reviewers: int = 1,
    allowed_reviewers: List[str] | None = None,
) -> ReviewerResult:
    """Validate that the PR has the required number of requested reviewers.

    Args:
        requested_reviewers: List of GitHub login strings from the PR payload.
        require_reviewer: When False the check is advisory only (warning).
        min_reviewers: Minimum number of reviewers required.
        allowed_reviewers: Optional whitelist; if provided every reviewer must
            be in the list.

    Returns:
        A :class:`ReviewerResult` describing the outcome.
    """
    result = ReviewerResult(reviewers=list(requested_reviewers))

    if len(requested_reviewers) < min_reviewers:
        msg = (
            f"PR requires at least {min_reviewers} reviewer(s), "
            f"but {len(requested_reviewers)} assigned."
        )
        if require_reviewer:
            result.fail(msg)
        else:
            result.warn(msg)

    if allowed_reviewers is not None:
        disallowed = [
            r for r in requested_reviewers if r not in allowed_reviewers
        ]
        if disallowed:
            result.fail(
                f"Reviewer(s) not in allowed list: {', '.join(disallowed)}"
            )

    return result
