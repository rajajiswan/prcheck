"""Tests for pr_comment_enforcer."""
from unittest.mock import patch, MagicMock

import pytest

from src.pr_comment_enforcer import enforce_pr_comment, CommentEnforcementResult
from src.run_checks import CheckSuite
from src.pr_comment_poster import CommentResult
from src.config_loader import PRCheckConfig


def _make_config(post_comment: bool = True) -> PRCheckConfig:
    cfg = PRCheckConfig()
    cfg.post_comment_on_failure = post_comment
    return cfg


def _make_suite(passed: bool = False) -> CheckSuite:
    suite = MagicMock(spec=CheckSuite)
    suite.passed = passed
    return suite


class TestCommentEnforcementResult:
    def test_defaults(self):
        r = CommentEnforcementResult()
        assert r.posted is False
        assert r.skipped is False
        assert r.skip_reason == ""
        assert r.comment_result is None
        assert r.error is None

    def test_bool_true_when_no_error(self):
        r = CommentEnforcementResult()
        assert bool(r) is True

    def test_bool_false_when_error(self):
        r = CommentEnforcementResult(error="something went wrong")
        assert bool(r) is False


class TestEnforcePrComment:
    def test_skips_when_disabled_in_config(self):
        suite = _make_suite(passed=False)
        config = _make_config(post_comment=False)
        result = enforce_pr_comment(suite, config, "owner/repo", 42, "tok")
        assert result.skipped is True
        assert "disabled" in result.skip_reason
        assert result.posted is False

    def test_skips_when_suite_passed(self):
        suite = _make_suite(passed=True)
        config = _make_config(post_comment=True)
        result = enforce_pr_comment(suite, config, "owner/repo", 42, "tok")
        assert result.skipped is True
        assert "passed" in result.skip_reason
        assert result.posted is False

    def test_posts_comment_on_failure(self):
        suite = _make_suite(passed=False)
        config = _make_config(post_comment=True)
        mock_comment_result = CommentResult(posted=True, comment_id=99)

        with patch(
            "src.pr_comment_enforcer.post_failure_comment",
            return_value=mock_comment_result,
        ) as mock_post:
            result = enforce_pr_comment(suite, config, "owner/repo", 7, "tok")

        mock_post.assert_called_once_with(
            token="tok", repo="owner/repo", pr_number=7, suite=suite
        )
        assert result.posted is True
        assert result.skipped is False
        assert result.comment_result is mock_comment_result
        assert result.error is None

    def test_sets_error_when_comment_not_posted(self):
        suite = _make_suite(passed=False)
        config = _make_config(post_comment=True)
        mock_comment_result = CommentResult(posted=False, error="API error")

        with patch(
            "src.pr_comment_enforcer.post_failure_comment",
            return_value=mock_comment_result,
        ):
            result = enforce_pr_comment(suite, config, "owner/repo", 3, "tok")

        assert result.posted is False
        assert result.error == "API error"
        assert bool(result) is False
