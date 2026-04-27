"""Reports label application results to action outputs and step summary."""

from __future__ import annotations

from src.action_output import set_output, write_summary
from src.label_manager import LabelResult


def report_label_result(result: LabelResult) -> None:
    """Write label outcome to GitHub Actions outputs and step summary."""
    set_output("label_applied", str(result.label or ""))
    set_output("label_success", str(result.success).lower())

    _write_label_summary(result)


def _write_label_summary(result: LabelResult) -> None:
    """Append label section to the step summary markdown."""
    lines: list[str] = []
    lines.append("## Label Application\n")

    if result.success:
        lines.append(f"✅ Label `{result.label}` successfully applied to the PR.\n")
    else:
        lines.append("❌ Label could not be applied.\n")
        if result.label:
            lines.append(f"- Attempted label: `{result.label}`\n")
        lines.append(f"- Reason: {result.message}\n")

    write_summary("".join(lines))
