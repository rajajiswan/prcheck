from src.action_output import set_output, write_summary
from src.pr_reopen_checker import ReopenResult


def report_reopen_result(result: ReopenResult) -> None:
    """Emit GitHub Action outputs and step summary for a ReopenResult."""
    set_output("reopen_passed", str(result.passed).lower())
    set_output("reopen_count", str(result.reopen_count))
    write_summary(_build_reopen_summary(result))


def _build_reopen_summary(result: ReopenResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ PR Reopen Check Passed")
    else:
        lines.append("### ❌ PR Reopen Check Failed")

    lines.append("")
    lines.append(f"**Reopen count:** {result.reopen_count}")

    if result.last_closed_at:
        lines.append(f"**Last closed at:** {result.last_closed_at}")

    if result.errors:
        lines.append("")
        lines.append("**Errors:**")
        for error in result.errors:
            lines.append(f"- {error}")

    if result.warnings:
        lines.append("")
        lines.append("**Warnings:**")
        for warning in result.warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines)
