"""Checks whether a PR includes a changelog entry when required."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.pr_diff_fetcher import PRDiff


@dataclass
class ChangelogResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    changelog_file: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_changelog(
    diff: PRDiff,
    *,
    require_changelog: bool = True,
    changelog_patterns: Optional[list[str]] = None,
    warn_only: bool = False,
) -> ChangelogResult:
    """Check that the PR diff includes a changelog entry.

    Args:
        diff: The fetched PR diff.
        require_changelog: Whether a changelog entry is required.
        changelog_patterns: List of filename patterns that count as changelog
            files (e.g. ``["CHANGELOG.md", "CHANGES.rst"]``).  Defaults to
            common names when *None*.
        warn_only: Emit a warning instead of a failure when the entry is absent.
    """
    result = ChangelogResult()

    if not require_changelog:
        return result

    if diff.error:
        result.fail(f"Cannot check changelog: diff fetch error — {diff.error}")
        return result

    patterns = changelog_patterns or [
        "CHANGELOG.md",
        "CHANGELOG.rst",
        "CHANGELOG.txt",
        "CHANGES.md",
        "CHANGES.rst",
        "HISTORY.md",
    ]

    matched: Optional[str] = None
    for filename in diff.files:
        for pattern in patterns:
            if filename.lower().endswith(pattern.lower()):
                matched = filename
                break
        if matched:
            break

    if matched:
        result.changelog_file = matched
    else:
        message = (
            "No changelog entry found. Expected one of: "
            + ", ".join(patterns)
        )
        if warn_only:
            result.warn(message)
        else:
            result.fail(message)

    return result
