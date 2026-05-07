import pytest
from src.pr_reopen_checker import ReopenResult, check_pr_reopen


class TestReopenResult:
    def test_initial_state_is_passing(self):
        r = ReopenResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.reopen_count == 0
        assert r.last_closed_at is None

    def test_fail_sets_passed_false(self):
        r = ReopenResult()
        r.fail("too many reopens")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ReopenResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = ReopenResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = ReopenResult()
        assert bool(r) is True

    def test_bool_false_when_failed(self):
        r = ReopenResult()
        r.fail("nope")
        assert bool(r) is False


class TestCheckPrReopen:
    def test_zero_reopens_passes_cleanly(self):
        result = check_pr_reopen(reopen_count=0, last_closed_at=None)
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []

    def test_single_reopen_warns_by_default(self):
        result = check_pr_reopen(reopen_count=1, last_closed_at="2024-01-10T12:00:00Z")
        assert result.passed is True
        assert len(result.warnings) == 1
        assert "1 time" in result.warnings[0]

    def test_reopen_within_limit_warns_but_passes(self):
        result = check_pr_reopen(reopen_count=2, last_closed_at=None, max_reopens=3)
        assert result.passed is True
        assert result.warnings

    def test_reopen_exceeds_limit_fails(self):
        result = check_pr_reopen(reopen_count=4, last_closed_at=None, max_reopens=2)
        assert result.passed is False
        assert any("4 time" in e for e in result.errors)

    def test_warn_on_reopen_false_suppresses_warning(self):
        result = check_pr_reopen(
            reopen_count=1, last_closed_at=None, warn_on_reopen=False
        )
        assert result.passed is True
        assert result.warnings == []

    def test_fail_on_exceed_false_never_fails(self):
        result = check_pr_reopen(
            reopen_count=100, last_closed_at=None, max_reopens=1, fail_on_exceed=False
        )
        assert result.passed is True
        assert result.errors == []

    def test_stores_last_closed_at(self):
        ts = "2024-03-15T08:30:00Z"
        result = check_pr_reopen(reopen_count=0, last_closed_at=ts)
        assert result.last_closed_at == ts

    def test_stores_reopen_count(self):
        result = check_pr_reopen(reopen_count=3, last_closed_at=None)
        assert result.reopen_count == 3

    def test_exact_limit_passes(self):
        result = check_pr_reopen(reopen_count=2, last_closed_at=None, max_reopens=2)
        assert result.passed is True
