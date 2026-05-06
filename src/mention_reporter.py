from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_mention_checker import MentionResult


def report_mention_result(result: MentionResult) -> None:
    """Emit GitHub Action outputs and a step summary for a MentionResult."""
    set_output("mention_check_passed", str(result.passed).lower())
    set_output("mention_count", str(len(result.mentions_found)))
    if result.errors:
        set_output("mention_errors", "; ".join(result.errors))
    write_summary(_build_mention_summary(result))


def _build_mention_summary(result: MentionResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Mention Check Passed")
    else:
        lines.append("### ❌ Mention Check Failed")

    if result.mentions_found:
        formatted = ", ".join(f"`@{u}`" for u in result.mentions_found)
        lines.append(f"\n**Mentions found:** {formatted}")
    else:
        lines.append("\n**Mentions found:** none")

    if result.errors:
        lines.append("\n**Errors:**")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    return "\n".join(lines)
