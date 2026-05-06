from src.pr_checklist_checker import check_pr_checklist


BODY_FULL = """
## Description
Fixes the login bug.

## Checklist
- [x] Tests added
- [x] Docs updated
- [x] Reviewed by peer
"""

BODY_INCOMPLETE = """
## Description
Adds a feature.

## Checklist
- [x] Tests added
- [ ] Docs updated
- [ ] Reviewed by peer
"""

BODY_NO_CHECKLIST = """
## Description
Just a description, no checklist here.
"""


def test_full_pass_pipeline():
    result = check_pr_checklist(
        BODY_FULL,
        require_all_checked=True,
        min_checked=3,
        fail_on_empty=True,
    )
    assert result.passed is True
    assert result.errors == []
    assert result.total_items == 3
    assert result.checked_items == 3


def test_incomplete_checklist_fails_require_all():
    result = check_pr_checklist(BODY_INCOMPLETE, require_all_checked=True)
    assert result.passed is False
    assert result.unchecked_items == 2
    assert any("not checked" in e for e in result.errors)


def test_incomplete_passes_without_require_all():
    result = check_pr_checklist(BODY_INCOMPLETE, require_all_checked=False)
    assert result.passed is True


def test_no_checklist_warns_by_default():
    result = check_pr_checklist(BODY_NO_CHECKLIST)
    assert result.passed is True
    assert result.total_items == 0
    assert any("no checklist" in w for w in result.warnings)


def test_no_checklist_fails_when_required():
    result = check_pr_checklist(BODY_NO_CHECKLIST, fail_on_empty=True)
    assert result.passed is False
    assert any("no checklist" in e for e in result.errors)
