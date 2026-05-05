"""Checks that a PR title conforms to configured conventions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import re

from src.branch_parser import BranchInfo


@dataclass
class TitleResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    title: str = ""

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_title(
    title: str,
    branch: BranchInfo,
    *,
    min_length: int = 10,
    max_length: int = 72,
    require_prefix: bool = False,
    allowed_prefixes: Optional[List[str]] = None,
    forbidden_patterns: Optional[List[str]] = None,
) -> TitleResult:
    """Validate *title* against the supplied constraints.

    Args:
        title: The PR title string.
        branch: Parsed branch information (used for contextual checks).
        min_length: Minimum acceptable title length (default 10).
        max_length: Maximum acceptable title length (default 72).
        require_prefix: When True, the title must start with one of
            *allowed_prefixes*.
        allowed_prefixes: List of acceptable title prefixes (e.g.
            ``["feat:", "fix:", "chore:"]``).
        forbidden_patterns: List of regex patterns that must NOT appear
            in the title.

    Returns:
        A :class:`TitleResult` describing the outcome.
    """
    result = TitleResult(title=title)

    stripped = title.strip()

    if not stripped:
        result.fail("PR title must not be empty.")
        return result

    if len(stripped) < min_length:
        result.fail(
            f"PR title is too short ({len(stripped)} chars); "
            f"minimum is {min_length}."
        )

    if len(stripped) > max_length:
        result.fail(
            f"PR title is too long ({len(stripped)} chars); "
            f"maximum is {max_length}."
        )

    if require_prefix and allowed_prefixes:
        if not any(stripped.startswith(p) for p in allowed_prefixes):
            joined = ", ".join(f'"{p}"' for p in allowed_prefixes)
            result.fail(
                f"PR title must begin with one of: {joined}."
            )

    for pattern in forbidden_patterns or []:
        if re.search(pattern, stripped, re.IGNORECASE):
            result.fail(
                f"PR title contains forbidden pattern: {pattern!r}."
            )

    if stripped.endswith("."):
        result.warn("PR title ends with a period; consider removing it.")

    if stripped == stripped.upper() and len(stripped) > 3:
        result.warn("PR title appears to be ALL CAPS.")

    return result
