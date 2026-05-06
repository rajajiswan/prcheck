"""Tests for enforcement_reporter module."""

from __future__ import annotations

from unittest.mock import call, patch

import pytest

from src.enforcement_reporter import _build_summary, report_enforcement_result
from src.pr_body_enforcer import EnforcementResult


@pytest.fixture()
def passing_result() -> EnforcementResult:
    return EnforcementResult(missing_sections=[], unchecked_boxes=0)


@pytest.fixture()
def failing_result_sections() -> EnforcementResult:
    return EnforcementResult(missing_sections=["## Description", "## Testing"], unchecked_boxes=0)


@pytest.fixture()
def failing_result_boxes() -> EnforcementResult:
    return EnforcementResult(missing_sections=[], unchecked_boxes=3)


@pytest.fixture()
def failing_result_both() -> EnforcementResult:
    return EnforcementResult(missing_sections=["## Checklist"], unchecked_boxes=2)


class TestReportEnforcementResult:
    def test_passing_sets_correct_outputs(self, passing_result: EnforcementResult) -> None:
        with patch("src.enforcement_reporter.set_output") as mock_out, \
             patch("src.enforcement_reporter.write_summary"):
            report_enforcement_result(passing_result)
            mock_out.assert_any_call("enforcement_passed", "true")
            mock_out.assert_any_call("missing_sections", "")
            mock_out.assert_any_call("unchecked_boxes", "0")

    def test_failing_sets_correct_outputs(self, failing_result_both: EnforcementResult) -> None:
        with patch("src.enforcement_reporter.set_output") as mock_out, \
             patch("src.enforcement_reporter.write_summary"):
            report_enforcement_result(failing_result_both)
            mock_out.assert_any_call("enforcement_passed", "false")
            mock_out.assert_any_call("missing_sections", "## Checklist")
            mock_out.assert_any_call("unchecked_boxes", "2")

    def test_calls_write_summary(self, passing_result: EnforcementResult) -> None:
        with patch("src.enforcement_reporter.set_output"), \
             patch("src.enforcement_reporter.write_summary") as mock_summary:
            report_enforcement_result(passing_result)
            mock_summary.assert_called_once()


class TestBuildSummary:
    def test_passing_summary_contains_check_mark(self, passing_result: EnforcementResult) -> None:
        summary = _build_summary(passing_result)
        assert "✅" in summary
        assert "Passed" in summary

    def test_failing_summary_contains_cross(self, failing_result_sections: EnforcementResult) -> None:
        summary = _build_summary(failing_result_sections)
        assert "❌" in summary
        assert "Failed" in summary

    def test_missing_sections_listed(self, failing_result_sections: EnforcementResult) -> None:
        summary = _build_summary(failing_result_sections)
        assert "## Description" in summary
        assert "## Testing" in summary

    def test_unchecked_boxes_mentioned(self, failing_result_boxes: EnforcementResult) -> None:
        summary = _build_summary(failing_result_boxes)
        assert "3" in summary

    def test_passing_summary_does_not_contain_cross(self, passing_result: EnforcementResult) -> None:
        summary = _build_summary(passing_result)
        assert "❌" not in summary

    def test_failing_summary_does_not_contain_check_mark(self, failing_result_both: EnforcementResult) -> None:
        summary = _build_summary(failing_result_both)
        assert "✅" not in summary
