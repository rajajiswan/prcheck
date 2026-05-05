from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConflictResult:
    passed: bool = True
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.error = message

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_conflicts(
    mergeable: Optional[bool],
    mergeable_state: Optional[str],
    *,
    require_no_conflicts: bool = True,
) -> ConflictResult:
    """Check whether a pull request has merge conflicts.

    Args:
        mergeable: The ``mergeable`` field from the GitHub PR payload.
            ``None`` means GitHub has not yet computed mergeability.
        mergeable_state: The ``mergeable_state`` field (e.g. ``'clean'``,
            ``'dirty'``, ``'unknown'``, ``'blocked'``).
        require_no_conflicts: When *True* (default) a dirty/conflicting PR
            fails the check.  Set to *False* to only warn.

    Returns:
        A :class:`ConflictResult` describing the outcome.
    """
    result = ConflictResult()

    if mergeable is None or mergeable_state in (None, "unknown"):
        result.warn(
            "GitHub has not yet determined mergeability for this PR. "
            "Re-run the check once the merge status is resolved."
        )
        return result

    if mergeable is False or mergeable_state == "dirty":
        message = (
            "This PR has merge conflicts and cannot be merged cleanly. "
            "Please resolve conflicts before merging."
        )
        if require_no_conflicts:
            result.fail(message)
        else:
            result.warn(message)
        return result

    if mergeable_state == "blocked":
        result.warn(
            "Merging is currently blocked (e.g. required status checks "
            "are pending or failing)."
        )

    return result
