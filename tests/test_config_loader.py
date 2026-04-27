"""Tests for src/config_loader.py."""

from __future__ import annotations

import pytest
import yaml

from src.config_loader import ConfigLoader, PRCheckConfig, DEFAULT_CONFIG_PATH


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_config(tmp_path, data: dict) -> str:
    cfg_file = tmp_path / "prcheck.yml"
    cfg_file.write_text(yaml.dump(data), encoding="utf-8")
    return str(cfg_file)


# ---------------------------------------------------------------------------
# PRCheckConfig defaults
# ---------------------------------------------------------------------------

class TestPRCheckConfigDefaults:
    def test_default_templates_dir(self):
        cfg = PRCheckConfig()
        assert cfg.templates_dir == ".github/pr_templates"

    def test_default_require_label(self):
        assert PRCheckConfig().require_label is True

    def test_default_enforce_sections_is_empty_list(self):
        assert PRCheckConfig().enforce_sections == []

    def test_default_fail_on_missing_template_is_false(self):
        assert PRCheckConfig().fail_on_missing_template is False

    def test_default_label_prefix_is_empty(self):
        assert PRCheckConfig().label_prefix == ""


# ---------------------------------------------------------------------------
# ConfigLoader
# ---------------------------------------------------------------------------

class TestConfigLoaderMissingFile:
    def test_returns_defaults_when_file_absent(self, tmp_path):
        loader = ConfigLoader(str(tmp_path / "nonexistent.yml"))
        cfg = loader.load()
        assert isinstance(cfg, PRCheckConfig)
        assert cfg.templates_dir == ".github/pr_templates"


class TestConfigLoaderValidFile:
    def test_loads_templates_dir(self, tmp_path):
        path = write_config(tmp_path, {"templates_dir": ".github/tmpl"})
        cfg = ConfigLoader(path).load()
        assert cfg.templates_dir == ".github/tmpl"

    def test_loads_enforce_sections(self, tmp_path):
        path = write_config(tmp_path, {"enforce_sections": ["## Summary", "## Testing"]})
        cfg = ConfigLoader(path).load()
        assert cfg.enforce_sections == ["## Summary", "## Testing"]

    def test_loads_require_label_false(self, tmp_path):
        path = write_config(tmp_path, {"require_label": False})
        cfg = ConfigLoader(path).load()
        assert cfg.require_label is False

    def test_loads_fail_on_missing_template_true(self, tmp_path):
        path = write_config(tmp_path, {"fail_on_missing_template": True})
        cfg = ConfigLoader(path).load()
        assert cfg.fail_on_missing_template is True

    def test_loads_label_prefix(self, tmp_path):
        path = write_config(tmp_path, {"label_prefix": "type:"})
        cfg = ConfigLoader(path).load()
        assert cfg.label_prefix == "type:"

    def test_invalid_yaml_root_returns_defaults(self, tmp_path):
        cfg_file = tmp_path / "prcheck.yml"
        cfg_file.write_text("- just\n- a\n- list", encoding="utf-8")
        cfg = ConfigLoader(str(cfg_file)).load()
        assert cfg.templates_dir == ".github/pr_templates"


class TestConfigLoaderEnvVar:
    def test_uses_env_var_when_no_path_given(self, tmp_path, monkeypatch):
        path = write_config(tmp_path, {"label_prefix": "scope:"})
        monkeypatch.setenv("PRCHECK_CONFIG", path)
        cfg = ConfigLoader().load()
        assert cfg.label_prefix == "scope:"

    def test_explicit_path_overrides_env_var(self, tmp_path, monkeypatch):
        env_path = write_config(tmp_path, {"label_prefix": "env:"})
        explicit_path = write_config(tmp_path / "sub", {"label_prefix": "explicit:"})
        (tmp_path / "sub").mkdir(exist_ok=True)
        monkeypatch.setenv("PRCHECK_CONFIG", env_path)
        cfg = ConfigLoader(explicit_path).load()
        assert cfg.label_prefix == "explicit:"
