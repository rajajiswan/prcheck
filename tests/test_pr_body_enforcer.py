"""Tests for pr_body_enforcer module."""

from __future__ import annotations

import pytest

from src.pr_body_enforcer import (
    EnforcementResult,
    PRBodyEnforcer,
    _count_unchecked_boxes,
    _extract_sections,
)

PR_BODY_FULL = """
## Description

This PR adds a new feature.

## Testing

- [x] Unit tests added
- [x] Integration tests verified

## Checklist

- [x] Docs updated
"""

PR_BODY_MISSING_SECTION = """
## Description

Only a description here.
"""

PR_BODY_UNCHECKED = """
## Description

Some text.

## Checklist

- [ ] Item one
- [x] Item two
- [ ] Item three
"""


class TestEnforcementResult:
    def test_initial_state_is_passing(self) -> None:
        result = EnforcementResult()
        assert result.passed() is True
        assert bool(result) is True

    def test_missing_section_fails(self) -> None:
        result = EnforcementResult(missing_sections=["## Description"])
        assert result.passed() is False
        assert bool(result) is False

    def test_unchecked_boxes_fail(self) -> None:
        result = EnforcementResult(unchecked_boxes=2)
        assert result.passed() is False

    def test_both_failures(self) -> None:
        result = EnforcementResult(missing_sections=["## Foo"], unchecked_boxes=1)
        assert bool(result) is False


class TestExtractSections:
    def test_finds_all_headings(self) -> None:
        sections = _extract_sections(PR_BODY_FULL)
        headings = [s.strip() for s in sections]
        assert "## Description" in headings
        assert "## Testing" in headings
        assert "## Checklist" in headings

    def test_empty_body_returns_empty(self) -> None:
        assert _extract_sections("") == []

    def test_no_headings(self) -> None:
        assert _extract_sections("Just some plain text.") == []


class TestCountUncheckedBoxes:
    def test_counts_unchecked(self) -> None:
        assert _count_unchecked_boxes(PR_BODY_UNCHECKED) == 2

    def test_no_unchecked(self) -> None:
        assert _count_unchecked_boxes(PR_BODY_FULL) == 0

    def test_empty_body(self) -> None:
        assert _count_unchecked_boxes("") == 0


class TestPRBodyEnforcer:
    def test_passes_with_all_sections(self) -> None:
        enforcer = PRBodyEnforcer(required_sections=["## Description", "## Testing"])
        result = enforcer.enforce(PR_BODY_FULL)
        assert bool(result) is True
        assert result.missing_sections == []

    def test_fails_with_missing_section(self) -> None:
        enforcer = PRBodyEnforcer(required_sections=["## Description", "## Testing"])
        result = enforcer.enforce(PR_BODY_MISSING_SECTION)
        assert bool(result) is False
        assert "## Testing" in result.missing_sections

    def test_checklist_not_enforced_by_default(self) -> None:
        enforcer = PRBodyEnforcer(required_sections=[])
        result = enforcer.enforce(PR_BODY_UNCHECKED)
        assert result.unchecked_boxes == 0

    def test_checklist_enforced_when_enabled(self) -> None:
        enforcer = PRBodyEnforcer(required_sections=[], enforce_checklist=True)
        result = enforcer.enforce(PR_BODY_UNCHECKED)
        assert result.unchecked_boxes == 2
        assert bool(result) is False

    def test_no_required_sections_always_passes_sections(self) -> None:
        enforcer = PRBodyEnforcer(required_sections=[])
        result = enforcer.enforce("")
        assert result.missing_sections == []
