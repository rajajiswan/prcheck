import pytest
from src.pr_squash_checker import SquashResult, check_pr_squash


def _commits(n: int) -> list:
    return [{"sha": f"abc{i:03d}"} for i in range(n)]


class TestSquashResult:
    def test_initial_state_is_passing(self):
        r = SquashResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.commit_count == 0
        assert r.squash_recommended is False

    def test_fail_sets_passed_false(self):
        r = SquashResult()
        r.fail("too many commits")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = SquashResult()
        r.fail("msg1")
        r.fail("msg2")
        assert r.errors == ["msg1", "msg2"]

    def test_warn_does_not_change_passed(self):
        r = SquashResult()
        r.warn("please squash")
        assert r.passed is True
        assert r.warnings == ["please squash"]

    def test_bool_true_when_passing(self):
        assert bool(SquashResult()) is True

    def test_bool_false_when_failed(self):
        r = SquashResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrSquash:
    def test_under_threshold_passes(self):
        result = check_pr_squash(_commits(5), max_commits_before_squash=10)
        assert result.passed is True
        assert result.squash_recommended is False

    def test_exactly_at_threshold_passes(self):
        result = check_pr_squash(_commits(10), max_commits_before_squash=10)
        assert result.passed is True

    def test_over_threshold_fails(self):
        result = check_pr_squash(_commits(11), max_commits_before_squash=10)
        assert result.passed is False
        assert result.squash_recommended is True
        assert len(result.errors) == 1
        assert "11 commits" in result.errors[0]

    def test_over_threshold_warn_only(self):
        result = check_pr_squash(
            _commits(15), max_commits_before_squash=10, warn_only=True
        )
        assert result.passed is True
        assert result.squash_recommended is True
        assert len(result.warnings) == 1

    def test_label_requires_squash_fails(self):
        result = check_pr_squash(
            _commits(2),
            max_commits_before_squash=10,
            require_squash_for_labels=["needs-squash"],
            pr_labels=["needs-squash", "bug"],
        )
        assert result.passed is False
        assert result.squash_recommended is True
        assert "needs-squash" in result.errors[0]

    def test_label_not_present_passes(self):
        result = check_pr_squash(
            _commits(2),
            max_commits_before_squash=10,
            require_squash_for_labels=["needs-squash"],
            pr_labels=["bug"],
        )
        assert result.passed is True

    def test_both_threshold_and_label_single_error(self):
        result = check_pr_squash(
            _commits(12),
            max_commits_before_squash=10,
            require_squash_for_labels=["squash-me"],
            pr_labels=["squash-me"],
        )
        assert result.passed is False
        assert len(result.errors) == 1
        assert "12 commits" in result.errors[0]
        assert "squash-me" in result.errors[0]

    def test_commit_count_stored(self):
        result = check_pr_squash(_commits(7), max_commits_before_squash=10)
        assert result.commit_count == 7

    def test_empty_commits_passes(self):
        result = check_pr_squash([], max_commits_before_squash=10)
        assert result.passed is True
        assert result.commit_count == 0
