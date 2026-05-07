"""Formats and reports changelog check results as GitHub Action outputs."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_changelog_checker import ChangelogResult


def report_changelog_result(result: ChangelogResult) -> None:
    """Emit Action outputs and a step summary for *result*."""
    set_output("changelog_passed", str(result.passed).lower())
    set_output("changelog_file", result.changelog_file or "")
    write_summary(_build_changelog_summary(result))


def _build_changelog_summary(result: ChangelogResult) -> str:
    lines: list[str] = []

    if result.passed:
        header = "### ✅ Changelog Check Passed"
    else:
        header = "### ❌ Changelog Check Failed"

    lines.append(header)
    lines.append("")

    if result.changelog_file:
        lines.append(f"- Changelog entry found: `{result.changelog_file}`")

    for error in result.errors:
        lines.append(f"- ❌ {error}")

    for warning in result.warnings:
        lines.append(f"- ⚠️ {warning}")

    return "\n".join(lines)
