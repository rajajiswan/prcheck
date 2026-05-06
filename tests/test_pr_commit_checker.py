import pytest
from src.pr_commit_checker import CommitResult, check_pr_commits


class TestCommitResult:
    def test_initial_state_is_passing(self):
        r = CommitResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.commit_count == 0
        assert r.non_conventional_commits == []

    def test_fail_sets_passed_false(self):
        r = CommitResult()
        r.fail("too many commits")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = CommitResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = CommitResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(CommitResult()) is True

    def test_bool_false_when_failed(self):
        r = CommitResult()
        r.fail("bad")
        assert bool(r) is False


class TestCheckPrCommits:
    def test_single_valid_commit_passes(self):
        result = check_pr_commits(["feat: add login page"])
        assert result.passed is True
        assert result.commit_count == 1

    def test_empty_commits_fails_min_check(self):
        result = check_pr_commits([], min_commits=1)
        assert result.passed is False
        assert any("at least 1" in e for e in result.errors)

    def test_exceeds_max_commits_fails(self):
        commits = [f"fix: patch {i}" for i in range(6)]
        result = check_pr_commits(commits, max_commits=5)
        assert result.passed is False
        assert any("exceeds" in e for e in result.errors)

    def test_conventional_commit_passes(self):
        result = check_pr_commits(
            ["feat(auth): add OAuth2 support"], require_conventional=True
        )
        assert result.passed is True
        assert result.non_conventional_commits == []

    def test_non_conventional_commit_fails(self):
        result = check_pr_commits(
            ["Added login button"], require_conventional=True
        )
        assert result.passed is False
        assert "Added login button" in result.non_conventional_commits

    def test_mixed_commits_collects_all_bad(self):
        commits = ["feat: good", "WIP stuff", "also bad"]
        result = check_pr_commits(commits, require_conventional=True)
        assert result.passed is False
        assert len(result.non_conventional_commits) == 2

    def test_breaking_change_conventional_passes(self):
        result = check_pr_commits(
            ["feat(api)!: remove deprecated endpoint"], require_conventional=True
        )
        assert result.passed is True

    def test_no_max_allows_many_commits(self):
        commits = [f"fix: patch {i}" for i in range(50)]
        result = check_pr_commits(commits, max_commits=None)
        assert result.passed is True

    def test_multiline_commit_uses_subject_only(self):
        msg = "feat: short subject\n\nLonger body paragraph."
        result = check_pr_commits([msg], require_conventional=True)
        assert result.passed is True
