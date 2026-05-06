"""Report label check results to GitHub Actions outputs and step summary."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_label_checker import LabelCheckResult


def report_label_check_result(result: LabelCheckResult) -> None:
    """Emit Action outputs and a Markdown step summary for *result*."""
    set_output("label_check_passed", str(result.passed).lower())
    set_output("label_check_errors", "|".join(result.errors))
    write_summary(_build_label_summary(result))


def _build_label_summary(result: LabelCheckResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("## ✅ Label Check Passed")
    else:
        lines.append("## ❌ Label Check Failed")

    if result.applied_labels:
        labels_md = ", ".join(f"`{lbl}`" for lbl in result.applied_labels)
        lines.append(f"**Applied labels:** {labels_md}")
    else:
        lines.append("**Applied labels:** _none_")

    if result.errors:
        lines.append("\n### Errors")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("\n### Warnings")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    return "\n".join(lines)
