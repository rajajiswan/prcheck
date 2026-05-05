from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_conflict_checker import ConflictResult


def report_conflict_result(result: ConflictResult) -> None:
    """Emit GitHub Action outputs and a step summary for *result*."""
    set_output("conflict_check_passed", "true" if result.passed else "false")

    if result.error:
        set_output("conflict_check_error", result.error)

    summary = _build_conflict_summary(result)
    write_summary(summary)


def _build_conflict_summary(result: ConflictResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Conflict Check Passed")
    else:
        lines.append("### ❌ Conflict Check Failed")

    if result.error:
        lines.append(f"\n**Error:** {result.error}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warning in result.warnings:
            lines.append(f"- ⚠️ {warning}")

    return "\n".join(lines)
