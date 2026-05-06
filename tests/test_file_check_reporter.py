from __future__ import annotations

from unittest.mock import call, patch

import pytest

from src.file_check_reporter import _build_file_summary, report_file_check_result
from src.pr_file_checker import FileCheckResult


@pytest.fixture
def passing_result():
    return FileCheckResult()


@pytest.fixture
def failing_result():
    r = FileCheckResult()
    r.fail("Forbidden file matched 'secrets/*': secrets/prod.env")
    r.warn("No files matching required pattern 'tests/*' were changed.")
    r.matched_patterns.append("secrets/*")
    return r


class TestBuildFileSummary:
    def test_passing_header(self, passing_result):
        summary = _build_file_summary(passing_result)
        assert "✅ File Check Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_file_summary(failing_result)
        assert "❌ File Check Failed" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_file_summary(failing_result)
        assert "Forbidden file matched" in summary

    def test_warnings_listed(self, failing_result):
        summary = _build_file_summary(failing_result)
        assert "No files matching required pattern" in summary

    def test_matched_patterns_listed(self, failing_result):
        summary = _build_file_summary(failing_result)
        assert "`secrets/*`" in summary

    def test_no_warnings_section_when_empty(self, passing_result):
        summary = _build_file_summary(passing_result)
        assert "Warnings" not in summary


class TestReportFileCheckResult:
    def test_success_sets_outputs(self, passing_result):
        with patch("src.file_check_reporter.set_output") as mock_out, \
             patch("src.file_check_reporter.write_summary"):
            report_file_check_result(passing_result)
            mock_out.assert_any_call("file_check_passed", "true")
            mock_out.assert_any_call("file_check_errors", "0")
            mock_out.assert_any_call("file_check_warnings", "0")

    def test_failure_sets_outputs(self, failing_result):
        with patch("src.file_check_reporter.set_output") as mock_out, \
             patch("src.file_check_reporter.write_summary"):
            report_file_check_result(failing_result)
            mock_out.assert_any_call("file_check_passed", "false")
            mock_out.assert_any_call("file_check_errors", "1")

    def test_writes_summary(self, passing_result):
        with patch("src.file_check_reporter.set_output"), \
             patch("src.file_check_reporter.write_summary") as mock_summary:
            report_file_check_result(passing_result)
            mock_summary.assert_called_once()
