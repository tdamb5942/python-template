"""Tests for the setup.py bootstrap script."""

import sys
from pathlib import Path

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
