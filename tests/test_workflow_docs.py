"""Structural validation tests for workflow documents.

These tests run in CI to enforce that workflow documents maintain
valid structure and that the parsed plan has no consistency errors.
This is the mechanism that makes review gates non-honor-system.
"""

from pathlib import Path

from workflow.plan_parser import (
    parse_decisions_md,
    parse_gates_md,
    parse_plan_md,
    validate_workflow_docs,
)

DOCS_DIR = Path(__file__).parent.parent / "docs" / "workflow"
PLAN_PATH = DOCS_DIR / "PLAN.md"
DECISIONS_PATH = DOCS_DIR / "DECISIONS.md"
GATES_PATH = DOCS_DIR / "GATES.md"


def test_plan_md_exists_and_has_phases() -> None:
    """Verify PLAN.md exists and contains at least one phase definition."""
    assert PLAN_PATH.exists(), "docs/workflow/PLAN.md not found"
    plan = parse_plan_md(PLAN_PATH)
    assert len(plan.phases) >= 1, "PLAN.md must define at least one phase"


def test_plan_md_has_current_phase_marker() -> None:
    """Verify PLAN.md has a valid Current Phase marker."""
    plan = parse_plan_md(PLAN_PATH)
    keys = [p.key for p in plan.phases]
    assert plan.current_phase_key in keys, (
        f"Current phase '{plan.current_phase_key}' not found in phase keys: {keys}"
    )


def test_decisions_md_exists_and_has_entries() -> None:
    """Verify DECISIONS.md exists and contains at least the seed entry."""
    assert DECISIONS_PATH.exists(), "docs/workflow/DECISIONS.md not found"
    decisions = parse_decisions_md(DECISIONS_PATH)
    assert len(decisions) >= 1, "DECISIONS.md should have at least ADR-000"


def test_gates_md_exists_and_has_phases() -> None:
    """Verify GATES.md exists and has gate definitions."""
    assert GATES_PATH.exists(), "docs/workflow/GATES.md not found"
    gates = parse_gates_md(GATES_PATH)
    assert len(gates) >= 1, "GATES.md must define gates for at least one phase"


def test_gates_cover_all_plan_phases() -> None:
    """Verify GATES.md has entries for every phase in PLAN.md."""
    plan = parse_plan_md(PLAN_PATH)
    gates = parse_gates_md(GATES_PATH)
    for phase in plan.phases:
        assert phase.key in gates, f"GATES.md missing section for Phase {phase.key}"


def test_plan_state_validates_cleanly() -> None:
    """Verify the parsed plan has no error-severity validation issues."""
    issues = validate_workflow_docs(PLAN_PATH, DECISIONS_PATH, GATES_PATH)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], f"Workflow doc errors: {[e.message for e in errors]}"
