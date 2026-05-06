from src.pr_approval_checker import ApprovalResult
from src.action_output import set_output, write_summary


def report_approval_result(result: ApprovalResult) -> None:
    """Emit GitHub Action outputs and step summary for approval check."""
    set_output("approval_passed", str(result.passed).lower())
    set_output("approval_count", str(result.approval_count))
    set_output("approved_by", ",".join(result.approved_by))

    summary = _build_approval_summary(result)
    write_summary(summary)


def _build_approval_summary(result: ApprovalResult) -> str:
    lines = []

    if result.passed:
        lines.append("### ✅ Approval Check Passed")
    else:
        lines.append("### ❌ Approval Check Failed")

    lines.append("")
    lines.append(
        f"**Approvals:** {result.approval_count} / {result.required_count} required"
    )

    if result.approved_by:
        lines.append("")
        lines.append("**Approved by:**")
        for reviewer in result.approved_by:
            lines.append(f"- `{reviewer}`")

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
