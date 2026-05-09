from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ContributorResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    author: Optional[str] = None
    is_first_time: bool = False

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_contributor(
    author: Optional[str],
    collaborators: List[str],
    org_members: List[str],
    require_org_member: bool = False,
    require_collaborator: bool = False,
    warn_first_time: bool = True,
    blocked_users: Optional[List[str]] = None,
) -> ContributorResult:
    result = ContributorResult(author=author)
    blocked = blocked_users or []

    if not author:
        result.fail("PR author is missing or unknown.")
        return result

    if author in blocked:
        result.fail(f"Author '{author}' is on the blocked contributors list.")
        return result

    if require_org_member and author not in org_members:
        result.fail(
            f"Author '{author}' is not a member of the required organisation."
        )

    if require_collaborator and author not in collaborators:
        result.fail(
            f"Author '{author}' is not listed as a repository collaborator."
        )

    if warn_first_time and author not in collaborators and author not in org_members:
        result.is_first_time = True
        result.warn(
            f"'{author}' appears to be a first-time contributor — please review carefully."
        )

    return result
