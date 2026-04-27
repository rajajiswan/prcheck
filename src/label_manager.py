"""Manages GitHub PR label application based on branch info."""

from __future__ import annotations

import os
import urllib.request
import urllib.error
import json
from dataclasses import dataclass
from typing import Optional

from src.branch_parser import BranchInfo


@dataclass
class LabelResult:
    success: bool
    label: Optional[str]
    message: str


class LabelManager:
    """Applies labels to a GitHub PR via the GitHub REST API."""

    GITHUB_API_BASE = "https://api.github.com"

    def __init__(self, token: str, repo: str, pr_number: int) -> None:
        self.token = token
        self.repo = repo
        self.pr_number = pr_number

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }

    def apply_label(self, branch_info: BranchInfo) -> LabelResult:
        """Apply a label derived from branch_info to the PR."""
        label = branch_info.label
        if label is None:
            return LabelResult(
                success=False,
                label=None,
                message=f"No label mapping for branch type '{branch_info.kind}'",
            )

        url = f"{self.GITHUB_API_BASE}/repos/{self.repo}/issues/{self.pr_number}/labels"
        payload = json.dumps({"labels": [label]}).encode()
        req = urllib.request.Request(url, data=payload, headers=self._headers(), method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 201):
                    return LabelResult(success=True, label=label, message=f"Label '{label}' applied.")
                return LabelResult(success=False, label=label, message=f"Unexpected status {resp.status}")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            return LabelResult(success=False, label=label, message=f"HTTP {exc.code}: {body}")
        except urllib.error.URLError as exc:
            return LabelResult(success=False, label=label, message=f"URL error: {exc.reason}")


def build_label_manager_from_env() -> LabelManager:
    """Construct a LabelManager from standard GitHub Actions environment variables."""
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    return LabelManager(token=token, repo=repo, pr_number=pr_number)
