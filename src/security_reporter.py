from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_security_checker import SecurityResult


def report_security_result(result: SecurityResult) -> None:
    set_output("security_passed", "true" if result.passed else "false")
    set_output("secrets_found", ",".join(result.secrets_found) if result.secrets_found else "")
    write_summary(_build_security_summary(result))


def _build_security_summary(result: SecurityResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("## ✅ Security Check Passed")
    else:
        lines.append("## ❌ Security Check Failed")

    if result.errors:
        lines.append("\n### Errors")
        for err in result.errors:
            lines.append(f"- ❌ {err}")

    if result.warnings:
        lines.append("\n### Warnings")
        for warn in result.warnings:
            lines.append(f"- ⚠️ {warn}")

    if result.secrets_found:
        lines.append("\n### Secrets Detected")
        for secret in result.secrets_found:
            lines.append(f"- 🔑 {secret}")
        lines.append("\n> Please remove all secrets before merging.")

    if result.passed and not result.warnings:
        lines.append("\nNo sensitive files or secrets detected in this PR.")

    return "\n".join(lines)
