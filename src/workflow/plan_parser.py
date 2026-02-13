"""Parse workflow markdown documents into phase_workflow dataclass instances.

Parses PLAN.md, DECISIONS.md, and GATES.md from their structured markdown
format into the dataclasses defined in phase_workflow.py. Uses line-by-line
regex parsing — no external markdown library required.
"""

from __future__ import annotations

import re
from pathlib import Path

from workflow.phase_workflow import (
    ChecklistItem,
    GateCriterion,
    PhaseDefinition,
    PlanState,
    ReviewGate,
    ValidationIssue,
)

# --- PLAN.md Patterns ---
_PHASE_HEADER = re.compile(r"^## Phase (\d+):\s*(.+)$")
_GOAL_LINE = re.compile(r"^\*\*Goal:\*\*\s*(.+)$")
_CURRENT_PHASE = re.compile(r"^\*\*Current Phase:\*\*\s*(\d+)")
_CHECKLIST_ITEM = re.compile(r"^- \[([ xX])\] \((\S+)\)\s+(.+)$")
_SECTION_HEADER = re.compile(r"^### (.+)$")
_BULLET = re.compile(r"^- (.+)$")

# --- GATES.md Patterns ---
_GATE_CRITERION = re.compile(r"^- \[([ xX])\] `\[(command|manual)\]`\s*(?:`([^`]+)`\s*)?(.*)$")

# --- DECISIONS.md Patterns ---
_ADR_HEADER = re.compile(r"^## (ADR-\d+):\s*(.+)$")
_ADR_FIELD = re.compile(r"^- \*\*(\w[\w\s]*):\*\*\s*(.+)$")


def parse_plan_md(plan_path: Path) -> PlanState:
    """Parse a PLAN.md file into a PlanState instance.

    Args:
        plan_path: Absolute path to PLAN.md.

    Returns:
        PlanState populated from the markdown content.

    Raises:
        FileNotFoundError: If plan_path does not exist.
        ValueError: If required sections are missing or malformed.
    """
    text = plan_path.read_text()
    lines = text.splitlines()

    current_phase_key = _extract_current_phase(lines)
    blockers = _extract_blockers(lines)
    phases = _extract_phases(lines)

    if not phases:
        msg = f"No phases found in {plan_path}. Expected '## Phase N: Title' headers."
        raise ValueError(msg)

    return PlanState(
        phases=tuple(phases),
        current_phase_key=current_phase_key,
        blockers=tuple(blockers),
    )


def parse_gates_md(gates_path: Path) -> dict[str, list[GateCriterion]]:
    """Parse GATES.md into a mapping of phase_key to criteria.

    Args:
        gates_path: Absolute path to GATES.md.

    Returns:
        Dict mapping phase keys (e.g. "1", "2") to lists of GateCriterion.

    Raises:
        FileNotFoundError: If gates_path does not exist.
    """
    text = gates_path.read_text()
    lines = text.splitlines()

    result: dict[str, list[GateCriterion]] = {}
    current_phase: str | None = None

    for line in lines:
        phase_match = _PHASE_HEADER.match(line)
        if phase_match:
            current_phase = phase_match.group(1)
            result[current_phase] = []
            continue

        if current_phase is None:
            continue

        gate_match = _GATE_CRITERION.match(line)
        if gate_match:
            passed = gate_match.group(1).lower() == "x"
            gate_type = gate_match.group(2)
            command = gate_match.group(3) or None
            description = gate_match.group(4).strip() if gate_match.group(4) else ""

            # For command gates, the command IS the description if no trailing text
            if gate_type == "command" and command and not description:
                description = command

            result[current_phase].append(
                GateCriterion(
                    description=description or command or "",
                    gate_type=gate_type,
                    command=command,
                    passed=passed,
                )
            )

    return result


def parse_decisions_md(decisions_path: Path) -> list[dict[str, str]]:
    """Parse DECISIONS.md into a list of decision records.

    Args:
        decisions_path: Absolute path to DECISIONS.md.

    Returns:
        List of dicts with keys matching ADR field names (number, title,
        date, phase, status, context, decision, rationale, consequences).

    Raises:
        FileNotFoundError: If decisions_path does not exist.
    """
    text = decisions_path.read_text()
    lines = text.splitlines()

    decisions: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in lines:
        # Skip HTML comments
        if line.strip().startswith("<!--"):
            # Flush current decision before comment block
            if current is not None:
                decisions.append(current)
                current = None
            break

        header_match = _ADR_HEADER.match(line)
        if header_match:
            if current is not None:
                decisions.append(current)
            current = {
                "number": header_match.group(1),
                "title": header_match.group(2),
            }
            continue

        if current is None:
            continue

        field_match = _ADR_FIELD.match(line)
        if field_match:
            field_name = field_match.group(1).strip().lower()
            field_value = field_match.group(2).strip()
            current[field_name] = field_value

    if current is not None:
        decisions.append(current)

    return decisions


