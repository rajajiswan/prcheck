import pytest
from src.pr_base_branch_checker import BaseBranchResult, check_pr_base_branch


class TestBaseBranchResult:
    def test_initial_state_is_passing(self):
        result = BaseBranchResult()
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []

    def test_fail_sets_passed_false(self):
        result = BaseBranchResult()
        result.fail("bad branch")
        assert result.passed is False

    def test_fail_appends_error(self):
        result = BaseBranchResult()
        result.fail("error one")
        result.fail("error two")
        assert len(result.errors) == 2
        assert "error one" in result.errors

    def test_warn_does_not_change_passed(self):
        result = BaseBranchResult()
        result.warn("heads up")
        assert result.passed is True
        assert "heads up" in result.warnings

    def test_bool_true_when_passing(self):
        result = BaseBranchResult()
        assert bool(result) is True

    def test_bool_false_when_failed(self):
        result = BaseBranchResult()
        result.fail("oops")
        assert bool(result) is False


class TestCheckPrBaseBranch:
    def test_allowed_exact_match_passes(self):
        result = check_pr_base_branch("main", ["main", "develop"])
        assert result.passed is True
        assert result.errors == []

    def test_disallowed_branch_fails(self):
        result = check_pr_base_branch("random-branch", ["main", "develop"])
        assert result.passed is False
        assert any("random-branch" in e for e in result.errors)

    def test_disallowed_branch_warn_only(self):
        result = check_pr_base_branch(
            "random-branch", ["main"], warn_only=True
        )
        assert result.passed is True
        assert any("random-branch" in w for w in result.warnings)

    def test_glob_prefix_match_passes(self):
        result = check_pr_base_branch("release/1.2", ["release/*", "main"])
        assert result.passed is True

    def test_glob_prefix_no_match_fails(self):
        result = check_pr_base_branch("hotfix/urgent", ["release/*", "main"])
        assert result.passed is False

    def test_result_stores_base_branch(self):
        result = check_pr_base_branch("main", ["main"])
        assert result.base_branch == "main"

    def test_result_stores_expected_branches(self):
        allowed = ["main", "develop"]
        result = check_pr_base_branch("main", allowed)
        assert result.expected_branches == allowed

    def test_protected_base_emits_warning_for_unusual_source(self):
        result = check_pr_base_branch(
            "main",
            ["main", "develop"],
            protected_bases=["main"],
            source_branch="feature/my-thing",
        )
        assert result.passed is True
        assert any("protected" in w for w in result.warnings)

    def test_no_warning_when_no_protected_bases(self):
        result = check_pr_base_branch(
            "main",
            ["main"],
            source_branch="feature/my-thing",
        )
        assert result.warnings == []

    def test_multiple_allowed_bases(self):
        for branch in ["main", "develop", "release/2.0"]:
            result = check_pr_base_branch(
                branch, ["main", "develop", "release/*"]
            )
            assert result.passed is True, f"Expected {branch} to pass"
