import pytest
from src.pr_draft_checker import DraftResult, check_pr_draft


class TestDraftResult:
    def test_initial_state_is_passing(self):
        r = DraftResult()
        assert r.passed is True
        assert r.error is None
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = DraftResult()
        r.fail("blocked")
        assert r.passed is False

    def test_fail_stores_error_message(self):
        r = DraftResult()
        r.fail("some error")
        assert r.error == "some error"

    def test_warn_does_not_change_passed(self):
        r = DraftResult()
        r.warn("heads up")
        assert r.passed is True

    def test_warn_appends_warning(self):
        r = DraftResult()
        r.warn("first")
        r.warn("second")
        assert r.warnings == ["first", "second"]

    def test_bool_true_when_passing(self):
        assert bool(DraftResult()) is True

    def test_bool_false_when_failed(self):
        r = DraftResult()
        r.fail("err")
        assert bool(r) is False


class TestCheckPrDraft:
    def test_non_draft_always_passes(self):
        result = check_pr_draft(is_draft=False)
        assert result.passed is True
        assert result.error is None
        assert result.warnings == []

    def test_draft_blocked_by_default(self):
        result = check_pr_draft(is_draft=True)
        assert result.passed is False
        assert result.error is not None
        assert "draft" in result.error.lower()

    def test_draft_warns_when_warn_on_draft_true(self):
        result = check_pr_draft(is_draft=True, block_draft_merge=False, warn_on_draft=True)
        assert result.passed is True
        assert len(result.warnings) == 1
        assert "draft" in result.warnings[0].lower()

    def test_draft_blocked_overrides_warn_flag(self):
        """block_draft_merge=True takes precedence over warn_on_draft."""
        result = check_pr_draft(is_draft=True, block_draft_merge=True, warn_on_draft=False)
        assert result.passed is False

    def test_no_block_no_warn_draft_passes(self):
        result = check_pr_draft(is_draft=True, block_draft_merge=False, warn_on_draft=False)
        assert result.passed is True
        assert result.warnings == []
        assert result.error is None

    def test_non_draft_no_warnings_emitted(self):
        result = check_pr_draft(is_draft=False, warn_on_draft=True)
        assert result.warnings == []
