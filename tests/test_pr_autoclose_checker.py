from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.pr_autoclose_checker import AutocloseResult, check_pr_autoclose


def _ts(days_ago: int) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class TestAutocloseResult:
    def test_initial_state_is_passing(self):
        r = AutocloseResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.days_inactive is None
        assert r.would_close is False

    def test_fail_sets_passed_false(self):
        r = AutocloseResult()
        r.fail("too old")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = AutocloseResult()
        r.fail("msg1")
        r.fail("msg2")
        assert r.errors == ["msg1", "msg2"]

    def test_warn_does_not_change_passed(self):
        r = AutocloseResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(AutocloseResult()) is True

    def test_bool_false_when_failed(self):
        r = AutocloseResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrAutoclose:
    def test_active_pr_passes(self):
        result = check_pr_autoclose(_ts(5), is_draft=False)
        assert result.passed is True
        assert result.would_close is False
        assert result.days_inactive == 5

    def test_inactive_pr_fails_at_threshold(self):
        result = check_pr_autoclose(_ts(30), is_draft=False, autoclose_days=30)
        assert result.passed is False
        assert result.would_close is True
        assert len(result.errors) == 1

    def test_warning_issued_before_threshold(self):
        result = check_pr_autoclose(
            _ts(22), is_draft=False, autoclose_days=30, warn_days=21
        )
        assert result.passed is True
        assert result.would_close is False
        assert len(result.warnings) == 1

    def test_draft_skipped_when_skip_drafts_true(self):
        result = check_pr_autoclose(_ts(60), is_draft=True, skip_drafts=True)
        assert result.passed is True
        assert result.would_close is False
        assert any("draft" in w.lower() for w in result.warnings)

    def test_draft_not_skipped_when_skip_drafts_false(self):
        result = check_pr_autoclose(
            _ts(60), is_draft=True, skip_drafts=False, autoclose_days=30
        )
        assert result.passed is False
        assert result.would_close is True

    def test_disabled_autoclose_always_passes(self):
        result = check_pr_autoclose(
            _ts(999), is_draft=False, autoclose_enabled=False
        )
        assert result.passed is True

    def test_invalid_timestamp_fails(self):
        result = check_pr_autoclose("not-a-date", is_draft=False)
        assert result.passed is False
        assert any("Invalid" in e for e in result.errors)

    def test_days_inactive_stored(self):
        result = check_pr_autoclose(_ts(10), is_draft=False)
        assert result.days_inactive == 10
