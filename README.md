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
    - Run smoke tests to validate the environment
    - Clean up smoke test files on success

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
- `tests/`: Test files (must match `src` filenames, prefixed with `test_`).
- `pyproject.toml`: Configuration for all tools.