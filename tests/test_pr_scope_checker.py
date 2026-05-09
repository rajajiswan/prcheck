"""Unit tests for pr_scope_checker."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from src.pr_scope_checker import ScopeResult, check_pr_scope


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@dataclass
class _FakeDiff:
    files: List[str] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None


def _make_diff(files=None, ok=True, error=None):
    return _FakeDiff(files=files or [], ok=ok, error=error)


# ---------------------------------------------------------------------------
# ScopeResult unit tests
# ---------------------------------------------------------------------------

class TestScopeResult:
    def test_initial_state_is_passing(self):
        r = ScopeResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.out_of_scope_files == []

    def test_fail_sets_passed_false(self):
        r = ScopeResult()
        r.fail("bad file")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ScopeResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = ScopeResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(ScopeResult()) is True

    def test_bool_false_after_fail(self):
        r = ScopeResult()
        r.fail("x")
        assert bool(r) is False


# ---------------------------------------------------------------------------
# check_pr_scope tests
# ---------------------------------------------------------------------------

def test_diff_fetch_error_fails():
    diff = _make_diff(ok=False, error="network timeout")
    result = check_pr_scope(diff)
    assert not result
    assert any("network timeout" in e for e in result.errors)


def test_no_files_warns():
    diff = _make_diff(files=[])
    result = check_pr_scope(diff)
    assert result.passed is True
    assert result.warnings


def test_allowed_patterns_pass():
    diff = _make_diff(files=["src/foo.py", "src/bar.py"])
    result = check_pr_scope(diff, allowed_patterns=["src/*.py"])
    assert result.passed is True
    assert result.out_of_scope_files == []


def test_allowed_patterns_fail_on_mismatch():
    diff = _make_diff(files=["src/foo.py", "docs/readme.md"])
    result = check_pr_scope(diff, allowed_patterns=["src/*.py"])
    assert not result
    assert "docs/readme.md" in result.out_of_scope_files


def test_forbidden_patterns_fail():
    diff = _make_diff(files=["src/foo.py", "secrets/key.pem"])
    result = check_pr_scope(diff, forbidden_patterns=["secrets/*"])
    assert not result
    assert "secrets/key.pem" in result.out_of_scope_files


def test_forbidden_patterns_clean_passes():
    diff = _make_diff(files=["src/foo.py"])
    result = check_pr_scope(diff, forbidden_patterns=["secrets/*"])
    assert result.passed is True


def test_warn_only_mode_does_not_fail():
    diff = _make_diff(files=["docs/readme.md"])
    result = check_pr_scope(diff, allowed_patterns=["src/*.py"], warn_only=True)
    assert result.passed is True
    assert result.warnings
    assert "docs/readme.md" in result.out_of_scope_files


def test_forbidden_warn_only():
    diff = _make_diff(files=["secrets/key.pem"])
    result = check_pr_scope(diff, forbidden_patterns=["secrets/*"], warn_only=True)
    assert result.passed is True
    assert result.warnings
