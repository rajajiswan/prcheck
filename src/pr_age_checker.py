from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class AgeResult:
    passed: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    age_days: Optional[float] = None

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_age(
    created_at: str,
    max_age_days: Optional[int] = None,
    warn_age_days: Optional[int] = None,
    is_draft: bool = False,
) -> AgeResult:
    """Check whether a PR has been open too long.

    Args:
        created_at: ISO-8601 timestamp string from the GitHub API.
        max_age_days: If set, PRs older than this many days will fail.
        warn_age_days: If set, PRs older than this many days will warn.
        is_draft: Draft PRs receive a relaxed warning instead of a hard fail.

    Returns:
        AgeResult with pass/fail status and any messages.
    """
    result = AgeResult()

    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        result.fail(f"Could not parse PR creation date '{created_at}': {exc}")
        return result

    now = datetime.now(tz=timezone.utc)
    age = now - created
    age_days = age.total_seconds() / 86400
    result.age_days = round(age_days, 2)

    if max_age_days is not None and age_days > max_age_days:
        if is_draft:
            result.warn(
                f"Draft PR has been open for {result.age_days} days "
                f"(max allowed: {max_age_days} days)."
            )
        else:
            result.fail(
                f"PR has been open for {result.age_days} days, "
                f"which exceeds the maximum of {max_age_days} days."
            )
        return result

    if warn_age_days is not None and age_days > warn_age_days:
        result.warn(
            f"PR has been open for {result.age_days} days "
            f"(consider merging or closing; threshold: {warn_age_days} days)."
        )

    return result
