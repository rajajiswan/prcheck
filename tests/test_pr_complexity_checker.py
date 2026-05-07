from __future__ import annotations

import pytest

from src.pr_complexity_checker import ComplexityResult, check_pr_complexity
from src.pr_diff_fetcher import PRDiff


def _make_diff(
    files: list[str] | None = None,
    additions: int = 0,
    deletions: int = 0,
    error: str | None = None,
) -> PRDiff:
    return PRDiff(
        files=files or [],
        additions=additions,
        deletions=deletions,
        error=error,
    )


class TestComplexityResult:
    def test_initial_state_is_passing(self):
        r = ComplexityResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.score == 0
        assert r.label is None

    def test_fail_sets_passed_false(self):
        r = ComplexityResult()
        r.fail("too complex")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ComplexityResult()
        r.fail("msg1")
        r.fail("msg2")
        assert r.errors == ["msg1", "msg2"]

    def test_warn_does_not_change_passed(self):
        r = ComplexityResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(ComplexityResult()) is True

    def test_bool_false_after_fail(self):
        r = ComplexityResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrComplexity:
    def test_low_complexity_passes_with_low_label(self):
        diff = _make_diff(files=["a.py"], additions=5, deletions=2)
        result = check_pr_complexity(diff)
        assert result.passed is True
        assert result.label == "complexity: low"
        assert result.errors == []

    def test_score_calculation(self):
        # score = 1*2 + 10*1 + 5*1 = 17
        diff = _make_diff(files=["a.py"], additions=10, deletions=5)
        result = check_pr_complexity(diff, file_weight=2, addition_weight=1, deletion_weight=1)
        assert result.score == 17

    def test_warn_threshold_triggers_warning(self):
        # score = 2*2 + 30*1 + 10*1 = 44; warn_threshold=40
        diff = _make_diff(files=["a.py", "b.py"], additions=30, deletions=10)
        result = check_pr_complexity(diff, warn_threshold=40, max_score=100)
        assert result.passed is True
        assert len(result.warnings) == 1
        assert result.label == "complexity: medium"

    def test_exceeds_max_score_fails(self):
        # score = 5*2 + 50*1 + 20*1 = 80; max_score=50
        diff = _make_diff(
            files=["a.py", "b.py", "c.py", "d.py", "e.py"],
            additions=50,
            deletions=20,
        )
        result = check_pr_complexity(diff, max_score=50, warn_threshold=30)
        assert result.passed is False
        assert len(result.errors) == 1
        assert result.label == "complexity: high"

    def test_fetch_error_fails_immediately(self):
        diff = _make_diff(error="network timeout")
        result = check_pr_complexity(diff)
        assert result.passed is False
        assert "network timeout" in result.errors[0]

    def test_empty_diff_passes_with_low_label(self):
        diff = _make_diff()
        result = check_pr_complexity(diff)
        assert result.passed is True
        assert result.score == 0
        assert result.label == "complexity: low"
