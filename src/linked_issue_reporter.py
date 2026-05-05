from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_linked_issue_checker import LinkedIssueResult


def report_linked_issue_result(result: LinkedIssueResult) -> None:
    """Emit GitHub Action outputs and a step summary for a LinkedIssueResult."""
    set_output("linked_issue_passed", str(result.passed).lower())
    set_output("linked_issues", ",".join(result.issue_numbers))
    write_summary(_build_linked_issue_summary(result))


def _build_linked_issue_summary(result: LinkedIssueResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Linked Issue Check Passed")
    else:
        lines.append("### ❌ Linked Issue Check Failed")

    if result.issue_numbers:
        formatted = ", ".join(f"#{n}" for n in result.issue_numbers)
        lines.append(f"\n**Linked issues:** {formatted}")
    else:
        lines.append("\n**Linked issues:** _none detected_")

    if result.errors:
        lines.append("\n**Errors:**")
        for err in result.errors:
            lines.append(f"- ❌ {err}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- ⚠️ {warn}")

    return "\n".join(lines)
