from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AssigneeResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_assignees(
    assignees: List[str],
    require_assignee: bool = True,
    allowed_assignees: Optional[List[str]] = None,
    max_assignees: Optional[int] = None,
) -> AssigneeResult:
    """Check that a PR has valid assignees based on config rules."""
    result = AssigneeResult(assignees=list(assignees))

    if require_assignee and not assignees:
        result.fail("PR must have at least one assignee.")
        return result

    if allowed_assignees is not None:
        for assignee in assignees:
            if assignee not in allowed_assignees:
                result.fail(
                    f"Assignee '{assignee}' is not in the allowed assignees list."
                )

    if max_assignees is not None and len(assignees) > max_assignees:
        result.fail(
            f"PR has {len(assignees)} assignees but the maximum allowed is {max_assignees}."
        )

    if not assignees and not require_assignee:
        result.warn("PR has no assignees. Consider assigning someone.")

    return result
