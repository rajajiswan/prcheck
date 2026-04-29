import pytest
from src.pr_size_classifier import classify_pr_size, SizeClassification, _size_label
from src.pr_diff_fetcher import PRDiff


def _make_diff(files=None, error=None):
    diff = PRDiff()
    if error:
        diff.error = error
    diff.files = files or []
    return diff


class TestSizeClassification:
    def test_defaults(self):
        r = SizeClassification()
        assert r.label is None
        assert r.total_changes == 0
        assert r.files_changed == 0
        assert r.error is None

    def test_ok_true_when_no_error(self):
        r = SizeClassification(label="S", total_changes=20, files_changed=2)
        assert r.ok is True
        assert bool(r) is True

    def test_ok_false_when_error_set(self):
        r = SizeClassification(error="fetch failed")
        assert r.ok is False
        assert bool(r) is False


class TestSizeLabel:
    @pytest.mark.parametrize("changes,expected", [
        (0, "XS"),
        (10, "XS"),
        (11, "S"),
        (50, "S"),
        (51, "M"),
        (200, "M"),
        (201, "L"),
        (500, "L"),
        (501, "XL"),
        (9999, "XL"),
    ])
    def test_thresholds(self, changes, expected):
        assert _size_label(changes) == expected


class TestClassifyPrSize:
    def test_error_diff_returns_error_result(self):
        diff = _make_diff(error="API timeout")
        result = classify_pr_size(diff)
        assert not result.ok
        assert "API timeout" in result.error
        assert result.label is None

    def test_empty_diff_is_xs(self):
        diff = _make_diff(files=[])
        result = classify_pr_size(diff)
        assert result.ok
        assert result.label == "XS"
        assert result.total_changes == 0
        assert result.files_changed == 0

    def test_small_diff_classified_correctly(self):
        files = [{"additions": 10, "deletions": 5}]
        diff = _make_diff(files=files)
        result = classify_pr_size(diff)
        assert result.label == "S"
        assert result.total_changes == 15
        assert result.files_changed == 1

    def test_large_diff_classified_as_xl(self):
        files = [{"additions": 300, "deletions": 250}]
        diff = _make_diff(files=files)
        result = classify_pr_size(diff)
        assert result.label == "XL"
        assert result.total_changes == 550

    def test_multiple_files_summed(self):
        files = [
            {"additions": 20, "deletions": 10},
            {"additions": 15, "deletions": 5},
        ]
        diff = _make_diff(files=files)
        result = classify_pr_size(diff)
        assert result.total_changes == 50
        assert result.files_changed == 2
        assert result.label == "S"

    def test_missing_keys_default_to_zero(self):
        files = [{"additions": 5}]
        diff = _make_diff(files=files)
        result = classify_pr_size(diff)
        assert result.total_changes == 5
