"""Tests for src/branch_label_enforcer.py."""
import pytest

from src.branch_parser import BranchInfo
from src.branch_label_enforcer import LabelEnforcementResult, enforce_branch_label


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def feature_branch():
    return BranchInfo(type="feature", ticket="PROJ-1", description="add-login", raw="feature/PROJ-1-add-login", label="feature")


@pytest.fixture
def unknown_branch():
    return BranchInfo(type=None, ticket=None, description=None, raw="my-random-branch", label=None)


# ---------------------------------------------------------------------------
# LabelEnforcementResult unit tests
# ---------------------------------------------------------------------------

class TestLabelEnforcementResult:
    def test_initial_state_is_passing(self):
        r = LabelEnforcementResult()
        assert r.passed is True
        assert r.errors == []
        assert bool(r) is True

    def test_fail_sets_passed_false(self):
        r = LabelEnforcementResult()
        r.fail("something went wrong")
        assert r.passed is False
        assert bool(r) is False

    def test_fail_appends_message(self):
        r = LabelEnforcementResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]


# ---------------------------------------------------------------------------
# enforce_branch_label tests
# ---------------------------------------------------------------------------

class TestEnforceBranchLabel:
    def test_passes_when_label_present(self, feature_branch):
        result = enforce_branch_label(feature_branch, ["feature", "ready-for-review"])
        assert result.passed is True
        assert result.errors == []

    def test_fails_when_label_missing(self, feature_branch):
        result = enforce_branch_label(feature_branch, ["bugfix"])
        assert result.passed is False
        assert any("feature" in e for e in result.errors)

    def test_fails_with_no_labels_applied(self, feature_branch):
        result = enforce_branch_label(feature_branch, [])
        assert result.passed is False

    def test_fails_for_unknown_branch_type(self, unknown_branch):
        result = enforce_branch_label(unknown_branch, [])
        assert result.passed is False
        assert any("naming convention" in e for e in result.errors)

    def test_skipped_when_require_label_false(self, feature_branch):
        result = enforce_branch_label(feature_branch, [], require_label=False)
        assert result.passed is True

    def test_skipped_for_unknown_branch_when_disabled(self, unknown_branch):
        result = enforce_branch_label(unknown_branch, [], require_label=False)
        assert result.passed is True

    def test_stores_expected_label(self, feature_branch):
        result = enforce_branch_label(feature_branch, ["feature"])
        assert result.expected_label == "feature"

    def test_stores_actual_labels(self, feature_branch):
        result = enforce_branch_label(feature_branch, ["feature", "wip"])
        assert result.actual_labels == ["feature", "wip"]
