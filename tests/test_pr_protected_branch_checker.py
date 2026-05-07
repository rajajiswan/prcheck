import pytest
from src.pr_protected_branch_checker import ProtectedBranchResult, check_pr_protected_branch


class TestProtectedBranchResult:
    def test_initial_state_is_passing(self):
        r = ProtectedBranchResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = ProtectedBranchResult()
        r.fail("blocked")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ProtectedBranchResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ProtectedBranchResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = ProtectedBranchResult()
        assert bool(r) is True

    def test_bool_false_when_failing(self):
        r = ProtectedBranchResult()
        r.fail("oops")
        assert bool(r) is False


class TestCheckPrProtectedBranch:
    def test_no_protected_branches_warns(self):
        result = check_pr_protected_branch("main", [])
        assert result.passed is True
        assert any("No protected branches" in w for w in result.warnings)

    def test_unprotected_target_warns(self):
        result = check_pr_protected_branch("feature/x", ["main", "develop"])
        assert result.passed is True
        assert result.is_protected is False
        assert any("not in the protected" in w for w in result.warnings)

    def test_protected_target_clean_state_passes(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state="clean"
        )
        assert result.passed is True
        assert result.is_protected is True
        assert result.errors == []

    def test_blocked_state_fails(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state="blocked"
        )
        assert result.passed is False
        assert any("blocked" in e for e in result.errors)

    def test_dirty_state_fails(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state="dirty"
        )
        assert result.passed is False

    def test_custom_blocked_states(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state="unstable",
            blocked_states=["unstable"]
        )
        assert result.passed is False

    def test_behind_fails_when_require_up_to_date(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state="behind",
            require_up_to_date=True
        )
        assert result.passed is False
        assert any("up to date" in e for e in result.errors)

    def test_behind_passes_without_require_up_to_date(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state="behind",
            require_up_to_date=False
        )
        assert result.passed is True

    def test_none_mergeable_state_skips_state_check(self):
        result = check_pr_protected_branch(
            "main", ["main"], mergeable_state=None
        )
        assert result.passed is True
        assert result.errors == []
