"""Tests for the workflow CLI script (scripts/workflow.py)."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
WORKFLOW_SCRIPT = PROJECT_ROOT / "scripts" / "workflow.py"


def _run_workflow(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the workflow CLI with given arguments.

    Args:
        *args: Subcommand and arguments to pass.

    Returns:
        Completed process with captured stdout and stderr.
    """
    return subprocess.run(
        [sys.executable, str(WORKFLOW_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


class TestWorkflowStatus:
    """Tests for the 'status' subcommand."""

    def test_status_exits_zero(self) -> None:
        """Verify status command succeeds on valid docs."""
        result = _run_workflow("status")
        assert result.returncode == 0

    def test_status_shows_current_phase(self) -> None:
        """Verify status output includes the current phase name."""
        result = _run_workflow("status")
        assert "Phase 1" in result.stdout

    def test_status_shows_progress(self) -> None:
        """Verify status output includes progress indicators."""
        result = _run_workflow("status")
        assert "0/5" in result.stdout

    def test_status_shows_checklist(self) -> None:
        """Verify status output includes checklist items."""
        result = _run_workflow("status")
        assert "1-1" in result.stdout


class TestWorkflowPrompt:
    """Tests for the 'prompt' subcommand."""

    def test_prompt_exits_zero(self) -> None:
        """Verify prompt command succeeds on valid docs."""
        result = _run_workflow("prompt")
        assert result.returncode == 0

    def test_prompt_contains_goal_section(self) -> None:
        """Verify prompt output includes the Goal section."""
        result = _run_workflow("prompt")
        assert "## Goal" in result.stdout

    def test_prompt_contains_scope_section(self) -> None:
        """Verify prompt output includes the Scope section."""
        result = _run_workflow("prompt")
        assert "## Scope" in result.stdout

    def test_prompt_contains_review_gate(self) -> None:
        """Verify prompt output includes the Review Gate section."""
        result = _run_workflow("prompt")
        assert "## Review Gate" in result.stdout


class TestWorkflowValidate:
    """Tests for the 'validate' subcommand."""

    def test_validate_exits_zero_for_valid_docs(self) -> None:
        """Verify validate passes on the shipped template docs."""
        result = _run_workflow("validate")
        assert result.returncode == 0
        assert "OK" in result.stdout

    def test_validate_exits_one_for_missing_docs(self, tmp_path: Path, monkeypatch: object) -> None:
        """Verify validate fails when pointed at empty directory."""
        # Run workflow.py with a modified PROJECT_ROOT won't work easily,
        # so we test the underlying function directly instead
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from workflow.plan_parser import validate_workflow_docs

        issues = validate_workflow_docs(
            tmp_path / "PLAN.md",
            tmp_path / "DECISIONS.md",
            tmp_path / "GATES.md",
        )
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) >= 1


class TestWorkflowNoArgs:
    """Tests for CLI with no subcommand."""

    def test_no_args_exits_nonzero(self) -> None:
        """Verify running without a subcommand fails gracefully."""
        result = _run_workflow()
        assert result.returncode != 0
