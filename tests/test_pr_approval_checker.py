import pytest
from src.pr_approval_checker import ApprovalResult, check_pr_approvals


def _make_review(login: str, state: str, teams: list = None) -> dict:
    return {
        "user": {"login": login, "teams": teams or []},
        "state": state,
    }


class TestApprovalResult:
    def test_initial_state_is_passing(self):
        r = ApprovalResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.approval_count == 0
        assert r.approved_by == []

    def test_fail_sets_passed_false(self):
        r = ApprovalResult()
        r.fail("not enough approvals")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ApprovalResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = ApprovalResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = ApprovalResult()
        assert bool(r) is True

    def test_bool_false_when_failing(self):
        r = ApprovalResult()
        r.fail("oops")
        assert bool(r) is False


class TestCheckPrApprovals:
    def test_single_approval_passes(self):
        reviews = [_make_review("alice", "APPROVED")]
        result = check_pr_approvals(reviews, required_approvals=1)
        assert result.passed is True
        assert result.approval_count == 1
        assert "alice" in result.approved_by

    def test_no_approvals_fails(self):
        result = check_pr_approvals([], required_approvals=1)
        assert result.passed is False
        assert result.approval_count == 0

    def test_insufficient_approvals_fails(self):
        reviews = [_make_review("alice", "APPROVED")]
        result = check_pr_approvals(reviews, required_approvals=2)
        assert result.passed is False
        assert "2 approval(s)" in result.errors[0]

    def test_multiple_approvals_pass(self):
        reviews = [
            _make_review("alice", "APPROVED"),
            _make_review("bob", "APPROVED"),
        ]
        result = check_pr_approvals(reviews, required_approvals=2)
        assert result.passed is True
        assert result.approval_count == 2

    def test_changes_requested_not_counted(self):
        reviews = [_make_review("alice", "CHANGES_REQUESTED")]
        result = check_pr_approvals(reviews, required_approvals=1)
        assert result.passed is False
        assert result.approval_count == 0

    def test_dismiss_stale_uses_latest_state(self):
        reviews = [
            _make_review("alice", "APPROVED"),
            _make_review("alice", "CHANGES_REQUESTED"),
        ]
        result = check_pr_approvals(reviews, required_approvals=1, dismiss_stale=True)
        assert result.passed is False

    def test_team_filter_excludes_non_members(self):
        reviews = [_make_review("alice", "APPROVED", teams=["other-team"])]
        result = check_pr_approvals(
            reviews, required_approvals=1, require_team="core-team"
        )
        assert result.passed is False

    def test_team_filter_includes_members(self):
        reviews = [_make_review("alice", "APPROVED", teams=["core-team"])]
        result = check_pr_approvals(
            reviews, required_approvals=1, require_team="core-team"
        )
        assert result.passed is True
        assert "alice" in result.approved_by

    def test_duplicate_reviewer_counted_once(self):
        reviews = [
            _make_review("alice", "APPROVED"),
            _make_review("alice", "APPROVED"),
        ]
        result = check_pr_approvals(reviews, required_approvals=2)
        assert result.approval_count == 1
        assert result.passed is False
