"""Tests for action_output helpers."""

import importlib
import os
from pathlib import Path

import pytest

from src.pr_validator import ValidationResult
import src.action_output as action_output


@pytest.fixture(autouse=True)
def reset_module_env(tmp_path, monkeypatch):
    """Point GITHUB_OUTPUT and GITHUB_STEP_SUMMARY to temp files."""
    out_file = tmp_path / "output.txt"
    summary_file = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out_file))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
    # Reload so module-level constants pick up new env vars
    importlib.reload(action_output)
    yield out_file, summary_file


def test_set_output_writes_to_file(reset_module_env):
    out_file, _ = reset_module_env
    action_output.set_output("valid", "true")
    assert "valid=true" in out_file.read_text()


def test_emit_outputs_valid_result(reset_module_env):
    out_file, _ = reset_module_env
    result = ValidationResult(valid=True)
    action_output.emit_outputs(result)
    content = out_file.read_text()
    assert "valid=true" in content
    assert "error_count=0" in content
    assert "warning_count=0" in content


def test_emit_outputs_invalid_result(reset_module_env):
    out_file, _ = reset_module_env
    result = ValidationResult(valid=False, errors=["Missing section"], warnings=["Short body"])
    action_output.emit_outputs(result)
    content = out_file.read_text()
    assert "valid=false" in content
    assert "error_count=1" in content
    assert "warning_count=1" in content
    assert "first_error=Missing section" in content


def test_write_summary_passed(reset_module_env):
    _, summary_file = reset_module_env
    result = ValidationResult(valid=True)
    action_output.write_summary(result, "feature/PROJ-1/my-feature")
    content = summary_file.read_text()
    assert "✅" in content
    assert "feature/PROJ-1/my-feature" in content


def test_write_summary_failed_includes_errors(reset_module_env):
    _, summary_file = reset_module_env
    result = ValidationResult(valid=False, errors=["Label missing"], warnings=["Short body"])
    action_output.write_summary(result, "bugfix/PROJ-2/fix")
    content = summary_file.read_text()
    assert "❌" in content
    assert "Label missing" in content
    assert "Short body" in content
