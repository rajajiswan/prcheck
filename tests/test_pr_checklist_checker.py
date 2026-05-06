import pytest
from src.pr_checklist_checker import ChecklistResult, check_pr_checklist


class TestChecklistResult:
    def test_initial_state_is_passing(self):
        r = ChecklistResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.total_items == 0
        assert r.checked_items == 0
        assert r.unchecked_items == 0

    def test_fail_sets_passed_false(self):
        r = ChecklistResult()
        r.fail("something wrong")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ChecklistResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ChecklistResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(ChecklistResult()) is True

    def test_bool_false_when_failing(self):
        r = ChecklistResult()
        r.fail("x")
        assert bool(r) is False


BODY_ALL_CHECKED = "- [x] Step one\n- [x] Step two\n- [x] Step three"
BODY_PARTIAL = "- [x] Step one\n- [ ] Step two\n- [ ] Step three"
BODY_NONE_CHECKED = "- [ ] Step one\n- [ ] Step two"
BODY_EMPTY = ""


def test_all_checked_passes_require_all():
    r = check_pr_checklist(BODY_ALL_CHECKED, require_all_checked=True)
    assert r.passed is True
    assert r.total_items == 3
    assert r.checked_items == 3
    assert r.unchecked_items == 0


def test_partial_fails_require_all():
    r = check_pr_checklist(BODY_PARTIAL, require_all_checked=True)
    assert r.passed is False
    assert "2 checklist item(s) are not checked" in r.errors[0]


def test_min_checked_passes_when_met():
    r = check_pr_checklist(BODY_PARTIAL, min_checked=1)
    assert r.passed is True


def test_min_checked_fails_when_not_met():
    r = check_pr_checklist(BODY_NONE_CHECKED, min_checked=1)
    assert r.passed is False
    assert "At least 1 checklist item(s) must be checked" in r.errors[0]


def test_empty_body_warns_by_default():
    r = check_pr_checklist(BODY_EMPTY)
    assert r.passed is True
    assert any("no checklist items" in w for w in r.warnings)


def test_empty_body_fails_when_fail_on_empty():
    r = check_pr_checklist(BODY_EMPTY, fail_on_empty=True)
    assert r.passed is False
    assert any("no checklist items" in e for e in r.errors)


def test_counts_are_accurate_for_partial_body():
    r = check_pr_checklist(BODY_PARTIAL)
    assert r.total_items == 3
    assert r.checked_items == 1
    assert r.unchecked_items == 2


def test_none_body_treated_as_empty():
    r = check_pr_checklist(None)
    assert r.total_items == 0
    assert r.passed is True
