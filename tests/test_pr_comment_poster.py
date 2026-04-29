"""Tests for pr_comment_poster."""

from unittest.mock import MagicMock, patch

import pytest

from src.github_client import GitHubAPIError
from src.pr_comment_poster import CommentResult, _build_comment_body, post_failure_comment
from src.run_checks import CheckSuite


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_suite(passed: bool, errors: list[str] | None = None) -> CheckSuite:
    suite = MagicMock(spec=CheckSuite)
    suite.passed = passed
    suite.errors = errors or []
    return suite


# ---------------------------------------------------------------------------
# CommentResult
# ---------------------------------------------------------------------------

class TestCommentResult:
    def test_defaults(self):
        result = CommentResult(posted=True)
        assert result.comment_url is None
        assert result.error is None

    def test_stores_fields(self):
        result = CommentResult(posted=True, comment_url="https://example.com", error=None)
        assert result.posted is True
        assert result.comment_url == "https://example.com"


# ---------------------------------------------------------------------------
# _build_comment_body
# ---------------------------------------------------------------------------

class TestBuildCommentBody:
    def test_contains_header(self):
        suite = _make_suite(False, ["Missing section: Summary"])
        body = _build_comment_body(suite)
        assert "## ❌ PR Check Failed" in body

    def test_lists_each_error(self):
        errors = ["Missing section: Summary", "Label not applied"]
        suite = _make_suite(False, errors)
        body = _build_comment_body(suite)
        for error in errors:
            assert error in body

    def test_contains_prcheck_attribution(self):
        suite = _make_suite(False, ["err"])
        body = _build_comment_body(suite)
        assert "prcheck" in body


# ---------------------------------------------------------------------------
# post_failure_comment
# ---------------------------------------------------------------------------

class TestPostFailureComment:
    def test_no_comment_when_suite_passes(self):
        client = MagicMock()
        suite = _make_suite(passed=True)
        result = post_failure_comment(client, "org/repo", 42, suite)
        assert result.posted is False
        client.post.assert_not_called()

    def test_posts_comment_on_failure(self):
        client = MagicMock()
        client.post.return_value = {"html_url": "https://github.com/org/repo/issues/42#issuecomment-1"}
        suite = _make_suite(passed=False, errors=["Missing label"])
        result = post_failure_comment(client, "org/repo", 42, suite)
        assert result.posted is True
        assert result.comment_url == "https://github.com/org/repo/issues/42#issuecomment-1"
        client.post.assert_called_once()

    def test_returns_error_on_api_failure(self):
        client = MagicMock()
        client.post.side_effect = GitHubAPIError("403 Forbidden")
        suite = _make_suite(passed=False, errors=["err"])
        result = post_failure_comment(client, "org/repo", 7, suite)
        assert result.posted is False
        assert result.error is not None
        assert "403" in result.error

    def test_correct_endpoint_called(self):
        client = MagicMock()
        client.post.return_value = {"html_url": "https://example.com"}
        suite = _make_suite(passed=False, errors=["err"])
        post_failure_comment(client, "myorg/myrepo", 99, suite)
        call_args = client.post.call_args
        assert "/repos/myorg/myrepo/issues/99/comments" in call_args[0][0]
