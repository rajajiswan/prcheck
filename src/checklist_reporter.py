from src.pr_checklist_checker import ChecklistResult
from src.action_output import set_output, write_summary


def report_checklist_result(result: ChecklistResult) -> None:
    """Emit GitHub Action outputs and a step summary for a ChecklistResult."""
    set_output("checklist_passed", str(result.passed).lower())
    set_output("checklist_total", str(result.total_items))
    set_output("checklist_checked", str(result.checked_items))
    set_output("checklist_unchecked", str(result.unchecked_items))

    summary = _build_checklist_summary(result)
    write_summary(summary)


def _build_checklist_summary(result: ChecklistResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Checklist Check Passed")
    else:
        lines.append("### ❌ Checklist Check Failed")

    lines.append("")
    lines.append(
        f"| Total | Checked | Unchecked |"
    )
    lines.append("|-------|---------|-----------|")
    lines.append(
        f"| {result.total_items} "
        f"| {result.checked_items} "
        f"| {result.unchecked_items} |"
    )

    if result.errors:
        lines.append("")
        lines.append("**Errors:**")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("")
        lines.append("**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    return "\n".join(lines)
