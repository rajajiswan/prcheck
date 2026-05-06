from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BaseBranchResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    base_branch: Optional[str] = None
    expected_branches: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_base_branch(
    base_branch: str,
    allowed_bases: List[str],
    *,
    warn_only: bool = False,
    protected_bases: Optional[List[str]] = None,
    source_branch: Optional[str] = None,
) -> BaseBranchResult:
    """Check that a PR targets an allowed base branch.

    Args:
        base_branch: The branch the PR is targeting.
        allowed_bases: List of permitted base branch names or glob-style
            prefixes ending with ``*``.
        warn_only: If True, emit a warning instead of a hard failure.
        protected_bases: Branches that require the source branch to follow
            a strict naming convention (e.g. ``hotfix/*``).
        source_branch: The head/source branch name, used for protected
            base validation.
    """
    result = BaseBranchResult(
        base_branch=base_branch,
        expected_branches=allowed_bases,
    )

    def _matches(branch: str, pattern: str) -> bool:
        if pattern.endswith("*"):
            return branch.startswith(pattern[:-1])
        return branch == pattern

    is_allowed = any(_matches(base_branch, p) for p in allowed_bases)

    if not is_allowed:
        msg = (
            f"PR targets '{base_branch}' which is not in the allowed base "
            f"branches: {allowed_bases}."
        )
        if warn_only:
            result.warn(msg)
        else:
            result.fail(msg)
        return result

    if protected_bases and source_branch:
        for protected in protected_bases:
            if _matches(base_branch, protected):
                if not any(
                    _matches(source_branch, p) for p in (protected_bases or [])
                ):
                    result.warn(
                        f"Base branch '{base_branch}' is protected. Ensure "
                        f"'{source_branch}' follows the required naming convention."
                    )

    return result
