"""Orchestrates all PR checks: description, label enforcement, and reporting."""

from dataclasses import dataclass, field
from typing import Optional

from src.branch_parser import BranchInfo
from src.config_loader import PRCheckConfig
from src.pr_description_enforcer import DescriptionResult, enforce_pr_description
from src.branch_label_enforcer import LabelEnforcementResult, enforce_branch_label
from src.template_loader import TemplateLoader


@dataclass
class CheckSuite:
    """Aggregated result of all PR checks."""
    description_result: Optional[DescriptionResult] = None
    label_result: Optional[LabelEnforcementResult] = None

    @property
    def passed(self) -> bool:
        results = [r for r in (self.description_result, self.label_result) if r is not None]
        return all(bool(r) for r in results)

    @property
    def errors(self) -> list[str]:
        errs: list[str] = []
        if self.description_result and not self.description_result:
            errs.extend(self.description_result.errors)
        if self.label_result and not self.label_result:
            errs.extend(self.label_result.errors)
        return errs

    def __bool__(self) -> bool:
        return self.passed


def run_checks(
    branch: BranchInfo,
    pr_body: str,
    applied_labels: list[str],
    config: PRCheckConfig,
) -> CheckSuite:
    """Run all configured checks and return a combined CheckSuite."""
    suite = CheckSuite()

    # Description check
    loader = TemplateLoader(config.templates_dir)
    template = loader.load(branch)
    suite.description_result = enforce_pr_description(
        pr_body=pr_body,
        template=template,
        enforce_sections=config.enforce_sections,
    )

    # Label check
    if config.require_label:
        suite.label_result = enforce_branch_label(
            branch=branch,
            applied_labels=applied_labels,
        )

    return suite
