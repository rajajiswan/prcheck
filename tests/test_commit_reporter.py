import pytest
from unittest.mock import patch, call
from src.pr_commit_checker import CommitResult
from src.commit_reporter import report_commit_result, _build_commit_summary


@pytest.fixture
def passing_result():
    return CommitResult(passed=True, commit_count=3)


@pytest.fixture
def failing_result():
    r = CommitResult(commit_count=2)
    r.fail("2 non-conventional commits found.")
    r.non_conventional_commits.extend(["WIP stuff", "added thing"])
    return r


class TestBuildCommitSummary:
    def test_passing_header(self, passing_result):
        summary = _build_commit_summary(passing_result)
        assert "✅" in summary
        assert "Commit Check" in summary

    def test_failing_header(self, failing_result):
        summary = _build_commit_summary(failing_result)
        assert "❌" in summary

    def test_commit_count_shown(self, passing_result):
        summary = _build_commit_summary(passing_result)
        assert "3" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_commit_summary(failing_result)
        assert "Errors" in summary
        assert "non-conventional" in summary

    def test_non_conventional_listed(self, failing_result):
        summary = _build_commit_summary(failing_result)
        assert "WIP stuff" in summary
        assert "added thing" in summary

    def test_warnings_listed_when_present(self):
        r = CommitResult(commit_count=1)
        r.warn("consider squashing")
        summary = _build_commit_summary(r)
        assert "Warnings" in summary
        assert "consider squashing" in summary


class TestReportCommitResult:
    def test_sets_passed_output(self, passing_result):
        with patch("src.commit_reporter.set_output") as mock_out, \
             patch("src.commit_reporter.write_summary"):
            report_commit_result(passing_result)
            mock_out.assert_any_call("commits_passed", "true")

    def test_sets_commit_count_output(self, passing_result):
        with patch("src.commit_reporter.set_output") as mock_out, \
             patch("src.commit_reporter.write_summary"):
            report_commit_result(passing_result)
            mock_out.assert_any_call("commit_count", "3")

    def test_sets_errors_output_when_failing(self, failing_result):
        with patch("src.commit_reporter.set_output") as mock_out, \
             patch("src.commit_reporter.write_summary"):
            report_commit_result(failing_result)
            keys = [c.args[0] for c in mock_out.call_args_list]
            assert "commit_errors" in keys

    def test_no_errors_output_when_passing(self, passing_result):
        with patch("src.commit_reporter.set_output") as mock_out, \
             patch("src.commit_reporter.write_summary"):
            report_commit_result(passing_result)
            keys = [c.args[0] for c in mock_out.call_args_list]
            assert "commit_errors" not in keys

    def test_writes_summary(self, passing_result):
        with patch("src.commit_reporter.set_output"), \
             patch("src.commit_reporter.write_summary") as mock_summary:
            report_commit_result(passing_result)
            mock_summary.assert_called_once()
