import pytest
from src.pr_security_checker import SecurityResult, check_pr_security


class TestSecurityResult:
    def test_initial_state_is_passing(self):
        r = SecurityResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.secrets_found == []

    def test_fail_sets_passed_false(self):
        r = SecurityResult()
        r.fail("bad thing")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = SecurityResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = SecurityResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(SecurityResult()) is True

    def test_bool_false_when_failed(self):
        r = SecurityResult()
        r.fail("x")
        assert bool(r) is False


class TestCheckPrSecurity:
    def test_clean_diff_passes(self):
        result = check_pr_security("some body", ["src/main.py"], "+ print('hello')")
        assert result.passed is True
        assert result.errors == []

    def test_sensitive_file_fails(self):
        result = check_pr_security("", [".env"], "")
        assert result.passed is False
        assert any(".env" in e for e in result.errors)

    def test_sensitive_file_glob_fails(self):
        result = check_pr_security("", ["certs/server.pem"], "")
        assert result.passed is False

    def test_sensitive_file_warns_when_warn_only(self):
        result = check_pr_security("", [".env"], "", warn_only=True)
        assert result.passed is True
        assert result.warnings != []

    def test_api_key_in_diff_fails(self):
        patch = '+API_KEY = "supersecretkey123"'
        result = check_pr_security("", [], patch)
        assert result.passed is False
        assert "API key" in result.secrets_found

    def test_aws_key_in_diff_fails(self):
        patch = "+key = AKIAIOSFODNN7EXAMPLE"
        result = check_pr_security("", [], patch)
        assert result.passed is False
        assert "AWS access key" in result.secrets_found

    def test_secret_warns_when_warn_only(self):
        patch = '+SECRET = "mysupersecret"'
        result = check_pr_security("", [], patch, warn_only=True)
        assert result.passed is True
        assert result.warnings != []

    def test_block_secrets_false_skips_scan(self):
        patch = '+API_KEY = "supersecretkey123"'
        result = check_pr_security("", [], patch, block_secrets=False)
        assert result.passed is True
        assert result.secrets_found == []

    def test_block_sensitive_files_false_skips_scan(self):
        result = check_pr_security("", [".env"], "", block_sensitive_files=False)
        assert result.passed is True

    def test_multiple_issues_accumulate(self):
        patch = '+TOKEN = "abc123def456"\n+PASSWORD = "hunter2"'
        result = check_pr_security("", ["secrets.yaml"], patch)
        assert result.passed is False
        assert len(result.errors) >= 2