def validate_workflow_docs(
    plan_path: Path,
    decisions_path: Path,
    gates_path: Path,
) -> list[ValidationIssue]:
    """Validate structural consistency across all workflow documents.

    Args:
        plan_path: Path to PLAN.md.
        decisions_path: Path to DECISIONS.md.
        gates_path: Path to GATES.md.

    Returns:
        List of validation issues. Empty means all documents are structurally sound.
    """
    issues: list[ValidationIssue] = []

    # Check existence
    for path, name in [
        (plan_path, "PLAN.md"),
        (decisions_path, "DECISIONS.md"),
        (gates_path, "GATES.md"),
    ]:
        if not path.exists():
            issues.append(ValidationIssue(severity="error", message=f"{name} not found at {path}."))

    if any(i.severity == "error" for i in issues):
        return issues

    # Parse and validate PLAN.md
    try:
        plan_state = parse_plan_md(plan_path)
    except ValueError as e:
        issues.append(ValidationIssue(severity="error", message=f"PLAN.md parse error: {e}"))
        return issues

    from workflow.phase_workflow import validate_plan_state

    issues.extend(validate_plan_state(plan_state))

    # Check GATES.md has entries for each plan phase
    gates = parse_gates_md(gates_path)
    for phase in plan_state.phases:
        if phase.key not in gates:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"GATES.md has no section for Phase {phase.key}.",
                )
            )

    # Check DECISIONS.md has at least the seed entry
    decisions = parse_decisions_md(decisions_path)
    if not decisions:
        issues.append(
            ValidationIssue(
                severity="warning",
                message="DECISIONS.md has no decision entries.",
            )
        )

    return issues


# --- Private helpers ---


def _extract_current_phase(lines: list[str]) -> str:
    """Find the **Current Phase:** marker in the document header."""
    for line in lines:
        match = _CURRENT_PHASE.match(line)
        if match:
            return match.group(1)
    msg = "PLAN.md missing '**Current Phase:** N' marker."
    raise ValueError(msg)


def _extract_blockers(lines: list[str]) -> list[str]:
    """Extract blocker items from the ## Blockers section."""
    in_blockers = False
    blockers: list[str] = []

    for line in lines:
        if line.strip() == "## Blockers":
            in_blockers = True
            continue

        if in_blockers:
            # Stop at next section
            if line.startswith("## ") or line.startswith("---"):
                break

            # Skip comments and empty lines
            stripped = line.strip()
            if stripped.startswith("<!--") or not stripped:
                continue

            bullet_match = _BULLET.match(stripped)
            if bullet_match:
                text = bullet_match.group(1).strip()
                if text.lower() != "none":
                    blockers.append(text)

    return blockers


def _extract_phases(lines: list[str]) -> list[PhaseDefinition]:
    """Extract all phase definitions from the document."""
    phases: list[PhaseDefinition] = []
    phase_blocks = _split_into_phase_blocks(lines)

    for phase_key, phase_title, block_lines in phase_blocks:
        phase = _parse_phase_block(phase_key, phase_title, block_lines)
        phases.append(phase)

    return phases


def _split_into_phase_blocks(
    lines: list[str],
) -> list[tuple[str, str, list[str]]]:
    """Split the document into (key, title, lines) per phase."""
    blocks: list[tuple[str, str, list[str]]] = []
    current_key: str | None = None
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        match = _PHASE_HEADER.match(line)
        if match:
            if current_key is not None and current_title is not None:
                blocks.append((current_key, current_title, current_lines))
            current_key = match.group(1)
            current_title = match.group(2).strip()
            current_lines = []
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None and current_title is not None:
        blocks.append((current_key, current_title, current_lines))

    return blocks


def _parse_phase_block(key: str, title: str, lines: list[str]) -> PhaseDefinition:
    """Parse a single phase block into a PhaseDefinition."""
    goal = ""
    read_first: list[str] = []
    scope: list[str] = []
    out_of_scope: list[str] = []
    checklist: list[ChecklistItem] = []
    current_section: str | None = None

    for line in lines:
        # Check for goal line
        goal_match = _GOAL_LINE.match(line)
        if goal_match:
            goal = goal_match.group(1).strip()
            continue

        # Check for subsection header
        section_match = _SECTION_HEADER.match(line)
        if section_match:
            current_section = section_match.group(1).strip().lower()
            continue

        # Check for checklist item
        checklist_match = _CHECKLIST_ITEM.match(line)
        if checklist_match:
            done = checklist_match.group(1).lower() == "x"
            item_key = checklist_match.group(2)
            description = checklist_match.group(3).strip()
            checklist.append(ChecklistItem(key=item_key, description=description, done=done))
            continue

        # Collect bullets into the current section
        stripped = line.strip()
        bullet_match = _BULLET.match(stripped)
        if bullet_match and current_section:
            text = bullet_match.group(1).strip()
            if current_section == "read first":
                read_first.append(text)
            elif current_section == "scope":
                scope.append(text)
            elif current_section in ("out of scope", "out_of_scope"):
                out_of_scope.append(text)

    review_gate = ReviewGate(key=f"{key}-gate", criteria=())

    return PhaseDefinition(
        key=key,
        title=f"Phase {key}: {title}",
        goal=goal,
        read_first=tuple(read_first),
        scope=tuple(scope),
        out_of_scope=tuple(out_of_scope),
        checklist=tuple(checklist),
        review_gate=review_gate,
    )
