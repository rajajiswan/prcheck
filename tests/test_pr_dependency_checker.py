import pytest
from src.pr_dependency_checker import DependencyResult, check_pr_dependencies


class TestDependencyResult:
    def test_initial_state_is_passing(self):
        r = DependencyResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.blocking_prs == []
        assert r.label is None

    def test_fail_sets_passed_false(self):
        r = DependencyResult()
        r.fail("blocked")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = DependencyResult()
        r.fail("blocked by #42")
        assert "blocked by #42" in r.errors

    def test_warn_does_not_change_passed(self):
        r = DependencyResult()
        r.warn("soft dependency on #7")
        assert r.passed is True
        assert "soft dependency on #7" in r.warnings

    def test_bool_true_when_passing(self):
        assert bool(DependencyResult()) is True

    def test_bool_false_when_failed(self):
        r = DependencyResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrDependencies:
    def test_no_body_returns_passing(self):
        result = check_pr_dependencies("", [])
        assert result.passed is True
        assert result.blocking_prs == []

    def test_no_dependency_keyword_returns_passing(self):
        body = "This PR adds a new feature."
        result = check_pr_dependencies(body, [1, 2, 3])
        assert result.passed is True
        assert result.blocking_prs == []

    def test_dependency_on_closed_pr_passes(self):
        body = "Depends on #10 for the base changes."
        result = check_pr_dependencies(body, open_pr_numbers=[20, 30])
        assert result.passed is True
        assert result.blocking_prs == []

    def test_dependency_on_open_pr_fails_by_default(self):
        body = "Depends on #42"
        result = check_pr_dependencies(body, open_pr_numbers=[42])
        assert result.passed is False
        assert "#42" in result.blocking_prs
        assert any("42" in e for e in result.errors)

    def test_dependency_on_open_pr_warns_when_block_disabled(self):
        body = "depends-on #7"
        result = check_pr_dependencies(body, open_pr_numbers=[7], block_on_open=False)
        assert result.passed is True
        assert "#7" in result.blocking_prs
        assert any("7" in w for w in result.warnings)

    def test_multiple_dependencies_all_open_fails(self):
        body = "Depends on #1\nDepends on #2"
        result = check_pr_dependencies(body, open_pr_numbers=[1, 2])
        assert result.passed is False
        assert "#1" in result.blocking_prs
        assert "#2" in result.blocking_prs

    def test_multiple_dependencies_some_open(self):
        body = "Depends on #1\nDepends on #2"
        result = check_pr_dependencies(body, open_pr_numbers=[2])
        assert result.passed is False
        assert "#1" not in result.blocking_prs
        assert "#2" in result.blocking_prs

    def test_label_set_when_dependency_found(self):
        body = "Depends on #99"
        result = check_pr_dependencies(body, open_pr_numbers=[])
        assert result.label == "has-dependencies"

    def test_label_none_when_no_dependency(self):
        body = "No dependencies here."
        result = check_pr_dependencies(body, open_pr_numbers=[])
        assert result.label is None

    def test_case_insensitive_pattern(self):
        body = "DEPENDS ON #55"
        result = check_pr_dependencies(body, open_pr_numbers=[55])
        assert result.passed is False
        assert "#55" in result.blocking_prs
