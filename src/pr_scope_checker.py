"""Check that a PR does not touch files outside its declared scope."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import List, Optional

from src.pr_diff_fetcher import PRDiff


@dataclass
class ScopeResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    out_of_scope_files: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_scope(
    diff: PRDiff,
    allowed_patterns: Optional[List[str]] = None,
    forbidden_patterns: Optional[List[str]] = None,
    warn_only: bool = False,
) -> ScopeResult:
    """Validate that changed files stay within allowed scope.

    Args:
        diff: The PR diff containing changed file paths.
        allowed_patterns: Glob patterns that files MUST match (if provided).
        forbidden_patterns: Glob patterns that files MUST NOT match.
        warn_only: If True, violations produce warnings instead of errors.

    Returns:
        ScopeResult with pass/fail status and details.
    """
    result = ScopeResult()

    if not diff.ok:
        result.fail(f"Could not fetch diff: {diff.error}")
        return result

    if not diff.files:
        result.warn("No files changed in this PR.")
        return result

    for path in diff.files:
        # Check forbidden patterns first
        if forbidden_patterns:
            for pattern in forbidden_patterns:
                if fnmatch(path, pattern):
                    result.out_of_scope_files.append(path)
                    msg = f"File '{path}' matches forbidden scope pattern '{pattern}'."
                    if warn_only:
                        result.warn(msg)
                    else:
                        result.fail(msg)
                    break
            else:
                # Only check allowed patterns if not already flagged
                _check_allowed(path, allowed_patterns, result, warn_only)
        else:
            _check_allowed(path, allowed_patterns, result, warn_only)

    return result


def _check_allowed(
    path: str,
    allowed_patterns: Optional[List[str]],
    result: ScopeResult,
    warn_only: bool,
) -> None:
    if not allowed_patterns:
        return
    if not any(fnmatch(path, p) for p in allowed_patterns):
        result.out_of_scope_files.append(path)
        msg = f"File '{path}' is outside the allowed scope patterns."
        if warn_only:
            result.warn(msg)
        else:
            result.fail(msg)
