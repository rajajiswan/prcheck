"""Tests for src/label_result_reporter.py."""

from __future__ import annotations

from unittest.mock import call, patch

import pytest

from src.label_manager import LabelResult
from src.label_result_reporter import report_label_result


@pytest.fixture
def successful_result() -> LabelResult:
    return LabelResult(success=True, label="feature", message="Label 'feature' applied.")


@pytest.fixture
def failed_result_with_label() -> LabelResult:
    return LabelResult(success=False, label="bugfix", message="HTTP 422: already exists")


@pytest.fixture
def failed_result_no_label() -> LabelResult:
    return LabelResult(success=False, label=None, message="No label mapping for branch type 'unknown'")


class TestReportLabelResult:
    def test_success_sets_outputs(self, successful_result: LabelResult) -> None:
        with patch("src.label_result_reporter.set_output") as mock_out, \
             patch("src.label_result_reporter.write_summary"):
            report_label_result(successful_result)
        mock_out.assert_any_call("label_applied", "feature")
        mock_out.assert_any_call("label_success", "true")

    def test_failure_sets_outputs(self, failed_result_with_label: LabelResult) -> None:
        with patch("src.label_result_reporter.set_output") as mock_out, \
             patch("src.label_result_reporter.write_summary"):
            report_label_result(failed_result_with_label)
        mock_out.assert_any_call("label_applied", "bugfix")
        mock_out.assert_any_call("label_success", "false")

    def test_no_label_sets_empty_string(self, failed_result_no_label: LabelResult) -> None:
        with patch("src.label_result_reporter.set_output") as mock_out, \
             patch("src.label_result_reporter.write_summary"):
            report_label_result(failed_result_no_label)
        mock_out.assert_any_call("label_applied", "")

    def test_success_summary_contains_label(self, successful_result: LabelResult) -> None:
        with patch("src.label_result_reporter.set_output"), \
             patch("src.label_result_reporter.write_summary") as mock_summary:
            report_label_result(successful_result)
        summary_text = mock_summary.call_args[0][0]
        assert "feature" in summary_text
        assert "✅" in summary_text

    def test_failure_summary_contains_reason(self, failed_result_with_label: LabelResult) -> None:
        with patch("src.label_result_reporter.set_output"), \
             patch("src.label_result_reporter.write_summary") as mock_summary:
            report_label_result(failed_result_with_label)
        summary_text = mock_summary.call_args[0][0]
        assert "❌" in summary_text
        assert "HTTP 422" in summary_text

    def test_failure_no_label_summary_no_attempted_line(self, failed_result_no_label: LabelResult) -> None:
        with patch("src.label_result_reporter.set_output"), \
             patch("src.label_result_reporter.write_summary") as mock_summary:
            report_label_result(failed_result_no_label)
        summary_text = mock_summary.call_args[0][0]
        assert "Attempted label" not in summary_text
        assert "No label mapping" in summary_text
