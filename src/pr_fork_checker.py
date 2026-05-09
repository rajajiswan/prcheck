from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ForkResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    is_fork: bool = False
    fork_owner: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_fork(
    head_repo_full_name: Optional[str],
    base_repo_full_name: Optional[str],
    author: Optional[str] = None,
    *,
    allow_forks: bool = True,
    require_signed_commits: bool = False,
    blocked_fork_owners: Optional[list[str]] = None,
    warn_on_fork: bool = False,
) -> ForkResult:
    """Check whether the PR originates from a fork and enforce fork policy."""
    result = ForkResult()

    if not head_repo_full_name or not base_repo_full_name:
        result.fail("Could not determine repository information for fork check.")
        return result

    is_fork = head_repo_full_name != base_repo_full_name
    result.is_fork = is_fork

    if is_fork:
        fork_owner = head_repo_full_name.split("/")[0]
        result.fork_owner = fork_owner

        if not allow_forks:
            result.fail(
                f"PRs from forks are not allowed. "
                f"Fork origin: '{head_repo_full_name}'."
            )
            return result

        blocked = blocked_fork_owners or []
        if fork_owner in blocked:
            result.fail(
                f"PRs from fork owner '{fork_owner}' are blocked by policy."
            )
            return result

        if require_signed_commits:
            result.warn(
                "This PR originates from a fork. "
                "Ensure all commits are signed before merging."
            )

        if warn_on_fork:
            result.warn(
                f"This PR originates from a fork ('{head_repo_full_name}'). "
                "Please review carefully."
            )

    return result
