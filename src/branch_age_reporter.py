"""Report branch age check results to GitHub Actions outputs and step summary."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_branch_age_checker import BranchAgeResult


def report_branch_age_result(result: BranchAgeResult) -> None:
    """Emit GitHub Actions outputs and write a step-summary for a BranchAgeResult."""
    set_output("branch_age_passed", str(result.passed).lower())
    set_output("branch_age_days", str(result.age_days) if result.age_days is not None else "")

    summary = _build_branch_age_summary(result)
    write_summary(summary)


def _build_branch_age_summary(result: BranchAgeResult) -> str:
    """Build a Markdown summary block for the branch age check."""
    if result.passed and not result.warnings:
        header = "### ✅ Branch Age Check Passed"
    elif result.passed and result.warnings:
        header = "### ⚠️ Branch Age Check Passed with Warnings"
    else:
        header = "### ❌ Branch Age Check Failed"

    lines = [header, ""]

    if result.branch_name:
        lines.append(f"**Branch:** `{result.branch_name}`")
    if result.age_days is not None:
        lines.append(f"**Age:** {result.age_days} day(s)")

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
