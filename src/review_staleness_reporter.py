from __future__ import annotations

from src.action_output import set_output, write_summary
from src.pr_review_staleness_checker import ReviewStalenessResult


def report_review_staleness_result(result: ReviewStalenessResult) -> None:
    """Emit GitHub Action outputs and a step summary for review staleness."""
    set_output("review_staleness_passed", str(result.passed).lower())
    set_output("stale_reviews", str(result.stale_reviews))
    set_output("total_reviews", str(result.total_reviews))
    write_summary(_build_staleness_summary(result))


def _build_staleness_summary(result: ReviewStalenessResult) -> str:
    lines: list[str] = []

    if result.passed:
        lines.append("### ✅ Review Staleness Check Passed")
    else:
        lines.append("### ❌ Review Staleness Check Failed")

    lines.append("")
    lines.append(
        f"- **Approvals checked:** {result.total_reviews}  "
        f"**Stale approvals:** {result.stale_reviews}"
    )

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
