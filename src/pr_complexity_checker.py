from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.pr_diff_fetcher import PRDiff


@dataclass
class ComplexityResult:
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    score: int = 0
    label: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_complexity(
    diff: PRDiff,
    max_score: int = 100,
    file_weight: int = 2,
    addition_weight: int = 1,
    deletion_weight: int = 1,
    warn_threshold: int = 60,
) -> ComplexityResult:
    """Compute a simple complexity score from diff statistics.

    score = (files * file_weight) + (additions * addition_weight)
            + (deletions * deletion_weight)

    Fails when score > max_score; warns when score > warn_threshold.
    """
    result = ComplexityResult()

    if not diff.ok:
        result.fail(f"Cannot compute complexity: diff fetch error — {diff.error}")
        return result

    score = (
        len(diff) * file_weight
        + diff.additions * addition_weight
        + diff.deletions * deletion_weight
    )
    result.score = score

    if score > max_score:
        result.label = "complexity: high"
        result.fail(
            f"PR complexity score {score} exceeds maximum allowed {max_score}. "
            "Consider splitting this PR into smaller pieces."
        )
    elif score > warn_threshold:
        result.label = "complexity: medium"
        result.warn(
            f"PR complexity score {score} is above the warning threshold {warn_threshold}."
        )
    else:
        result.label = "complexity: low"

    return result
