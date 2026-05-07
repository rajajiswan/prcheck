from src.pr_protected_branch_checker import ProtectedBranchResult
from src.action_output import set_output, write_summary


def report_protected_branch_result(result: ProtectedBranchResult) -> None:
    """Emit GitHub Action outputs and step summary for a ProtectedBranchResult."""
    set_output("protected_branch_passed", str(result.passed).lower())
    set_output("protected_branch_errors", ";".join(result.errors))
    set_output("protected_branch_warnings", ";".join(result.warnings))
    write_summary(_build_protected_branch_summary(result))


def _build_protected_branch_summary(result: ProtectedBranchResult) -> str:
    header = (
        "### ✅ Protected Branch Check Passed"
        if result.passed
        else "### ❌ Protected Branch Check Failed"
    )
    lines = [header, ""]

    if result.target_branch:
        protected_label = "yes" if result.is_protected else "no"
        lines.append(f"- **Target branch:** `{result.target_branch}`")
        lines.append(f"- **Is protected:** {protected_label}")
        lines.append("")

    if result.errors:
        lines.append("**Errors:**")
        for err in result.errors:
            lines.append(f"- {err}")
        lines.append("")

    if result.warnings:
        lines.append("**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- {warn}")
        lines.append("")

    return "\n".join(lines)
