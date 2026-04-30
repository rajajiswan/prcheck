from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MilestoneResult:
    passed: bool = True
    milestone: Optional[str] = None
    error: Optional[str] = None
    warnings: list = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.error = message

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_milestone(
    milestone: Optional[str],
    require_milestone: bool,
    allowed_milestones: Optional[list] = None,
) -> MilestoneResult:
    """Check that a PR has a valid milestone set."""
    result = MilestoneResult(milestone=milestone)

    if not require_milestone:
        if milestone is None:
            result.warn("No milestone set (not required by config).")
        return result

    if milestone is None:
        result.fail("PR must have a milestone set.")
        return result

    if allowed_milestones and milestone not in allowed_milestones:
        result.fail(
            f"Milestone '{milestone}' is not in the allowed list: "
            f"{', '.join(allowed_milestones)}."
        )
        return result

    return result
