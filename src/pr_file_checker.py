from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from src.pr_diff_fetcher import PRDiff


@dataclass
class FileCheckResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    matched_patterns: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_files(
    diff: PRDiff,
    forbidden_patterns: Optional[List[str]] = None,
    required_patterns: Optional[List[str]] = None,
    max_files: Optional[int] = None,
) -> FileCheckResult:
    """Check PR changed files against forbidden/required patterns and size limits."""
    result = FileCheckResult()

    if not diff.ok:
        result.fail(f"Could not retrieve diff: {diff.error}")
        return result

    if max_files is not None and len(diff) > max_files:
        result.fail(
            f"PR changes {len(diff)} files, which exceeds the maximum of {max_files}."
        )

    forbidden = forbidden_patterns or []
    for pattern in forbidden:
        import fnmatch
        matched = [f for f in diff.files if fnmatch.fnmatch(f, pattern)]
        if matched:
            result.fail(
                f"PR modifies forbidden file(s) matching '{pattern}': {', '.join(matched)}"
            )
            result.matched_patterns.append(pattern)

    required = required_patterns or []
    for pattern in required:
        import fnmatch
        matched = [f for f in diff.files if fnmatch.fnmatch(f, pattern)]
        if matched:
            result.matched_patterns.append(pattern)
        else:
            result.warn(
                f"No files matching required pattern '{pattern}' were changed."
            )

    return result
