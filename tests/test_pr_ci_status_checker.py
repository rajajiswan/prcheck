"""Unit tests for pr_ci_status_checker."""
import pytest
from src.pr_ci_status_checker import CIStatusResult, check_pr_ci_status


class TestCIStatusResult:
    def test_initial_state_is_passing(self):
        r = CIStatusResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = CIStatusResult()
        r.fail("something broke")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = CIStatusResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = CIStatusResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(CIStatusResult()) is True

    def test_bool_false_when_failed(self):
        r = CIStatusResult()
        r.fail("oops")
        assert bool(r) is False


class TestCheckPrCiStatus:
    def _s(self, name, state):
        return {"name": name, "state": state}

    def test_all_success_passes(self):
        statuses = [self._s("build", "success"), self._s("lint", "success")]
        r = check_pr_ci_status(statuses)
        assert r.passed is True
        assert r.total_checks == 2

    def test_failure_state_fails(self):
        statuses = [self._s("build", "failure")]
        r = check_pr_ci_status(statuses)
        assert r.passed is False
        assert "build" in r.failed_checks

    def test_error_state_fails(self):
        statuses = [self._s("tests", "error")]
        r = check_pr_ci_status(statuses)
        assert r.passed is False

    def test_cancelled_state_fails(self):
        statuses = [self._s("deploy", "cancelled")]
        r = check_pr_ci_status(statuses)
        assert r.passed is False

    def test_pending_warns_by_default(self):
        statuses = [self._s("ci", "pending")]
        r = check_pr_ci_status(statuses)
        assert r.passed is True
        assert r.warnings
        assert "ci" in r.pending_checks

    def test_pending_fails_when_block_on_pending(self):
        statuses = [self._s("ci", "pending")]
        r = check_pr_ci_status(statuses, block_on_pending=True)
        assert r.passed is False

    def test_skipped_passes_when_allow_skipped(self):
        statuses = [self._s("optional", "skipped")]
        r = check_pr_ci_status(statuses, allow_skipped=True)
        assert r.passed is True
        assert not r.errors

    def test_skipped_warns_when_not_allow_skipped(self):
        statuses = [self._s("optional", "skipped")]
        r = check_pr_ci_status(statuses, allow_skipped=False)
        assert r.warnings

    def test_missing_required_check_fails(self):
        statuses = [self._s("build", "success")]
        r = check_pr_ci_status(statuses, required_checks=["build", "security"])
        assert r.passed is False
        assert any("security" in e for e in r.errors)

    def test_all_required_present_passes(self):
        statuses = [self._s("build", "success"), self._s("lint", "success")]
        r = check_pr_ci_status(statuses, required_checks=["build", "lint"])
        assert r.passed is True

    def test_empty_statuses_passes(self):
        r = check_pr_ci_status([])
        assert r.passed is True
        assert r.total_checks == 0
