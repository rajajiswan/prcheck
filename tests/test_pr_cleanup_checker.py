from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from src.pr_cleanup_checker import CleanupResult, check_pr_cleanup


class TestCleanupResult:
    def test_initial_state_is_passing(self):
        r = CleanupResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = CleanupResult()
        r.fail("bad branch")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = CleanupResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = CleanupResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = CleanupResult()
        assert bool(r) is True

    def test_bool_false_when_failed(self):
        r = CleanupResult()
        r.fail("oops")
        assert bool(r) is False


class TestCheckPrCleanup:
    def test_protected_branch_fails(self):
        result = check_pr_cleanup(
            branch_name="main", state="closed", is_merged=True
        )
        assert result.passed is False
        assert any("protected" in e for e in result.errors)

    def test_custom_protected_branch_fails(self):
        result = check_pr_cleanup(
            branch_name="release",
            state="closed",
            is_merged=True,
            protected_branches=["release"],
        )
        assert result.passed is False

    def test_open_pr_warns_only(self):
        result = check_pr_cleanup(
            branch_name="feature/foo", state="open", is_merged=False
        )
        assert result.passed is True
        assert any("still open" in w for w in result.warnings)

    def test_merged_branch_warns_safe_to_delete(self):
        result = check_pr_cleanup(
            branch_name="feature/bar", state="closed", is_merged=True
        )
        assert result.passed is True
        assert any("merged" in w for w in result.warnings)

    def test_stale_closed_unmerged_warns(self):
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        result = check_pr_cleanup(
            branch_name="feature/baz",
            state="closed",
            is_merged=False,
            closed_at=old_date,
            days_closed_threshold=7,
        )
        assert result.passed is True
        assert any("closed (unmerged)" in w for w in result.warnings)

    def test_recently_closed_unmerged_no_warning(self):
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        result = check_pr_cleanup(
            branch_name="feature/qux",
            state="closed",
            is_merged=False,
            closed_at=recent_date,
            days_closed_threshold=7,
        )
        assert result.passed is True
        assert result.warnings == []

    def test_invalid_closed_at_does_not_raise(self):
        result = check_pr_cleanup(
            branch_name="feature/x",
            state="closed",
            is_merged=False,
            closed_at="not-a-date",
        )
        assert result.passed is True

    def test_warn_on_stale_disabled_skips_check(self):
        old_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        result = check_pr_cleanup(
            branch_name="feature/y",
            state="closed",
            is_merged=False,
            closed_at=old_date,
            warn_on_stale_closed=False,
        )
        assert result.warnings == []
