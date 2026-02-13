# Python Data Engineering Template

A standardized template for Langland Conservation Python projects, configured with `uv`, `ruff`, and `pytest`.

## 🚀 Getting Started

### Quick Start (Recommended)
1.  **Clone this repo** (or use "Use this template").
2.  **Run the bootstrap script**:
    ```bash
    uv run scripts/setup.py
    ```
    This will:
    - Install all dependencies (including dev tools)
    - Create `.env` from `.env.example`
    - Interactively configure your project context in `CLAUDE.md`
    - Initialize workflow docs with your project name
    - Run only the bootstrap smoke test (`tests/test_smoke.py`) to validate the environment
    - Clean up bootstrap artifacts on success (`src/smoke.py`, `tests/test_smoke.py`, and `scripts/setup.py`)

### Manual Setup (Alternative)
1.  **Clone this repo** (or use "Use this template").
2.  **Initialize Environment**:
    ```bash
    uv sync
    ```
3.  **Configure AI Context**:
    - Open `CLAUDE.md`.
    - Replace `{{ROLE}}`, `{{PROJECT_GOAL}}`, and `{{CONSTRAINTS}}` placeholders with your information.
4.  **Remove smoke test files** after verifying everything works:
    ```bash
    rm src/smoke.py tests/test_smoke.py
    ```

### 2. Development Workflow
- **Add Dependencies**: `uv add pandas`
- **Format Code**: `uv run ruff format .`
- **Lint Code**: `uv run ruff check .`
- **Run Tests**: `uv run pytest`

## 📁 Structure
- `src/`: Source code goes here.
- `src/workflow/`: Phase-gated workflow types and parser.
- `tests/`: Test files (must match `src` filenames, prefixed with `test_`).
- `docs/workflow/`: Implementation plan, architecture decisions, and review gates.
- `scripts/workflow.py`: CLI for workflow management.
- `pyproject.toml`: Configuration for all tools.

## 📋 Workflow (Phase-Gated Delivery)

This template includes a lightweight phase-gated workflow for structured project delivery.

- **`docs/workflow/PLAN.md`** — Your implementation plan with phases, checklists, and scope boundaries.
- **`docs/workflow/DECISIONS.md`** — Architecture decision log.
- **`docs/workflow/GATES.md`** — Review gate criteria per phase.

### Usage
```bash
uv run scripts/workflow.py status     # See current phase and progress
uv run scripts/workflow.py prompt     # Get focused prompt for current phase
uv run scripts/workflow.py validate   # Validate plan structure (used by CI)
```

Customize `docs/workflow/PLAN.md` with your project's phases, then work through them sequentially. See `CLAUDE.md` Section 5 for the rules.
