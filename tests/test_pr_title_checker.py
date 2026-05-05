"""Tests for src/pr_title_checker.py"""
import pytest

from src.branch_parser import BranchInfo
from src.pr_title_checker import TitleResult, check_pr_title


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def feature_branch() -> BranchInfo:
    return BranchInfo(type="feature", ticket="PROJ-1", description="my-feature", raw="feature/PROJ-1-my-feature")


# ---------------------------------------------------------------------------
# TitleResult unit tests
# ---------------------------------------------------------------------------

class TestTitleResult:
    def test_initial_state_is_passing(self):
        r = TitleResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = TitleResult()
        r.fail("oops")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = TitleResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = TitleResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(TitleResult()) is True

    def test_bool_false_when_failed(self):
        r = TitleResult()
        r.fail("bad")
        assert bool(r) is False


# ---------------------------------------------------------------------------
# check_pr_title tests
# ---------------------------------------------------------------------------

class TestCheckPrTitle:
    def test_valid_title_passes(self, feature_branch):
        result = check_pr_title("Add login endpoint", feature_branch)
        assert result.passed is True
        assert result.errors == []

    def test_empty_title_fails(self, feature_branch):
        result = check_pr_title("", feature_branch)
        assert result.passed is False
        assert any("empty" in e for e in result.errors)

    def test_title_too_short_fails(self, feature_branch):
        result = check_pr_title("Fix", feature_branch, min_length=10)
        assert result.passed is False
        assert any("too short" in e for e in result.errors)

    def test_title_too_long_fails(self, feature_branch):
        long_title = "A" * 80
        result = check_pr_title(long_title, feature_branch, max_length=72)
        assert result.passed is False
        assert any("too long" in e for e in result.errors)

    def test_require_prefix_passes_when_present(self, feature_branch):
        result = check_pr_title(
            "feat: add login endpoint",
            feature_branch,
            require_prefix=True,
            allowed_prefixes=["feat:", "fix:"],
        )
        assert result.passed is True

    def test_require_prefix_fails_when_missing(self, feature_branch):
        result = check_pr_title(
            "add login endpoint",
            feature_branch,
            require_prefix=True,
            allowed_prefixes=["feat:", "fix:"],
        )
        assert result.passed is False
        assert any("must begin with" in e for e in result.errors)

    def test_forbidden_pattern_fails(self, feature_branch):
        result = check_pr_title(
            "WIP: add login endpoint",
            feature_branch,
            forbidden_patterns=[r"^WIP"],
        )
        assert result.passed is False
        assert any("forbidden pattern" in e for e in result.errors)

    def test_trailing_period_warns(self, feature_branch):
        result = check_pr_title("Add login endpoint.", feature_branch)
        assert result.passed is True
        assert any("period" in w for w in result.warnings)

    def test_all_caps_warns(self, feature_branch):
        result = check_pr_title("ADD LOGIN ENDPOINT", feature_branch)
        assert result.passed is True
        assert any("ALL CAPS" in w for w in result.warnings)

    def test_title_stored_on_result(self, feature_branch):
        result = check_pr_title("Add login endpoint", feature_branch)
        assert result.title == "Add login endpoint"
