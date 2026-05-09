"""Unit tests for scope_reporter."""
from __future__ import annotations

from unittest.mock import call, patch

import pytest

from src.pr_scope_checker import ScopeResult
from src.scope_reporter import _build_scope_summary, report_scope_result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def passing_result():
    return ScopeResult()


@pytest.fixture
def failing_result():
    r = ScopeResult()
    r.fail("File 'secrets/key.pem' matches forbidden scope pattern 'secrets/*'.")
    r.out_of_scope_files.append("secrets/key.pem")
    return r


@pytest.fixture
def warning_result():
    r = ScopeResult()
    r.warn("No files changed in this PR.")
    return r


# ---------------------------------------------------------------------------
# _build_scope_summary
# ---------------------------------------------------------------------------

class TestBuildScopeSummary:
    def test_passing_header(self, passing_result):
        summary = _build_scope_summary(passing_result)
        assert "✅ Scope Check Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_scope_summary(failing_result)
        assert "❌ Scope Check Failed" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_scope_summary(failing_result)
        assert "secrets/key.pem" in summary
        assert "Errors" in summary

    def test_warnings_listed(self, warning_result):
        summary = _build_scope_summary(warning_result)
        assert "Warnings" in summary
        assert "No files changed" in summary

    def test_out_of_scope_files_listed(self, failing_result):
        summary = _build_scope_summary(failing_result)
        assert "Out-of-Scope Files" in summary
        assert "`secrets/key.pem`" in summary

    def test_no_extra_sections_when_clean(self, passing_result):
        summary = _build_scope_summary(passing_result)
        assert "Errors" not in summary
        assert "Warnings" not in summary
        assert "Out-of-Scope" not in summary


# ---------------------------------------------------------------------------
# report_scope_result
# ---------------------------------------------------------------------------

class TestReportScopeResult:
    def test_sets_passed_true_for_passing(self, passing_result):
        with patch("src.scope_reporter.set_output") as mock_out, \
             patch("src.scope_reporter.write_summary"):
            report_scope_result(passing_result)
        mock_out.assert_any_call("scope_passed", "true")

    def test_sets_passed_false_for_failing(self, failing_result):
        with patch("src.scope_reporter.set_output") as mock_out, \
             patch("src.scope_reporter.write_summary"):
            report_scope_result(failing_result)
        mock_out.assert_any_call("scope_passed", "false")

    def test_sets_error_count(self, failing_result):
        with patch("src.scope_reporter.set_output") as mock_out, \
             patch("src.scope_reporter.write_summary"):
            report_scope_result(failing_result)
        mock_out.assert_any_call("scope_errors", "1")

    def test_sets_out_of_scope_files(self, failing_result):
        with patch("src.scope_reporter.set_output") as mock_out, \
             patch("src.scope_reporter.write_summary"):
            report_scope_result(failing_result)
        mock_out.assert_any_call("out_of_scope_files", "secrets/key.pem")

    def test_writes_summary(self, passing_result):
        with patch("src.scope_reporter.set_output"), \
             patch("src.scope_reporter.write_summary") as mock_summary:
            report_scope_result(passing_result)
        mock_summary.assert_called_once()
