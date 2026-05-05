from unittest.mock import call, patch

import pytest

from src.conflict_reporter import _build_conflict_summary, report_conflict_result
from src.pr_conflict_checker import ConflictResult


@pytest.fixture()
def passing_result() -> ConflictResult:
    return ConflictResult()


@pytest.fixture()
def failing_result() -> ConflictResult:
    result = ConflictResult()
    result.fail("This PR has merge conflicts.")
    return result


@pytest.fixture()
def warning_result() -> ConflictResult:
    result = ConflictResult()
    result.warn("Mergeability not yet determined.")
    return result


class TestBuildConflictSummary:
    def test_passing_header(self, passing_result):
        summary = _build_conflict_summary(passing_result)
        assert "✅" in summary
        assert "Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_conflict_summary(failing_result)
        assert "❌" in summary
        assert "Failed" in summary

    def test_error_message_included(self, failing_result):
        summary = _build_conflict_summary(failing_result)
        assert "merge conflicts" in summary

    def test_warning_included(self, warning_result):
        summary = _build_conflict_summary(warning_result)
        assert "⚠️" in summary
        assert "Mergeability not yet determined" in summary

    def test_no_warnings_section_when_clean(self, passing_result):
        summary = _build_conflict_summary(passing_result)
        assert "Warnings" not in summary


class TestReportConflictResult:
    def test_success_sets_outputs(self, passing_result):
        with patch("src.conflict_reporter.set_output") as mock_out, \
             patch("src.conflict_reporter.write_summary"):
            report_conflict_result(passing_result)
            mock_out.assert_any_call("conflict_check_passed", "true")

    def test_failure_sets_passed_false_output(self, failing_result):
        with patch("src.conflict_reporter.set_output") as mock_out, \
             patch("src.conflict_reporter.write_summary"):
            report_conflict_result(failing_result)
            mock_out.assert_any_call("conflict_check_passed", "false")

    def test_failure_sets_error_output(self, failing_result):
        with patch("src.conflict_reporter.set_output") as mock_out, \
             patch("src.conflict_reporter.write_summary"):
            report_conflict_result(failing_result)
            calls = [str(c) for c in mock_out.call_args_list]
            assert any("conflict_check_error" in c for c in calls)

    def test_no_error_output_when_passing(self, passing_result):
        with patch("src.conflict_reporter.set_output") as mock_out, \
             patch("src.conflict_reporter.write_summary"):
            report_conflict_result(passing_result)
            output_names = [c.args[0] for c in mock_out.call_args_list]
            assert "conflict_check_error" not in output_names

    def test_write_summary_called(self, passing_result):
        with patch("src.conflict_reporter.set_output"), \
             patch("src.conflict_reporter.write_summary") as mock_summary:
            report_conflict_result(passing_result)
            mock_summary.assert_called_once()
