"""Writes GitHub Step Summary and sets action outputs for the full check suite."""

from src.run_checks import CheckSuite
from src.action_output import set_output, write_summary


def report_check_suite(suite: CheckSuite) -> None:
    """Emit outputs and write a markdown summary for the entire check suite."""
    set_output("passed", str(suite.passed).lower())

    error_list = suite.errors
    set_output("errors", "|".join(error_list) if error_list else "")

    summary = _build_suite_summary(suite)
    write_summary(summary)


def _build_suite_summary(suite: CheckSuite) -> str:
    lines: list[str] = ["## PR Check Results\n"]

    overall = "✅ All checks passed" if suite.passed else "❌ Some checks failed"
    lines.append(f"{overall}\n")

    if suite.description_result is not None:
        status = "✅" if suite.description_result else "❌"
        lines.append(f"### {status} Description Check")
        if not suite.description_result:
            for err in suite.description_result.errors:
                lines.append(f"- {err}")
        lines.append("")

    if suite.label_result is not None:
        status = "✅" if suite.label_result else "❌"
        lines.append(f"### {status} Label Check")
        if not suite.label_result:
            for err in suite.label_result.errors:
                lines.append(f"- {err}")
        lines.append("")

    return "\n".join(lines)
