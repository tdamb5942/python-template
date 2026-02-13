"""Bootstrap script for initializing the template repository.

This script:
1. Installs dependencies via uv
2. Installs pre-commit git hooks
3. Creates .env from .env.example if needed
4. Interactively fills out CLAUDE.md context
5. Initializes workflow docs with project name and date
6. Runs smoke tests to validate the environment
7. Cleans up smoke test artifacts on success
"""

import datetime
import subprocess
import sys
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
SMOKE_FILES = [
    PROJECT_ROOT / "src" / "smoke.py",
    PROJECT_ROOT / "tests" / "test_smoke.py",
]
SELF_SCRIPT = PROJECT_ROOT / "scripts" / "setup.py"
CLAUDE_PLACEHOLDERS = [
    (
        "{{ROLE}}",
        "  What is your Role? (e.g., Junior Data Engineer, Lead Dev, Analyst)\n  \u2192 ",
        "Not specified",
    ),
    (
        "{{PROJECT_GOAL}}",
        "  What is the Core Project Goal? (e.g., ETL pipeline for camera trap data)\n  \u2192 ",
        "Not specified",
    ),
    (
        "{{CONSTRAINTS}}",
        "  Are there specific constraints? (e.g., Raspberry Pi only, or press Enter to skip)\n"
        "  \u2192 ",
        "None",
    ),
]
CLEANUP_ALLOWLIST = {
    Path("src/smoke.py"),
    Path("tests/test_smoke.py"),
    Path("scripts/setup.py"),
}
WORKFLOW_DOCS = [
    PROJECT_ROOT / "docs" / "workflow" / "PLAN.md",
    PROJECT_ROOT / "docs" / "workflow" / "DECISIONS.md",
    PROJECT_ROOT / "docs" / "workflow" / "GATES.md",
]
WORKFLOW_PLACEHOLDERS = ("{{PROJECT_NAME}}", "{{DATE}}")


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and handle errors.

    Args:
        cmd: Command and arguments as a list.
        description: Human-readable description for logging.

    Returns:
        bool: True if command succeeded, False otherwise.
    """
    print(f"\U0001f527 {description}...")
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\u274c Failed: {description}")
        print(f"   Error: {e}")
        return False


def install_dependencies() -> bool:
    """Install project dependencies using uv.

    Returns:
        bool: True if all installations succeeded.
    """
    if not run_command(["uv", "sync"], "Installing all dependencies (including dev tools)"):
        return False

    print("\u2705 Dependencies installed successfully\n")
    return True


def install_pre_commit_hooks() -> bool:
    """Install pre-commit git hooks.

    Returns:
        bool: True if installation succeeded.
    """
    if not run_command(["uv", "run", "pre-commit", "install"], "Installing pre-commit git hooks"):
        return False

    print("\u2705 Pre-commit hooks installed successfully\n")
    return True


def setup_env_file() -> None:
    """Create .env from .env.example if it doesn't exist."""
    if ENV_FILE.exists():
        print("\u2139\ufe0f  .env already exists, skipping...\n")
        return

    if ENV_EXAMPLE.exists():
        ENV_FILE.write_text(ENV_EXAMPLE.read_text())
        print("\u2139\ufe0f  Created .env from template\n")
    else:
        print("\u26a0\ufe0f  No .env.example found, skipping .env creation\n")


def update_claude_context() -> None:
    """Interactively update CLAUDE.md with user's project context."""
    if not CLAUDE_MD.exists():
        print("\u26a0\ufe0f  CLAUDE.md not found, skipping context setup\n")
        return

    content = CLAUDE_MD.read_text()

    placeholders_to_replace = [item for item in CLAUDE_PLACEHOLDERS if item[0] in content]
    if not placeholders_to_replace:
        print("\u2139\ufe0f  CLAUDE.md already configured, skipping...\n")
        return

    print("\U0001f4dd Let's configure your AI context (CLAUDE.md):\n")

    for placeholder, prompt, default_value in placeholders_to_replace:
        user_value = input(prompt).strip()
        content = content.replace(placeholder, user_value or default_value)

    CLAUDE_MD.write_text(content)
    print("\n\u2705 CLAUDE.md updated with your project context\n")


def initialize_workflow_docs() -> None:
    """Replace template placeholders in workflow documents.

    Prompts the user for a project name and fills in {{PROJECT_NAME}} and
    {{DATE}} placeholders across all workflow docs. Skips files that don't
    exist or have already been initialized.
    """
    docs_needing_init = [
        doc
        for doc in WORKFLOW_DOCS
        if doc.exists() and any(ph in doc.read_text() for ph in WORKFLOW_PLACEHOLDERS)
    ]

    if not docs_needing_init:
        print("\u2139\ufe0f  Workflow docs already initialized, skipping...\n")
        return

    print("\U0001f4cb Let's configure your workflow docs:\n")
    project_name = input("  Project name (e.g., camera-trap-etl)\n  \u2192 ").strip()
    if not project_name:
        project_name = "Unnamed Project"

    today = datetime.date.today().isoformat()

    for doc_path in docs_needing_init:
        content = doc_path.read_text()
        content = content.replace("{{PROJECT_NAME}}", project_name)
        content = content.replace("{{DATE}}", today)
        doc_path.write_text(content)
        print(f"   Initialized: {doc_path.relative_to(PROJECT_ROOT)}")

    print("\n\u2705 Workflow docs initialized\n")


def run_smoke_tests() -> bool:
    """Run pytest smoke tests to validate the environment.

    Returns:
        bool: True if all tests passed.
    """
    print("\U0001f525 Running Smoke Tests...\n")

    result = subprocess.run(
        ["uv", "run", "pytest", "-v", "tests/test_smoke.py"],
        cwd=PROJECT_ROOT,
        capture_output=False,
    )

    if result.returncode == 0:
        print("\n\u2705 Tests passed. Environment is healthy.\n")
        return True
    else:
        print("\n\u274c Smoke tests failed! Keeping files for debugging.")
        return False


def cleanup_smoke_files() -> None:
    """Remove smoke test artifacts and setup script after successful validation."""
    print("\U0001f9f9 Removing smoke test artifacts...")

    for file_path in [*SMOKE_FILES, SELF_SCRIPT]:
        try:
            relative_path = file_path.relative_to(PROJECT_ROOT)
        except ValueError:
            continue

        if relative_path not in CLEANUP_ALLOWLIST:
            print(f"   Skipped (not allowlisted): {relative_path}")
            continue

        if file_path.exists():
            file_path.unlink()
            print(f"   Deleted: {relative_path}")

    print()


def main() -> int:
    """Execute the bootstrap process.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("=" * 60)
    print("\U0001f680 Python Template Repository Setup")
    print("=" * 60)
    print()

    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n\U0001f4a5 Setup failed during dependency installation")
        return 1

    # Step 2: Install pre-commit hooks
    if not install_pre_commit_hooks():
        print("\n\U0001f4a5 Setup failed during pre-commit installation")
        return 1

    # Step 3: Setup environment variables
    setup_env_file()

    # Step 4: Configure AI context
    update_claude_context()

    # Step 5: Initialize workflow docs
    initialize_workflow_docs()

    # Step 6: Validate with smoke tests
    if not run_smoke_tests():
        return 1

    # Step 7: Cleanup
    cleanup_smoke_files()

    # Success!
    print("=" * 60)
    print("\u2728 Project is ready! Don't forget to commit the cleanup deletions.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
