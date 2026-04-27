"""Tests for src/pr_description_enforcer.py."""

import pytest
from src.pr_description_enforcer import DescriptionResult, enforce_pr_description


# ---------------------------------------------------------------------------
# DescriptionResult unit tests
# ---------------------------------------------------------------------------

class TestDescriptionResult:
    def test_initial_state_is_passing(self):
        result = DescriptionResult()
        assert result.passed is True
        assert result.errors == []
        assert bool(result) is True

    def test_fail_sets_passed_false(self):
        result = DescriptionResult()
        result.fail("something went wrong")
        assert result.passed is False
        assert bool(result) is False

    def test_fail_appends_error_message(self):
        result = DescriptionResult()
        result.fail("error one")
        result.fail("error two")
        assert len(result.errors) == 2
        assert "error one" in result.errors
        assert "error two" in result.errors


# ---------------------------------------------------------------------------
# enforce_pr_description tests
# ---------------------------------------------------------------------------

class TestEnforcePrDescription:
    def test_valid_description_passes(self):
        body = "This PR fixes a critical bug in the authentication flow."
        result = enforce_pr_description(body)
        assert result.passed is True
        assert result.errors == []

    def test_empty_body_fails(self):
        result = enforce_pr_description("")
        assert result.passed is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_whitespace_only_body_fails(self):
        result = enforce_pr_description("   \n\t  ")
        assert result.passed is False

    def test_body_below_min_length_fails(self):
        result = enforce_pr_description("Too short.", min_length=50)
        assert result.passed is False
        assert any("too short" in e.lower() for e in result.errors)

    def test_body_exactly_at_min_length_passes(self):
        # 20 non-whitespace chars
        body = "a" * 20
        result = enforce_pr_description(body, min_length=20)
        assert result.passed is True

    def test_forbidden_placeholder_detected(self):
        body = "This PR does stuff. <!-- Add description here --> more text to pass length."
        result = enforce_pr_description(
            body, forbidden_placeholders=["<!-- Add description here -->"]
        )
        assert result.passed is False
        assert any("placeholder" in e.lower() for e in result.errors)

    def test_multiple_forbidden_placeholders(self):
        body = "TODO: describe changes. FIXME: add more detail. " + "x" * 30
        result = enforce_pr_description(
            body, forbidden_placeholders=["TODO: describe changes", "FIXME: add more detail"]
        )
        assert result.passed is False
        assert len(result.errors) == 2

    def test_no_forbidden_placeholders_by_default(self):
        body = "TODO: describe changes. " + "x" * 30
        result = enforce_pr_description(body)
        assert result.passed is True
