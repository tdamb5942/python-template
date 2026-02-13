"""CLI for phase-gated workflow management.

Usage:
    uv run scripts/workflow.py status    # Show current phase and progress
    uv run scripts/workflow.py prompt    # Render prompt for current phase
    uv run scripts/workflow.py validate  # Validate plan structure (CI-friendly)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PLAN_PATH = PROJECT_ROOT / "docs" / "workflow" / "PLAN.md"
DECISIONS_PATH = PROJECT_ROOT / "docs" / "workflow" / "DECISIONS.md"
GATES_PATH = PROJECT_ROOT / "docs" / "workflow" / "GATES.md"

# Add src to path so workflow package is importable
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from workflow.phase_workflow import build_phase_prompt  # noqa: E402
from workflow.plan_parser import (  # noqa: E402
    parse_plan_md,
    validate_workflow_docs,
)


def cmd_status(_args: argparse.Namespace) -> int:
    """Display current phase, checklist progress, and blockers.

    Args:
        _args: Parsed CLI arguments (unused).

    Returns:
        Exit code (0 on success, 1 on parse error).
    """
    try:
        plan = parse_plan_md(PLAN_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Find current phase
    current = None
    for phase in plan.phases:
        if phase.key == plan.current_phase_key:
            current = phase
            break

    if current is None:
        print(f"Error: Current phase '{plan.current_phase_key}' not found.", file=sys.stderr)
        return 1

    # Progress summary
    print("Project Workflow Status")
    print(f"{'=' * 40}")
    print(f"Current Phase: {current.title}")
    print()

    for phase in plan.phases:
        done = sum(1 for item in phase.checklist if item.done)
        total = len(phase.checklist)
        marker = ">>>" if phase.key == plan.current_phase_key else "   "
        bar = _progress_bar(done, total)
        print(f"  {marker} Phase {phase.key}: {bar} {done}/{total}")

    if plan.blockers:
        print()
        print("Blockers:")
        for blocker in plan.blockers:
            print(f"  - {blocker}")

    # Current phase detail
    print()
    print(f"Checklist ({current.title}):")
    for item in current.checklist:
        check = "x" if item.done else " "
        print(f"  [{check}] {item.key}: {item.description}")

    return 0


def cmd_prompt(_args: argparse.Namespace) -> int:
    """Render the current phase prompt to stdout.

    Args:
        _args: Parsed CLI arguments (unused).

    Returns:
        Exit code (0 on success, 1 on parse error).
    """
    try:
        plan = parse_plan_md(PLAN_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    current = None
    for phase in plan.phases:
        if phase.key == plan.current_phase_key:
            current = phase
            break

    if current is None:
        print(f"Error: Current phase '{plan.current_phase_key}' not found.", file=sys.stderr)
        return 1

    print(build_phase_prompt(current))
    return 0


def cmd_validate(_args: argparse.Namespace) -> int:
    """Validate plan structure and consistency across workflow docs.

    Args:
        _args: Parsed CLI arguments (unused).

    Returns:
        Exit code (0 if valid, 1 if errors found).
    """
    issues = validate_workflow_docs(PLAN_PATH, DECISIONS_PATH, GATES_PATH)

    if not issues:
        print("Workflow docs: OK")
        return 0

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    for issue in errors:
        print(f"ERROR: {issue.message}", file=sys.stderr)
    for issue in warnings:
        print(f"WARNING: {issue.message}", file=sys.stderr)

    if errors:
        print(f"\nValidation failed: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1

    print(f"Validation passed with {len(warnings)} warning(s).")
    return 0


def _progress_bar(done: int, total: int, width: int = 20) -> str:
    """Render a text progress bar.

    Args:
        done: Number of completed items.
        total: Total number of items.
        width: Character width of the bar.

    Returns:
        A string like [========----] representing progress.
    """
    if total == 0:
        return f"[{'=' * width}]"
    filled = int(width * done / total)
    return f"[{'=' * filled}{'-' * (width - filled)}]"


def main() -> int:
    """Entry point for the workflow CLI.

    Returns:
        Exit code from the selected subcommand.
    """
    parser = argparse.ArgumentParser(
        description="Phase-gated workflow management",
        prog="workflow",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show current phase and progress")
    subparsers.add_parser("prompt", help="Render prompt for current phase")
    subparsers.add_parser("validate", help="Validate plan structure")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    commands = {
        "status": cmd_status,
        "prompt": cmd_prompt,
        "validate": cmd_validate,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
