from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DraftResult:
    passed: bool = True
    error: Optional[str] = None
    warnings: list = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.error = message

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_draft(
    is_draft: bool,
    block_draft_merge: bool = True,
    warn_on_draft: bool = False,
) -> DraftResult:
    """Check whether the PR is in draft state and enforce policy.

    Args:
        is_draft: Whether the PR is currently a draft.
        block_draft_merge: If True, fail when the PR is a draft.
        warn_on_draft: If True, emit a warning instead of failing.

    Returns:
        DraftResult with pass/fail state and any messages.
    """
    result = DraftResult()

    if not is_draft:
        return result

    if warn_on_draft:
        result.warn(
            "This PR is still a draft. Mark it as ready for review before merging."
        )
        return result

    if block_draft_merge:
        result.fail(
            "Draft PRs cannot be merged. Mark the PR as ready for review first."
        )

    return result
