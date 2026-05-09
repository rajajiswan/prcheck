"""Integration tests: scope checker + reporter through the full pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from unittest.mock import patch

from src.pr_scope_checker import check_pr_scope
from src.scope_reporter import report_scope_result


@dataclass
class _FakeDiff:
    files: List[str] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None


def test_full_pass_pipeline():
    diff = _FakeDiff(files=["src/foo.py", "src/bar.py"])
    result = check_pr_scope(diff, allowed_patterns=["src/*.py"])
    assert result.passed is True
    with patch("src.scope_reporter.set_output") as mock_out, \
         patch("src.scope_reporter.write_summary"):
        report_scope_result(result)
    mock_out.assert_any_call("scope_passed", "true")
    mock_out.assert_any_call("scope_errors", "0")


def test_forbidden_file_fails_pipeline():
    diff = _FakeDiff(files=["src/main.py", "secrets/token.txt"])
    result = check_pr_scope(diff, forbidden_patterns=["secrets/*"])
    assert not result
    assert "secrets/token.txt" in result.out_of_scope_files
    with patch("src.scope_reporter.set_output") as mock_out, \
         patch("src.scope_reporter.write_summary"):
        report_scope_result(result)
    mock_out.assert_any_call("scope_passed", "false")


def test_out_of_allowed_scope_fails_pipeline():
    diff = _FakeDiff(files=["src/main.py", "infra/terraform.tf"])
    result = check_pr_scope(diff, allowed_patterns=["src/*.py"])
    assert not result
    assert "infra/terraform.tf" in result.out_of_scope_files


def test_warn_only_full_pipeline():
    diff = _FakeDiff(files=["infra/terraform.tf"])
    result = check_pr_scope(diff, allowed_patterns=["src/*.py"], warn_only=True)
    assert result.passed is True
    assert result.warnings
    with patch("src.scope_reporter.set_output") as mock_out, \
         patch("src.scope_reporter.write_summary"):
        report_scope_result(result)
    mock_out.assert_any_call("scope_passed", "true")
    mock_out.assert_any_call("scope_warnings", "1")


def test_fetch_error_propagates_pipeline():
    diff = _FakeDiff(ok=False, error="API rate limit")
    result = check_pr_scope(diff)
    assert not result
    assert any("API rate limit" in e for e in result.errors)
