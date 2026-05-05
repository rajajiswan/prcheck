from datetime import datetime, timedelta, timezone

import pytest

from src.pr_age_checker import AgeResult, check_pr_age


def _ts(days_ago: float) -> str:
    """Return an ISO-8601 UTC timestamp for *days_ago* days in the past."""
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class TestAgeResult:
    def test_initial_state_is_passing(self):
        r = AgeResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.age_days is None

    def test_fail_sets_passed_false(self):
        r = AgeResult()
        r.fail("too old")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = AgeResult()
        r.fail("too old")
        assert "too old" in r.errors

    def test_warn_does_not_change_passed(self):
        r = AgeResult()
        r.warn("getting stale")
        assert r.passed is True
        assert "getting stale" in r.warnings

    def test_bool_true_when_passing(self):
        assert bool(AgeResult()) is True

    def test_bool_false_when_failed(self):
        r = AgeResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrAge:
    def test_young_pr_passes_with_no_limits(self):
        result = check_pr_age(_ts(1))
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []

    def test_age_days_is_populated(self):
        result = check_pr_age(_ts(3))
        assert result.age_days is not None
        assert 2.9 < result.age_days < 3.1

    def test_exceeds_max_age_fails(self):
        result = check_pr_age(_ts(10), max_age_days=7)
        assert result.passed is False
        assert any("10" in e or "9" in e for e in result.errors)

    def test_within_max_age_passes(self):
        result = check_pr_age(_ts(5), max_age_days=7)
        assert result.passed is True

    def test_exceeds_warn_age_warns(self):
        result = check_pr_age(_ts(6), warn_age_days=5)
        assert result.passed is True
        assert len(result.warnings) == 1

    def test_within_warn_age_no_warning(self):
        result = check_pr_age(_ts(3), warn_age_days=5)
        assert result.warnings == []

    def test_draft_exceeds_max_age_warns_not_fails(self):
        result = check_pr_age(_ts(15), max_age_days=7, is_draft=True)
        assert result.passed is True
        assert len(result.warnings) == 1
        assert "Draft" in result.warnings[0]

    def test_invalid_timestamp_fails(self):
        result = check_pr_age("not-a-date")
        assert result.passed is False
        assert any("parse" in e for e in result.errors)

    def test_max_and_warn_age_max_takes_precedence(self):
        result = check_pr_age(_ts(20), max_age_days=10, warn_age_days=5)
        assert result.passed is False
        assert result.warnings == []
