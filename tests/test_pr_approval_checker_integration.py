from src.pr_approval_checker import check_pr_approvals


def _review(login: str, state: str, teams: list = None) -> dict:
    return {"user": {"login": login, "teams": teams or []}, "state": state}


def test_full_pass_pipeline():
    reviews = [
        _review("alice", "APPROVED"),
        _review("bob", "APPROVED"),
    ]
    result = check_pr_approvals(reviews, required_approvals=2)
    assert result.passed is True
    assert result.approval_count == 2
    assert set(result.approved_by) == {"alice", "bob"}
    assert result.errors == []


def test_mixed_states_pipeline():
    reviews = [
        _review("alice", "APPROVED"),
        _review("bob", "CHANGES_REQUESTED"),
        _review("carol", "COMMENTED"),
    ]
    result = check_pr_approvals(reviews, required_approvals=2)
    assert result.passed is False
    assert result.approval_count == 1
    assert "alice" in result.approved_by


def test_team_gate_pipeline():
    reviews = [
        _review("alice", "APPROVED", teams=["security"]),
        _review("bob", "APPROVED", teams=["frontend"]),
    ]
    result = check_pr_approvals(
        reviews, required_approvals=1, require_team="security"
    )
    assert result.passed is True
    assert result.approved_by == ["alice"]


def test_stale_dismissal_pipeline():
    reviews = [
        _review("alice", "APPROVED"),
        _review("alice", "CHANGES_REQUESTED"),
    ]
    result = check_pr_approvals(reviews, required_approvals=1, dismiss_stale=True)
    assert result.passed is False
    assert result.approval_count == 0


def test_empty_reviews_pipeline():
    result = check_pr_approvals([], required_approvals=1)
    assert result.passed is False
    assert result.approval_count == 0
    assert any("requires 1" in e for e in result.errors)
