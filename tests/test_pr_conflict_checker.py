import pytest

from src.pr_conflict_checker import ConflictResult, check_pr_conflicts


class TestConflictResult:
    def test_initial_state_is_passing(self):
        result = ConflictResult()
        assert result.passed is True
        assert result.error is None
        assert result.warnings == []

    def test_fail_sets_passed_false(self):
        result = ConflictResult()
        result.fail("conflict detected")
        assert result.passed is False

    def test_fail_stores_error_message(self):
        result = ConflictResult()
        result.fail("conflict detected")
        assert result.error == "conflict detected"

    def test_warn_does_not_change_passed(self):
        result = ConflictResult()
        result.warn("something is off")
        assert result.passed is True

    def test_warn_appends_warning(self):
        result = ConflictResult()
        result.warn("first")
        result.warn("second")
        assert result.warnings == ["first", "second"]

    def test_bool_true_when_passing(self):
        assert bool(ConflictResult()) is True

    def test_bool_false_when_failed(self):
        result = ConflictResult()
        result.fail("oops")
        assert bool(result) is False


class TestCheckPrConflicts:
    def test_clean_pr_passes(self):
        result = check_pr_conflicts(mergeable=True, mergeable_state="clean")
        assert result.passed is True
        assert result.error is None
        assert result.warnings == []

    def test_dirty_pr_fails_by_default(self):
        result = check_pr_conflicts(mergeable=False, mergeable_state="dirty")
        assert result.passed is False
        assert result.error is not None
        assert "conflict" in result.error.lower()

    def test_dirty_pr_warns_when_not_required(self):
        result = check_pr_conflicts(
            mergeable=False,
            mergeable_state="dirty",
            require_no_conflicts=False,
        )
        assert result.passed is True
        assert len(result.warnings) == 1
        assert "conflict" in result.warnings[0].lower()

    def test_unknown_mergeability_warns(self):
        result = check_pr_conflicts(mergeable=None, mergeable_state="unknown")
        assert result.passed is True
        assert len(result.warnings) == 1
        assert "not yet determined" in result.warnings[0]

    def test_none_mergeable_state_warns(self):
        result = check_pr_conflicts(mergeable=None, mergeable_state=None)
        assert result.passed is True
        assert result.warnings

    def test_blocked_state_warns(self):
        result = check_pr_conflicts(mergeable=True, mergeable_state="blocked")
        assert result.passed is True
        assert any("blocked" in w.lower() for w in result.warnings)

    def test_mergeable_false_without_dirty_state_fails(self):
        result = check_pr_conflicts(mergeable=False, mergeable_state="clean")
        assert result.passed is False

    def test_require_no_conflicts_false_blocked_only_warns(self):
        result = check_pr_conflicts(
            mergeable=True,
            mergeable_state="blocked",
            require_no_conflicts=False,
        )
        assert result.passed is True
        assert result.warnings
