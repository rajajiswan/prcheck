"""Writes GitHub Actions outputs and step summary for PR body enforcement."""

from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_body_enforcer import EnforcementResult


def report_enforcement_result(result: EnforcementResult) -> None:
    """Emit GitHub Actions outputs and a step-summary for *result*.

    Outputs set:
        - ``enforcement_passed``: ``"true"`` or ``"false"``
        - ``missing_sections``: comma-separated list of missing section names
        - ``unchecked_boxes``: integer count as a string
    """
    passed_str = "true" if result.passed else "false"
    set_output("enforcement_passed", passed_str)
    set_output("missing_sections", ",".join(result.missing_sections))
    set_output("unchecked_boxes", str(result.unchecked_boxes))

    write_summary(_build_summary(result))


def _build_summary(result: EnforcementResult) -> str:
    """Return a markdown summary string for the enforcement result."""
    if result.passed:
        return "### ✅ PR Body Enforcement Passed\n\nAll required sections are present and all checkboxes are checked.\n"

    lines = ["### ❌ PR Body Enforcement Failed\n"]

    if result.missing_sections:
        lines.append("**Missing sections:**")
        for section in result.missing_sections:
            lines.append(f"- `{section}`")
        lines.append("")

    if result.unchecked_boxes:
        lines.append(
            f"**Unchecked checklist items:** {result.unchecked_boxes} item(s) still need to be checked off.\n"
        )

    return "\n".join(lines)
