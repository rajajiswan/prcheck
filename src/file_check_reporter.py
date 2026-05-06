from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_file_checker import FileCheckResult


def report_file_check_result(result: FileCheckResult) -> None:
    """Emit GitHub Action outputs and a step summary for the file check result."""
    set_output("file_check_passed", str(result.passed).lower())
    set_output("file_check_errors", str(len(result.errors)))
    set_output("file_check_warnings", str(len(result.warnings)))
    write_summary(_build_file_summary(result))


def _build_file_summary(result: FileCheckResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ File Check Passed")
    else:
        lines.append("### ❌ File Check Failed")

    if result.errors:
        lines.append("\n**Errors:**")
        for error in result.errors:
            lines.append(f"- {error}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warning in result.warnings:
            lines.append(f"- {warning}")

    if result.matched_patterns:
        lines.append("\n**Matched Patterns:**")
        for pattern in result.matched_patterns:
            lines.append(f"- `{pattern}`")

    return "\n".join(lines)
