"""Tests for src/main.py entry point."""

import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, "src")

import main


@pytest.fixture()
def base_env(monkeypatch):
    monkeypatch.setenv("BRANCH_NAME", "feature/123-add-login")
    monkeypatch.setenv("PR_BODY", "## Summary\nAdded login feature.")
    monkeypatch.setenv("TEMPLATES_DIR", ".github/pr_templates")
    monkeypatch.setenv("REQUIRE_LABEL", "true")


def test_get_required_env_present(monkeypatch):
    monkeypatch.setenv("BRANCH_NAME", "feature/42-test")
    assert main.get_required_env("BRANCH_NAME") == "feature/42-test"


def test_get_required_env_missing_exits(monkeypatch):
    monkeypatch.delenv("BRANCH_NAME", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        main.get_required_env("BRANCH_NAME")
    assert exc_info.value.code == 1


def test_main_passes_valid_pr(base_env):
    mock_result = MagicMock()
    mock_result.__bool__ = lambda self: True
    mock_result.errors = []
    mock_result.warnings = []

    with patch("main.PRValidator") as MockValidator, \
         patch("main.TemplateLoader") as MockLoader, \
         patch("main.emit_outputs") as mock_emit, \
         patch("main.write_summary") as mock_summary:

        MockValidator.return_value.validate.return_value = mock_result
        MockLoader.return_value.load.return_value = "## Summary"

        main.main()

        mock_emit.assert_called_once_with(mock_result)
        mock_summary.assert_called_once_with(mock_result)


def test_main_exits_on_invalid_pr(base_env):
    mock_result = MagicMock()
    mock_result.__bool__ = lambda self: False
    mock_result.errors = ["Missing section"]
    mock_result.warnings = []

    with patch("main.PRValidator") as MockValidator, \
         patch("main.TemplateLoader") as MockLoader, \
         patch("main.emit_outputs"), \
         patch("main.write_summary"):

        MockValidator.return_value.validate.return_value = mock_result
        MockLoader.return_value.load.return_value = "## Summary"

        with pytest.raises(SystemExit) as exc_info:
            main.main()

        assert exc_info.value.code == 1


def test_main_missing_branch_name_exits(monkeypatch):
    monkeypatch.delenv("BRANCH_NAME", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        main.main()
    assert exc_info.value.code == 1
