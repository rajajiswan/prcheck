"""Reports enforcement results via GitHub Action outputs and step summaries."""

from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_body_enforcer import EnforcementResult


def report_enforcement_result(result: EnforcementResult) -> None:
    """Emit outputs and write a step summary for the given enforcement result."""
    passed = bool(result)
    set_output("enforcement_passed", str(passed).lower())
    set_output("missing_sections", ",".join(result.missing_sections))
    set_output("unchecked_boxes", str(result.unchecked_boxes))

    summary = _build_summary(result)
    write_summary(summary)


def _build_summary(result: EnforcementResult) -> str:
    """Build a markdown summary string for the enforcement result."""
    lines: list[str] = []

    if result:
        lines.append("## ✅ PR Body Enforcement Passed")
        lines.append("All required sections are present and checkboxes are checked.")
    else:
        lines.append("## ❌ PR Body Enforcement Failed")

        if result.missing_sections:
            lines.append("")
            lines.append("### Missing Sections")
            for section in result.missing_sections:
                lines.append(f"- `{section}`")

        if result.unchecked_boxes > 0:
            lines.append("")
            lines.append(
                f"### Unchecked Boxes: {result.unchecked_boxes} item(s) not checked"
            )

    return "\n".join(lines)
