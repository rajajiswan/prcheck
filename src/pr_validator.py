"""Validates PR descriptions and labels against branch conventions."""

from dataclasses import dataclass, field
from typing import Optional

from src.branch_parser import BranchInfo


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.valid


class PRValidator:
    """Validates a pull request description and labels."""

    REQUIRED_SECTIONS = ["## Description", "## Changes"]
    MIN_DESCRIPTION_LENGTH = 20

    def __init__(self, branch_info: BranchInfo, body: str, labels: list[str]) -> None:
        self.branch_info = branch_info
        self.body = body or ""
        self.labels = labels or []

    def validate(self) -> ValidationResult:
        result = ValidationResult(valid=True)
        self._check_body_not_empty(result)
        self._check_required_sections(result)
        self._check_minimum_length(result)
        self._check_label_present(result)
        return result

    def _check_body_not_empty(self, result: ValidationResult) -> None:
        if not self.body.strip():
            result.add_error("PR description must not be empty.")

    def _check_required_sections(self, result: ValidationResult) -> None:
        for section in self.REQUIRED_SECTIONS:
            if section not in self.body:
                result.add_error(f"PR description is missing required section: '{section}'.")

    def _check_minimum_length(self, result: ValidationResult) -> None:
        if len(self.body.strip()) < self.MIN_DESCRIPTION_LENGTH:
            result.add_warning(
                f"PR description is very short (< {self.MIN_DESCRIPTION_LENGTH} chars)."
            )

    def _check_label_present(self, result: ValidationResult) -> None:
        expected = self.branch_info.label
        if expected is None:
            result.add_warning(
                "Could not determine expected label from branch name; skipping label check."
            )
            return
        if expected not in self.labels:
            result.add_error(
                f"Expected label '{expected}' is missing from the PR labels: {self.labels}."
            )
