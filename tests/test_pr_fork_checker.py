import pytest
from src.pr_fork_checker import ForkResult, check_pr_fork

BASE_REPO = "org/repo"
FORK_REPO = "contributor/repo"


class TestForkResult:
    def test_initial_state_is_passing(self):
        r = ForkResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.is_fork is False
        assert r.fork_owner is None

    def test_fail_sets_passed_false(self):
        r = ForkResult()
        r.fail("not allowed")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ForkResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ForkResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(ForkResult()) is True

    def test_bool_false_when_failed(self):
        r = ForkResult()
        r.fail("bad")
        assert bool(r) is False


class TestCheckPrFork:
    def test_same_repo_is_not_fork(self):
        result = check_pr_fork(BASE_REPO, BASE_REPO)
        assert result.passed is True
        assert result.is_fork is False
        assert result.fork_owner is None

    def test_different_repo_is_fork(self):
        result = check_pr_fork(FORK_REPO, BASE_REPO)
        assert result.is_fork is True
        assert result.fork_owner == "contributor"

    def test_fork_allowed_by_default_passes(self):
        result = check_pr_fork(FORK_REPO, BASE_REPO)
        assert result.passed is True
        assert result.errors == []

    def test_fork_disallowed_fails(self):
        result = check_pr_fork(FORK_REPO, BASE_REPO, allow_forks=False)
        assert result.passed is False
        assert any("not allowed" in e for e in result.errors)

    def test_blocked_fork_owner_fails(self):
        result = check_pr_fork(
            FORK_REPO, BASE_REPO, blocked_fork_owners=["contributor"]
        )
        assert result.passed is False
        assert any("contributor" in e for e in result.errors)

    def test_non_blocked_owner_passes(self):
        result = check_pr_fork(
            FORK_REPO, BASE_REPO, blocked_fork_owners=["otherperson"]
        )
        assert result.passed is True

    def test_require_signed_commits_adds_warning(self):
        result = check_pr_fork(
            FORK_REPO, BASE_REPO, require_signed_commits=True
        )
        assert result.passed is True
        assert any("signed" in w for w in result.warnings)

    def test_warn_on_fork_adds_warning(self):
        result = check_pr_fork(FORK_REPO, BASE_REPO, warn_on_fork=True)
        assert result.passed is True
        assert any("fork" in w.lower() for w in result.warnings)

    def test_missing_repo_info_fails(self):
        result = check_pr_fork(None, BASE_REPO)
        assert result.passed is False
        assert any("repository information" in e for e in result.errors)

    def test_both_none_fails(self):
        result = check_pr_fork(None, None)
        assert result.passed is False

    def test_blocked_owner_takes_priority_over_warn_on_fork(self):
        result = check_pr_fork(
            FORK_REPO,
            BASE_REPO,
            blocked_fork_owners=["contributor"],
            warn_on_fork=True,
        )
        assert result.passed is False
        assert result.warnings == []
