import pytest
from unittest.mock import patch, call
from src.pr_checklist_checker import ChecklistResult
from src.checklist_reporter import report_checklist_result, _build_checklist_summary


@pytest.fixture
def passing_result():
    return ChecklistResult(
        passed=True,
        total_items=3,
        checked_items=3,
        unchecked_items=0,
    )


@pytest.fixture
def failing_result():
    r = ChecklistResult(
        passed=False,
        total_items=3,
        checked_items=1,
        unchecked_items=2,
    )
    r.errors.append("2 checklist item(s) are not checked.")
    return r


class TestBuildChecklistSummary:
    def test_passing_header(self, passing_result):
        summary = _build_checklist_summary(passing_result)
        assert "\u2705 Checklist Check Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_checklist_summary(failing_result)
        assert "\u274c Checklist Check Failed" in summary

    def test_table_contains_counts(self, passing_result):
        summary = _build_checklist_summary(passing_result)
        assert "3" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_checklist_summary(failing_result)
        assert "2 checklist item(s) are not checked." in summary

    def test_warnings_listed(self):
        r = ChecklistResult()
        r.warn("heads up")
        summary = _build_checklist_summary(r)
        assert "heads up" in summary

    def test_no_errors_section_when_none(self, passing_result):
        summary = _build_checklist_summary(passing_result)
        assert "**Errors:**" not in summary

    def test_no_warnings_section_when_none(self, passing_result):
        summary = _build_checklist_summary(passing_result)
        assert "**Warnings:**" not in summary


class TestReportChecklistResult:
    def test_sets_outputs_for_passing(self, passing_result):
        with patch("src.checklist_reporter.set_output") as mock_out, \
             patch("src.checklist_reporter.write_summary"):
            report_checklist_result(passing_result)
            mock_out.assert_any_call("checklist_passed", "true")
            mock_out.assert_any_call("checklist_total", "3")
            mock_out.assert_any_call("checklist_checked", "3")
            mock_out.assert_any_call("checklist_unchecked", "0")

    def test_sets_outputs_for_failing(self, failing_result):
        with patch("src.checklist_reporter.set_output") as mock_out, \
             patch("src.checklist_reporter.write_summary"):
            report_checklist_result(failing_result)
            mock_out.assert_any_call("checklist_passed", "false")

    def test_writes_summary(self, passing_result):
        with patch("src.checklist_reporter.set_output"), \
             patch("src.checklist_reporter.write_summary") as mock_sum:
            report_checklist_result(passing_result)
            mock_sum.assert_called_once()
            summary_arg = mock_sum.call_args[0][0]
            assert "Checklist" in summary_arg
