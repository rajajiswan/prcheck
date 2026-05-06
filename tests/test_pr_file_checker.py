from __future__ import annotations

import pytest

from src.pr_diff_fetcher import PRDiff
from src.pr_file_checker import FileCheckResult, check_pr_files


def _make_diff(files=None, error=None):
    d = PRDiff()
    d.files = files or []
    d.error = error
    return d


class TestFileCheckResult:
    def test_initial_state_is_passing(self):
        r = FileCheckResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.matched_patterns == []

    def test_fail_sets_passed_false(self):
        r = FileCheckResult()
        r.fail("bad file")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = FileCheckResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_change_passed(self):
        r = FileCheckResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(FileCheckResult()) is True

    def test_bool_false_when_failing(self):
        r = FileCheckResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrFiles:
    def test_diff_error_fails(self):
        diff = _make_diff(error="network error")
        result = check_pr_files(diff)
        assert not result
        assert any("network error" in e for e in result.errors)

    def test_within_max_files_passes(self):
        diff = _make_diff(files=["a.py", "b.py"])
        result = check_pr_files(diff, max_files=5)
        assert result.passed

    def test_exceeds_max_files_fails(self):
        diff = _make_diff(files=[f"file{i}.py" for i in range(10)])
        result = check_pr_files(diff, max_files=5)
        assert not result
        assert any("10 files" in e for e in result.errors)

    def test_forbidden_pattern_match_fails(self):
        diff = _make_diff(files=["secrets/prod.env", "src/main.py"])
        result = check_pr_files(diff, forbidden_patterns=["secrets/*"])
        assert not result
        assert "secrets/*" in result.matched_patterns

    def test_no_forbidden_match_passes(self):
        diff = _make_diff(files=["src/main.py", "README.md"])
        result = check_pr_files(diff, forbidden_patterns=["secrets/*"])
        assert result.passed

    def test_required_pattern_present_warns_not(self):
        diff = _make_diff(files=["tests/test_foo.py"])
        result = check_pr_files(diff, required_patterns=["tests/*"])
        assert result.passed
        assert "tests/*" in result.matched_patterns
        assert result.warnings == []

    def test_required_pattern_missing_warns(self):
        diff = _make_diff(files=["src/foo.py"])
        result = check_pr_files(diff, required_patterns=["tests/*"])
        assert result.passed  # warning only
        assert any("tests/*" in w for w in result.warnings)

    def test_empty_diff_with_no_rules_passes(self):
        diff = _make_diff(files=[])
        result = check_pr_files(diff)
        assert result.passed
