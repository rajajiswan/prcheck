"""Loads and validates the prcheck action configuration from a YAML file."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = ".github/prcheck.yml"


@dataclass
class PRCheckConfig:
    templates_dir: str = ".github/pr_templates"
    enforce_sections: list[str] = field(default_factory=list)
    require_label: bool = True
    fail_on_missing_template: bool = False
    label_prefix: str = ""


class ConfigLoader:
    """Reads prcheck.yml and returns a PRCheckConfig instance."""

    def __init__(self, config_path: str | None = None) -> None:
        self._path = Path(
            config_path
            or os.environ.get("PRCHECK_CONFIG", DEFAULT_CONFIG_PATH)
        )

    def load(self) -> PRCheckConfig:
        """Load configuration from disk, returning defaults if file is absent."""
        if not self._path.exists():
            return PRCheckConfig()

        raw: Any = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return PRCheckConfig()

        return self._parse(raw)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _parse(self, data: dict[str, Any]) -> PRCheckConfig:
        return PRCheckConfig(
            templates_dir=str(
                data.get("templates_dir", ".github/pr_templates")
            ),
            enforce_sections=list(
                data.get("enforce_sections") or []
            ),
            require_label=bool(data.get("require_label", True)),
            fail_on_missing_template=bool(
                data.get("fail_on_missing_template", False)
            ),
            label_prefix=str(data.get("label_prefix", "")),
        )
