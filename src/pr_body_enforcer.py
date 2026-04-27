"""Enforces that a PR body satisfies the required sections from a template."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


_SECTION_HEADER_RE = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)
_CHECKBOX_RE = re.compile(r"^\s*-\s*\[\s\]\s+", re.MULTILINE)


@dataclass
class EnforcementResult:
    missing_sections: List[str] = field(default_factory=list)
    unchecked_boxes: int = 0

    @property
    def passed(self) -> bool:
        return not self.missing_sections and self.unchecked_boxes == 0

    def __bool__(self) -> bool:
        return self.passed


def _extract_sections(text: str) -> List[str]:
    """Return a list of section heading titles found in *text*."""
    return [m.group(1).strip() for m in _SECTION_HEADER_RE.finditer(text)]


def _count_unchecked_boxes(text: str) -> int:
    """Return the number of unchecked markdown checkboxes in *text*."""
    return len(_CHECKBOX_RE.findall(text))


def enforce(template_body: str, pr_body: str) -> EnforcementResult:
    """Check that *pr_body* contains all sections present in *template_body*.

    Args:
        template_body: The rendered template string (source of truth).
        pr_body: The actual PR description submitted by the author.

    Returns:
        An :class:`EnforcementResult` describing any violations found.
    """
    result = EnforcementResult()

    required_sections = _extract_sections(template_body)
    present_sections = _extract_sections(pr_body)
    present_lower = {s.lower() for s in present_sections}

    for section in required_sections:
        if section.lower() not in present_lower:
            result.missing_sections.append(section)

    result.unchecked_boxes = _count_unchecked_boxes(pr_body)

    return result
