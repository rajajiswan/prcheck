"""Report WIP check results to GitHub Actions outputs and step summary."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_wip_checker import WIPResult


def report_wip_result(result: WIPResult) -> None:
    """Emit Action outputs and a step-summary for the WIP check."""
    set_output("wip_passed", str(result.passed).lower())
    set_output("is_wip", str(result.is_wip).lower())
    write_summary(_build_wip_summary(result))


def _build_wip_summary(result: WIPResult) -> str:
    lines: list[str] = []

    if result.passed:
        header = "### ✅ WIP Check — Passed"
    else:
        header = "### ❌ WIP Check — Failed"

    lines.append(header)
    lines.append("")

    if result.is_wip:
        lines.append("⚠️ **This PR is currently marked as Work In Progress.**")
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

    if not result.errors and not result.warnings:
        lines.append("No WIP indicators detected.")

    return "\n".join(lines)
