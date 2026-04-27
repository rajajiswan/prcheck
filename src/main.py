"""Entry point for the prcheck GitHub Action."""

import os
import sys

from branch_parser import parse_branch
from template_loader import TemplateLoader
from pr_validator import PRValidator
from action_output import emit_outputs, write_summary


def get_required_env(name: str) -> str:
    """Retrieve a required environment variable or exit with an error."""
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"::error::Missing required environment variable: {name}")
        sys.exit(1)
    return value


def main() -> None:
    """Run the prcheck action."""
    branch_name = get_required_env("BRANCH_NAME")
    pr_body = os.environ.get("PR_BODY", "")
    templates_dir = os.environ.get("TEMPLATES_DIR", ".github/pr_templates")
    require_label = os.environ.get("REQUIRE_LABEL", "true").lower() == "true"

    # Parse branch
    branch_info = parse_branch(branch_name)

    # Load template
    loader = TemplateLoader(templates_dir)
    template = loader.load(branch_info)

    # Validate PR
    validator = PRValidator(branch_info, pr_body, template)
    result = validator.validate(require_label=require_label)

    # Emit outputs and summary
    emit_outputs(result)
    write_summary(result)

    if not result:
        print("::error::PR validation failed. See summary for details.")
        sys.exit(1)

    print("PR validation passed.")


if __name__ == "__main__":
    main()
