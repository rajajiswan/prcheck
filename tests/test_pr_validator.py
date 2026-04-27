"""Tests for PRValidator and ValidationResult."""

import pytest

from src.branch_parser import BranchInfo
from src.pr_validator import PRValidator, ValidationResult


VALID_BODY = "## Description\nThis PR adds a new feature.\n\n## Changes\n- Added X\n- Updated Y"


@pytest.fixture
def feature_branch_info():
    return BranchInfo(type="feature", ticket="PROJ-42", description="add-login", label="feature", raw="feature/PROJ-42/add-login")


@pytest.fixture
def unknown_branch_info():
    return BranchInfo(type=None, ticket=None, description=None, label=None, raw="random-branch")


class TestValidationResult:
    def test_initial_state_is_valid(self):
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error_marks_invalid(self):
        result = ValidationResult(valid=True)
        result.add_error("something went wrong")
        assert result.valid is False
        assert "something went wrong" in result.errors

    def test_add_warning_does_not_invalidate(self):
        result = ValidationResult(valid=True)
        result.add_warning("heads up")
        assert result.valid is True
        assert "heads up" in result.warnings

    def test_bool_reflects_valid(self):
        assert bool(ValidationResult(valid=True)) is True
        assert bool(ValidationResult(valid=False)) is False


class TestPRValidator:
    def test_valid_pr_passes(self, feature_branch_info):
        validator = PRValidator(feature_branch_info, VALID_BODY, ["feature"])
        result = validator.validate()
        assert result.valid is True
        assert result.errors == []

    def test_empty_body_fails(self, feature_branch_info):
        validator = PRValidator(feature_branch_info, "", ["feature"])
        result = validator.validate()
        assert result.valid is False
        assert any("empty" in e for e in result.errors)

    def test_missing_section_fails(self, feature_branch_info):
        body = "## Description\nSome description without changes section."
        validator = PRValidator(feature_branch_info, body, ["feature"])
        result = validator.validate()
        assert result.valid is False
        assert any("## Changes" in e for e in result.errors)

    def test_missing_label_fails(self, feature_branch_info):
        validator = PRValidator(feature_branch_info, VALID_BODY, ["bugfix"])
        result = validator.validate()
        assert result.valid is False
        assert any("feature" in e for e in result.errors)

    def test_unknown_branch_label_warns(self, unknown_branch_info):
        validator = PRValidator(unknown_branch_info, VALID_BODY, [])
        result = validator.validate()
        assert any("label" in w for w in result.warnings)

    def test_short_body_warns(self, feature_branch_info):
        body = "## Description\nOK\n\n## Changes\nX"
        validator = PRValidator(feature_branch_info, body, ["feature"])
        result = validator.validate()
        assert any("short" in w for w in result.warnings)

    def test_none_body_treated_as_empty(self, feature_branch_info):
        validator = PRValidator(feature_branch_info, None, ["feature"])
        result = validator.validate()
        assert result.valid is False
