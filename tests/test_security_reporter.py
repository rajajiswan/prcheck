import pytest
from unittest.mock import call, patch
from src.pr_security_checker import SecurityResult
from src.security_reporter import _build_security_summary, report_security_result


@pytest.fixture
def passing_result():
    return SecurityResult()


@pytest.fixture
def failing_result():
    r = SecurityResult()
    r.fail("Sensitive file detected in diff: '.env'")
    r.secrets_found.append("API key")
    return r


@pytest.fixture
def warning_result():
    r = SecurityResult()
    r.warn("Possible token detected in diff")
    return r


class TestBuildSecuritySummary:
    def test_passing_header(self, passing_result):
        summary = _build_security_summary(passing_result)
        assert "✅ Security Check Passed" in summary

    def test_failing_header(self, failing_result):
        summary = _build_security_summary(failing_result)
        assert "❌ Security Check Failed" in summary

    def test_errors_listed(self, failing_result):
        summary = _build_security_summary(failing_result)
        assert ".env" in summary

    def test_secrets_section_present(self, failing_result):
        summary = _build_security_summary(failing_result)
        assert "Secrets Detected" in summary
        assert "API key" in summary

    def test_warnings_listed(self, warning_result):
        summary = _build_security_summary(warning_result)
        assert "Warnings" in summary
        assert "token" in summary

    def test_clean_message_when_passing(self, passing_result):
        summary = _build_security_summary(passing_result)
        assert "No sensitive files" in summary

    def test_remove_secrets_advice_shown(self, failing_result):
        summary = _build_security_summary(failing_result)
        assert "remove all secrets" in summary


class TestReportSecurityResult:
    def test_sets_passed_true_for_passing(self, passing_result):
        with patch("src.security_reporter.set_output") as mock_out, \
             patch("src.security_reporter.write_summary"):
            report_security_result(passing_result)
            mock_out.assert_any_call("security_passed", "true")

    def test_sets_passed_false_for_failing(self, failing_result):
        with patch("src.security_reporter.set_output") as mock_out, \
             patch("src.security_reporter.write_summary"):
            report_security_result(failing_result)
            mock_out.assert_any_call("security_passed", "false")

    def test_sets_secrets_found_output(self, failing_result):
        with patch("src.security_reporter.set_output") as mock_out, \
             patch("src.security_reporter.write_summary"):
            report_security_result(failing_result)
            mock_out.assert_any_call("secrets_found", "API key")

    def test_sets_empty_secrets_when_none(self, passing_result):
        with patch("src.security_reporter.set_output") as mock_out, \
             patch("src.security_reporter.write_summary"):
            report_security_result(passing_result)
            mock_out.assert_any_call("secrets_found", "")

    def test_calls_write_summary(self, passing_result):
        with patch("src.security_reporter.set_output"), \
             patch("src.security_reporter.write_summary") as mock_summary:
            report_security_result(passing_result)
            mock_summary.assert_called_once()
