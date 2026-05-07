from __future__ import annotations

import pytest

from src.pr_review_staleness_checker import (
    ReviewStalenessResult,
    check_review_staleness,
)


FRESH_COMMIT = "2024-06-10T12:00:00Z"
OLD_REVIEW_DATE = "2024-05-01T12:00:00Z"   # >7 days before commit
RECENT_REVIEW_DATE = "2024-06-09T12:00:00Z"  # 1 day before commit


class TestReviewStalenessResult:
    def test_initial_state_is_passing(self):
        r = ReviewStalenessResult()
        assert r.passed is True
        assert r.errors == []
        assert r.warnings == []
        assert r.stale_reviews == 0
        assert r.total_reviews == 0

    def test_fail_sets_passed_false(self):
        r = ReviewStalenessResult()
        r.fail("too stale")
        assert r.passed is False

    def test_fail_appends_error(self):
        r = ReviewStalenessResult()
        r.fail("error one")
        r.fail("error two")
        assert r.errors == ["error one", "error two"]

    def test_warn_does_not_change_passed(self):
        r = ReviewStalenessResult()
        r.warn("heads up")
        assert r.passed is True
        assert r.warnings == ["heads up"]

    def test_bool_true_when_passing(self):
        r = ReviewStalenessResult()
        assert bool(r) is True

    def test_bool_false_when_failing(self):
        r = ReviewStalenessResult()
        r.fail("nope")
        assert bool(r) is False


class TestCheckReviewStaleness:
    def _approval(self, submitted_at: str) -> dict:
        return {"state": "APPROVED", "submitted_at": submitted_at}

    def test_no_reviews_passes(self):
        result = check_review_staleness([], FRESH_COMMIT)
        assert result.passed is True
        assert result.stale_reviews == 0

    def test_fresh_approval_passes(self):
        reviews = [self._approval(RECENT_REVIEW_DATE)]
        result = check_review_staleness(reviews, FRESH_COMMIT)
        assert result.passed is True
        assert result.stale_reviews == 0

    def test_stale_approval_warns_by_default(self):
        reviews = [self._approval(OLD_REVIEW_DATE)]
        result = check_review_staleness(reviews, FRESH_COMMIT)
        assert result.passed is True
        assert result.stale_reviews == 1
        assert result.warnings

    def test_stale_approval_fails_when_required_fresh(self):
        reviews = [self._approval(OLD_REVIEW_DATE)]
        result = check_review_staleness(
            reviews, FRESH_COMMIT, require_fresh_approval=True
        )
        assert result.passed is False
        assert result.stale_reviews == 1

    def test_mixed_reviews_counts_stale_only(self):
        reviews = [
            self._approval(OLD_REVIEW_DATE),
            self._approval(RECENT_REVIEW_DATE),
        ]
        result = check_review_staleness(reviews, FRESH_COMMIT)
        assert result.total_reviews == 2
        assert result.stale_reviews == 1

    def test_non_approval_states_ignored(self):
        reviews = [
            {"state": "CHANGES_REQUESTED", "submitted_at": OLD_REVIEW_DATE},
            {"state": "COMMENTED", "submitted_at": OLD_REVIEW_DATE},
        ]
        result = check_review_staleness(reviews, FRESH_COMMIT)
        assert result.total_reviews == 0
        assert result.stale_reviews == 0

    def test_missing_commit_date_warns(self):
        result = check_review_staleness([], "")
        assert result.passed is True
        assert result.warnings

    def test_invalid_commit_date_fails(self):
        result = check_review_staleness([], "not-a-date")
        assert result.passed is False

    def test_missing_review_timestamp_treated_as_stale(self):
        reviews = [{"state": "APPROVED"}]
        result = check_review_staleness(reviews, FRESH_COMMIT)
        assert result.stale_reviews == 1
        assert result.warnings

    def test_custom_max_stale_days(self):
        # review is 5 days old; default threshold 7 → fresh; custom 3 → stale
        reviews = [self._approval("2024-06-05T12:00:00Z")]
        result_fresh = check_review_staleness(reviews, FRESH_COMMIT, max_stale_days=7)
        result_stale = check_review_staleness(reviews, FRESH_COMMIT, max_stale_days=3)
        assert result_fresh.stale_reviews == 0
        assert result_stale.stale_reviews == 1
