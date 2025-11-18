"""Bootstrap script for initializing the template repository.

This script:
1. Installs dependencies via uv
2. Creates .env from .env.example if needed
3. Interactively fills out CLAUDE.md context
4. Runs smoke tests to validate the environment
5. Cleans up smoke test artifacts on success
"""

import shutil
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


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and handle errors.

    Args:
        cmd: Command and arguments as a list.
        description: Human-readable description for logging.

    Returns:
        bool: True if command succeeded, False otherwise.
    """
    print(f"🔧 {description}...")
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Failed: {description}")
        print(f"   Error: {e}")
        return False


def install_dependencies() -> bool:
    """Install project dependencies using uv.

    Returns:
        bool: True if all installations succeeded.
    """
    if not run_command(["uv", "sync"], "Installing all dependencies (including dev tools)"):
        return False

    print("✅ Dependencies installed successfully\n")
    return True


def setup_env_file() -> None:
    """Create .env from .env.example if it doesn't exist."""
    if ENV_FILE.exists():
        print("ℹ️  .env already exists, skipping...\n")
        return

    if ENV_EXAMPLE.exists():
        ENV_FILE.write_text(ENV_EXAMPLE.read_text())
        print("ℹ️  Created .env from template\n")
    else:
        print("⚠️  No .env.example found, skipping .env creation\n")


def update_claude_context() -> None:
    """Interactively update CLAUDE.md with user's project context."""
    if not CLAUDE_MD.exists():
        print("⚠️  CLAUDE.md not found, skipping context setup\n")
        return

    content = CLAUDE_MD.read_text()

    # Check if placeholders exist
    if "{{ROLE}}" not in content:
        print("ℹ️  CLAUDE.md already configured, skipping...\n")
        return

    print("📝 Let's configure your AI context (CLAUDE.md):\n")

    # Collect user input
    role = input(
        "  What is your Role? (e.g., Junior Data Engineer, Lead Dev, Analyst)\n  → "
    ).strip()
    project_goal = input(
        "  What is the Core Project Goal? (e.g., ETL pipeline for camera trap data)\n  → "
    ).strip()
    constraints = input(
        "  Are there specific constraints? (e.g., Raspberry Pi only, or press Enter to skip)\n  → "
    ).strip()

    # Replace placeholders with user input
    content = content.replace("{{ROLE}}", role or "Not specified")
    content = content.replace("{{PROJECT_GOAL}}", project_goal or "Not specified")
    content = content.replace("{{CONSTRAINTS}}", constraints or "None")

    CLAUDE_MD.write_text(content)
    print("\n✅ CLAUDE.md updated with your project context\n")


def run_smoke_tests() -> bool:
    """Run pytest smoke tests to validate the environment.

    Returns:
        bool: True if all tests passed.
    """
    print("🔥 Running Smoke Tests...\n")

    result = subprocess.run(
        ["uv", "run", "pytest", "-v"],
        cwd=PROJECT_ROOT,
        capture_output=False,
    )

    if result.returncode == 0:
        print("\n✅ Tests passed. Environment is healthy.\n")
        return True
    else:
        print("\n❌ Smoke tests failed! Keeping files for debugging.")
        return False


def cleanup_smoke_files() -> None:
    """Remove smoke test artifacts and setup scripts after successful validation."""
    print("🧹 Removing smoke test artifacts...")

    for file_path in SMOKE_FILES:
        if file_path.exists():
            file_path.unlink()
            print(f"   Deleted: {file_path.relative_to(PROJECT_ROOT)}")

    # Remove the scripts directory (including this setup script)
    scripts_dir = PROJECT_ROOT / "scripts"
    if scripts_dir.exists():
        shutil.rmtree(scripts_dir)
        print(f"   Deleted: {scripts_dir.relative_to(PROJECT_ROOT)}/")

    print()


def main() -> int:
    """Execute the bootstrap process.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("=" * 60)
    print("🚀 Python Template Repository Setup")
    print("=" * 60)
    print()

    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n💥 Setup failed during dependency installation")
        return 1

    # Step 2: Setup environment variables
    setup_env_file()

    # Step 3: Configure AI context
    update_claude_context()

    # Step 4: Validate with smoke tests
    if not run_smoke_tests():
        return 1

    # Step 5: Cleanup
    cleanup_smoke_files()

    # Success!
    print("=" * 60)
    print("✨ Project is ready! Don't forget to commit the cleanup deletions.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
