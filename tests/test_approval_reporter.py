import pytest
from unittest.mock import patch, call
from src.pr_approval_checker import ApprovalResult
from src.approval_reporter import report_approval_result, _build_approval_summary


@pytest.fixture
def passing_result():
    return ApprovalResult(
        passed=True,
        approval_count=2,
        required_count=2,
        approved_by=["alice", "bob"],
    )


@pytest.fixture
def failing_result():
    r = ApprovalResult(required_count=2)
    r.fail("PR requires 2 approval(s) but has 0.")
    return r


class TestBuildApprovalSummary:
    def test_passing_header(self, passing_result):
        summary = _build_approval_summary(passing_result)
        assert "✅ Approval Check Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_approval_summary(failing_result)
        assert "❌ Approval Check Failed" in summary

    def test_shows_approval_count(self, passing_result):
        summary = _build_approval_summary(passing_result)
        assert "2 / 2" in summary

    def test_lists_approvers(self, passing_result):
        summary = _build_approval_summary(passing_result)
        assert "`alice`" in summary
        assert "`bob`" in summary

    def test_shows_errors(self, failing_result):
        summary = _build_approval_summary(failing_result)
        assert "requires 2 approval" in summary

    def test_shows_warnings(self):
        r = ApprovalResult(passed=True, required_count=1, approval_count=1)
        r.warn("heads up")
        summary = _build_approval_summary(r)
        assert "heads up" in summary

    def test_no_approvers_section_when_empty(self, failing_result):
        summary = _build_approval_summary(failing_result)
        assert "Approved by" not in summary


class TestReportApprovalResult:
    def test_sets_outputs_on_pass(self, passing_result):
        with patch("src.approval_reporter.set_output") as mock_out, \
             patch("src.approval_reporter.write_summary"):
            report_approval_result(passing_result)
            mock_out.assert_any_call("approval_passed", "true")
            mock_out.assert_any_call("approval_count", "2")
            mock_out.assert_any_call("approved_by", "alice,bob")

    def test_sets_outputs_on_fail(self, failing_result):
        with patch("src.approval_reporter.set_output") as mock_out, \
             patch("src.approval_reporter.write_summary"):
            report_approval_result(failing_result)
            mock_out.assert_any_call("approval_passed", "false")
            mock_out.assert_any_call("approval_count", "0")

    def test_writes_summary(self, passing_result):
        with patch("src.approval_reporter.set_output"), \
             patch("src.approval_reporter.write_summary") as mock_summary:
            report_approval_result(passing_result)
            mock_summary.assert_called_once()
            args = mock_summary.call_args[0][0]
            assert "✅" in args
