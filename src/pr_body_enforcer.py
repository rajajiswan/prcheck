"""Enforces required sections and checkbox completion in PR body text."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class EnforcementResult:
    """Holds the outcome of a PR body enforcement check."""

    missing_sections: List[str] = field(default_factory=list)
    unchecked_boxes: int = 0

    def passed(self) -> bool:
        return not self.missing_sections and self.unchecked_boxes == 0

    def __bool__(self) -> bool:
        return self.passed()


def _extract_sections(body: str) -> list[str]:
    """Return all markdown headings (## level) found in the body."""
    return re.findall(r"^#{1,6}\s+.+", body, re.MULTILINE)


def _count_unchecked_boxes(body: str) -> int:
    """Return the number of unchecked markdown task-list items."""
    return len(re.findall(r"^\s*-\s*\[\s\]", body, re.MULTILINE))


class PRBodyEnforcer:
    """Checks a PR body against a list of required sections and checkbox rules."""

    def __init__(self, required_sections: list[str], enforce_checklist: bool = False) -> None:
        self.required_sections = required_sections
        self.enforce_checklist = enforce_checklist

    def enforce(self, body: str) -> EnforcementResult:
        """Run all enforcement checks and return an EnforcementResult."""
        result = EnforcementResult()

        present = _extract_sections(body)
        present_lower = [s.strip().lower() for s in present]

        for required in self.required_sections:
            if required.strip().lower() not in present_lower:
                result.missing_sections.append(required)

        if self.enforce_checklist:
            result.unchecked_boxes = _count_unchecked_boxes(body)

        return result
