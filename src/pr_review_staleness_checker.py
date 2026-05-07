from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class ReviewStalenessResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stale_reviews: int = 0
    total_reviews: int = 0

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_review_staleness(
    reviews: List[dict],
    head_commit_date: str,
    max_stale_days: int = 7,
    require_fresh_approval: bool = False,
) -> ReviewStalenessResult:
    """Check whether existing PR approvals are stale relative to the latest commit."""
    result = ReviewStalenessResult()

    if not head_commit_date:
        result.warn("No head commit date provided; skipping review staleness check.")
        return result

    try:
        commit_dt = datetime.fromisoformat(head_commit_date.rstrip("Z")).replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        result.fail(f"Invalid head_commit_date format: {head_commit_date!r}")
        return result

    approvals = [r for r in reviews if r.get("state") == "APPROVED"]
    result.total_reviews = len(approvals)

    for review in approvals:
        submitted_at: Optional[str] = review.get("submitted_at")
        if not submitted_at:
            result.warn("Approval found with no submitted_at timestamp; treating as stale.")
            result.stale_reviews += 1
            continue

        try:
            review_dt = datetime.fromisoformat(submitted_at.rstrip("Z")).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            result.warn(f"Could not parse review timestamp: {submitted_at!r}")
            result.stale_reviews += 1
            continue

        age_days = (commit_dt - review_dt).days
        if age_days > max_stale_days:
            result.stale_reviews += 1

    if result.stale_reviews > 0:
        msg = (
            f"{result.stale_reviews} of {result.total_reviews} approval(s) are stale "
            f"(older than {max_stale_days} day(s) before the latest commit)."
        )
        if require_fresh_approval:
            result.fail(msg)
        else:
            result.warn(msg)

    return result
