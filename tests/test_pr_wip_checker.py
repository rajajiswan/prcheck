"""Tests for pr_wip_checker and wip_reporter."""
from __future__ import annotations

import pytest

from src.pr_wip_checker import WIPResult, check_pr_wip
from src.wip_reporter import _build_wip_summary


# ---------------------------------------------------------------------------
# WIPResult unit tests
# ---------------------------------------------------------------------------

class TestWIPResult:
    def test_initial_state_is_passing(self):
        r = WIPResult()
        assert r.passed is True
        assert r.is_wip is False
        assert r.errors == []
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = WIPResult()
        r.fail("wip")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = WIPResult()
        r.fail("msg")
        assert "msg" in r.errors

    def test_warn_does_not_change_passed(self):
        r = WIPResult()
        r.warn("heads up")
        assert r.passed is True
        assert "heads up" in r.warnings

    def test_bool_true_when_passing(self):
        assert bool(WIPResult()) is True

    def test_bool_false_when_failed(self):
        r = WIPResult()
        r.fail("x")
        assert bool(r) is False


# ---------------------------------------------------------------------------
# check_pr_wip tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("title", [
    "WIP: my feature",
    "wip some work",
    "[WIP] refactor",
    "Draft: not done yet",
    "[draft] cleanup",
])
def test_wip_title_detected(title):
    result = check_pr_wip(title, [])
    assert result.is_wip is True
    assert result.passed is False


@pytest.mark.parametrize("label", ["wip", "work in progress", "do not merge", "dnm"])
def test_wip_label_detected(label):
    result = check_pr_wip("Add feature", [label])
    assert result.is_wip is True
    assert result.passed is False


def test_clean_pr_passes():
    result = check_pr_wip("Add new feature", ["enhancement"])
    assert result.passed is True
    assert result.is_wip is False


def test_warn_only_does_not_fail():
    result = check_pr_wip("WIP: something", [], warn_only=True)
    assert result.is_wip is True
    assert result.passed is True
    assert len(result.warnings) == 1


def test_block_merge_false_does_not_fail():
    result = check_pr_wip("WIP: something", [], block_merge=False)
    assert result.passed is True
    assert result.is_wip is True


# ---------------------------------------------------------------------------
# _build_wip_summary tests
# ---------------------------------------------------------------------------

def test_passing_summary_header():
    r = WIPResult()
    summary = _build_wip_summary(r)
    assert "✅" in summary
    assert "Passed" in summary


def test_failing_summary_header():
    r = WIPResult()
    r.fail("WIP detected")
    summary = _build_wip_summary(r)
    assert "❌" in summary
    assert "Failed" in summary


def test_summary_contains_error_message():
    r = WIPResult()
    r.fail("PR is marked as WIP via title")
    summary = _build_wip_summary(r)
    assert "PR is marked as WIP via title" in summary


def test_summary_no_indicators_message_when_clean():
    r = WIPResult()
    summary = _build_wip_summary(r)
    assert "No WIP indicators detected" in summary
