from src.action_output import set_output, write_summary
from src.pr_base_branch_checker import BaseBranchResult


def report_base_branch_result(result: BaseBranchResult) -> None:
    """Emit GitHub Action outputs and a step summary for a BaseBranchResult."""
    set_output("base_branch_passed", "true" if result.passed else "false")
    set_output("base_branch", result.base_branch or "")
    write_summary(_build_base_branch_summary(result))


def _build_base_branch_summary(result: BaseBranchResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("## ✅ Base Branch Check Passed")
    else:
        lines.append("## ❌ Base Branch Check Failed")

    if result.base_branch:
        lines.append(f"- **Target branch:** `{result.base_branch}`")

    if result.expected_branches:
        formatted = ", ".join(f"`{b}`" for b in result.expected_branches)
        lines.append(f"- **Allowed bases:** {formatted}")

    if result.errors:
        lines.append("\n### Errors")
        for err in result.errors:
            lines.append(f"- ❌ {err}")

    if result.warnings:
        lines.append("\n### Warnings")
        for warn in result.warnings:
            lines.append(f"- ⚠️ {warn}")

    return "\n".join(lines)
