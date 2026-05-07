from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProtectedBranchResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    target_branch: Optional[str] = None
    is_protected: Optional[bool] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_protected_branch(
    target_branch: str,
    protected_branches: list[str],
    mergeable_state: Optional[str] = None,
    require_up_to_date: bool = False,
    blocked_states: Optional[list[str]] = None,
) -> ProtectedBranchResult:
    """Check whether the PR targets a protected branch and respects branch protection rules."""
    result = ProtectedBranchResult(target_branch=target_branch)

    if not protected_branches:
        result.warn("No protected branches configured; skipping protection check.")
        return result

    is_protected = target_branch in protected_branches
    result.is_protected = is_protected

    if not is_protected:
        result.warn(
            f"Target branch '{target_branch}' is not in the protected branches list."
        )
        return result

    _blocked = blocked_states or ["blocked", "dirty"]

    if mergeable_state is not None:
        if mergeable_state in _blocked:
            result.fail(
                f"PR cannot be merged: branch protection status is '{mergeable_state}'."
            )
        elif require_up_to_date and mergeable_state == "behind":
            result.fail(
                f"Branch '{target_branch}' requires the PR branch to be up to date before merging."
            )

    return result
