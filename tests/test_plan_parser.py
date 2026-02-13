"""Tests for the plan_parser markdown-to-dataclass parsing module."""

from pathlib import Path
from textwrap import dedent

import pytest

from workflow.plan_parser import (
    parse_decisions_md,
    parse_gates_md,
    parse_plan_md,
    validate_workflow_docs,
)

FIXTURES = Path(__file__).parent.parent / "docs" / "workflow"


# --- parse_plan_md ---


class TestParsePlanMd:
    """Tests for PLAN.md parsing."""

    def test_parse_template_produces_three_phases(self) -> None:
        """Verify the template PLAN.md parses into 3 phases."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        assert len(plan.phases) == 3
        assert plan.phases[0].key == "1"
        assert plan.phases[1].key == "2"
        assert plan.phases[2].key == "3"

    def test_parse_template_current_phase_is_one(self) -> None:
        """Verify the template starts at Phase 1."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        assert plan.current_phase_key == "1"

    def test_parse_template_no_blockers(self) -> None:
        """Verify the template has no active blockers."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        assert plan.blockers == ()

    def test_parse_template_phase_goals_populated(self) -> None:
        """Verify each phase has a non-empty goal."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        for phase in plan.phases:
            assert phase.goal, f"Phase {phase.key} has no goal"

    def test_parse_template_phase_checklists_populated(self) -> None:
        """Verify each phase has checklist items."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        for phase in plan.phases:
            assert len(phase.checklist) > 0, f"Phase {phase.key} has no checklist"

    def test_parse_template_all_items_unchecked(self) -> None:
        """Verify all checklist items in the template start unchecked."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        for phase in plan.phases:
            for item in phase.checklist:
                assert not item.done, f"Item {item.key} should not be done in template"

    def test_parse_checklist_toggle(self, tmp_path: Path) -> None:
        """Verify parsing correctly reads checked items."""
        md = tmp_path / "PLAN.md"
        md.write_text(
            dedent("""\
            **Current Phase:** 1

            ## Blockers
            - None

            ## Phase 1: Test

            **Goal:** Test goal

            ### Checklist
            - [x] (1-1) Done item
            - [ ] (1-2) Pending item
        """)
        )
        plan = parse_plan_md(md)
        assert plan.phases[0].checklist[0].done is True
        assert plan.phases[0].checklist[1].done is False

    def test_parse_extracts_scope_and_out_of_scope(self) -> None:
        """Verify scope and out-of-scope bullets are parsed."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        phase_1 = plan.phases[0]
        assert len(phase_1.scope) > 0
        assert len(phase_1.out_of_scope) > 0

    def test_parse_extracts_read_first(self) -> None:
        """Verify read-first references are parsed."""
        plan = parse_plan_md(FIXTURES / "PLAN.md")
        phase_1 = plan.phases[0]
        assert len(phase_1.read_first) > 0

    def test_parse_missing_file_raises(self) -> None:
        """Verify FileNotFoundError for non-existent path."""
        with pytest.raises(FileNotFoundError):
            parse_plan_md(Path("/nonexistent/PLAN.md"))

    def test_parse_no_phases_raises(self, tmp_path: Path) -> None:
        """Verify ValueError when no phase headers found."""
        md = tmp_path / "PLAN.md"
        md.write_text("**Current Phase:** 1\n\nJust some text.\n")
        with pytest.raises(ValueError, match="No phases found"):
            parse_plan_md(md)

    def test_parse_missing_current_phase_raises(self, tmp_path: Path) -> None:
        """Verify ValueError when Current Phase marker is missing."""
        md = tmp_path / "PLAN.md"
        md.write_text("## Phase 1: Test\n\n**Goal:** Test\n")
        with pytest.raises(ValueError, match="missing"):
            parse_plan_md(md)

    def test_parse_blockers(self, tmp_path: Path) -> None:
        """Verify active blockers are extracted."""
        md = tmp_path / "PLAN.md"
        md.write_text(
            dedent("""\
            **Current Phase:** 1

            ## Blockers
            - Waiting on API access
            - Data format TBD

            ## Phase 1: Test

            **Goal:** Test goal

            ### Checklist
            - [ ] (1-1) Something
        """)
        )
        plan = parse_plan_md(md)
        assert len(plan.blockers) == 2
        assert "API access" in plan.blockers[0]


# --- parse_gates_md ---


class TestParseGatesMd:
    """Tests for GATES.md parsing."""

    def test_parse_template_has_three_phases(self) -> None:
        """Verify the template GATES.md has entries for 3 phases."""
        gates = parse_gates_md(FIXTURES / "GATES.md")
        assert "1" in gates
        assert "2" in gates
        assert "3" in gates

    def test_parse_command_criteria(self) -> None:
        """Verify command-type criteria are parsed with their commands."""
        gates = parse_gates_md(FIXTURES / "GATES.md")
        command_gates = [g for g in gates["2"] if g.gate_type == "command"]
        assert len(command_gates) >= 3
        commands = [g.command for g in command_gates]
        assert any("pytest" in (c or "") for c in commands)
        assert any("ruff check" in (c or "") for c in commands)

    def test_parse_manual_criteria(self) -> None:
        """Verify manual-type criteria are parsed."""
        gates = parse_gates_md(FIXTURES / "GATES.md")
        manual_gates = [g for g in gates["1"] if g.gate_type == "manual"]
        assert len(manual_gates) >= 1

    def test_all_criteria_start_unchecked(self) -> None:
        """Verify all template gate criteria start unpassed."""
        gates = parse_gates_md(FIXTURES / "GATES.md")
        for phase_key, criteria in gates.items():
            for criterion in criteria:
                assert not criterion.passed, (
                    f"Phase {phase_key} criterion should not be passed in template"
                )

    def test_parse_missing_file_raises(self) -> None:
        """Verify FileNotFoundError for non-existent path."""
        with pytest.raises(FileNotFoundError):
            parse_gates_md(Path("/nonexistent/GATES.md"))


# --- parse_decisions_md ---


class TestParseDecisionsMd:
    """Tests for DECISIONS.md parsing."""

    def test_parse_template_has_seed_entry(self) -> None:
        """Verify the template has the ADR-000 seed decision."""
        decisions = parse_decisions_md(FIXTURES / "DECISIONS.md")
        assert len(decisions) >= 1
        assert decisions[0]["number"] == "ADR-000"

    def test_parse_extracts_fields(self) -> None:
        """Verify ADR field extraction."""
        decisions = parse_decisions_md(FIXTURES / "DECISIONS.md")
        adr = decisions[0]
        assert "title" in adr
        assert "status" in adr
        assert adr["status"] == "Accepted"

    def test_parse_missing_file_raises(self) -> None:
        """Verify FileNotFoundError for non-existent path."""
        with pytest.raises(FileNotFoundError):
            parse_decisions_md(Path("/nonexistent/DECISIONS.md"))

    def test_parse_multiple_decisions(self, tmp_path: Path) -> None:
        """Verify parsing multiple ADR entries."""
        md = tmp_path / "DECISIONS.md"
        md.write_text(
            dedent("""\
            # Architecture Decisions

            ## ADR-001: Use PostgreSQL
            - **Date:** 2026-01-01
            - **Phase:** 1
            - **Status:** Accepted
            - **Context:** Need a database.
            - **Decision:** Use PostgreSQL.
            - **Rationale:** Mature and reliable.
            - **Consequences:** Must provision a Postgres instance.

            ## ADR-002: Use Polars
            - **Date:** 2026-01-02
            - **Phase:** 2
            - **Status:** Accepted
            - **Context:** Need a DataFrame library.
            - **Decision:** Use Polars.
            - **Rationale:** Faster than Pandas.
            - **Consequences:** Team must learn Polars API.
        """)
        )
        decisions = parse_decisions_md(md)
        assert len(decisions) == 2
        assert decisions[0]["number"] == "ADR-001"
        assert decisions[1]["number"] == "ADR-002"


# --- validate_workflow_docs ---


class TestValidateWorkflowDocs:
    """Tests for cross-document validation."""

    def test_template_docs_validate_cleanly(self) -> None:
        """Verify the shipped template docs have no error-severity issues."""
        issues = validate_workflow_docs(
            FIXTURES / "PLAN.md",
            FIXTURES / "DECISIONS.md",
            FIXTURES / "GATES.md",
        )
        errors = [i for i in issues if i.severity == "error"]
        assert errors == [], f"Template docs have errors: {errors}"

    def test_missing_plan_returns_error(self, tmp_path: Path) -> None:
        """Verify missing PLAN.md produces an error."""
        issues = validate_workflow_docs(
            tmp_path / "PLAN.md",
            FIXTURES / "DECISIONS.md",
            FIXTURES / "GATES.md",
        )
        errors = [i for i in issues if i.severity == "error"]
        assert any("PLAN.md" in e.message for e in errors)

    def test_missing_gates_returns_error(self, tmp_path: Path) -> None:
        """Verify missing GATES.md produces an error."""
        issues = validate_workflow_docs(
            FIXTURES / "PLAN.md",
            FIXTURES / "DECISIONS.md",
            tmp_path / "GATES.md",
        )
        errors = [i for i in issues if i.severity == "error"]
        assert any("GATES.md" in e.message for e in errors)
