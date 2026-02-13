"""Tests for the phase_workflow core types and helpers."""

from workflow.phase_workflow import (
    ChecklistItem,
    GateCriterion,
    PhaseDefinition,
    PlanState,
    ReviewGate,
    ValidationIssue,
    build_phase_prompt,
    default_plan_state,
    validate_plan_state,
)


def test_default_plan_state_has_two_phases() -> None:
    """Verify the default starter plan contains two phases."""
    plan = default_plan_state()
    assert len(plan.phases) == 2
    assert plan.current_phase_key == "1"
    assert plan.phases[0].key == "1"
    assert plan.phases[1].key == "2"


def test_default_plan_state_validates_cleanly() -> None:
    """Verify the default plan has no error-severity issues."""
    plan = default_plan_state()
    issues = validate_plan_state(plan)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == []


def test_validate_flags_invalid_current_phase() -> None:
    """Verify validation catches a current phase key not in the plan."""
    plan = PlanState(phases=(default_plan_state().phases[0],), current_phase_key="99")
    issues = validate_plan_state(plan)
    assert any("not defined" in i.message for i in issues)


def test_validate_flags_advanced_past_incomplete_prior_phase() -> None:
    """Verify validation catches advancing past an incomplete phase."""
    phase_1 = PhaseDefinition(
        key="1",
        title="Phase 1",
        goal="Test",
        checklist=(ChecklistItem("1-1", "Incomplete item", done=False),),
        review_gate=ReviewGate(key="1-gate", criteria=("test",)),
    )
    phase_2 = PhaseDefinition(
        key="2",
        title="Phase 2",
        goal="Test",
        checklist=(ChecklistItem("2-1", "Item", done=False),),
        review_gate=ReviewGate(key="2-gate", criteria=("test",)),
    )
    plan = PlanState(phases=(phase_1, phase_2), current_phase_key="2")
    issues = validate_plan_state(plan)
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 1
    assert "incomplete" in errors[0].message.lower()


def test_validate_flags_gate_passed_with_incomplete_checklist() -> None:
    """Verify validation catches a passed gate on an incomplete checklist."""
    phase = PhaseDefinition(
        key="1",
        title="Phase 1",
        goal="Test",
        checklist=(ChecklistItem("1-1", "Incomplete", done=False),),
        review_gate=ReviewGate(key="1-gate", criteria=("test",), passed=True),
    )
    plan = PlanState(phases=(phase,), current_phase_key="1")
    issues = validate_plan_state(plan)
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 1
    assert "marked passed" in errors[0].message.lower()


def test_validate_warns_complete_checklist_without_gate_passed() -> None:
    """Verify validation warns when checklist is complete but gate not passed."""
    phase = PhaseDefinition(
        key="1",
        title="Phase 1",
        goal="Test",
        checklist=(ChecklistItem("1-1", "Done", done=True),),
        review_gate=ReviewGate(key="1-gate", criteria=("test",), passed=False),
    )
    plan = PlanState(phases=(phase,), current_phase_key="1")
    issues = validate_plan_state(plan)
    warnings = [i for i in issues if i.severity == "warning"]
    assert len(warnings) == 1
    assert "not marked passed" in warnings[0].message.lower()


def test_build_phase_prompt_contains_expected_sections() -> None:
    """Verify the prompt renderer includes all phase sections."""
    phase = default_plan_state().phases[0]
    prompt = build_phase_prompt(phase)

    assert "## Goal" in prompt
    assert "## Read First (Required)" in prompt
    assert "## Scope (Only This Phase)" in prompt
    assert "## Out Of Scope" in prompt
    assert "## Checklist" in prompt
    assert "## Review Gate" in prompt
    assert phase.title in prompt
    assert phase.goal in prompt


def test_build_phase_prompt_shows_checklist_status() -> None:
    """Verify the prompt shows done/undone checkboxes correctly."""
    phase = PhaseDefinition(
        key="1",
        title="Test",
        goal="Test",
        checklist=(
            ChecklistItem("1-1", "Done item", done=True),
            ChecklistItem("1-2", "Pending item", done=False),
        ),
        review_gate=ReviewGate(key="1-gate", criteria=()),
    )
    prompt = build_phase_prompt(phase)
    assert "- [x] 1-1: Done item" in prompt
    assert "- [ ] 1-2: Pending item" in prompt


def test_gate_criterion_defaults() -> None:
    """Verify GateCriterion has correct defaults."""
    manual = GateCriterion(description="Review design", gate_type="manual")
    assert manual.command is None
    assert manual.passed is False

    command = GateCriterion(description="Tests pass", gate_type="command", command="uv run pytest")
    assert command.command == "uv run pytest"
    assert command.passed is False


def test_validation_issue_fields() -> None:
    """Verify ValidationIssue stores severity and message."""
    issue = ValidationIssue(severity="error", message="Something broke")
    assert issue.severity == "error"
    assert issue.message == "Something broke"


def test_frozen_dataclasses_are_immutable() -> None:
    """Verify core types are frozen and reject mutation."""
    item = ChecklistItem(key="1", description="test")
    try:
        item.done = True  # type: ignore[misc]
        raised = False
    except AttributeError:
        raised = True
    assert raised, "ChecklistItem should be immutable"
