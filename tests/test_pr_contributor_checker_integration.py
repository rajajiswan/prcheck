from src.pr_contributor_checker import check_pr_contributor

COLLABS = ["alice", "bob"]
ORG = ["alice", "carol"]


def test_full_pass_pipeline():
    result = check_pr_contributor(
        author="alice",
        collaborators=COLLABS,
        org_members=ORG,
        require_org_member=True,
        require_collaborator=True,
        warn_first_time=True,
    )
    assert result.passed
    assert result.errors == []
    assert result.warnings == []
    assert result.is_first_time is False


def test_blocked_author_full_pipeline():
    result = check_pr_contributor(
        author="spammer",
        collaborators=COLLABS,
        org_members=ORG,
        blocked_users=["spammer"],
    )
    assert not result
    assert any("blocked" in e for e in result.errors)


def test_first_time_warns_but_passes_pipeline():
    result = check_pr_contributor(
        author="newbie",
        collaborators=COLLABS,
        org_members=ORG,
        warn_first_time=True,
    )
    assert result.passed
    assert result.is_first_time is True
    assert result.warnings != []


def test_missing_org_membership_fails_pipeline():
    result = check_pr_contributor(
        author="dave",
        collaborators=COLLABS,
        org_members=ORG,
        require_org_member=True,
    )
    assert not result
    assert any("organisation" in e for e in result.errors)


def test_multiple_failures_accumulate_pipeline():
    result = check_pr_contributor(
        author="dave",
        collaborators=COLLABS,
        org_members=ORG,
        require_org_member=True,
        require_collaborator=True,
        warn_first_time=False,
    )
    assert not result
    assert len(result.errors) == 2
