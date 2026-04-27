"""Integration tests: run_checks with real sub-modules (no mocks)."""

import pytest

from src.run_checks import run_checks
from src.branch_parser import BranchInfo
from src.config_loader import PRCheckConfig


@pytest.fixture
def templates_dir(tmp_path):
    (tmp_path / "feature.md").write_text(
        "## Summary\n\nDescribe your change.\n\n## Checklist\n- [ ] Tests added\n"
    )
    return tmp_path


@pytest.fixture
def feature_branch():
    return BranchInfo(type="feature", ticket="PROJ-42", description="login", raw="feature/PROJ-42-login")


def test_full_pass(feature_branch, templates_dir):
    config = PRCheckConfig(
        templates_dir=str(templates_dir),
        require_label=True,
        enforce_sections=["## Summary"],
    )
    suite = run_checks(
        branch=feature_branch,
        pr_body="## Summary\nAdded login flow.\n",
        applied_labels=["feature"],
        config=config,
    )
    assert suite.passed is True
    assert suite.errors == []


def test_missing_section_fails(feature_branch, templates_dir):
    config = PRCheckConfig(
        templates_dir=str(templates_dir),
        require_label=False,
        enforce_sections=["## Summary"],
    )
    suite = run_checks(
        branch=feature_branch,
        pr_body="No summary header here.",
        applied_labels=[],
        config=config,
    )
    assert suite.passed is False
    assert any("Summary" in e for e in suite.errors)


def test_missing_label_fails(feature_branch, templates_dir):
    config = PRCheckConfig(
        templates_dir=str(templates_dir),
        require_label=True,
        enforce_sections=[],
    )
    suite = run_checks(
        branch=feature_branch,
        pr_body="anything",
        applied_labels=[],
        config=config,
    )
    assert suite.passed is False
    assert suite.label_result is not None


def test_no_label_check_when_disabled(feature_branch, templates_dir):
    config = PRCheckConfig(
        templates_dir=str(templates_dir),
        require_label=False,
        enforce_sections=[],
    )
    suite = run_checks(
        branch=feature_branch,
        pr_body="anything",
        applied_labels=[],
        config=config,
    )
    assert suite.label_result is None
