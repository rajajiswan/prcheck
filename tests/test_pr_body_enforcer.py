"""Tests for src/pr_body_enforcer.py."""

import pytest

from src.pr_body_enforcer import (
    EnforcementResult,
    _count_unchecked_boxes,
    _extract_sections,
    enforce,
)


TEMPLATE = """\
## Description

Describe your changes here.

## Motivation

Why is this change needed?

## Checklist
- [ ] Tests added
- [ ] Docs updated
"""

GOOD_PR_BODY = """\
## Description

Added new feature X.

## Motivation

Improves performance.

## Checklist
- [x] Tests added
- [x] Docs updated
"""

MISSING_SECTION_BODY = """\
## Description

Added new feature X.

## Checklist
- [x] Tests added
"""

UNCHECKED_BODY = """\
## Description

Some text.

## Motivation

Some reason.

## Checklist
- [ ] Tests added
- [x] Docs updated
"""


class TestEnforcementResult:
    def test_initial_state_is_passing(self):
        r = EnforcementResult()
        assert r.passed is True
        assert bool(r) is True

    def test_missing_section_fails(self):
        r = EnforcementResult(missing_sections=["Motivation"])
        assert r.passed is False

    def test_unchecked_boxes_fail(self):
        r = EnforcementResult(unchecked_boxes=1)
        assert r.passed is False


class TestExtractSections:
    def test_finds_all_headings(self):
        sections = _extract_sections(TEMPLATE)
        assert sections == ["Description", "Motivation", "Checklist"]

    def test_empty_string_returns_empty(self):
        assert _extract_sections("") == []


class TestCountUncheckedBoxes:
    def test_counts_correctly(self):
        assert _count_unchecked_boxes(UNCHECKED_BODY) == 1

    def test_no_boxes(self):
        assert _count_unchecked_boxes(GOOD_PR_BODY) == 0


class TestEnforce:
    def test_valid_pr_passes(self):
        result = enforce(TEMPLATE, GOOD_PR_BODY)
        assert result.passed is True
        assert result.missing_sections == []
        assert result.unchecked_boxes == 0

    def test_missing_section_detected(self):
        result = enforce(TEMPLATE, MISSING_SECTION_BODY)
        assert result.passed is False
        assert "Motivation" in result.missing_sections

    def test_unchecked_boxes_detected(self):
        result = enforce(TEMPLATE, UNCHECKED_BODY)
        assert result.passed is False
        assert result.unchecked_boxes == 1

    def test_section_match_is_case_insensitive(self):
        body = GOOD_PR_BODY.replace("## Description", "## description")
        result = enforce(TEMPLATE, body)
        assert "Description" not in result.missing_sections
