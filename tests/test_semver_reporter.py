"""Unit tests for semver_reporter."""
import pytest
from unittest.mock import call, patch

from src.pr_semantic_version_checker import SemverResult
from src.semver_reporter import report_semver_result, _build_semver_summary


@pytest.fixture
def passing_result():
    r = SemverResult()
    r.detected_version = "1.2.3"
    return r


@pytest.fixture
def failing_result():
    r = SemverResult()
    r.fail("Version bump type 'major' is not in allowed types: ['patch'].")
    r.detected_version = "2.0.0"
    return r


class TestBuildSemverSummary:
    def test_passing_header(self, passing_result):
        summary = _build_semver_summary(passing_result)
        assert "✅" in summary
        assert "Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_semver_summary(failing_result)
        assert "❌" in summary
        assert "Failed" in summary

    def test_detected_version_shown(self, passing_result):
        summary = _build_semver_summary(passing_result)
        assert "1.2.3" in summary

    def test_no_version_shown_as_none(self):
        r = SemverResult()
        summary = _build_semver_summary(r)
        assert "_(none)_" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_semver_summary(failing_result)
        assert "major" in summary

    def test_warnings_listed(self):
        r = SemverResult()
        r.warn("heads up")
        summary = _build_semver_summary(r)
        assert "heads up" in summary
        assert "⚠️" in summary


class TestReportSemverResult:
    def test_sets_outputs_and_summary(self, passing_result):
        with patch("src.semver_reporter.set_output") as mock_out, \
             patch("src.semver_reporter.write_summary") as mock_sum:
            report_semver_result(passing_result)
            mock_out.assert_any_call("semver_passed", "true")
            mock_out.assert_any_call("semver_version", "1.2.3")
            mock_sum.assert_called_once()

    def test_sets_passed_false_output(self, failing_result):
        with patch("src.semver_reporter.set_output") as mock_out, \
             patch("src.semver_reporter.write_summary"):
            report_semver_result(failing_result)
            mock_out.assert_any_call("semver_passed", "false")

    def test_errors_joined_with_semicolon(self, failing_result):
        failing_result.fail("second error")
        with patch("src.semver_reporter.set_output") as mock_out, \
             patch("src.semver_reporter.write_summary"):
            report_semver_result(failing_result)
            calls = {c.args[0]: c.args[1] for c in mock_out.call_args_list}
            assert ";" in calls["semver_errors"]
