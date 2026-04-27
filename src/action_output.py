"""Formats and writes GitHub Actions outputs and step summaries."""

import os
from typing import Optional

from src.pr_validator import ValidationResult


GITHUB_OUTPUT = os.environ.get("GITHUB_OUTPUT", "")
GITHUB_STEP_SUMMARY = os.environ.get("GITHUB_STEP_SUMMARY", "")


def _write_to_file(path: str, content: str) -> None:
    """Append content to a file if path is set, otherwise print."""
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(content + "\n")
    else:
        print(content)


def set_output(name: str, value: str) -> None:
    """Write a GitHub Actions output variable."""
    _write_to_file(GITHUB_OUTPUT, f"{name}={value}")


def write_summary(result: ValidationResult, branch_name: str) -> None:
    """Write a Markdown step summary for the validation result."""
    lines = [f"# PR Check — `{branch_name}`", ""]

    if result.valid:
        lines.append("✅ **All checks passed.**")
    else:
        lines.append("❌ **Validation failed.**")

    if result.errors:
        lines.append("\n## Errors")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("\n## Warnings")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    summary = "\n".join(lines)
    _write_to_file(GITHUB_STEP_SUMMARY, summary)


def emit_outputs(result: ValidationResult) -> None:
    """Emit structured outputs consumed by subsequent workflow steps."""
    set_output("valid", str(result.valid).lower())
    set_output("error_count", str(len(result.errors)))
    set_output("warning_count", str(len(result.warnings)))
    if result.errors:
        set_output("first_error", result.errors[0])
