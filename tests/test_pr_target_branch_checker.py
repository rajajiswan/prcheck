import pytest
from src.pr_target_branch_checker import TargetBranchResult, check_pr_target_branch


class TestTargetBranchResult:
    def test_initial_state_is_passing(self):
        result = TargetBranchResult()
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []
        assert result.target_branch is None

    def test_fail_sets_passed_false(self):
        result = TargetBranchResult()
        result.fail("not allowed")
        assert result.passed is False

    def test_fail_appends_error(self):
        result = TargetBranchResult()
        result.fail("bad target")
        assert "bad target" in result.errors

    def test_warn_does_not_change_passed(self):
        result = TargetBranchResult()
        result.warn("consider main instead")
        assert result.passed is True
        assert "consider main instead" in result.warnings

    def test_bool_true_when_passing(self):
        result = TargetBranchResult()
        assert bool(result) is True

    def test_bool_false_when_failed(self):
        result = TargetBranchResult()
        result.fail("nope")
        assert bool(result) is False


class TestCheckPrTargetBranch:
    def test_empty_target_fails(self):
        result = check_pr_target_branch(target_branch="")
        assert not result
        assert any("empty" in e for e in result.errors)

    def test_allowed_target_passes(self):
        result = check_pr_target_branch(
            target_branch="main",
            allowed_targets=["main", "develop"],
        )
        assert result.passed is True
        assert result.errors == []

    def test_disallowed_target_in_allowed_list_fails(self):
        result = check_pr_target_branch(
            target_branch="staging",
            allowed_targets=["main", "develop"],
        )
        assert not result
        assert any("staging" in e for e in result.errors)

    def test_explicit_disallowed_target_fails(self):
        result = check_pr_target_branch(
            target_branch="production",
            disallowed_targets=["production"],
        )
        assert not result
        assert any("production" in e for e in result.errors)

    def test_target_not_in_disallowed_passes(self):
        result = check_pr_target_branch(
            target_branch="develop",
            disallowed_targets=["production"],
        )
        assert result.passed is True

    def test_required_for_type_matches_passes(self):
        result = check_pr_target_branch(
            target_branch="main",
            required_for_types={"hotfix": "main"},
            branch_type="hotfix",
        )
        assert result.passed is True

    def test_required_for_type_mismatch_fails(self):
        result = check_pr_target_branch(
            target_branch="develop",
            required_for_types={"hotfix": "main"},
            branch_type="hotfix",
        )
        assert not result
        assert any("hotfix" in e and "main" in e for e in result.errors)

    def test_required_for_type_ignored_when_no_branch_type(self):
        result = check_pr_target_branch(
            target_branch="develop",
            required_for_types={"hotfix": "main"},
            branch_type=None,
        )
        assert result.passed is True

    def test_multiple_violations_accumulate(self):
        result = check_pr_target_branch(
            target_branch="production",
            allowed_targets=["main"],
            disallowed_targets=["production"],
        )
        assert not result
        assert len(result.errors) == 2
