"""Enforces that a PR has the correct label based on its branch name."""
from dataclasses import dataclass, field
from typing import Optional

from src.branch_parser import BranchInfo


@dataclass
class LabelEnforcementResult:
    passed: bool = True
    errors: list = field(default_factory=list)
    expected_label: Optional[str] = None
    actual_labels: list = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def __bool__(self) -> bool:
        return self.passed


def enforce_branch_label(
    branch_info: BranchInfo,
    actual_labels: list[str],
    require_label: bool = True,
) -> LabelEnforcementResult:
    """Check that the PR carries the label derived from its branch name.

    Args:
        branch_info: Parsed branch information including the expected label.
        actual_labels: Labels currently applied to the PR.
        require_label: When False the check is skipped and always passes.

    Returns:
        A :class:`LabelEnforcementResult` describing the outcome.
    """
    result = LabelEnforcementResult(
        expected_label=branch_info.label,
        actual_labels=list(actual_labels),
    )

    if not require_label:
        return result

    if branch_info.label is None:
        result.fail(
            f"Branch '{branch_info.raw}' does not map to a known label. "
            "Ensure your branch follows the naming convention "
            "(e.g. feature/, bugfix/, hotfix/, chore/, docs/)."
        )
        return result

    if branch_info.label not in actual_labels:
        result.fail(
            f"Expected label '{branch_info.label}' is not applied to this PR. "
            f"Current labels: {actual_labels or ['(none)']}."
        )

    return result
