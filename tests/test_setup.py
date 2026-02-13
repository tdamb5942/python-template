"""Tests for the setup.py bootstrap script."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add scripts to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import setup  # noqa: E402


def test_constants_are_valid_paths() -> None:
    """Verify that all path constants point to expected locations."""
    assert setup.PROJECT_ROOT.exists()
    assert setup.CLAUDE_MD.exists()
    assert setup.ENV_EXAMPLE.exists()
    # smoke files should exist in template
    for smoke_file in setup.SMOKE_FILES:
        assert smoke_file.exists(), f"Expected smoke file missing: {smoke_file}"


def test_run_command_handles_invalid_command() -> None:
    """Verify run_command returns False for invalid commands."""
    result = setup.run_command(["this-command-does-not-exist-xyz123"], "Test invalid command")
    assert result is False


def test_smoke_files_constant_is_complete() -> None:
    """Verify SMOKE_FILES list contains expected files."""
    smoke_file_names = [f.name for f in setup.SMOKE_FILES]
    assert "smoke.py" in smoke_file_names
    assert "test_smoke.py" in smoke_file_names
    assert len(setup.SMOKE_FILES) == 2


def test_update_claude_context_updates_only_missing_placeholders(monkeypatch, tmp_path) -> None:
    """Verify only remaining placeholders are prompted and replaced."""
    claude_path = tmp_path / "CLAUDE.md"
    claude_path.write_text(
        "Role: Senior Analyst\nProject Goal: {{PROJECT_GOAL}}\nConstraints: {{CONSTRAINTS}}\n"
    )
    monkeypatch.setattr(setup, "CLAUDE_MD", claude_path)

    answers = iter(["ETL camera trap pipeline", "Raspberry Pi only"])

    def fake_input(prompt: str) -> str:
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    setup.update_claude_context()

    updated = claude_path.read_text()
    assert "{{PROJECT_GOAL}}" not in updated
    assert "{{CONSTRAINTS}}" not in updated
    assert "Senior Analyst" in updated
    assert "ETL camera trap pipeline" in updated
    assert "Raspberry Pi only" in updated


def test_run_smoke_tests_is_scoped_to_smoke_file(monkeypatch) -> None:
    """Verify smoke tests only execute the smoke test module."""
    fake_result = MagicMock(returncode=0)
    run_mock = MagicMock(return_value=fake_result)
    monkeypatch.setattr(setup.subprocess, "run", run_mock)

    assert setup.run_smoke_tests() is True
    run_mock.assert_called_once_with(
        ["uv", "run", "pytest", "-v", "tests/test_smoke.py"],
        cwd=setup.PROJECT_ROOT,
        capture_output=False,
    )


def test_initialize_workflow_docs_replaces_placeholders(monkeypatch, tmp_path) -> None:
    """Verify workflow doc initialization replaces {{PROJECT_NAME}} and {{DATE}}."""
    docs_dir = tmp_path / "docs" / "workflow"
    docs_dir.mkdir(parents=True)

    plan = docs_dir / "PLAN.md"
    plan.write_text("**Project:** {{PROJECT_NAME}}\n**Last Updated:** {{DATE}}\n")

    decisions = docs_dir / "DECISIONS.md"
    decisions.write_text("- **Date:** {{DATE}}\n")

    gates = docs_dir / "GATES.md"
    gates.write_text("# Gates\nNo placeholders here.\n")

    monkeypatch.setattr(setup, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(setup, "WORKFLOW_DOCS", [plan, decisions, gates])
    monkeypatch.setattr("builtins.input", lambda _: "camera-trap-etl")

    setup.initialize_workflow_docs()

    plan_text = plan.read_text()
    assert "{{PROJECT_NAME}}" not in plan_text
    assert "camera-trap-etl" in plan_text
    assert "{{DATE}}" not in plan_text

    decisions_text = decisions.read_text()
    assert "{{DATE}}" not in decisions_text

    # gates had no placeholders, should be unchanged
    assert gates.read_text() == "# Gates\nNo placeholders here.\n"


def test_initialize_workflow_docs_skips_already_initialized(monkeypatch, tmp_path) -> None:
    """Verify workflow init is skipped when no placeholders remain."""
    docs_dir = tmp_path / "docs" / "workflow"
    docs_dir.mkdir(parents=True)

    plan = docs_dir / "PLAN.md"
    plan.write_text("**Project:** camera-trap-etl\n")

    monkeypatch.setattr(setup, "WORKFLOW_DOCS", [plan])

    # Should not prompt for input
    setup.initialize_workflow_docs()

    assert plan.read_text() == "**Project:** camera-trap-etl\n"


def test_cleanup_smoke_files_removes_only_allowlisted_paths(monkeypatch, tmp_path) -> None:
    """Verify cleanup does not remove arbitrary scripts."""
    src_dir = tmp_path / "src"
    tests_dir = tmp_path / "tests"
    scripts_dir = tmp_path / "scripts"
    src_dir.mkdir()
    tests_dir.mkdir()
    scripts_dir.mkdir()

    smoke_src = src_dir / "smoke.py"
    smoke_test = tests_dir / "test_smoke.py"
    setup_script = scripts_dir / "setup.py"
    keep_script = scripts_dir / "keep.py"

    smoke_src.write_text("def smoke_test():\n    return True\n")
    smoke_test.write_text("def test_smoke():\n    assert True\n")
    setup_script.write_text("print('setup')\n")
    keep_script.write_text("print('keep')\n")

    monkeypatch.setattr(setup, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(setup, "SMOKE_FILES", [smoke_src, smoke_test])
    monkeypatch.setattr(setup, "SELF_SCRIPT", setup_script)

    setup.cleanup_smoke_files()

    assert not smoke_src.exists()
    assert not smoke_test.exists()
    assert not setup_script.exists()
    assert keep_script.exists()
    assert scripts_dir.exists()
