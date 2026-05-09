"""Unit tests for ci_status_reporter."""
import pytest
from unittest.mock import call, patch

from src.pr_ci_status_checker import CIStatusResult
from src.ci_status_reporter import report_ci_status_result, _build_ci_status_summary


@pytest.fixture()
def passing_result():
    return CIStatusResult(total_checks=3)


@pytest.fixture()
def failing_result():
    r = CIStatusResult(total_checks=2)
    r.failed_checks = ["build"]
    r.fail("CI check 'build' failed with state 'failure'.")
    return r


class TestBuildCIStatusSummary:
    def test_passing_header(self, passing_result):
        summary = _build_ci_status_summary(passing_result)
        assert "✅" in summary

    def test_failing_header(self, failing_result):
        summary = _build_ci_status_summary(failing_result)
        assert "❌" in summary

    def test_total_checks_shown(self, passing_result):
        passing_result.total_checks = 5
        summary = _build_ci_status_summary(passing_result)
        assert "5" in summary

    def test_failed_checks_listed(self, failing_result):
        summary = _build_ci_status_summary(failing_result)
        assert "`build`" in summary

    def test_pending_checks_listed(self):
        r = CIStatusResult(total_checks=1)
        r.pending_checks = ["lint"]
        r.warn("CI check 'lint' is pending.")
        summary = _build_ci_status_summary(r)
        assert "`lint`" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_ci_status_summary(failing_result)
        assert "Errors" in summary

    def test_warnings_listed(self):
        r = CIStatusResult()
        r.warn("some warning")
        summary = _build_ci_status_summary(r)
        assert "some warning" in summary

    def test_no_sections_when_clean(self, passing_result):
        summary = _build_ci_status_summary(passing_result)
        assert "Failed" not in summary
        assert "Pending" not in summary


class TestReportCIStatusResult:
    def test_sets_passed_true_output(self, passing_result):
        with patch("src.ci_status_reporter.set_output") as mock_out, \
             patch("src.ci_status_reporter.write_summary"):
            report_ci_status_result(passing_result)
            mock_out.assert_any_call("ci_status_passed", "true")

    def test_sets_passed_false_output(self, failing_result):
        with patch("src.ci_status_reporter.set_output") as mock_out, \
             patch("src.ci_status_reporter.write_summary"):
            report_ci_status_result(failing_result)
            mock_out.assert_any_call("ci_status_passed", "false")

    def test_sets_error_count_output(self, failing_result):
        with patch("src.ci_status_reporter.set_output") as mock_out, \
             patch("src.ci_status_reporter.write_summary"):
            report_ci_status_result(failing_result)
            mock_out.assert_any_call("ci_status_errors", "1")

    def test_writes_summary(self, passing_result):
        with patch("src.ci_status_reporter.set_output"), \
             patch("src.ci_status_reporter.write_summary") as mock_sum:
            report_ci_status_result(passing_result)
            mock_sum.assert_called_once()
