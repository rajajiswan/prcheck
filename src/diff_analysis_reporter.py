"""Emit GitHub Action outputs and step summary for DiffAnalysisResult."""
from src.pr_diff_analyzer import DiffAnalysisResult
from src.action_output import set_output, write_summary


def report_diff_analysis(result: DiffAnalysisResult) -> None:
    """Write outputs and a markdown summary for the diff analysis."""
    set_output("diff_analysis_passed", "true" if result.passed else "false")

    if result.errors:
        set_output("diff_analysis_errors", " | ".join(result.errors))
    else:
        set_output("diff_analysis_errors", "")

    if result.warnings:
        set_output("diff_analysis_warnings", " | ".join(result.warnings))
    else:
        set_output("diff_analysis_warnings", "")

    write_summary(_build_diff_summary(result))


def _build_diff_summary(result: DiffAnalysisResult) -> str:
    lines = []
    if result.passed:
        lines.append("### ✅ Diff Analysis Passed")
    else:
        lines.append("### ❌ Diff Analysis Failed")

    if result.errors:
        lines.append("\n**Errors:**")
        for err in result.errors:
            lines.append(f"- {err}")

    if result.warnings:
        lines.append("\n**Warnings:**")
        for warn in result.warnings:
            lines.append(f"- {warn}")

    if not result.errors and not result.warnings:
        lines.append("\nNo issues detected.")

    return "\n".join(lines)
