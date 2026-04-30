from src.action_output import set_output, write_summary
from src.pr_milestone_checker import MilestoneResult


def report_milestone_result(result: MilestoneResult) -> None:
    """Emit GitHub Action outputs and step summary for a MilestoneResult."""
    set_output("milestone_passed", str(result.passed).lower())
    set_output("milestone_value", result.milestone or "")
    write_summary(_build_milestone_summary(result))


def _build_milestone_summary(result: MilestoneResult) -> str:
    lines = []
    if result.passed:
        icon = "✅"
        headline = "Milestone check passed."
    else:
        icon = "❌"
        headline = "Milestone check failed."

    lines.append(f"## {icon} Milestone Check")
    lines.append("")
    lines.append(headline)

    if result.milestone:
        lines.append(f"- **Milestone**: `{result.milestone}`")

    if result.error:
        lines.append(f"- **Error**: {result.error}")

    for warning in result.warnings:
        lines.append(f"- ⚠️ {warning}")

    return "\n".join(lines)
