"""Tests for check_reporter.py."""

import pytest
from unittest.mock import patch, call

from src.check_reporter import report_check_suite, _build_suite_summary
from src.run_checks import CheckSuite
from src.pr_description_enforcer import DescriptionResult
from src.branch_label_enforcer import LabelEnforcementResult


@pytest.fixture
def passing_suite():
    return CheckSuite()


@pytest.fixture
def failing_suite():
    dr = DescriptionResult()
    dr.fail("Missing ## Summary")
    lr = LabelEnforcementResult()
    lr.fail("Label 'feature' not applied")
    return CheckSuite(description_result=dr, label_result=lr)


class TestReportCheckSuite:
    def test_sets_passed_true_for_passing(self, passing_suite):
        with patch("src.check_reporter.set_output") as mock_out, \
             patch("src.check_reporter.write_summary"):
            report_check_suite(passing_suite)
            mock_out.assert_any_call("passed", "true")

    def test_sets_passed_false_for_failing(self, failing_suite):
        with patch("src.check_reporter.set_output") as mock_out, \
             patch("src.check_reporter.write_summary"):
            report_check_suite(failing_suite)
            mock_out.assert_any_call("passed", "false")

    def test_sets_errors_output(self, failing_suite):
        with patch("src.check_reporter.set_output") as mock_out, \
             patch("src.check_reporter.write_summary"):
            report_check_suite(failing_suite)
            calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
            assert "errors" in calls
            assert "Missing ## Summary" in calls["errors"]

    def test_errors_empty_string_when_passing(self, passing_suite):
        with patch("src.check_reporter.set_output") as mock_out, \
             patch("src.check_reporter.write_summary"):
            report_check_suite(passing_suite)
            calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
            assert calls["errors"] == ""

    def test_write_summary_called(self, passing_suite):
        with patch("src.check_reporter.set_output"), \
             patch("src.check_reporter.write_summary") as mock_summary:
            report_check_suite(passing_suite)
            mock_summary.assert_called_once()


class TestBuildSuiteSummary:
    def test_contains_passed_header(self, passing_suite):
        summary = _build_suite_summary(passing_suite)
        assert "All checks passed" in summary

    def test_contains_failed_header(self, failing_suite):
        summary = _build_suite_summary(failing_suite)
        assert "Some checks failed" in summary

    def test_contains_description_errors(self, failing_suite):
        summary = _build_suite_summary(failing_suite)
        assert "Missing ## Summary" in summary

    def test_contains_label_errors(self, failing_suite):
        summary = _build_suite_summary(failing_suite)
        assert "Label 'feature' not applied" in summary

    def test_no_label_section_when_none(self):
        dr = DescriptionResult()
        suite = CheckSuite(description_result=dr)
        summary = _build_suite_summary(suite)
        assert "Label Check" not in summary
