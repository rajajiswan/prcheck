from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# Patterns that indicate a linked issue in a PR body
_CLOSING_KEYWORDS = r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)"
_ISSUE_PATTERN = re.compile(
    rf"(?i){_CLOSING_KEYWORDS}\s+(?:#(\d+)|https?://github\.com/[\w.-]+/[\w.-]+/issues/(\d+))"
)


@dataclass
class LinkedIssueResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    issue_numbers: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_linked_issue(
    pr_body: Optional[str],
    require_linked_issue: bool = False,
    allowed_issue_prefixes: Optional[list[str]] = None,
) -> LinkedIssueResult:
    """Check whether a PR body contains a linked issue reference."""
    result = LinkedIssueResult()

    if not pr_body:
        if require_linked_issue:
            result.fail("PR body is empty; a linked issue is required.")
        else:
            result.warn("PR body is empty; no linked issue found.")
        return result

    matches = _ISSUE_PATTERN.findall(pr_body)
    issue_numbers = [m[0] or m[1] for m in matches if m[0] or m[1]]

    if not issue_numbers:
        if require_linked_issue:
            result.fail(
                "No linked issue found. Use a closing keyword such as "
                "'Closes #123' or 'Fixes #456'."
            )
        else:
            result.warn("No linked issue detected in PR body.")
        return result

    result.issue_numbers = issue_numbers

    if allowed_issue_prefixes:
        for num in issue_numbers:
            if not any(num.startswith(p) for p in allowed_issue_prefixes):
                result.fail(
                    f"Issue #{num} does not match any allowed prefix: "
                    f"{allowed_issue_prefixes}."
                )

    return result
