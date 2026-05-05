"""Tests for pr_reviewer_checker."""
import pytest

from src.pr_reviewer_checker import ReviewerResult, check_pr_reviewers


# ---------------------------------------------------------------------------
# ReviewerResult unit tests
# ---------------------------------------------------------------------------

class TestReviewerResult:
    def test_initial_state_is_passing(self):
        r = ReviewerResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.reviewers == []

    def test_fail_sets_passed_false(self):
        r = ReviewerResult()
        r.fail("no reviewer")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ReviewerResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ReviewerResult()
        r.warn("advisory")
        assert r.passed is True
        assert r.warnings == ["advisory"]

    def test_bool_true_when_passing(self):
        assert bool(ReviewerResult()) is True

    def test_bool_false_when_failed(self):
        r = ReviewerResult()
        r.fail("x")
        assert bool(r) is False


# ---------------------------------------------------------------------------
# check_pr_reviewers tests
# ---------------------------------------------------------------------------

def test_single_reviewer_passes():
    result = check_pr_reviewers(["alice"])
    assert result.passed is True
    assert result.reviewers == ["alice"]


def test_no_reviewer_fails_when_required():
    result = check_pr_reviewers([], require_reviewer=True)
    assert result.passed is False
    assert any("1 reviewer" in e for e in result.errors)


def test_no_reviewer_warns_when_not_required():
    result = check_pr_reviewers([], require_reviewer=False)
    assert result.passed is True
    assert result.warnings != []


def test_min_reviewers_two_with_one_fails():
    result = check_pr_reviewers(["alice"], min_reviewers=2)
    assert result.passed is False


def test_min_reviewers_two_with_two_passes():
    result = check_pr_reviewers(["alice", "bob"], min_reviewers=2)
    assert result.passed is True


def test_allowed_reviewers_all_valid():
    result = check_pr_reviewers(
        ["alice", "bob"], allowed_reviewers=["alice", "bob", "carol"]
    )
    assert result.passed is True


def test_allowed_reviewers_disallowed_fails():
    result = check_pr_reviewers(
        ["alice", "external"], allowed_reviewers=["alice", "bob"]
    )
    assert result.passed is False
    assert any("external" in e for e in result.errors)


def test_reviewers_stored_on_result():
    result = check_pr_reviewers(["alice", "bob"])
    assert result.reviewers == ["alice", "bob"]
