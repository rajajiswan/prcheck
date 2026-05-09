"""Integration tests for the full CI status check pipeline."""
from src.pr_ci_status_checker import check_pr_ci_status


def _s(name: str, state: str) -> dict:
    return {"name": name, "state": state}


def test_full_pass_pipeline():
    statuses = [
        _s("build", "success"),
        _s("lint", "success"),
        _s("test", "success"),
    ]
    result = check_pr_ci_status(
        statuses,
        required_checks=["build", "lint", "test"],
    )
    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []
    assert result.total_checks == 3


def test_failed_check_full_pipeline():
    statuses = [
        _s("build", "success"),
        _s("test", "failure"),
    ]
    result = check_pr_ci_status(statuses, required_checks=["build", "test"])
    assert result.passed is False
    assert "test" in result.failed_checks
    assert any("test" in e for e in result.errors)


def test_missing_required_check_pipeline():
    statuses = [_s("build", "success")]
    result = check_pr_ci_status(statuses, required_checks=["build", "security-scan"])
    assert result.passed is False
    assert any("security-scan" in e for e in result.errors)


def test_pending_blocks_when_configured():
    statuses = [
        _s("build", "success"),
        _s("slow-test", "pending"),
    ]
    result = check_pr_ci_status(statuses, block_on_pending=True)
    assert result.passed is False
    assert "slow-test" in result.pending_checks


def test_skipped_neutral_allowed_pipeline():
    statuses = [
        _s("build", "success"),
        _s("optional-scan", "skipped"),
        _s("docs", "neutral"),
    ]
    result = check_pr_ci_status(statuses, allow_skipped=True)
    assert result.passed is True
    assert result.errors == []
