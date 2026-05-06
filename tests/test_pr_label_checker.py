"""Unit tests for src/pr_label_checker.py."""
import pytest

from src.pr_label_checker import LabelCheckResult, check_pr_labels


class TestLabelCheckResult:
    def test_initial_state_is_passing(self):
        r = LabelCheckResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.applied_labels == []

    def test_fail_sets_passed_false(self):
        r = LabelCheckResult()
        r.fail("bad label")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = LabelCheckResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = LabelCheckResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(LabelCheckResult()) is True

    def test_bool_false_when_failing(self):
        r = LabelCheckResult()
        r.fail("oops")
        assert bool(r) is False


class TestCheckPrLabels:
    def test_empty_labels_warns(self):
        result = check_pr_labels([])
        assert result.passed is True
        assert any("no labels" in w for w in result.warnings)

    def test_min_labels_not_met_fails(self):
        result = check_pr_labels(["bug"], min_labels=2)
        assert result.passed is False
        assert any("at least 2" in e for e in result.errors)

    def test_min_labels_met_passes(self):
        result = check_pr_labels(["bug", "enhancement"], min_labels=2)
        assert result.passed is True

    def test_disallowed_label_fails(self):
        result = check_pr_labels(
            ["bug", "wip"],
            allowed_labels=["bug", "enhancement"],
        )
        assert result.passed is False
        assert any("wip" in e for e in result.errors)

    def test_all_allowed_labels_passes(self):
        result = check_pr_labels(
            ["bug"],
            allowed_labels=["bug", "enhancement"],
        )
        assert result.passed is True

    def test_missing_required_label_fails(self):
        result = check_pr_labels(
            ["enhancement"],
            required_labels=["bug"],
        )
        assert result.passed is False
        assert any("bug" in e for e in result.errors)

    def test_required_label_present_passes(self):
        result = check_pr_labels(
            ["bug", "enhancement"],
            required_labels=["bug"],
        )
        assert result.passed is True

    def test_applied_labels_stored(self):
        result = check_pr_labels(["bug", "enhancement"])
        assert result.applied_labels == ["bug", "enhancement"]

    def test_combined_failures_accumulate(self):
        result = check_pr_labels(
            ["wip"],
            allowed_labels=["bug"],
            required_labels=["bug"],
            min_labels=2,
        )
        assert result.passed is False
        assert len(result.errors) == 3
