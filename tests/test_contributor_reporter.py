import pytest
from unittest.mock import patch, call
from src.pr_contributor_checker import ContributorResult
from src.contributor_reporter import report_contributor_result, _build_contributor_summary


@pytest.fixture()
def passing_result():
    return ContributorResult(passed=True, author="alice")


@pytest.fixture()
def first_time_result():
    r = ContributorResult(passed=True, author="newbie", is_first_time=True)
    r.warn("'newbie' appears to be a first-time contributor — please review carefully.")
    return r


@pytest.fixture()
def failing_result():
    r = ContributorResult(passed=False, author="mallory")
    r.fail("Author 'mallory' is on the blocked contributors list.")
    return r


class TestBuildContributorSummary:
    def test_passing_header(self, passing_result):
        summary = _build_contributor_summary(passing_result)
        assert "✅" in summary
        assert "Contributor Check" in summary

    def test_failing_header(self, failing_result):
        summary = _build_contributor_summary(failing_result)
        assert "❌" in summary

    def test_author_shown(self, passing_result):
        summary = _build_contributor_summary(passing_result)
        assert "`alice`" in summary

    def test_first_time_badge(self, first_time_result):
        summary = _build_contributor_summary(first_time_result)
        assert "🆕" in summary

    def test_warning_listed(self, first_time_result):
        summary = _build_contributor_summary(first_time_result)
        assert "⚠️" in summary
        assert "first-time" in summary

    def test_error_listed(self, failing_result):
        summary = _build_contributor_summary(failing_result)
        assert "blocked" in summary

    def test_no_issues_message_when_clean(self, passing_result):
        summary = _build_contributor_summary(passing_result)
        assert "no issues" in summary


class TestReportContributorResult:
    def test_sets_outputs_on_pass(self, passing_result):
        with patch("src.contributor_reporter.set_output") as mock_out, \
             patch("src.contributor_reporter.write_summary"):
            report_contributor_result(passing_result)
        calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
        assert calls["contributor_passed"] == "true"
        assert calls["contributor_author"] == "alice"
        assert calls["contributor_first_time"] == "false"

    def test_sets_outputs_on_fail(self, failing_result):
        with patch("src.contributor_reporter.set_output") as mock_out, \
             patch("src.contributor_reporter.write_summary"):
            report_contributor_result(failing_result)
        calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
        assert calls["contributor_passed"] == "false"
        assert "contributor_errors" in calls

    def test_writes_summary(self, passing_result):
        with patch("src.contributor_reporter.set_output"), \
             patch("src.contributor_reporter.write_summary") as mock_summary:
            report_contributor_result(passing_result)
        mock_summary.assert_called_once()
        assert "Contributor" in mock_summary.call_args.args[0]
