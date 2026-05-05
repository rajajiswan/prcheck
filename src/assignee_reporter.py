from src.action_output import set_output, write_summary
from src.pr_assignee_checker import AssigneeResult


def report_assignee_result(result: AssigneeResult) -> None:
    """Emit GitHub Action outputs and step summary for assignee check."""
    set_output("assignee_check_passed", str(result.passed).lower())
    set_output("assignee_count", str(len(result.assignees)))

    summary = _build_assignee_summary(result)
    write_summary(summary)


def _build_assignee_summary(result: AssigneeResult) -> str:
    lines = []

    if result.passed:
        lines.append("### ✅ Assignee Check Passed")
    else:
        lines.append("### ❌ Assignee Check Failed")

    if result.assignees:
        assignee_list = ", ".join(f"`{a}`" for a in result.assignees)
        lines.append(f"**Assignees:** {assignee_list}")
    else:
        lines.append("**Assignees:** _none_")

    if result.errors:
        lines.append("\n**Errors:**")
        for error in result.errors:
            lines.append(f"- {error}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warning in result.warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines)
