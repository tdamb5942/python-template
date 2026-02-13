"""Core types and helpers for a phase-gated implementation workflow."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChecklistItem:
    """Represents one checklist item within a phase."""

    key: str
    description: str
    done: bool = False


@dataclass(frozen=True)
class GateCriterion:
    """A single review gate criterion.

    Args:
        description: Human-readable description of what this criterion checks.
        gate_type: Either "command" (runnable, CI-verifiable) or "manual" (human judgment).
        command: Shell command to run if gate_type is "command". None for manual gates.
        passed: Whether this criterion has been satisfied.
    """

    description: str
    gate_type: str  # "command" | "manual"
    command: str | None = None
    passed: bool = False


@dataclass(frozen=True)
class ReviewGate:
    """Represents an explicit phase review gate and its acceptance criteria."""

    key: str
    criteria: tuple[str, ...]
    passed: bool = False


@dataclass(frozen=True)
class PhaseDefinition:
    """Represents one implementation phase with explicit boundaries."""

    key: str
    title: str
    goal: str
    read_first: tuple[str, ...] = ()
    scope: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()
    checklist: tuple[ChecklistItem, ...] = ()
    review_gate: ReviewGate = field(default_factory=lambda: ReviewGate(key="", criteria=()))


@dataclass(frozen=True)
class ValidationIssue:
    """Represents a validation issue found in a plan."""

    severity: str  # "error" | "warning"
    message: str


@dataclass(frozen=True)
class PlanState:
    """Represents the complete state of a multi-phase execution plan."""

    phases: tuple[PhaseDefinition, ...]
    current_phase_key: str
    blockers: tuple[str, ...] = field(default_factory=tuple)


def build_phase_prompt(phase: PhaseDefinition) -> str:
    """Render a prompt for one phase with strict scope and verification gates.

    Args:
        phase: The phase definition to render.

    Returns:
        Formatted markdown string suitable for use as an AI prompt.
    """
    read_first = "\n".join(f"- {entry}" for entry in phase.read_first)
    scope = "\n".join(f"- {entry}" for entry in phase.scope)
    not_scope = "\n".join(f"- {entry}" for entry in phase.out_of_scope)
    checklist = "\n".join(
        f"- [{'x' if item.done else ' '}] {item.key}: {item.description}"
        for item in phase.checklist
    )
    criteria = "\n".join(f"- {criterion}" for criterion in phase.review_gate.criteria)

    return (
        f"# {phase.title}\n\n"
        f"## Goal\n{phase.goal}\n\n"
        "## Read First (Required)\n"
        f"{read_first}\n\n"
        "## Scope (Only This Phase)\n"
        f"{scope}\n\n"
        "## Out Of Scope\n"
        f"{not_scope}\n\n"
        "## Checklist\n"
        f"{checklist}\n\n"
        f"## Review Gate ({phase.review_gate.key})\n"
        f"{criteria}\n"
    )


def validate_plan_state(plan: PlanState) -> list[ValidationIssue]:
    """Validate ordering, checklist progression, and review-gate consistency.

    Args:
        plan: The plan state to validate.

    Returns:
        List of validation issues found. Empty list means valid.
    """
    issues: list[ValidationIssue] = []
    keys = [phase.key for phase in plan.phases]

    if plan.current_phase_key not in keys:
        issues.append(
            ValidationIssue(
                severity="error",
                message=f"Current phase '{plan.current_phase_key}' is not defined in plan phases.",
            )
        )
        return issues

    current_index = keys.index(plan.current_phase_key)
    for index, phase in enumerate(plan.phases):
        completed = all(item.done for item in phase.checklist)

        if index < current_index and not completed:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=(
                        f"Prior phase '{phase.key}' has incomplete checklist items "
                        "but current phase has advanced past it."
                    ),
                )
            )

        if phase.review_gate.passed and not completed:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=(
                        f"Review gate '{phase.review_gate.key}' is marked passed, "
                        f"but checklist for phase '{phase.key}' is incomplete."
                    ),
                )
            )

        if completed and not phase.review_gate.passed:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=(
                        f"Checklist for phase '{phase.key}' is complete but review gate "
                        f"'{phase.review_gate.key}' is not marked passed."
                    ),
                )
            )

    return issues


def default_plan_state() -> PlanState:
    """Create a starter plan for this repository with two baseline phases.

    Returns:
        A PlanState with two template phases for contract baseline and skeleton
        implementation.
    """
    phase_1 = PhaseDefinition(
        key="1",
        title="Phase 1: Contract Baseline",
        goal=(
            "Define and freeze core contracts and constraints before implementation work begins."
        ),
        read_first=(
            "docs/workflow/PLAN.md",
            "docs/workflow/DECISIONS.md",
            "docs/workflow/GATES.md",
        ),
        scope=(
            "Write contract docs and acceptance criteria.",
            "Create initial parity checklist.",
            "Establish review-gate criteria.",
        ),
        out_of_scope=(
            "No production feature implementation.",
            "No new dependencies unless documented in plan decisions.",
        ),
        checklist=(
            ChecklistItem("1-1", "Contract docs are drafted and reviewed."),
            ChecklistItem("1-2", "Parity checklist includes user-visible behaviors."),
            ChecklistItem("1-3", "Review gate criteria are explicit and testable."),
        ),
        review_gate=ReviewGate(
            key="1-4",
            criteria=(
                "All checklist items 1-1 through 1-3 are complete.",
                "At least one reviewer confirms contract clarity.",
                "Scope for next phase is documented.",
            ),
        ),
    )

    phase_2 = PhaseDefinition(
        key="2",
        title="Phase 2: Skeleton Implementation",
        goal="Build minimal but runnable scaffolding aligned to phase 1 contracts.",
        read_first=(
            "docs/workflow/PLAN.md",
            "docs/workflow/GATES.md",
        ),
        scope=(
            "Create typed skeleton modules.",
            "Add tests for boundary behavior.",
            "Run quality gates (lint + tests).",
        ),
        out_of_scope=(
            "No full feature implementation.",
            "Do not skip phase review gate.",
        ),
        checklist=(
            ChecklistItem("2-1", "Skeleton modules compile and import cleanly."),
            ChecklistItem("2-2", "Tests exist for core boundaries."),
            ChecklistItem("2-3", "Lint and tests pass."),
        ),
        review_gate=ReviewGate(
            key="2-4",
            criteria=(
                "Checklist items 2-1 through 2-3 are complete.",
                "No critical review findings remain open.",
                "Next-phase backlog is sequenced in plan.",
            ),
        ),
    )

    return PlanState(phases=(phase_1, phase_2), current_phase_key="1")
