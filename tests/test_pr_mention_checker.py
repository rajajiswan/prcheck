import pytest

from src.pr_mention_checker import MentionResult, check_pr_mentions


class TestMentionResult:
    def test_initial_state_is_passing(self):
        r = MentionResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.mentions_found == []

    def test_fail_sets_passed_false(self):
        r = MentionResult()
        r.fail("oops")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = MentionResult()
        r.fail("first")
        r.fail("second")
        assert r.errors == ["first", "second"]

    def test_warn_does_not_change_passed(self):
        r = MentionResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        assert bool(MentionResult()) is True

    def test_bool_false_when_failed(self):
        r = MentionResult()
        r.fail("bad")
        assert bool(r) is False


class TestCheckPrMentions:
    def test_no_mentions_no_requirements_passes(self):
        result = check_pr_mentions("No mentions here.")
        assert result.passed is True
        assert result.mentions_found == []

    def test_extracts_mentions(self):
        result = check_pr_mentions("Hey @alice and @bob, please review.")
        assert set(result.mentions_found) == {"alice", "bob"}

    def test_require_mention_fails_when_absent(self):
        result = check_pr_mentions("No one mentioned.", require_mention=True)
        assert result.passed is False
        assert any("@mention" in e for e in result.errors)

    def test_require_mention_passes_when_present(self):
        result = check_pr_mentions("CC @reviewer", require_mention=True)
        assert result.passed is True

    def test_blocked_user_fails(self):
        result = check_pr_mentions("Tagging @badbot here.", blocked_users=["badbot"])
        assert result.passed is False
        assert any("badbot" in e for e in result.errors)

    def test_blocked_user_case_insensitive(self):
        result = check_pr_mentions("CC @BadBot", blocked_users=["badbot"])
        assert result.passed is False

    def test_blocked_user_with_at_prefix_in_list(self):
        result = check_pr_mentions("CC @spammer", blocked_users=["@spammer"])
        assert result.passed is False

    def test_max_mentions_exceeded_fails(self):
        body = " ".join(f"@user{i}" for i in range(6))
        result = check_pr_mentions(body, max_mentions=5)
        assert result.passed is False
        assert any("maximum" in e for e in result.errors)

    def test_max_mentions_at_limit_passes(self):
        body = " ".join(f"@user{i}" for i in range(5))
        result = check_pr_mentions(body, max_mentions=5)
        assert result.passed is True

    def test_many_mentions_triggers_warning(self):
        body = " ".join(f"@user{i}" for i in range(7))
        result = check_pr_mentions(body)
        assert result.passed is True
        assert len(result.warnings) >= 1

    def test_empty_body_no_crash(self):
        result = check_pr_mentions("")
        assert result.passed is True
        assert result.mentions_found == []

    def test_none_body_no_crash(self):
        result = check_pr_mentions(None)  # type: ignore[arg-type]
        assert result.passed is True
