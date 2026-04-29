"""Loads prcheck configuration from a YAML file."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class PRCheckConfig:
    templates_dir: str = ".github/pr_templates"
    require_label: bool = True
    enforce_sections: List[str] = field(default_factory=list)
    post_comment_on_failure: bool = False
    max_retries: int = 3


class ConfigLoader:
    DEFAULT_PATH = ".github/prcheck.yml"

    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.environ.get("PRCHECK_CONFIG", self.DEFAULT_PATH)

    def load(self) -> PRCheckConfig:
        if not os.path.exists(self.path):
            return PRCheckConfig()
        with open(self.path, "r") as fh:
            raw = fh.read()
        return self._parse(raw)

    def _parse(self, raw: str) -> PRCheckConfig:
        if yaml is None:  # pragma: no cover
            raise RuntimeError("PyYAML is required to parse config files")
        data = yaml.safe_load(raw) or {}
        cfg = PRCheckConfig()
        cfg.templates_dir = data.get("templates_dir", cfg.templates_dir)
        cfg.require_label = data.get("require_label", cfg.require_label)
        cfg.enforce_sections = data.get("enforce_sections", cfg.enforce_sections)
        cfg.post_comment_on_failure = data.get(
            "post_comment_on_failure", cfg.post_comment_on_failure
        )
        cfg.max_retries = data.get("max_retries", cfg.max_retries)
        return cfg
