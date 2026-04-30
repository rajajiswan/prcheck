import pytest
from src.pr_milestone_checker import MilestoneResult, check_pr_milestone


class TestMilestoneResult:
    def test_initial_state_is_passing(self):
        r = MilestoneResult()
        assert r.passed is True
        assert r.error is None
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = MilestoneResult()
        r.fail("no milestone")
        assert r.passed is False

    def test_fail_stores_error_message(self):
        r = MilestoneResult()
        r.fail("missing")
        assert r.error == "missing"

    def test_warn_appends_warning(self):
        r = MilestoneResult()
        r.warn("optional")
        assert "optional" in r.warnings

    def test_bool_true_when_passing(self):
        assert bool(MilestoneResult()) is True

    def test_bool_false_when_failed(self):
        r = MilestoneResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrMilestone:
    def test_no_milestone_not_required_passes_with_warning(self):
        result = check_pr_milestone(None, require_milestone=False)
        assert result.passed is True
        assert any("not required" in w for w in result.warnings)

    def test_milestone_set_not_required_passes(self):
        result = check_pr_milestone("v1.0", require_milestone=False)
        assert result.passed is True
        assert result.warnings == []

    def test_no_milestone_required_fails(self):
        result = check_pr_milestone(None, require_milestone=True)
        assert result.passed is False
        assert "must have a milestone" in result.error

    def test_milestone_required_and_set_passes(self):
        result = check_pr_milestone("v2.0", require_milestone=True)
        assert result.passed is True
        assert result.milestone == "v2.0"

    def test_milestone_not_in_allowed_list_fails(self):
        result = check_pr_milestone(
            "v99", require_milestone=True, allowed_milestones=["v1.0", "v2.0"]
        )
        assert result.passed is False
        assert "v99" in result.error

    def test_milestone_in_allowed_list_passes(self):
        result = check_pr_milestone(
            "v1.0", require_milestone=True, allowed_milestones=["v1.0", "v2.0"]
        )
        assert result.passed is True

    def test_allowed_milestones_none_skips_list_check(self):
        result = check_pr_milestone(
            "any-value", require_milestone=True, allowed_milestones=None
        )
        assert result.passed is True
