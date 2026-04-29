"""Integration tests: analyze_pr_diff + diff_analysis_reporter pipeline."""
from unittest.mock import patch

from src.pr_diff_fetcher import PRDiff
from src.pr_diff_analyzer import analyze_pr_diff
from src.diff_analysis_reporter import report_diff_analysis


def _make_diff(files=5, additions=100, deletions=50, error=None):
    return PRDiff(
        filenames=[f"f{i}.py" for i in range(files)],
        additions=additions,
        deletions=deletions,
        error=error,
    )


def test_clean_diff_full_pipeline():
    diff = _make_diff(files=3, additions=80, deletions=30)
    result = analyze_pr_diff(diff)
    assert result.passed is True

    outputs = {}
    with patch("src.diff_analysis_reporter.set_output", side_effect=lambda k, v: outputs.update({k: v})), \
         patch("src.diff_analysis_reporter.write_summary"):
        report_diff_analysis(result)

    assert outputs["diff_analysis_passed"] == "true"
    assert outputs["diff_analysis_errors"] == ""
    assert outputs["diff_analysis_warnings"] == ""


def test_oversized_diff_full_pipeline():
    diff = _make_diff(files=55, additions=600, deletions=500)
    result = analyze_pr_diff(diff, max_files=50, max_lines=1000)
    assert result.passed is False

    outputs = {}
    with patch("src.diff_analysis_reporter.set_output", side_effect=lambda k, v: outputs.update({k: v})), \
         patch("src.diff_analysis_reporter.write_summary"):
        report_diff_analysis(result)

    assert outputs["diff_analysis_passed"] == "false"
    assert "55 files" in outputs["diff_analysis_errors"]
    assert "1100 lines" in outputs["diff_analysis_errors"]


def test_fetch_error_propagates_through_pipeline():
    diff = _make_diff(error="API rate limit exceeded")
    result = analyze_pr_diff(diff)
    assert result.passed is False

    outputs = {}
    with patch("src.diff_analysis_reporter.set_output", side_effect=lambda k, v: outputs.update({k: v})), \
         patch("src.diff_analysis_reporter.write_summary"):
        report_diff_analysis(result)

    assert outputs["diff_analysis_passed"] == "false"
    assert "API rate limit exceeded" in outputs["diff_analysis_errors"]
