from src.pr_size_classifier import SizeClassification
from src.action_output import set_output, write_summary


SIZE_EMOJI = {
    "XS": "🟢",
    "S": "🟢",
    "M": "🟡",
    "L": "🟠",
    "XL": "🔴",
}


def report_size_classification(result: SizeClassification) -> None:
    """Emit GitHub Action outputs and step summary for PR size classification."""
    if not result.ok:
        set_output("pr_size", "unknown")
        set_output("pr_size_ok", "false")
        write_summary(_build_error_summary(result))
        return

    set_output("pr_size", result.label)
    set_output("pr_size_ok", "true")
    write_summary(_build_size_summary(result))


def _build_size_summary(result: SizeClassification) -> str:
    emoji = SIZE_EMOJI.get(result.label, "❓")
    lines = [
        "## PR Size Classification",
        "",
        f"**Size:** {emoji} `{result.label}`",
        f"**Total line changes:** {result.total_changes}",
        f"**Files changed:** {result.files_changed}",
        "",
        _size_table(),
    ]
    return "\n".join(lines)


def _build_error_summary(result: SizeClassification) -> str:
    return "\n".join([
        "## PR Size Classification",
        "",
        f"⚠️ Could not classify PR size: {result.error}",
    ])


def _size_table() -> str:
    rows = [
        "| Label | Max changes |",
        "|-------|-------------|" ,
        "| XS    | 10          |",
        "| S     | 50          |",
        "| M     | 200         |",
        "| L     | 500         |",
        "| XL    | 500+        |",
    ]
    return "\n".join(rows)
