from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CommitResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    commit_count: int = 0
    non_conventional_commits: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


# Conventional Commits pattern: type(scope)!: description
_CONVENTIONAL_RE = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\(.+\))?!?:\s.+",
    re.IGNORECASE,
)


def check_pr_commits(
    commits: List[str],
    require_conventional: bool = False,
    max_commits: Optional[int] = None,
    min_commits: int = 1,
) -> CommitResult:
    """Validate a list of commit message subjects against project rules."""
    result = CommitResult(commit_count=len(commits))

    if len(commits) < min_commits:
        result.fail(
            f"PR must have at least {min_commits} commit(s); found {len(commits)}."
        )

    if max_commits is not None and len(commits) > max_commits:
        result.fail(
            f"PR exceeds maximum allowed commits ({max_commits}); found {len(commits)}."
        )

    if require_conventional:
        for msg in commits:
            subject = msg.splitlines()[0].strip()
            if not _CONVENTIONAL_RE.match(subject):
                result.non_conventional_commits.append(subject)

        if result.non_conventional_commits:
            bad = ", ".join(f'"{m}"' for m in result.non_conventional_commits)
            result.fail(
                f"The following commit(s) do not follow Conventional Commits: {bad}."
            )

    return result
