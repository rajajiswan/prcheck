"""Enforces that a PR description meets minimum length and non-empty requirements."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DescriptionResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)

    def fail(self, reason: str) -> None:
        self.passed = False
        self.errors.append(reason)

    def __bool__(self) -> bool:
        return self.passed


def enforce_pr_description(
    body: str,
    min_length: int = 20,
    forbidden_placeholders: List[str] | None = None,
) -> DescriptionResult:
    """Validate that *body* satisfies basic description requirements.

    Args:
        body: Raw PR body text.
        min_length: Minimum number of non-whitespace characters required.
        forbidden_placeholders: Substrings that must not appear in the body
            (e.g. template placeholder text left behind by the author).

    Returns:
        A :class:`DescriptionResult` with ``passed=True`` when all checks pass.
    """
    result = DescriptionResult()

    if forbidden_placeholders is None:
        forbidden_placeholders = []

    stripped = body.strip() if body else ""

    if not stripped:
        result.fail("PR description must not be empty.")
        return result

    effective_length = len(stripped.replace(" ", "").replace("\n", ""))
    if effective_length < min_length:
        result.fail(
            f"PR description is too short ({effective_length} chars); "
            f"minimum required is {min_length}."
        )

    for placeholder in forbidden_placeholders:
        if placeholder in body:
            result.fail(f"PR description still contains placeholder text: '{placeholder}'.")

    return result
