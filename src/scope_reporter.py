"""Report scope check results to GitHub Actions outputs and step summary."""
from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_scope_checker import ScopeResult


def report_scope_result(result: ScopeResult) -> None:
    """Emit Action outputs and write a markdown step summary for scope checks."""
    set_output("scope_passed", str(result.passed).lower())
    set_output("scope_errors", str(len(result.errors)))
    set_output("scope_warnings", str(len(result.warnings)))
    set_output("out_of_scope_files", ",".join(result.out_of_scope_files))
    write_summary(_build_scope_summary(result))


def _build_scope_summary(result: ScopeResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("## ✅ Scope Check Passed")
    else:
        lines.append("## ❌ Scope Check Failed")

    if result.errors:
        lines.append("\n### Errors")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("\n### Warnings")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    if result.out_of_scope_files:
        lines.append("\n### Out-of-Scope Files")
        for f in result.out_of_scope_files:
            lines.append(f"- `{f}`")

    return "\n".join(lines)
