from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_commit_checker import CommitResult


def report_commit_result(result: CommitResult) -> None:
    """Emit GitHub Action outputs and a step summary for commit check results."""
    set_output("commits_passed", str(result.passed).lower())
    set_output("commit_count", str(result.commit_count))

    if result.errors:
        set_output("commit_errors", " | ".join(result.errors))

    summary = _build_commit_summary(result)
    write_summary(summary)


def _build_commit_summary(result: CommitResult) -> str:
    icon = "✅" if result.passed else "❌"
    lines = [
        f"## {icon} Commit Check",
        f"",
        f"**Total commits:** {result.commit_count}",
    ]

    if result.errors:
        lines.append("")
        lines.append("### Errors")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.non_conventional_commits:
        lines.append("")
        lines.append("### Non-Conventional Commits")
        for msg in result.non_conventional_commits:
            lines.append(f"- `{msg}`")

    if result.warnings:
        lines.append("")
        lines.append("### Warnings")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    return "\n".join(lines)
