from src.pr_contributor_checker import ContributorResult
from src.action_output import set_output, write_summary


def report_contributor_result(result: ContributorResult) -> None:
    set_output("contributor_passed", str(result.passed).lower())
    set_output("contributor_author", result.author or "")
    set_output("contributor_first_time", str(result.is_first_time).lower())
    if result.errors:
        set_output("contributor_errors", " | ".join(result.errors))
    if result.warnings:
        set_output("contributor_warnings", " | ".join(result.warnings))
    write_summary(_build_contributor_summary(result))


def _build_contributor_summary(result: ContributorResult) -> str:
    icon = "✅" if result.passed else "❌"
    lines = [f"## {icon} Contributor Check"]

    if result.author:
        badge = " 🆕" if result.is_first_time else ""
        lines.append(f"**Author:** `{result.author}`{badge}")

    if result.warnings:
        lines.append("### ⚠️ Warnings")
        lines.extend(f"- {w}" for w in result.warnings)

    if result.errors:
        lines.append("### Errors")
        lines.extend(f"- {e}" for e in result.errors)

    if result.passed and not result.warnings:
        lines.append("Contributor check passed with no issues.")

    return "\n".join(lines)
