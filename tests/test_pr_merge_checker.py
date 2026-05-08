import pytest

from src.pr_merge_checker import MergeResult, check_pr_mergeability


# ---------------------------------------------------------------------------
# MergeResult unit tests
# ---------------------------------------------------------------------------

class TestMergeResult:
    def test_initial_state_is_passing(self):
        r = MergeResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.mergeable_state is None

    def test_fail_sets_passed_false(self):
        r = MergeResult()
        r.fail("conflict detected")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = MergeResult()
        r.fail("conflict detected")
        assert "conflict detected" in r.errors

    def test_warn_does_not_change_passed(self):
        r = MergeResult()
        r.warn("unstable checks")
        assert r.passed is True
        assert "unstable checks" in r.warnings

    def test_bool_true_when_passing(self):
        assert bool(MergeResult()) is True

    def test_bool_false_after_fail(self):
        r = MergeResult()
        r.fail("oops")
        assert bool(r) is False


# ---------------------------------------------------------------------------
# check_pr_mergeability integration tests
# ---------------------------------------------------------------------------

def test_clean_state_passes():
    result = check_pr_mergeability(mergeable=True, mergeable_state="clean")
    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []
    assert result.mergeable_state == "clean"


def test_not_mergeable_fails():
    result = check_pr_mergeability(mergeable=False, mergeable_state="dirty")
    assert result.passed is False
    assert any("not mergeable" in e for e in result.errors)


def test_dirty_state_fails_via_blocked_states():
    # mergeable=True but state is dirty — blocked by default list
    result = check_pr_mergeability(mergeable=True, mergeable_state="dirty")
    assert result.passed is False
    assert any("dirty" in e for e in result.errors)


def test_blocked_state_fails():
    result = check_pr_mergeability(mergeable=True, mergeable_state="blocked")
    assert result.passed is False


def test_custom_blocked_states():
    result = check_pr_mergeability(
        mergeable=True,
        mergeable_state="unstable",
        blocked_states=["unstable"],
    )
    assert result.passed is False
    assert any("unstable" in e for e in result.errors)


def test_unstable_warns_by_default():
    result = check_pr_mergeability(mergeable=True, mergeable_state="unstable")
    assert result.passed is True
    assert any("unstable" in w for w in result.warnings)


def test_none_mergeable_warns_by_default():
    result = check_pr_mergeability(mergeable=None, mergeable_state=None)
    assert result.passed is True
    assert any("could not be determined" in w for w in result.warnings)


def test_none_mergeable_fails_when_fail_on_unknown():
    result = check_pr_mergeability(
        mergeable=None, mergeable_state=None, fail_on_unknown=True
    )
    assert result.passed is False
    assert any("could not be determined" in e for e in result.errors)
