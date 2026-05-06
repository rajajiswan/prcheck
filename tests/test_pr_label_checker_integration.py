"""Integration tests for the PR label checker pipeline."""
from src.pr_label_checker import check_pr_labels


def test_full_pass_pipeline():
    """A PR with valid labels and all requirements met should pass."""
    result = check_pr_labels(
        pr_labels=["bug", "enhancement"],
        allowed_labels=["bug", "enhancement", "documentation"],
        required_labels=["bug"],
        min_labels=1,
    )
    assert result.passed is True
    assert result.errors == []


def test_disallowed_label_fails_pipeline():
    """A PR with a label outside the allowed set should fail."""
    result = check_pr_labels(
        pr_labels=["wip"],
        allowed_labels=["bug", "enhancement"],
    )
    assert result.passed is False
    assert any("wip" in e for e in result.errors)


def test_missing_required_label_fails_pipeline():
    """A PR missing a required label should fail."""
    result = check_pr_labels(
        pr_labels=["enhancement"],
        required_labels=["bug"],
    )
    assert result.passed is False
    assert any("bug" in e for e in result.errors)


def test_below_min_labels_fails_pipeline():
    """A PR with fewer labels than required minimum should fail."""
    result = check_pr_labels(pr_labels=[], min_labels=1)
    assert result.passed is False
    assert any("at least 1" in e for e in result.errors)


def test_no_labels_warns_but_passes_pipeline():
    """A PR with no labels and no requirements should pass with a warning."""
    result = check_pr_labels(pr_labels=[])
    assert result.passed is True
    assert result.warnings != []
