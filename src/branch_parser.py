"""Parse branch names to extract type, ticket, and description."""

import re
from dataclasses import dataclass
from typing import Optional

# Conventional branch naming: <type>/<ticket>-<description> or <type>/<description>
BRANCH_PATTERN = re.compile(
    r"^(?P<type>feature|fix|bugfix|hotfix|chore|docs|refactor|test|release)"
    r"[/\-](?:(?P<ticket>[A-Z]+-\d+)[/\-])?(?P<description>[a-z0-9][a-z0-9\-]*)$"
)

VALID_BRANCH_TYPES = (
    "feature",
    "fix",
    "bugfix",
    "hotfix",
    "chore",
    "docs",
    "refactor",
    "test",
    "release",
)


@dataclass
class BranchInfo:
    """Structured information extracted from a branch name."""

    raw: str
    branch_type: Optional[str] = None
    ticket: Optional[str] = None
    description: Optional[str] = None
    is_valid: bool = False

    @property
    def label(self) -> Optional[str]:
        """Return the GitHub label corresponding to the branch type."""
        label_map = {
            "feature": "enhancement",
            "fix": "bug",
            "bugfix": "bug",
            "hotfix": "hotfix",
            "chore": "chore",
            "docs": "documentation",
            "refactor": "refactor",
            "test": "testing",
            "release": "release",
        }
        return label_map.get(self.branch_type) if self.branch_type else None


def parse_branch(branch_name: str) -> BranchInfo:
    """Parse a branch name and return a BranchInfo instance.

    Args:
        branch_name: The full branch name (e.g. 'feature/PROJ-123-add-login').

    Returns:
        BranchInfo with extracted fields and validity flag.
    """
    if not branch_name or not isinstance(branch_name, str):
        return BranchInfo(raw=branch_name or "")

    # Strip common remote prefixes
    name = branch_name.strip().removeprefix("refs/heads/")

    match = BRANCH_PATTERN.match(name)
    if not match:
        return BranchInfo(raw=name, is_valid=False)

    return BranchInfo(
        raw=name,
        branch_type=match.group("type"),
        ticket=match.group("ticket"),
        description=match.group("description"),
        is_valid=True,
    )
