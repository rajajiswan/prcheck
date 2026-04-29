"""Tests for pr_diff_analyzer."""
import pytest

from src.pr_diff_fetcher import PRDiff
from src.pr_diff_analyzer import DiffAnalysisResult, analyze_pr_diff


def _make_diff(files=5, additions=100, deletions=50, error=None):
    filenames = [f"file_{i}.py" for i in range(files)]
    return PRDiff(
        filenames=filenames,
        additions=additions,
        deletions=deletions,
        error=error,
    )


class TestDiffAnalysisResult:
    def test_initial_state_is_passing(self):
        r = DiffAnalysisResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []

    def test_fail_sets_passed_false(self):
        r = DiffAnalysisResult()
        r.fail("too big")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = DiffAnalysisResult()
        r.fail("err1")
        r.fail("err2")
        assert r.errors == ["err1", "err2"]

    def test_warn_does_not_fail(self):
        r = DiffAnalysisResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = DiffAnalysisResult()
        assert bool(r) is True

    def test_bool_false_when_failed(self):
        r = DiffAnalysisResult()
        r.fail("x")
        assert bool(r) is False


class TestAnalyzePrDiff:
    def test_passes_for_small_diff(self):
        diff = _make_diff(files=3, additions=50, deletions=20)
        result = analyze_pr_diff(diff)
        assert result.passed is True
        assert result.errors == []

    def test_fails_when_diff_has_error(self):
        diff = _make_diff(error="network timeout")
        result = analyze_pr_diff(diff)
        assert result.passed is False
        assert any("network timeout" in e for e in result.errors)

    def test_fails_on_too_many_files(self):
        diff = _make_diff(files=60)
        result = analyze_pr_diff(diff, max_files=50)
        assert result.passed is False
        assert any("60 files" in e for e in result.errors)

    def test_warns_on_many_files(self):
        diff = _make_diff(files=25)
        result = analyze_pr_diff(diff, max_files=50, warn_files=20)
        assert result.passed is True
        assert any("25 files" in w for w in result.warnings)

    def test_fails_on_too_many_lines(self):
        diff = _make_diff(additions=800, deletions=300)
        result = analyze_pr_diff(diff, max_lines=1000)
        assert result.passed is False
        assert any("1100 lines" in e for e in result.errors)

    def test_warns_on_many_lines(self):
        diff = _make_diff(additions=400, deletions=200)
        result = analyze_pr_diff(diff, max_lines=1000, warn_lines=500)
        assert result.passed is True
        assert any("600 lines" in w for w in result.warnings)

    def test_multiple_violations_accumulate(self):
        diff = _make_diff(files=60, additions=900, deletions=200)
        result = analyze_pr_diff(diff, max_files=50, max_lines=1000)
        assert result.passed is False
        assert len(result.errors) == 2
