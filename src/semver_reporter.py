"""Formats and emits outputs for SemverResult."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_semantic_version_checker import SemverResult


def report_semver_result(result: SemverResult) -> None:
    """Write GitHub Action outputs and step summary for a SemverResult."""
    set_output("semver_passed", "true" if result.passed else "false")
    set_output("semver_version", result.detected_version or "")
    set_output("semver_errors", ";".join(result.errors))
    set_output("semver_warnings", ";".join(result.warnings))
    write_summary(_build_semver_summary(result))


def _build_semver_summary(result: SemverResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Semantic Version Check Passed")
    else:
        lines.append("### ❌ Semantic Version Check Failed")

    if result.detected_version:
        lines.append(f"- **Detected version:** `{result.detected_version}`")
    else:
        lines.append("- **Detected version:** _(none)_")

    if result.errors:
        lines.append("\n**Errors:**")
        for err in result.errors:
            lines.append(f"- ❌ {err}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- ⚠️ {warn}")

    return "\n".join(lines)
