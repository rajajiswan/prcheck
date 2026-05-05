from src.action_output import set_output, write_summary
from src.pr_draft_checker import DraftResult


def report_draft_result(result: DraftResult) -> None:
    """Emit GitHub Action outputs and a step summary for the draft check."""
    passed_str = "true" if result.passed else "false"
    set_output("draft_check_passed", passed_str)

    if result.error:
        set_output("draft_check_error", result.error)

    write_summary(_build_draft_summary(result))


def _build_draft_summary(result: DraftResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### \u2705 Draft Check Passed")
        if result.warnings:
            lines.append("")
            lines.append("**Warnings:**")
            for w in result.warnings:
                lines.append(f"- \u26a0\ufe0f {w}")
    else:
        lines.append("### \u274c Draft Check Failed")
        if result.error:
            lines.append("")
            lines.append(f"**Error:** {result.error}")

    return "\n".join(lines)
