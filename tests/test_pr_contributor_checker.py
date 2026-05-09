import pytest
from src.pr_contributor_checker import ContributorResult, check_pr_contributor


class TestContributorResult:
    def test_initial_state_is_passing(self):
        r = ContributorResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.author is None
        assert r.is_first_time is False

    def test_fail_sets_passed_false(self):
        r = ContributorResult()
        r.fail("blocked")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ContributorResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ContributorResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = ContributorResult()
        assert bool(r) is True

    def test_bool_false_after_fail(self):
        r = ContributorResult()
        r.fail("nope")
        assert bool(r) is False


COLLABS = ["alice", "bob"]
ORG = ["alice", "carol"]


def test_missing_author_fails():
    result = check_pr_contributor(None, COLLABS, ORG)
    assert not result
    assert any("missing" in e for e in result.errors)


def test_blocked_user_fails():
    result = check_pr_contributor("mallory", COLLABS, ORG, blocked_users=["mallory"])
    assert not result
    assert any("blocked" in e for e in result.errors)


def test_require_org_member_passes_for_member():
    result = check_pr_contributor("carol", COLLABS, ORG, require_org_member=True)
    assert result.passed


def test_require_org_member_fails_for_non_member():
    result = check_pr_contributor("dave", COLLABS, ORG, require_org_member=True)
    assert not result
    assert any("organisation" in e for e in result.errors)


def test_require_collaborator_passes():
    result = check_pr_contributor("bob", COLLABS, ORG, require_collaborator=True)
    assert result.passed


def test_require_collaborator_fails():
    result = check_pr_contributor("dave", COLLABS, ORG, require_collaborator=True)
    assert not result
    assert any("collaborator" in e for e in result.errors)


def test_first_time_contributor_warns():
    result = check_pr_contributor("newbie", COLLABS, ORG, warn_first_time=True)
    assert result.passed
    assert result.is_first_time is True
    assert result.warnings


def test_no_warn_when_flag_off():
    result = check_pr_contributor("newbie", COLLABS, ORG, warn_first_time=False)
    assert result.passed
    assert result.warnings == []


def test_known_collab_not_first_time():
    result = check_pr_contributor("alice", COLLABS, ORG, warn_first_time=True)
    assert result.is_first_time is False
    assert result.warnings == []
