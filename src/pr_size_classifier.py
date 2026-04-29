from dataclasses import dataclass, field
from typing import Optional
from src.pr_diff_fetcher import PRDiff


SIZE_THRESHOLDS = {
    "XS": 10,
    "S": 50,
    "M": 200,
    "L": 500,
    "XL": float("inf"),
}


@dataclass
class SizeClassification:
    label: Optional[str] = None
    total_changes: int = 0
    files_changed: int = 0
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def __bool__(self) -> bool:
        return self.ok


def classify_pr_size(diff: PRDiff) -> SizeClassification:
    """Classify a PR into a size bucket based on total line changes."""
    if not diff.ok:
        return SizeClassification(error=f"Cannot classify: {diff.error}")

    total = sum(
        f.get("additions", 0) + f.get("deletions", 0)
        for f in diff.files
    )
    files_changed = len(diff.files)

    label = _size_label(total)
    return SizeClassification(
        label=label,
        total_changes=total,
        files_changed=files_changed,
    )


def _size_label(total_changes: int) -> str:
    for label, threshold in SIZE_THRESHOLDS.items():
        if total_changes <= threshold:
            return label
    return "XL"
