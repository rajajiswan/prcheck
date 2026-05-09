"""Report CI status check results to GitHub Actions outputs and summary."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_ci_status_checker import CIStatusResult


def report_ci_status_result(result: CIStatusResult) -> None:
    """Emit GitHub Actions outputs and a step summary for CI status checks."""
    set_output("ci_status_passed", "true" if result.passed else "false")
    set_output("ci_status_errors", str(len(result.errors)))
    set_output("ci_status_warnings", str(len(result.warnings)))
    write_summary(_build_ci_status_summary(result))


def _build_ci_status_summary(result: CIStatusResult) -> str:
    header = "### ✅ CI Status Checks" if result.passed else "### ❌ CI Status Checks"
    lines = [header, ""]
    lines.append(f"- **Total checks:** {result.total_checks}")
    lines.append(f"- **Failed checks:** {len(result.failed_checks)}")
    lines.append(f"- **Pending checks:** {len(result.pending_checks)}")

    if result.failed_checks:
        lines.append("")
        lines.append("**Failed:**")
        for name in result.failed_checks:
            lines.append(f"  - `{name}`")

    if result.pending_checks:
        lines.append("")
        lines.append("**Pending:**")
        for name in result.pending_checks:
            lines.append(f"  - `{name}`")

    if result.errors:
        lines.append("")
        lines.append("**Errors:**")
        for err in result.errors:
            lines.append(f"  - {err}")

    if result.warnings:
        lines.append("")
        lines.append("**Warnings:**")
        for warn in result.warnings:
            lines.append(f"  - {warn}")

    return "\n".join(lines)
