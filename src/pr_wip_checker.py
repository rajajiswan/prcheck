"""Check whether a PR is marked as Work In Progress (WIP)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

_WIP_TITLE_PREFIXES = ("wip:", "wip ", "[wip]", "[wip ]", "draft:", "[draft]")
_WIP_LABEL_NAMES = ("wip", "work in progress", "do not merge", "dnm")


@dataclass
class WIPResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    is_wip: bool = False

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_wip(
    title: str,
    labels: List[str],
    *,
    block_merge: bool = True,
    warn_only: bool = False,
) -> WIPResult:
    """Detect WIP indicators in the PR title or labels.

    Args:
        title: The PR title string.
        labels: List of label names currently applied to the PR.
        block_merge: When True and warn_only is False, a WIP PR fails the check.
        warn_only: When True, WIP state produces a warning instead of an error.

    Returns:
        A :class:`WIPResult` describing the outcome.
    """
    result = WIPResult()

    title_lower = title.strip().lower()
    label_lower = [lbl.strip().lower() for lbl in labels]

    wip_via_title = any(title_lower.startswith(prefix) for prefix in _WIP_TITLE_PREFIXES)
    wip_via_label = any(lbl in _WIP_LABEL_NAMES for lbl in label_lower)

    if wip_via_title or wip_via_label:
        result.is_wip = True
        source = "title" if wip_via_title else "label"
        message = f"PR is marked as WIP via {source} — not ready for merge."
        if warn_only or not block_merge:
            result.warn(message)
        else:
            result.fail(message)

    return result
