from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MergeResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mergeable_state: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_mergeability(
    mergeable: Optional[bool],
    mergeable_state: Optional[str],
    *,
    blocked_states: Optional[List[str]] = None,
    fail_on_unknown: bool = False,
) -> MergeResult:
    """Check whether a PR is in a mergeable state.

    Args:
        mergeable: GitHub's ``mergeable`` field (True/False/None).
        mergeable_state: GitHub's ``mergeable_state`` string
            (e.g. 'clean', 'blocked', 'dirty', 'unstable', 'unknown').
        blocked_states: Additional mergeable_state values that should cause
            a failure.  Defaults to ['dirty', 'blocked'].
        fail_on_unknown: If True, treat a None/unknown mergeable state as a
            failure rather than a warning.
    """
    if blocked_states is None:
        blocked_states = ["dirty", "blocked"]

    result = MergeResult(mergeable_state=mergeable_state)

    if mergeable is None:
        msg = "PR mergeability could not be determined (GitHub is still computing it)."
        if fail_on_unknown:
            result.fail(msg)
        else:
            result.warn(msg)
        return result

    if not mergeable:
        result.fail(
            f"PR is not mergeable (mergeable_state='{mergeable_state}'). "
            "Resolve conflicts or address review requirements before merging."
        )
        return result

    if mergeable_state in blocked_states:
        result.fail(
            f"PR mergeable_state is '{mergeable_state}', which is not allowed. "
            f"Blocked states: {blocked_states}."
        )
        return result

    if mergeable_state == "unstable":
        result.warn(
            "PR is mergeable but has an unstable status check. "
            "Ensure all CI checks pass before merging."
        )

    return result
