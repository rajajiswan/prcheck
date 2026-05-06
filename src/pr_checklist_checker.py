from dataclasses import dataclass, field
from typing import List


@dataclass
class ChecklistResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_items: int = 0
    checked_items: int = 0
    unchecked_items: int = 0

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_checklist(
    body: str,
    require_all_checked: bool = False,
    min_checked: int = 0,
    fail_on_empty: bool = False,
) -> ChecklistResult:
    """Analyse checkbox items in a PR body and enforce checklist rules."""
    result = ChecklistResult()

    checked_pattern = "- [x]"
    unchecked_pattern = "- [ ]"

    lines = body.splitlines() if body else []
    checked = sum(1 for ln in lines if checked_pattern.lower() in ln.lower())
    unchecked = sum(1 for ln in lines if unchecked_pattern in ln)
    total = checked + unchecked

    result.total_items = total
    result.checked_items = checked
    result.unchecked_items = unchecked

    if total == 0:
        if fail_on_empty:
            result.fail("PR body contains no checklist items.")
        else:
            result.warn("PR body contains no checklist items.")
        return result

    if require_all_checked and unchecked > 0:
        result.fail(
            f"{unchecked} checklist item(s) are not checked. "
            "All items must be completed before merging."
        )

    if min_checked > 0 and checked < min_checked:
        result.fail(
            f"At least {min_checked} checklist item(s) must be checked, "
            f"but only {checked} are checked."
        )

    return result
