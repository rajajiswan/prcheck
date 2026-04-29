"""Posts a comment on a PR via the GitHub API when checks fail."""

from __future__ import annotations

from dataclasses import dataclass

from src.github_client import GitHubClient, GitHubAPIError
from src.run_checks import CheckSuite


@dataclass
class CommentResult:
    posted: bool
    comment_url: str | None = None
    error: str | None = None


def _build_comment_body(suite: CheckSuite) -> str:
    lines = [
        "## ❌ PR Check Failed",
        "",
        "The following issues were found with this pull request:",
        "",
    ]
    for error in suite.errors:
        lines.append(f"- {error}")
    lines.append("")
    lines.append("_Posted automatically by [prcheck](https://github.com/your-org/prcheck)._")
    return "\n".join(lines)


def post_failure_comment(
    client: GitHubClient,
    repo: str,
    pr_number: int,
    suite: CheckSuite,
) -> CommentResult:
    """Post a failure comment on the PR if the check suite did not pass.

    Returns a CommentResult indicating whether the comment was posted.
    If the suite passed, no comment is posted and ``posted`` is False.
    """
    if suite.passed:
        return CommentResult(posted=False)

    body = _build_comment_body(suite)
    endpoint = f"/repos/{repo}/issues/{pr_number}/comments"

    try:
        data = client.post(endpoint, json={"body": body})
        return CommentResult(posted=True, comment_url=data.get("html_url"))
    except GitHubAPIError as exc:
        return CommentResult(posted=False, error=str(exc))
