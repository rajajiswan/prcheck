"""Tests for pr_branch_age_checker."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.pr_branch_age_checker import BranchAgeResult, check_branch_age

_NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def _ts(days_ago: float) -> str:
    dt = _NOW - timedelta(days=days_ago)
    return dt.isoformat().replace("+00:00", "Z")


class TestBranchAgeResult:
    def test_initial_state_is_passing(self):
        r = BranchAgeResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.age_days is None

    def test_fail_sets_passed_false(self):
        r = BranchAgeResult()
        r.fail("too old")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = BranchAgeResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = BranchAgeResult()
        r.warn("getting old")
        assert r.passed is True
        assert r.warnings == ["getting old"]

    def test_bool_true_when_passing(self):
        r = BranchAgeResult()
        assert bool(r) is True

    def test_bool_false_when_failed(self):
        r = BranchAgeResult()
        r.fail("nope")
        assert bool(r) is False


def test_under_both_thresholds_passes():
    result = check_branch_age("feature/x", _ts(3), max_age_days=30, warn_age_days=14, now=_NOW)
    assert result.passed is True
    assert result.warnings == []
    assert result.age_days == 3.0


def test_exceeds_warn_threshold_warns():
    result = check_branch_age("feature/x", _ts(20), max_age_days=30, warn_age_days=14, now=_NOW)
    assert result.passed is True
    assert len(result.warnings) == 1
    assert "20.0" in result.warnings[0]


def test_exceeds_max_threshold_fails():
    result = check_branch_age("feature/x", _ts(45), max_age_days=30, warn_age_days=14, now=_NOW)
    assert result.passed is False
    assert len(result.errors) == 1
    assert "45.0" in result.errors[0]


def test_no_thresholds_always_passes():
    result = check_branch_age("feature/x", _ts(999), now=_NOW)
    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []


def test_invalid_timestamp_fails():
    result = check_branch_age("feature/x", "not-a-date", max_age_days=10, now=_NOW)
    assert result.passed is False
    assert any("parse" in e for e in result.errors)
    assert result.age_days is None


def test_branch_name_stored():
    result = check_branch_age("hotfix/urgent", _ts(1), now=_NOW)
    assert result.branch_name == "hotfix/urgent"


def test_exactly_at_max_passes():
    # age == max_age_days should NOT fail (strictly greater than)
    result = check_branch_age("feature/x", _ts(30), max_age_days=30, now=_NOW)
    assert result.passed is True
