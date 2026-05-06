"""Integration tests: commit checker + reporter wired together."""
from unittest.mock import patch
from src.pr_commit_checker import check_pr_commits
from src.commit_reporter import report_commit_result


def test_full_pass_pipeline():
    commits = [
        "feat(ui): add dark mode toggle",
        "fix(auth): handle token expiry",
    ]
    result = check_pr_commits(commits, require_conventional=True, max_commits=10)
    assert result.passed is True
    assert result.commit_count == 2

    with patch("src.commit_reporter.set_output") as mock_out, \
         patch("src.commit_reporter.write_summary"):
        report_commit_result(result)
        keys = [c.args[0] for c in mock_out.call_args_list]
        assert "commits_passed" in keys
        assert "commit_errors" not in keys


def test_non_conventional_fails_pipeline():
    commits = ["WIP: half done", "feat: proper commit"]
    result = check_pr_commits(commits, require_conventional=True)
    assert result.passed is False
    assert "WIP: half done" in result.non_conventional_commits

    with patch("src.commit_reporter.set_output") as mock_out, \
         patch("src.commit_reporter.write_summary"):
        report_commit_result(result)
        keys = [c.args[0] for c in mock_out.call_args_list]
        assert "commit_errors" in keys


def test_too_many_commits_fails_pipeline():
    commits = [f"fix: patch {i}" for i in range(8)]
    result = check_pr_commits(commits, max_commits=5)
    assert result.passed is False
    assert result.commit_count == 8

    with patch("src.commit_reporter.set_output") as mock_out, \
         patch("src.commit_reporter.write_summary"):
        report_commit_result(result)
        vals = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
        assert vals["commits_passed"] == "false"
        assert vals["commit_count"] == "8"
