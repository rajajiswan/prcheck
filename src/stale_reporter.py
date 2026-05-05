from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_stale_checker import StaleResult


def report_stale_result(result: StaleResult) -> None:
    """Emit GitHub Action outputs and a step summary for a StaleResult."""
    set_output("stale_passed", str(result.passed).lower())
    set_output("stale_days", str(result.days_since_update) if result.days_since_update is not None else "")
    set_output("is_stale", str(result.is_stale).lower())
    write_summary(_build_stale_summary(result))


def _build_stale_summary(result: StaleResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Stale Check Passed")
    else:
        lines.append("### ❌ Stale Check Failed")

    if result.days_since_update is not None:
        lines.append(f"- **Days since last update:** {result.days_since_update}")

    if result.is_stale:
        lines.append("- **Status:** 🟡 Stale")
    else:
        lines.append("- **Status:** 🟢 Active")

    if result.errors:
        lines.append("\n**Errors:**")
        for err in result.errors:
            lines.append(f"- ❌ {err}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- ⚠️ {warn}")

    return "\n".join(lines)
