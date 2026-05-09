from __future__ import annotations

from src.pr_cleanup_checker import CleanupResult
from src.action_output import set_output, write_summary


def report_cleanup_result(result: CleanupResult) -> None:
    """Emit GitHub Action outputs and step summary for a CleanupResult."""
    set_output("cleanup_passed", str(result.passed).lower())
    set_output("cleanup_branch", result.branch_name or "")
    set_output("cleanup_errors", ";".join(result.errors))
    set_output("cleanup_warnings", ";".join(result.warnings))
    write_summary(_build_cleanup_summary(result))


def _build_cleanup_summary(result: CleanupResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ PR Cleanup Check Passed")
    else:
        lines.append("### ❌ PR Cleanup Check Failed")

    branch = result.branch_name or "(unknown)"
    lines.append(f"**Branch:** `{branch}`")

    state_parts = []
    if result.is_merged:
        state_parts.append("merged")
    if result.is_closed:
        state_parts.append("closed")
    if state_parts:
        lines.append(f"**State:** {', '.join(state_parts)}")

    if result.errors:
        lines.append("\n**Errors:**")
        for err in result.errors:
            lines.append(f"- ❌ {err}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- ⚠️ {warn}")

    return "\n".join(lines)
