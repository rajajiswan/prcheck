"""Tests for src/label_manager.py."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from src.branch_parser import BranchInfo
from src.label_manager import LabelManager, LabelResult, build_label_manager_from_env


@pytest.fixture
def manager() -> LabelManager:
    return LabelManager(token="tok_test", repo="owner/repo", pr_number=42)


@pytest.fixture
def feature_branch() -> BranchInfo:
    return BranchInfo(kind="feature", ticket="PROJ-1", description="add-thing", raw="feature/PROJ-1/add-thing")


@pytest.fixture
def unknown_branch() -> BranchInfo:
    return BranchInfo(kind="unknown", ticket=None, description=None, raw="random-branch")


class TestLabelManagerInit:
    def test_stores_attributes(self, manager: LabelManager) -> None:
        assert manager.token == "tok_test"
        assert manager.repo == "owner/repo"
        assert manager.pr_number == 42

    def test_headers_contain_auth(self, manager: LabelManager) -> None:
        headers = manager._headers()
        assert headers["Authorization"] == "Bearer tok_test"
        assert "application/vnd.github+json" in headers["Accept"]


class TestApplyLabel:
    def _make_response(self, status: int, body: bytes = b"[]") -> MagicMock:
        resp = MagicMock()
        resp.status = status
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_no_label_for_unknown_branch(self, manager: LabelManager, unknown_branch: BranchInfo) -> None:
        result = manager.apply_label(unknown_branch)
        assert result.success is False
        assert result.label is None
        assert "unknown" in result.message

    def test_success_on_201(self, manager: LabelManager, feature_branch: BranchInfo) -> None:
        mock_resp = self._make_response(201)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = manager.apply_label(feature_branch)
        assert result.success is True
        assert result.label == "feature"
        assert "applied" in result.message

    def test_success_on_200(self, manager: LabelManager, feature_branch: BranchInfo) -> None:
        mock_resp = self._make_response(200)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = manager.apply_label(feature_branch)
        assert result.success is True

    def test_http_error_returns_failure(self, manager: LabelManager, feature_branch: BranchInfo) -> None:
        import urllib.error
        err = urllib.error.HTTPError(url="", code=422, msg="Unprocessable", hdrs=None, fp=BytesIO(b"bad label"))
        with patch("urllib.request.urlopen", side_effect=err):
            result = manager.apply_label(feature_branch)
        assert result.success is False
        assert "422" in result.message

    def test_url_error_returns_failure(self, manager: LabelManager, feature_branch: BranchInfo) -> None:
        import urllib.error
        err = urllib.error.URLError(reason="connection refused")
        with patch("urllib.request.urlopen", side_effect=err):
            result = manager.apply_label(feature_branch)
        assert result.success is False
        assert "connection refused" in result.message


class TestBuildFromEnv:
    def test_builds_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_TOKEN", "mytoken")
        monkeypatch.setenv("GITHUB_REPOSITORY", "org/project")
        monkeypatch.setenv("PR_NUMBER", "7")
        lm = build_label_manager_from_env()
        assert lm.token == "mytoken"
        assert lm.repo == "org/project"
        assert lm.pr_number == 7

    def test_missing_env_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with pytest.raises(KeyError):
            build_label_manager_from_env()
