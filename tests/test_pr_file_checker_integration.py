from __future__ import annotations

from src.pr_diff_fetcher import PRDiff
from src.pr_file_checker import check_pr_files


def _make_diff(files=None, error=None):
    d = PRDiff()
    d.files = files or []
    d.error = error
    return d


def test_full_pass_pipeline():
    diff = _make_diff(files=["src/main.py", "tests/test_main.py"])
    result = check_pr_files(
        diff,
        forbidden_patterns=["secrets/*", "*.pem"],
        required_patterns=["tests/*"],
        max_files=20,
    )
    assert result.passed
    assert result.errors == []
    assert result.warnings == []
    assert "tests/*" in result.matched_patterns


def test_forbidden_file_fails_pipeline():
    diff = _make_diff(files=["src/main.py", "deploy/prod.pem"])
    result = check_pr_files(
        diff,
        forbidden_patterns=["*.pem"],
        max_files=10,
    )
    assert not result
    assert len(result.errors) == 1
    assert "*.pem" in result.matched_patterns


def test_missing_required_warns_pipeline():
    diff = _make_diff(files=["src/utils.py"])
    result = check_pr_files(
        diff,
        required_patterns=["tests/*"],
    )
    assert result.passed  # warnings don't fail
    assert any("tests/*" in w for w in result.warnings)


def test_fetch_error_propagates_pipeline():
    diff = _make_diff(error="403 Forbidden")
    result = check_pr_files(diff, forbidden_patterns=["secrets/*"], max_files=5)
    assert not result
    assert any("403 Forbidden" in e for e in result.errors)
