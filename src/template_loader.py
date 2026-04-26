"""Template loader for PR description templates.

Loads and renders Markdown templates based on branch type,
supporting variable substitution for branch metadata.
"""

import os
import re
from pathlib import Path
from typing import Optional

from branch_parser import BranchInfo

# Default templates directory relative to this file
DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / ".github" / "pr_templates"

# Fallback template used when no matching template is found
FALLBACK_TEMPLATE = """## Description

<!-- Describe your changes -->

## Checklist

- [ ] Tests added or updated
- [ ] Documentation updated
"""


class TemplateLoader:
    """Loads PR description templates from a directory.

    Templates are Markdown files named after branch types,
    e.g. ``feature.md``, ``bugfix.md``, ``hotfix.md``.

    Variable substitution uses ``{{variable}}`` syntax and supports
    the following placeholders:

    - ``{{branch_type}}``  — e.g. ``feature``
    - ``{{ticket_id}}``    — e.g. ``PROJ-123`` (empty string if absent)
    - ``{{description}}``  — slugified description segment of the branch
    - ``{{branch_name}}``  — the full raw branch name
    """

    def __init__(self, templates_dir: Optional[Path] = None) -> None:
        self.templates_dir = Path(templates_dir) if templates_dir else DEFAULT_TEMPLATES_DIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, branch_info: BranchInfo) -> str:
        """Return the rendered template for *branch_info*.

        Falls back to :data:`FALLBACK_TEMPLATE` when no matching file
        is found in the templates directory.

        Args:
            branch_info: Parsed branch metadata produced by
                :func:`branch_parser.parse_branch`.

        Returns:
            A Markdown string ready to be used as a PR body.
        """
        raw = self._read_template(branch_info.branch_type)
        return self._render(raw, branch_info)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_template(self, branch_type: Optional[str]) -> str:
        """Read the template file for *branch_type*, or return the fallback."""
        if not branch_type:
            return FALLBACK_TEMPLATE

        candidate = self.templates_dir / f"{branch_type}.md"
        if candidate.is_file():
            try:
                return candidate.read_text(encoding="utf-8")
            except OSError:
                # Unreadable file — fall through to fallback
                pass

        # Try a generic "default.md" in the templates directory
        default = self.templates_dir / "default.md"
        if default.is_file():
            try:
                return default.read_text(encoding="utf-8")
            except OSError:
                pass

        return FALLBACK_TEMPLATE

    @staticmethod
    def _render(template: str, branch_info: BranchInfo) -> str:
        """Replace ``{{variable}}`` placeholders with values from *branch_info*."""
        variables = {
            "branch_type": branch_info.branch_type or "",
            "ticket_id": branch_info.ticket_id or "",
            "description": branch_info.description or "",
            "branch_name": branch_info.raw,
        }

        def replacer(match: re.Match) -> str:  # type: ignore[type-arg]
            key = match.group(1).strip()
            return variables.get(key, match.group(0))  # leave unknown vars intact

        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replacer, template)
