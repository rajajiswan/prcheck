"""Check that a PR has at least one label from an allowed set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass
class LabelCheckResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    applied_labels: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_labels(
    pr_labels: Sequence[str],
    allowed_labels: Optional[Sequence[str]] = None,
    required_labels: Optional[Sequence[str]] = None,
    min_labels: int = 0,
) -> LabelCheckResult:
    """Validate PR labels against allowed and required sets.

    Args:
        pr_labels: Labels currently applied to the PR.
        allowed_labels: If provided, every PR label must be in this list.
        required_labels: If provided, each of these labels must be present.
        min_labels: Minimum number of labels the PR must have (default 0).

    Returns:
        A :class:`LabelCheckResult` describing the outcome.
    """
    result = LabelCheckResult(applied_labels=list(pr_labels))

    if min_labels > 0 and len(pr_labels) < min_labels:
        result.fail(
            f"PR must have at least {min_labels} label(s); "
            f"found {len(pr_labels)}."
        )

    if allowed_labels is not None:
        allowed_set = set(allowed_labels)
        unknown = [lbl for lbl in pr_labels if lbl not in allowed_set]
        if unknown:
            result.fail(
                f"PR contains disallowed label(s): {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(allowed_set))}."
            )

    if required_labels:
        present = set(pr_labels)
        missing = [lbl for lbl in required_labels if lbl not in present]
        if missing:
            result.fail(
                f"PR is missing required label(s): {', '.join(missing)}."
            )

    if not pr_labels:
        result.warn("PR has no labels applied.")

    return result
