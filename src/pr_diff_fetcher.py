"""Fetches the diff/changed files for a pull request via the GitHub API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.github_client import GitHubClient, GitHubAPIError


@dataclass
class PRDiff:
    """Holds the list of filenames changed in a pull request."""

    files: List[str] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def __len__(self) -> int:
        return len(self.files)

    def __contains__(self, item: str) -> bool:
        return item in self.files


def fetch_pr_diff(client: GitHubClient, repo: str, pr_number: int) -> PRDiff:
    """Return a PRDiff containing filenames changed in *pr_number*.

    Args:
        client: Authenticated :class:`GitHubClient` instance.
        repo:   Full repository name, e.g. ``"owner/repo"``.
        pr_number: Pull-request number.

    Returns:
        :class:`PRDiff` with ``files`` populated on success, or ``error`` set
        on failure.
    """
    endpoint = f"/repos/{repo}/pulls/{pr_number}/files"
    try:
        data = client.get(endpoint)
    except GitHubAPIError as exc:
        return PRDiff(error=str(exc))

    if not isinstance(data, list):
        return PRDiff(error=f"Unexpected response format: {type(data).__name__}")

    filenames: List[str] = [
        entry["filename"]
        for entry in data
        if isinstance(entry, dict) and "filename" in entry
    ]
    return PRDiff(files=filenames)
