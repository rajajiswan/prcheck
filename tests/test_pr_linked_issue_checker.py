import pytest
from src.pr_linked_issue_checker import LinkedIssueResult, check_pr_linked_issue


class TestLinkedIssueResult:
    def test_initial_state_is_passing(self):
        r = LinkedIssueResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.issue_numbers == []

    def test_fail_sets_passed_false(self):
        r = LinkedIssueResult()
        r.fail("missing issue")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = LinkedIssueResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = LinkedIssueResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(LinkedIssueResult()) is True

    def test_bool_false_when_failed(self):
        r = LinkedIssueResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrLinkedIssue:
    def test_detects_closes_hash(self):
        result = check_pr_linked_issue("Closes #42")
        assert result.passed
        assert "42" in result.issue_numbers

    def test_detects_fixes_hash(self):
        result = check_pr_linked_issue("This PR fixes #101")
        assert result.passed
        assert "101" in result.issue_numbers

    def test_detects_resolves_hash(self):
        result = check_pr_linked_issue("Resolves #7")
        assert "7" in result.issue_numbers

    def test_detects_full_github_url(self):
        body = "Closes https://github.com/org/repo/issues/55"
        result = check_pr_linked_issue(body)
        assert "55" in result.issue_numbers

    def test_multiple_issues_detected(self):
        body = "Closes #1\nFixes #2"
        result = check_pr_linked_issue(body)
        assert "1" in result.issue_numbers
        assert "2" in result.issue_numbers

    def test_no_issue_warns_when_not_required(self):
        result = check_pr_linked_issue("Just some description")
        assert result.passed
        assert result.warnings

    def test_no_issue_fails_when_required(self):
        result = check_pr_linked_issue("No issue here", require_linked_issue=True)
        assert not result.passed
        assert result.errors

    def test_empty_body_warns_when_not_required(self):
        result = check_pr_linked_issue(None)
        assert result.passed
        assert result.warnings

    def test_empty_body_fails_when_required(self):
        result = check_pr_linked_issue("", require_linked_issue=True)
        assert not result.passed

    def test_allowed_prefixes_pass(self):
        result = check_pr_linked_issue(
            "Closes #123", allowed_issue_prefixes=["12"]
        )
        assert result.passed

    def test_disallowed_prefix_fails(self):
        result = check_pr_linked_issue(
            "Closes #999", allowed_issue_prefixes=["1", "2"]
        )
        assert not result.passed
        assert any("999" in e for e in result.errors)
