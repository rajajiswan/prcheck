"""Unit tests for src/label_check_reporter.py."""
from unittest.mock import call, patch

import pytest

from src.label_check_reporter import _build_label_summary, report_label_check_result
from src.pr_label_checker import LabelCheckResult


@pytest.fixture()
def passing_result() -> LabelCheckResult:
    return LabelCheckResult(applied_labels=["bug", "enhancement"])


@pytest.fixture()
def failing_result() -> LabelCheckResult:
    r = LabelCheckResult(applied_labels=["wip"])
    r.fail("PR contains disallowed label(s): wip.")
    r.warn("PR has no labels applied.")
    return r


class TestBuildLabelSummary:
    def test_passing_header(self, passing_result):
        summary = _build_label_summary(passing_result)
        assert "Label Check Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_label_summary(failing_result)
        assert "Label Check Failed" in summary

    def test_applied_labels_shown(self, passing_result):
        summary = _build_label_summary(passing_result)
        assert "`bug`" in summary
        assert "`enhancement`" in summary

    def test_no_labels_shown_as_none(self):
        r = LabelCheckResult()
        summary = _build_label_summary(r)
        assert "_none_" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_label_summary(failing_result)
        assert "Errors" in summary
        assert "disallowed" in summary

    def test_warnings_listed(self, failing_result):
        summary = _build_label_summary(failing_result)
        assert "Warnings" in summary

    def test_no_errors_section_when_passing(self, passing_result):
        summary = _build_label_summary(passing_result)
        assert "Errors" not in summary


class TestReportLabelCheckResult:
    def test_sets_passed_true_for_passing(self, passing_result):
        with patch("src.label_check_reporter.set_output") as mock_out, \
             patch("src.label_check_reporter.write_summary"):
            report_label_check_result(passing_result)
            mock_out.assert_any_call("label_check_passed", "true")

    def test_sets_passed_false_for_failing(self, failing_result):
        with patch("src.label_check_reporter.set_output") as mock_out, \
             patch("src.label_check_reporter.write_summary"):
            report_label_check_result(failing_result)
            mock_out.assert_any_call("label_check_passed", "false")

    def test_errors_joined_with_pipe(self, failing_result):
        with patch("src.label_check_reporter.set_output") as mock_out, \
             patch("src.label_check_reporter.write_summary"):
            report_label_check_result(failing_result)
            calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
            assert calls["label_check_errors"] == failing_result.errors[0]

    def test_write_summary_called(self, passing_result):
        with patch("src.label_check_reporter.set_output"), \
             patch("src.label_check_reporter.write_summary") as mock_sum:
            report_label_check_result(passing_result)
            mock_sum.assert_called_once()
