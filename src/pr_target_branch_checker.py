from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TargetBranchResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    target_branch: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_target_branch(
    target_branch: str,
    allowed_targets: Optional[List[str]] = None,
    disallowed_targets: Optional[List[str]] = None,
    required_for_types: Optional[dict] = None,
    branch_type: Optional[str] = None,
) -> TargetBranchResult:
    """
    Check whether a PR targets an allowed base branch.

    Args:
        target_branch: The base branch the PR is targeting.
        allowed_targets: If set, only these branches are permitted.
        disallowed_targets: If set, these branches are explicitly forbidden.
        required_for_types: Mapping of branch type -> required target branch.
        branch_type: The type of the source branch (e.g. 'hotfix', 'feature').
    """
    result = TargetBranchResult(target_branch=target_branch)

    if not target_branch:
        result.fail("Target branch is empty or could not be determined.")
        return result

    if disallowed_targets and target_branch in disallowed_targets:
        result.fail(
            f"PRs must not target '{target_branch}'. "
            f"Disallowed targets: {', '.join(disallowed_targets)}."
        )

    if allowed_targets and target_branch not in allowed_targets:
        result.fail(
            f"'{target_branch}' is not an allowed target branch. "
            f"Allowed: {', '.join(allowed_targets)}."
        )

    if required_for_types and branch_type:
        required = required_for_types.get(branch_type)
        if required and target_branch != required:
            result.fail(
                f"Branch type '{branch_type}' must target '{required}', "
                f"but targets '{target_branch}'."
            )

    return result
