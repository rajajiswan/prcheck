"""Thin wrapper around GitHub REST API calls used by prcheck."""
from __future__ import annotations

import os
from typing import Any

import requests

from src.retry_handler import with_retry

GITHUB_API_URL = "https://api.github.com"
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class GitHubAPIError(Exception):
    """Raised when a GitHub API call fails with a non-retryable status."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"GitHub API error {status_code}: {message}")


class GitHubClient:
    """Minimal GitHub REST client with built-in retry support."""

    def __init__(
        self,
        token: str | None = None,
        *,
        retries: int = 3,
        backoff: float = 2.0,
        base_url: str = GITHUB_API_URL,
    ) -> None:
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self._retries = retries
        self._backoff = backoff
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self._base_url}/{path.lstrip('/')}"

        def _do() -> requests.Response:
            resp = requests.request(
                method, url, headers=self._headers(), timeout=10, **kwargs
            )
            if resp.status_code in _RETRYABLE_STATUS:
                raise ConnectionError(
                    f"Retryable status {resp.status_code} from {url}"
                )
            if not resp.ok:
                raise GitHubAPIError(resp.status_code, resp.text[:200])
            return resp

        return with_retry(
            _do,
            retries=self._retries,
            backoff=self._backoff,
            retryable=(ConnectionError,),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> dict[str, Any]:
        """Return the PR object for *pr_number*."""
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}").json()

    def add_label(
        self, owner: str, repo: str, issue_number: int, label: str
    ) -> list[dict[str, Any]]:
        """Add *label* to the issue / PR identified by *issue_number*."""
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels",
            json={"labels": [label]},
        ).json()
