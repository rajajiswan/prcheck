"""Tests for src/branch_parser.py"""

import pytest
from src.branch_parser import parse_branch, BranchInfo, VALID_BRANCH_TYPES


@pytest.mark.parametrize(
    "branch, expected_type, expected_ticket, expected_desc",
    [
        ("feature/PROJ-42-add-login", "feature", "PROJ-42", "add-login"),
        ("fix/ABC-1-null-pointer", "fix", "ABC-1", "null-pointer"),
        ("hotfix/critical-patch", "hotfix", None, "critical-patch"),
        ("chore/update-deps", "chore", None, "update-deps"),
        ("docs/readme-update", "docs", None, "readme-update"),
        ("release/v1-0-0", "release", None, "v1-0-0"),
        ("refs/heads/feature/XY-99-cool-thing", "feature", "XY-99", "cool-thing"),
    ],
)
def test_valid_branches(branch, expected_type, expected_ticket, expected_desc):
    info = parse_branch(branch)
    assert info.is_valid is True
    assert info.branch_type == expected_type
    assert info.ticket == expected_ticket
    assert info.description == expected_desc


@pytest.mark.parametrize(
    "branch",
    [
        "main",
        "develop",
        "random-branch",
        "Feature/uppercase-type",
        "feature/",
        "",
        None,
        "unknown/PROJ-1-something",
    ],
)
def test_invalid_branches(branch):
    info = parse_branch(branch)
    assert info.is_valid is False
    assert info.branch_type is None


def test_label_mapping():
    cases = {
        "feature/add-thing": "enhancement",
        "fix/some-bug": "bug",
        "bugfix/another-bug": "bug",
        "hotfix/urgent": "hotfix",
        "chore/cleanup": "chore",
        "docs/update-readme": "documentation",
        "refactor/simplify-logic": "refactor",
        "test/add-unit-tests": "testing",
        "release/v2-0": "release",
    }
    for branch, expected_label in cases.items():
        info = parse_branch(branch)
        assert info.label == expected_label, f"Failed for branch: {branch}"


def test_label_none_for_invalid_branch():
    info = parse_branch("main")
    assert info.label is None


def test_branch_info_raw_preserved():
    raw = "feature/PROJ-10-my-feature"
    info = parse_branch(raw)
    assert info.raw == raw


def test_all_valid_types_covered():
    for branch_type in VALID_BRANCH_TYPES:
        info = parse_branch(f"{branch_type}/some-description")
        assert info.is_valid is True
        assert info.branch_type == branch_type
