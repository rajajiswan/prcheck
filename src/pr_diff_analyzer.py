"""Analyze a PR diff to detect large or risky changes."""
from dataclasses import dataclass, field
from typing import List

from src.pr_diff_fetcher import PRDiff


@dataclass
class DiffAnalysisResult:
    passed: bool = True
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def analyze_pr_diff(
    diff: PRDiff,
    max_files: int = 50,
    max_lines: int = 1000,
    warn_files: int = 20,
    warn_lines: int = 500,
) -> DiffAnalysisResult:
    """Inspect a PRDiff and return a DiffAnalysisResult."""
    result = DiffAnalysisResult()

    if not diff.ok:
        result.fail(f"Diff could not be fetched: {diff.error}")
        return result

    file_count = len(diff)
    line_count = diff.additions + diff.deletions

    if file_count > max_files:
        result.fail(
            f"PR touches {file_count} files which exceeds the limit of {max_files}."
        )
    elif file_count > warn_files:
        result.warn(
            f"PR touches {file_count} files (warning threshold: {warn_files})."
        )

    if line_count > max_lines:
        result.fail(
            f"PR changes {line_count} lines which exceeds the limit of {max_lines}."
        )
    elif line_count > warn_lines:
        result.warn(
            f"PR changes {line_count} lines (warning threshold: {warn_lines})."
        )

    return result
