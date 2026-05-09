from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SquashResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    commit_count: int = 0
    squash_recommended: bool = False

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_squash(
    commits: List[dict],
    *,
    max_commits_before_squash: int = 10,
    require_squash_for_labels: List[str] = None,
    pr_labels: List[str] = None,
    warn_only: bool = False,
) -> SquashResult:
    """Check whether a PR should be squashed before merging.

    Args:
        commits: List of commit dicts with at least a ``sha`` key.
        max_commits_before_squash: Threshold above which squash is recommended.
        require_squash_for_labels: Labels that mandate squashing.
        pr_labels: Labels currently applied to the PR.
        warn_only: If True, emit a warning instead of a hard failure.

    Returns:
        SquashResult with pass/fail state and any messages.
    """
    result = SquashResult(commit_count=len(commits))
    require_squash_for_labels = require_squash_for_labels or []
    pr_labels = pr_labels or []

    label_requires_squash = any(
        lbl in pr_labels for lbl in require_squash_for_labels
    )

    over_threshold = len(commits) > max_commits_before_squash

    if over_threshold or label_requires_squash:
        result.squash_recommended = True
        reason_parts: List[str] = []
        if over_threshold:
            reason_parts.append(
                f"{len(commits)} commits exceed the squash threshold of "
                f"{max_commits_before_squash}"
            )
        if label_requires_squash:
            matching = [l for l in require_squash_for_labels if l in pr_labels]
            reason_parts.append(
                f"label(s) {matching} require squashing before merge"
            )
        message = "Squash recommended: " + "; ".join(reason_parts) + "."
        if warn_only:
            result.warn(message)
        else:
            result.fail(message)

    return result
