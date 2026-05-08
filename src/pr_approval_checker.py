from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ApprovalResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    approval_count: int = 0
    required_count: int = 0
    approved_by: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


def check_pr_approvals(
    reviews: List[dict],
    required_approvals: int = 1,
    require_team: Optional[str] = None,
    dismiss_stale: bool = False,
    approved_states: Optional[List[str]] = None,
) -> ApprovalResult:
    """Check whether a PR has the required number of approvals.

    Args:
        reviews: List of review objects from the GitHub API.
        required_approvals: Minimum number of approvals needed to pass.
        require_team: If set, only approvals from members of this team count.
        dismiss_stale: If True, a later non-approving review from the same user
            overrides their earlier approval (stale dismissal behaviour).
        approved_states: Review states that count as an approval.
            Defaults to ["APPROVED"].

    Returns:
        An ApprovalResult indicating whether the PR meets approval requirements.
    """
    if approved_states is None:
        approved_states = ["APPROVED"]

    result = ApprovalResult(required_count=required_approvals)

    seen: dict = {}
    for review in reviews:
        login = review.get("user", {}).get("login", "")
        state = review.get("state", "")
        if dismiss_stale:
            seen[login] = state
        else:
            if state in approved_states:
                seen[login] = state

    approved_logins = [
        login for login, state in seen.items() if state in approved_states
    ]

    if require_team:
        approved_logins = [
            login for login in approved_logins if review_is_team_member(login, require_team, reviews)
        ]

    result.approved_by = approved_logins
    result.approval_count = len(approved_logins)

    if result.approval_count < required_approvals:
        result.fail(
            f"PR requires {required_approvals} approval(s) but has {result.approval_count}."
        )
    elif result.approval_count == 0:
        result.warn("No approvals recorded for this PR.")

    return result


def review_is_team_member(login: str, team: str, reviews: List[dict]) -> bool:
    """Check if a reviewer belongs to a required team (via review metadata)."""
    for review in reviews:
        if review.get("user", {}).get("login") == login:
            teams = review.get("user", {}).get("teams", [])
            return team in teams
    return False
