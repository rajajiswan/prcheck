"""Determines whether a failure comment should be posted to a PR."""
from dataclasses import dataclass, field
from typing import Optional

from src.run_checks import CheckSuite
from src.pr_comment_poster import post_failure_comment, CommentResult
from src.config_loader import PRCheckConfig


@dataclass
class CommentEnforcementResult:
    posted: bool = False
    skipped: bool = False
    skip_reason: str = ""
    comment_result: Optional[CommentResult] = None
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


def enforce_pr_comment(
    suite: CheckSuite,
    config: PRCheckConfig,
    repo: str,
    pr_number: int,
    token: str,
) -> CommentEnforcementResult:
    """Post a failure comment on the PR if checks failed and commenting is enabled."""
    result = CommentEnforcementResult()

    if not config.post_comment_on_failure:
        result.skipped = True
        result.skip_reason = "post_comment_on_failure is disabled in config"
        return result

    if suite.passed:
        result.skipped = True
        result.skip_reason = "all checks passed; no comment needed"
        return result

    try:
        comment_result = post_failure_comment(
            token=token,
            repo=repo,
            pr_number=pr_number,
            suite=suite,
        )
        result.comment_result = comment_result
        result.posted = comment_result.posted
        if not comment_result.posted:
            result.error = comment_result.error
    except Exception as exc:  # pragma: no cover
        result.error = str(exc)

    return result
