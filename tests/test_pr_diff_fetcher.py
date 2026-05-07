"""Tests for src/pr_diff_fetcher.py"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.github_client import GitHubAPIError
from src.pr_diff_fetcher import PRDiff, fetch_pr_diff


# ---------------------------------------------------------------------------
# PRDiff unit tests
# ---------------------------------------------------------------------------


class TestPRDiff:
    def test_defaults(self):
        diff = PRDiff()
        assert diff.files == []
        assert diff.error is None
        assert diff.ok is True

    def test_ok_false_when_error_set(self):
        diff = PRDiff(error="boom")
        assert diff.ok is False

    def test_len_reflects_file_count(self):
        diff = PRDiff(files=["a.py", "b.py"])
        assert len(diff) == 2

    def test_contains_checks_filenames(self):
        diff = PRDiff(files=["src/main.py"])
        assert "src/main.py" in diff
        assert "README.md" not in diff


# ---------------------------------------------------------------------------
# fetch_pr_diff tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> MagicMock:
    return MagicMock()


class TestFetchPRDiff:
    def test_returns_filenames_on_success(self, client):
        client.get.return_value = [
            {"filename": "src/foo.py", "status": "modified"},
            {"filename": "tests/test_foo.py", "status": "added"},
        ]
        result = fetch_pr_diff(client, "owner/repo", 42)
        assert result.ok
        assert result.files == ["src/foo.py", "tests/test_foo.py"]

    def test_calls_correct_endpoint(self, client):
        client.get.return_value = []
        fetch_pr_diff(client, "owner/repo", 7)
        client.get.assert_called_once_with("/repos/owner/repo/pulls/7/files")

    def test_returns_error_on_api_failure(self, client):
        client.get.side_effect = GitHubAPIError("rate limited", status_code=403)
        result = fetch_pr_diff(client, "owner/repo", 1)
        assert not result.ok
        assert "rate limited" in result.error
        assert result.files == []

    def test_returns_error_on_unexpected_format(self, client):
        client.get.return_value = {"unexpected": "dict"}
        result = fetch_pr_diff(client, "owner/repo", 1)
        assert not result.ok
        assert "Unexpected response format" in result.error

    def test_skips_entries_without_filename(self, client):
        client.get.return_value = [
            {"filename": "valid.py"},
            {"status": "removed"},  # no 'filename' key
        ]
        result = fetch_pr_diff(client, "owner/repo", 3)
        assert result.ok
        assert result.files == ["valid.py"]

    def test_empty_diff_is_ok(self, client):
        client.get.return_value = []
        result = fetch_pr_diff(client, "owner/repo", 99)
        assert result.ok
        assert len(result) == 0

    def test_returns_error_on_unexpected_exception(self, client):
        """Non-API exceptions (e.g. network errors) should also produce an error result."""
        client.get.side_effect = ConnectionError("connection refused")
        result = fetch_pr_diff(client, "owner/repo", 5)
        assert not result.ok
        assert "connection refused" in result.error
        assert result.files == []
