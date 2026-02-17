# Python Standards Profile

Apply this profile when a project in this template chooses Python.

## Toolchain and Dependency Management

- Python version: `>=3.11`
- Package manager: `uv`
- Do not use `pip` or `poetry` for project dependency resolution.

Required commands:

```bash
uv add <package>
uv add --dev <package>
uv lock
uv sync
uv run <command>
```

## Lockfile Policy

- Commit `uv.lock`.
- CI must use the committed lockfile (`uv sync --locked`).

## CI/CD Baseline

Minimum CI stages:

1. Setup pinned toolchain versions.
2. Install dependencies from lockfile.
3. Check formatting.
4. Run linting.
5. Run tests with coverage threshold enforcement.
6. Run workflow-doc validation (`./scripts/workflow.sh validate`).

Example Python gates:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=95
./scripts/workflow.sh validate
```

## Testing and Coverage Standard

- Required coverage threshold: `>=95%` for production modules.
- New behavior must include tests in the same change set.
- Integration tests should cover critical user flows and failure paths.

## Pre-commit Recommendation

Use pre-commit hooks that mirror CI checks to reduce drift between local and CI behavior.
