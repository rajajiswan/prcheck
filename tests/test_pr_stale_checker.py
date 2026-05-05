from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.pr_stale_checker import StaleResult, check_pr_stale


def _ts(days_ago: int) -> str:
    """Return an ISO-8601 UTC timestamp for *days_ago* days in the past."""
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class TestStaleResult:
    def test_initial_state_is_passing(self):
        r = StaleResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.days_since_update is None
        assert r.is_stale is False

    def test_fail_sets_passed_false(self):
        r = StaleResult()
        r.fail("too old")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = StaleResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = StaleResult()
        r.warn("getting old")
        assert r.passed is True
        assert r.warnings == ["getting old"]

    def test_bool_true_when_passing(self):
        r = StaleResult()
        assert bool(r) is True

    def test_bool_false_when_failed(self):
        r = StaleResult()
        r.fail("stale")
        assert bool(r) is False


class TestCheckPrStale:
    def test_fresh_pr_passes_silently(self):
        result = check_pr_stale(_ts(3), stale_days=30, warn_days=14)
        assert result.passed is True
        assert result.is_stale is False
        assert result.warnings == []
        assert result.days_since_update == 3

    def test_warn_zone_issues_warning(self):
        result = check_pr_stale(_ts(20), stale_days=30, warn_days=14)
        assert result.passed is True
        assert result.is_stale is False
        assert len(result.warnings) == 1
        assert "20" in result.warnings[0]

    def test_stale_pr_warns_by_default(self):
        result = check_pr_stale(_ts(35), stale_days=30, warn_days=14)
        assert result.passed is True
        assert result.is_stale is True
        assert len(result.warnings) == 1
        assert "35" in result.warnings[0]

    def test_stale_pr_fails_when_require_fresh(self):
        result = check_pr_stale(_ts(35), stale_days=30, warn_days=14, require_fresh=True)
        assert result.passed is False
        assert result.is_stale is True
        assert len(result.errors) == 1

    def test_invalid_timestamp_fails(self):
        result = check_pr_stale("not-a-date")
        assert result.passed is False
        assert "Could not parse" in result.errors[0]

    def test_days_since_update_recorded(self):
        result = check_pr_stale(_ts(10), stale_days=30, warn_days=14)
        assert result.days_since_update == 10

    def test_exactly_on_stale_threshold(self):
        result = check_pr_stale(_ts(30), stale_days=30, warn_days=14)
        assert result.is_stale is True

    def test_exactly_on_warn_threshold(self):
        result = check_pr_stale(_ts(14), stale_days=30, warn_days=14)
        assert result.passed is True
        assert len(result.warnings) == 1
