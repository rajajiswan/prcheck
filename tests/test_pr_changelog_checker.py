"""Tests for pr_changelog_checker and changelog_reporter."""
from __future__ import annotations

import pytest

from src.pr_changelog_checker import ChangelogResult, check_pr_changelog
from src.pr_diff_fetcher import PRDiff
from src.changelog_reporter import _build_changelog_summary


# ---------------------------------------------------------------------------
# ChangelogResult unit tests
# ---------------------------------------------------------------------------

class TestChangelogResult:
    def test_initial_state_is_passing(self):
        r = ChangelogResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.changelog_file is None

    def test_fail_sets_passed_false(self):
        r = ChangelogResult()
        r.fail("missing")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ChangelogResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ChangelogResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(ChangelogResult()) is True

    def test_bool_false_when_failed(self):
        r = ChangelogResult()
        r.fail("x")
        assert bool(r) is False


# ---------------------------------------------------------------------------
# check_pr_changelog
# ---------------------------------------------------------------------------

def _make_diff(files: list[str], error: str = "") -> PRDiff:
    return PRDiff(files=files, error=error)


def test_changelog_found_passes():
    diff = _make_diff(["src/foo.py", "CHANGELOG.md"])
    result = check_pr_changelog(diff)
    assert result.passed is True
    assert result.changelog_file == "CHANGELOG.md"


def test_no_changelog_fails_by_default():
    diff = _make_diff(["src/foo.py", "src/bar.py"])
    result = check_pr_changelog(diff)
    assert result.passed is False
    assert result.errors


def test_no_changelog_warns_when_warn_only():
    diff = _make_diff(["src/foo.py"])
    result = check_pr_changelog(diff, warn_only=True)
    assert result.passed is True
    assert result.warnings


def test_require_false_always_passes():
    diff = _make_diff([])
    result = check_pr_changelog(diff, require_changelog=False)
    assert result.passed is True


def test_diff_error_fails():
    diff = _make_diff([], error="network timeout")
    result = check_pr_changelog(diff)
    assert result.passed is False
    assert "network timeout" in result.errors[0]


def test_custom_patterns_matched():
    diff = _make_diff(["docs/HISTORY.md"])
    result = check_pr_changelog(diff, changelog_patterns=["HISTORY.md"])
    assert result.passed is True


def test_custom_patterns_not_matched():
    diff = _make_diff(["CHANGELOG.md"])
    result = check_pr_changelog(diff, changelog_patterns=["RELEASES.md"])
    assert result.passed is False


# ---------------------------------------------------------------------------
# _build_changelog_summary
# ---------------------------------------------------------------------------

def test_summary_passing_header():
    r = ChangelogResult(changelog_file="CHANGELOG.md")
    summary = _build_changelog_summary(r)
    assert "✅" in summary
    assert "CHANGELOG.md" in summary


def test_summary_failing_header():
    r = ChangelogResult()
    r.fail("No changelog found")
    summary = _build_changelog_summary(r)
    assert "❌" in summary
    assert "No changelog found" in summary


def test_summary_warning_included():
    r = ChangelogResult()
    r.warn("Consider adding a changelog")
    summary = _build_changelog_summary(r)
    assert "⚠️" in summary
    assert "Consider adding a changelog" in summary
