import pytest
from src.pr_assignee_checker import AssigneeResult, check_pr_assignees


class TestAssigneeResult:
    def test_initial_state_is_passing(self):
        result = AssigneeResult()
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []
        assert result.assignees == []

    def test_fail_sets_passed_false(self):
        result = AssigneeResult()
        result.fail("No assignee.")
        assert result.passed is False

    def test_fail_appends_error(self):
        result = AssigneeResult()
        result.fail("Error one")
        result.fail("Error two")
        assert result.errors == ["Error one", "Error two"]

    def test_warn_does_not_change_passed(self):
        result = AssigneeResult()
        result.warn("Consider assigning.")
        assert result.passed is True
        assert result.warnings == ["Consider assigning."]

    def test_bool_true_when_passing(self):
        result = AssigneeResult()
        assert bool(result) is True

    def test_bool_false_when_failed(self):
        result = AssigneeResult()
        result.fail("oops")
        assert bool(result) is False


class TestCheckPrAssignees:
    def test_passes_with_valid_assignee(self):
        result = check_pr_assignees(["alice"])
        assert result.passed is True
        assert result.assignees == ["alice"]

    def test_fails_when_no_assignee_required(self):
        result = check_pr_assignees([], require_assignee=True)
        assert result.passed is False
        assert any("at least one assignee" in e for e in result.errors)

    def test_warns_when_no_assignee_not_required(self):
        result = check_pr_assignees([], require_assignee=False)
        assert result.passed is True
        assert any("no assignees" in w.lower() for w in result.warnings)

    def test_fails_disallowed_assignee(self):
        result = check_pr_assignees(
            ["mallory"], allowed_assignees=["alice", "bob"]
        )
        assert result.passed is False
        assert any("mallory" in e for e in result.errors)

    def test_passes_allowed_assignee(self):
        result = check_pr_assignees(
            ["alice"], allowed_assignees=["alice", "bob"]
        )
        assert result.passed is True

    def test_fails_exceeds_max_assignees(self):
        result = check_pr_assignees(["alice", "bob", "carol"], max_assignees=2)
        assert result.passed is False
        assert any("maximum" in e for e in result.errors)

    def test_passes_within_max_assignees(self):
        result = check_pr_assignees(["alice", "bob"], max_assignees=2)
        assert result.passed is True

    def test_multiple_errors_accumulate(self):
        result = check_pr_assignees(
            ["mallory", "eve"],
            allowed_assignees=["alice"],
            max_assignees=1,
        )
        assert result.passed is False
        assert len(result.errors) >= 2
