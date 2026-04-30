import pytest
from src.pr_milestone_checker import check_pr_milestone
from src.milestone_reporter import _build_milestone_summary


def test_full_pass_pipeline():
    result = check_pr_milestone("v2.1", require_milestone=True, allowed_milestones=["v2.0", "v2.1"])
    assert result.passed is True
    summary = _build_milestone_summary(result)
    assert "✅" in summary
    assert "v2.1" in summary


def test_missing_milestone_pipeline():
    result = check_pr_milestone(None, require_milestone=True)
    assert result.passed is False
    summary = _build_milestone_summary(result)
    assert "❌" in summary
    assert "must have a milestone" in summary


def test_disallowed_milestone_pipeline():
    result = check_pr_milestone(
        "v0.1", require_milestone=True, allowed_milestones=["v1.0"]
    )
    assert result.passed is False
    summary = _build_milestone_summary(result)
    assert "v0.1" in summary
    assert "allowed list" in summary


def test_optional_milestone_warning_pipeline():
    result = check_pr_milestone(None, require_milestone=False)
    assert result.passed is True
    summary = _build_milestone_summary(result)
    assert "not required" in summary
