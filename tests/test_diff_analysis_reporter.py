"""Tests for diff_analysis_reporter."""
from unittest.mock import call, patch

import pytest

from src.pr_diff_analyzer import DiffAnalysisResult
from src.diff_analysis_reporter import report_diff_analysis, _build_diff_summary


@pytest.fixture
def passing_result():
    return DiffAnalysisResult(passed=True)


@pytest.fixture
def failing_result():
    r = DiffAnalysisResult()
    r.fail("PR touches 60 files which exceeds the limit of 50.")
    r.warn("PR changes 600 lines (warning threshold: 500).")
    return r


class TestBuildDiffSummary:
    def test_passing_header(self, passing_result):
        summary = _build_diff_summary(passing_result)
        assert "✅ Diff Analysis Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_diff_summary(failing_result)
        assert "❌ Diff Analysis Failed" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_diff_summary(failing_result)
        assert "60 files" in summary

    def test_warnings_listed(self, failing_result):
        summary = _build_diff_summary(failing_result)
        assert "600 lines" in summary

    def test_no_issues_message_when_clean(self, passing_result):
        summary = _build_diff_summary(passing_result)
        assert "No issues detected" in summary


class TestReportDiffAnalysis:
    def test_sets_passed_true_for_passing(self, passing_result):
        with patch("src.diff_analysis_reporter.set_output") as mock_out, \
             patch("src.diff_analysis_reporter.write_summary"):
            report_diff_analysis(passing_result)
            mock_out.assert_any_call("diff_analysis_passed", "true")

    def test_sets_passed_false_for_failing(self, failing_result):
        with patch("src.diff_analysis_reporter.set_output") as mock_out, \
             patch("src.diff_analysis_reporter.write_summary"):
            report_diff_analysis(failing_result)
            mock_out.assert_any_call("diff_analysis_passed", "false")

    def test_errors_output_joined(self, failing_result):
        with patch("src.diff_analysis_reporter.set_output") as mock_out, \
             patch("src.diff_analysis_reporter.write_summary"):
            report_diff_analysis(failing_result)
            calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
            assert "60 files" in calls["diff_analysis_errors"]

    def test_empty_errors_output_when_passing(self, passing_result):
        with patch("src.diff_analysis_reporter.set_output") as mock_out, \
             patch("src.diff_analysis_reporter.write_summary"):
            report_diff_analysis(passing_result)
            calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
            assert calls["diff_analysis_errors"] == ""

    def test_write_summary_called(self, passing_result):
        with patch("src.diff_analysis_reporter.set_output"), \
             patch("src.diff_analysis_reporter.write_summary") as mock_summary:
            report_diff_analysis(passing_result)
            mock_summary.assert_called_once()
