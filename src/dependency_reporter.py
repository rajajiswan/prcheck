from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_dependency_checker import DependencyResult


def report_dependency_result(result: DependencyResult) -> None:
    """Emit action outputs and step summary for a DependencyResult."""
    set_output("dependency_check_passed", str(result.passed).lower())
    set_output("blocking_prs", ",".join(result.blocking_prs))
    if result.label:
        set_output("dependency_label", result.label)
    write_summary(_build_dependency_summary(result))


def _build_dependency_summary(result: DependencyResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Dependency Check Passed")
    else:
        lines.append("### ❌ Dependency Check Failed")

    if result.blocking_prs:
        lines.append("")
        lines.append(f"**Blocking PRs:** {', '.join(result.blocking_prs)}")

    if result.errors:
        lines.append("")
        lines.append("**Errors:**")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("")
        lines.append("**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    return "\n".join(lines)
