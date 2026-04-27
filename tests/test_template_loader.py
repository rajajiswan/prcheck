"""Tests for the TemplateLoader class."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from src.template_loader import TemplateLoader
from src.branch_parser import BranchInfo


@pytest.fixture
def templates_dir(tmp_path):
    """Create a temporary templates directory with sample templates."""
    templates = tmp_path / "templates"
    templates.mkdir()

    # Feature template
    feature_tmpl = templates / "feature.md"
    feature_tmpl.write_text(
        "## Summary\n"
        "{{ description }}\n\n"
        "## Type\n"
        "Feature: `{{ ticket }}`\n\n"
        "## Checklist\n"
        "- [ ] Tests added\n"
        "- [ ] Docs updated\n"
    )

    # Bugfix template
    bugfix_tmpl = templates / "bugfix.md"
    bugfix_tmpl.write_text(
        "## Bug Fix\n"
        "Ticket: `{{ ticket }}`\n\n"
        "## Root Cause\n"
        "{{ description }}\n\n"
        "## Checklist\n"
        "- [ ] Regression test added\n"
    )

    # Default template
    default_tmpl = templates / "default.md"
    default_tmpl.write_text(
        "## Description\n"
        "{{ description }}\n"
    )

    return templates


@pytest.fixture
def feature_branch():
    return BranchInfo(
        raw="feature/PROJ-42-add-login",
        type="feature",
        ticket="PROJ-42",
        description="add login",
    )


@pytest.fixture
def bugfix_branch():
    return BranchInfo(
        raw="bugfix/PROJ-99-fix-crash",
        type="bugfix",
        ticket="PROJ-99",
        description="fix crash",
    )


@pytest.fixture
def unknown_branch():
    return BranchInfo(
        raw="random-branch",
        type=None,
        ticket=None,
        description=None,
    )


class TestTemplateLoaderInit:
    def test_init_with_valid_dir(self, templates_dir):
        loader = TemplateLoader(templates_dir=str(templates_dir))
        assert loader.templates_dir == Path(templates_dir)

    def test_init_with_default_dir(self):
        loader = TemplateLoader()
        assert loader.templates_dir is not None

    def test_init_with_missing_dir_raises(self, tmp_path):
        missing = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            TemplateLoader(templates_dir=str(missing))


class TestTemplateLoaderLoad:
    def test_load_feature_template(self, templates_dir, feature_branch):
        loader = TemplateLoader(templates_dir=str(templates_dir))
        result = loader.load(feature_branch)
        assert "PROJ-42" in result
        assert "add login" in result
        assert "Tests added" in result

    def test_load_bugfix_template(self, templates_dir, bugfix_branch):
        loader = TemplateLoader(templates_dir=str(templates_dir))
        result = loader.load(bugfix_branch)
        assert "PROJ-99" in result
        assert "fix crash" in result
        assert "Regression test added" in result

    def test_load_falls_back_to_default(self, templates_dir, unknown_branch):
        loader = TemplateLoader(templates_dir=str(templates_dir))
        result = loader.load(unknown_branch)
        assert result is not None
        assert len(result) > 0

    def test_load_returns_none_when_no_template_and_no_default(self, tmp_path, unknown_branch):
        empty_dir = tmp_path / "empty_templates"
        empty_dir.mkdir()
        loader = TemplateLoader(templates_dir=str(empty_dir))
        result = loader.load(unknown_branch)
        assert result is None

    def test_load_renders_ticket_placeholder(self, templates_dir, feature_branch):
        loader = TemplateLoader(templates_dir=str(templates_dir))
        result = loader.load(feature_branch)
        assert "{{ ticket }}" not in result

    def test_load_renders_description_placeholder(self, templates_dir, feature_branch):
        loader = TemplateLoader(templates_dir=str(templates_dir))
        result = loader.load(feature_branch)
        assert "{{ description }}" not in result

    def test_load_handles_none_ticket_gracefully(self, templates_dir):
        branch = BranchInfo(
            raw="feature/no-ticket-branch",
            type="feature",
            ticket=None,
            description="no ticket branch",
        )
        loader = TemplateLoader(templates_dir=str(templates_dir))
        result = loader.load(branch)
        assert result is not None
