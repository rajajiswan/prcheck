from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class MentionResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mentions_found: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


_MENTION_RE = re.compile(r"@([A-Za-z0-9_-]+)")


def check_pr_mentions(
    body: str,
    *,
    require_mention: bool = False,
    blocked_users: List[str] | None = None,
    max_mentions: int | None = None,
) -> MentionResult:
    """Inspect a PR body for @mentions.

    Args:
        body: The raw PR description text.
        require_mention: When True the PR must contain at least one @mention.
        blocked_users: List of usernames that must not be mentioned.
        max_mentions: If set, fail when the total mention count exceeds this.

    Returns:
        A :class:`MentionResult` describing the outcome.
    """
    result = MentionResult()
    blocked_users = [u.lstrip("@").lower() for u in (blocked_users or [])]

    mentions = _MENTION_RE.findall(body or "")
    result.mentions_found = mentions

    if require_mention and not mentions:
        result.fail("PR description must contain at least one @mention.")

    for user in mentions:
        if user.lower() in blocked_users:
            result.fail(f"Mention of blocked user '@{user}' is not allowed.")

    if max_mentions is not None and len(mentions) > max_mentions:
        result.fail(
            f"PR contains {len(mentions)} @mentions but the maximum allowed is {max_mentions}."
        )

    if mentions and not require_mention and not result.errors:
        if len(mentions) > 5:  # noqa: PLR2004
            result.warn(f"PR mentions {len(mentions)} users — consider reducing noise.")

    return result
