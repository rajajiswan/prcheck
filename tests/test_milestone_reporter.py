import pytest
from unittest.mock import call, patch
from src.pr_milestone_checker import MilestoneResult
from src.milestone_reporter import report_milestone_result, _build_milestone_summary


@pytest.fixture
def passing_result():
    return MilestoneResult(passed=True, milestone="v1.0")


@pytest.fixture
def failing_result():
    r = MilestoneResult(milestone=None)
    r.fail("PR must have a milestone set.")
    return r


class TestBuildMilestoneSummary:
    def test_passing_header(self, passing_result):
        summary = _build_milestone_summary(passing_result)
        assert "✅" in summary
        assert "passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_milestone_summary(failing_result)
        assert "❌" in summary
        assert "failed" in summary

    def test_milestone_value_shown(self, passing_result):
        summary = _build_milestone_summary(passing_result)
        assert "v1.0" in summary

    def test_error_shown_on_failure(self, failing_result):
        summary = _build_milestone_summary(failing_result)
        assert "must have a milestone" in summary

    def test_warning_shown(self):
        r = MilestoneResult()
        r.warn("no milestone set")
        summary = _build_milestone_summary(r)
        assert "no milestone set" in summary


class TestReportMilestoneResult:
    def test_sets_passed_true_output(self, passing_result):
        with patch("src.milestone_reporter.set_output") as mock_out, \
             patch("src.milestone_reporter.write_summary"):
            report_milestone_result(passing_result)
            mock_out.assert_any_call("milestone_passed", "true")

    def test_sets_passed_false_output(self, failing_result):
        with patch("src.milestone_reporter.set_output") as mock_out, \
             patch("src.milestone_reporter.write_summary"):
            report_milestone_result(failing_result)
            mock_out.assert_any_call("milestone_passed", "false")

    def test_sets_milestone_value_output(self, passing_result):
        with patch("src.milestone_reporter.set_output") as mock_out, \
             patch("src.milestone_reporter.write_summary"):
            report_milestone_result(passing_result)
            mock_out.assert_any_call("milestone_value", "v1.0")

    def test_sets_empty_milestone_when_none(self, failing_result):
        with patch("src.milestone_reporter.set_output") as mock_out, \
             patch("src.milestone_reporter.write_summary"):
            report_milestone_result(failing_result)
            mock_out.assert_any_call("milestone_value", "")

    def test_writes_summary(self, passing_result):
        with patch("src.milestone_reporter.set_output"), \
             patch("src.milestone_reporter.write_summary") as mock_sum:
            report_milestone_result(passing_result)
            mock_sum.assert_called_once()
