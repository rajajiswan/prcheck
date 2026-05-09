"""Check CI/status check results on a PR."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CIStatusResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_checks: int = 0
    failed_checks: List[str] = field(default_factory=list)
    pending_checks: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed

    def summary(self) -> str:
        """Return a human-readable summary of the CI status result."""
        parts = [
            f"Total checks: {self.total_checks}",
            f"Failed: {len(self.failed_checks)}",
            f"Pending: {len(self.pending_checks)}",
            f"Warnings: {len(self.warnings)}",
        ]
        status = "PASSED" if self.passed else "FAILED"
        return f"[{status}] " + " | ".join(parts)


def check_pr_ci_status(
    statuses: List[dict],
    required_checks: Optional[List[str]] = None,
    block_on_pending: bool = False,
    allow_skipped: bool = True,
) -> CIStatusResult:
    """Evaluate commit status checks / GitHub check runs.

    Args:
        statuses: List of dicts with keys 'name', 'state'.
                  'state' is one of: 'success', 'failure', 'error',
                  'pending', 'skipped', 'cancelled', 'neutral'.
        required_checks: If provided, these check names must be present and pass.
        block_on_pending: If True, pending checks are treated as failures.
        allow_skipped: If True, skipped/neutral checks are not flagged.
    """
    result = CIStatusResult(total_checks=len(statuses))

    passing_states = {"success"}
    if allow_skipped:
        passing_states.update({"skipped", "neutral"})

    for status in statuses:
        name = status.get("name", "<unknown>")
        state = status.get("state", "")

        if state in ("failure", "error", "cancelled"):
            result.failed_checks.append(name)
            result.fail(f"CI check '{name}' failed with state '{state}'.")
        elif state == "pending":
            result.pending_checks.append(name)
            if block_on_pending:
                result.fail(f"CI check '{name}' is still pending.")
            else:
                result.warn(f"CI check '{name}' is pending.")
        elif state not in passing_states:
            result.warn(f"CI check '{name}' has unexpected state '{state}'.")

    if required_checks:
        present_names = {s.get("name") for s in statuses}
        for required in required_checks:
            if required not in present_names:
                result.fail(f"Required CI check '{required}' is missing.")

    return result
