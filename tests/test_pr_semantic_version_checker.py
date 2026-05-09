"""Unit tests for pr_semantic_version_checker."""
import pytest
from src.pr_semantic_version_checker import (
    SemverResult,
    check_pr_semantic_version,
    _classify_bump,
)


class TestSemverResult:
    def test_initial_state_is_passing(self):
        r = SemverResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.detected_version is None

    def test_fail_sets_passed_false(self):
        r = SemverResult()
        r.fail("oops")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = SemverResult()
        r.fail("e1")
        r.fail("e2")
        assert r.errors == ["e1", "e2"]

    def test_warn_does_not_change_passed(self):
        r = SemverResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(SemverResult()) is True

    def test_bool_false_when_failed(self):
        r = SemverResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrSemanticVersion:
    def test_detects_version_in_title(self):
        r = check_pr_semantic_version("some body", "Release 2.3.4")
        assert r.passed is True
        assert r.detected_version == "2.3.4"

    def test_detects_version_in_body(self):
        r = check_pr_semantic_version("Bumps to 0.1.0", "chore: deps")
        assert r.detected_version == "0.1.0"

    def test_no_version_warns_when_not_required(self):
        r = check_pr_semantic_version("no version here", "fix: typo")
        assert r.passed is True
        assert any("No semantic version" in w for w in r.warnings)

    def test_no_version_fails_when_required(self):
        r = check_pr_semantic_version(
            "no version here", "fix: typo", require_version_bump=True
        )
        assert r.passed is False
        assert any("required" in e for e in r.errors)

    def test_allowed_bump_type_passes(self):
        r = check_pr_semantic_version(
            "bump to 1.1.0",
            "feat: new thing",
            allowed_bump_types=["minor"],
            version_file_contents="version = 1.0.0",
        )
        assert r.passed is True

    def test_disallowed_bump_type_fails(self):
        r = check_pr_semantic_version(
            "bump to 2.0.0",
            "feat!: breaking",
            allowed_bump_types=["patch", "minor"],
            version_file_contents="version = 1.9.9",
        )
        assert r.passed is False
        assert any("major" in e for e in r.errors)


class TestClassifyBump:
    def test_major(self):
        assert _classify_bump((1, 0, 0), (2, 0, 0)) == "major"

    def test_minor(self):
        assert _classify_bump((1, 0, 0), (1, 1, 0)) == "minor"

    def test_patch(self):
        assert _classify_bump((1, 0, 0), (1, 0, 1)) == "patch"

    def test_no_change(self):
        assert _classify_bump((1, 2, 3), (1, 2, 3)) is None
