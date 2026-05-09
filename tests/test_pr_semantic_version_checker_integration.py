"""Integration tests for the semantic version checker pipeline."""
from src.pr_semantic_version_checker import check_pr_semantic_version


def test_full_pass_pipeline():
    result = check_pr_semantic_version(
        pr_body="Bumps library to 1.4.0 — see changelog.",
        pr_title="chore(deps): update to 1.4.0",
        require_version_bump=True,
        allowed_bump_types=["minor"],
        version_file_contents="__version__ = '1.3.9'",
    )
    assert result.passed is True
    assert result.detected_version == "1.4.0"
    assert result.errors == []


def test_missing_version_fails_pipeline():
    result = check_pr_semantic_version(
        pr_body="Just a fix, no version mention.",
        pr_title="fix: correct typo",
        require_version_bump=True,
    )
    assert result.passed is False
    assert any("required" in e for e in result.errors)


def test_disallowed_bump_fails_pipeline():
    result = check_pr_semantic_version(
        pr_body="Breaking change bumps to 3.0.0",
        pr_title="feat!: redesign API",
        require_version_bump=True,
        allowed_bump_types=["patch", "minor"],
        version_file_contents="version=2.9.9",
    )
    assert result.passed is False
    assert any("major" in e for e in result.errors)


def test_no_version_warns_but_passes_pipeline():
    result = check_pr_semantic_version(
        pr_body="Small cleanup.",
        pr_title="chore: lint",
        require_version_bump=False,
    )
    assert result.passed is True
    assert any("No semantic version" in w for w in result.warnings)
