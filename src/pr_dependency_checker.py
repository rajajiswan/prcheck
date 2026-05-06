from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DependencyResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    blocking_prs: List[str] = field(default_factory=list)
    label: Optional[str] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_dependencies(
    pr_body: str,
    open_pr_numbers: List[int],
    *,
    block_on_open: bool = True,
    dependency_pattern: str = r"(?i)depends[- ]on\s+#(\d+)",
) -> DependencyResult:
    """Check whether a PR declares dependencies on other PRs and if those are still open."""
    import re

    result = DependencyResult()

    if not pr_body or not pr_body.strip():
        return result

    matches = re.findall(dependency_pattern, pr_body)
    if not matches:
        return result

    referenced = [int(m) for m in matches]
    result.label = "has-dependencies"

    open_set = set(open_pr_numbers)
    for pr_num in referenced:
        if pr_num in open_set:
            result.blocking_prs.append(f"#{pr_num}")
            if block_on_open:
                result.fail(f"Depends on open PR #{pr_num} which has not been merged yet.")
            else:
                result.warn(f"Depends on open PR #{pr_num} which has not been merged yet.")

    return result
