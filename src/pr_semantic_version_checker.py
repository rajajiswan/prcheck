"""Checks whether a PR includes a semantic version bump when required."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

_SEMVER_RE = re.compile(
    r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-[\w.]+)?"
)


@dataclass
class SemverResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    detected_version: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_semantic_version(
    pr_body: str,
    pr_title: str,
    *,
    require_version_bump: bool = False,
    allowed_bump_types: Optional[List[str]] = None,
    version_file_contents: Optional[str] = None,
) -> SemverResult:
    """Validate that the PR references a valid semantic version bump."""
    result = SemverResult()

    combined = f"{pr_title}\n{pr_body}"
    matches = _SEMVER_RE.findall(combined)

    if not matches:
        if require_version_bump:
            result.fail(
                "No semantic version found in PR title or body. "
                "A version bump (e.g. 1.2.3) is required."
            )
        else:
            result.warn("No semantic version detected in PR title or body.")
        return result

    raw = _SEMVER_RE.search(combined)
    if raw:
        result.detected_version = raw.group(0)

    if allowed_bump_types and version_file_contents:
        current = _SEMVER_RE.search(version_file_contents)
        new_match = raw
        if current and new_match:
            bump = _classify_bump(
                tuple(int(x) for x in current.group(1, 2, 3)),
                tuple(int(x) for x in new_match.group(1, 2, 3)),
            )
            if bump and bump not in allowed_bump_types:
                result.fail(
                    f"Version bump type '{bump}' is not in allowed types: "
                    f"{allowed_bump_types}."
                )

    return result


def _classify_bump(
    old: tuple, new: tuple
) -> Optional[str]:
    if new[0] > old[0]:
        return "major"
    if new[1] > old[1]:
        return "minor"
    if new[2] > old[2]:
        return "patch"
    return None
