"""Tests for run_checks.py orchestration logic."""

import pytest
from unittest.mock import patch, MagicMock

from src.run_checks import CheckSuite, run_checks
from src.branch_parser import BranchInfo
from src.config_loader import PRCheckConfig


@pytest.fixture
def feature_branch():
    return BranchInfo(type="feature", ticket="PROJ-1", description="add-login", raw="feature/PROJ-1-add-login")


@pytest.fixture
def base_config(tmp_path):
    return PRCheckConfig(templates_dir=str(tmp_path), require_label=True, enforce_sections=[])


class TestCheckSuite:
    def test_initial_state_no_results_passes(self):
        suite = CheckSuite()
        assert suite.passed is True

    def test_bool_true_when_all_pass(self):
        suite = CheckSuite()
        assert bool(suite) is True

    def test_errors_empty_when_passing(self):
        suite = CheckSuite()
        assert suite.errors == []

    def test_bool_false_when_description_fails(self):
        from src.pr_description_enforcer import DescriptionResult
        result = DescriptionResult()
        result.fail("Missing section")
        suite = CheckSuite(description_result=result)
        assert bool(suite) is False

    def test_errors_aggregated_from_children(self):
        from src.pr_description_enforcer import DescriptionResult
        from src.branch_label_enforcer import LabelEnforcementResult
        dr = DescriptionResult()
        dr.fail("desc error")
        lr = LabelEnforcementResult()
        lr.fail("label error")
        suite = CheckSuite(description_result=dr, label_result=lr)
        assert "desc error" in suite.errors
        assert "label error" in suite.errors

    def test_bool_false_when_label_fails(self):
        """Ensure a failing label result alone marks the suite as failed."""
        from src.branch_label_enforcer import LabelEnforcementResult
        lr = LabelEnforcementResult()
        lr.fail("missing required label")
        suite = CheckSuite(label_result=lr)
        assert bool(suite) is False


class TestRunChecks:
    def test_returns_check_suite(self, feature_branch, base_config, tmp_path):
        (tmp_path / "feature.md").write_text("## Summary\n")
        suite = run_checks(
            branch=feature_branch,
            pr_body="## Summary\nDone.",
            applied_labels=["feature"],
            config=base_config,
        )
        assert isinstance(suite, CheckSuite)

    def test_label_result_none_when_require_label_false(self, feature_branch, tmp_path):
        config = PRCheckConfig(templates_dir=str(tmp_path), require_label=False, enforce_sections=[])
        suite = run_checks(
            branch=feature_branch,
            pr_body="body",
            applied_labels=[],
            config=config,
        )
        assert suite.label_result is None

    def test_label_result_present_when_require_label_true(self, feature_branch, base_config, tmp_path):
        (tmp_path / "feature.md").write_text("")
        suite = run_checks(
            branch=feature_branch,
            pr_body="body",
            applied_labels=["feature"],
            config=base_config,
        )
        assert suite.label_result is not None
