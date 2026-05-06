"""Tests for branch_age_reporter."""
from __future__ import annotations

from unittest.mock import call, patch

import pytest

from src.branch_age_reporter import _build_branch_age_summary, report_branch_age_result
from src.pr_branch_age_checker import BranchAgeResult


@pytest.fixture()
def passing_result() -> BranchAgeResult:
    r = BranchAgeResult(branch_name="feature/login", age_days=5.0)
    return r


@pytest.fixture()
def warning_result() -> BranchAgeResult:
    r = BranchAgeResult(branch_name="feature/login", age_days=20.0)
    r.warn("Branch is 20.0 days old, exceeding the warning threshold of 14 days.")
    return r


@pytest.fixture()
def failing_result() -> BranchAgeResult:
    r = BranchAgeResult(branch_name="feature/login", age_days=45.0)
    r.fail("Branch 'feature/login' is 45.0 days old, exceeding the maximum of 30 days.")
    return r


class TestBuildBranchAgeSummary:
    def test_passing_header(self, passing_result):
        summary = _build_branch_age_summary(passing_result)
        assert "✅" in summary
        assert "Passed" in summary

    def test_warning_header(self, warning_result):
        summary = _build_branch_age_summary(warning_result)
        assert "⚠️" in summary
        assert "Warnings" in summary

    def test_failing_header(self, failing_result):
        summary = _build_branch_age_summary(failing_result)
        assert "❌" in summary
        assert "Failed" in summary

    def test_includes_branch_name(self, passing_result):
        summary = _build_branch_age_summary(passing_result)
        assert "feature/login" in summary

    def test_includes_age_days(self, passing_result):
        summary = _build_branch_age_summary(passing_result)
        assert "5.0" in summary

    def test_includes_error_messages(self, failing_result):
        summary = _build_branch_age_summary(failing_result)
        assert "45.0 days old" in summary

    def test_includes_warning_messages(self, warning_result):
        summary = _build_branch_age_summary(warning_result)
        assert "20.0 days old" in summary

    def test_no_age_when_none(self):
        r = BranchAgeResult(branch_name="x")
        summary = _build_branch_age_summary(r)
        assert "Age" not in summary


class TestReportBranchAgeResult:
    def test_sets_passed_true_for_passing(self, passing_result):
        with patch("src.branch_age_reporter.set_output") as mock_out, \
             patch("src.branch_age_reporter.write_summary"):
            report_branch_age_result(passing_result)
            mock_out.assert_any_call("branch_age_passed", "true")

    def test_sets_passed_false_for_failing(self, failing_result):
        with patch("src.branch_age_reporter.set_output") as mock_out, \
             patch("src.branch_age_reporter.write_summary"):
            report_branch_age_result(failing_result)
            mock_out.assert_any_call("branch_age_passed", "false")

    def test_sets_age_days_output(self, passing_result):
        with patch("src.branch_age_reporter.set_output") as mock_out, \
             patch("src.branch_age_reporter.write_summary"):
            report_branch_age_result(passing_result)
            mock_out.assert_any_call("branch_age_days", "5.0")

    def test_sets_empty_age_when_none(self):
        r = BranchAgeResult(branch_name="x")
        with patch("src.branch_age_reporter.set_output") as mock_out, \
             patch("src.branch_age_reporter.write_summary"):
            report_branch_age_result(r)
            mock_out.assert_any_call("branch_age_days", "")

    def test_calls_write_summary(self, passing_result):
        with patch("src.branch_age_reporter.set_output"), \
             patch("src.branch_age_reporter.write_summary") as mock_sum:
            report_branch_age_result(passing_result)
            mock_sum.assert_called_once()
