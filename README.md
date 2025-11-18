# Python Data Engineering Template

A standardized template for Langland Conservation Python projects, configured with `uv`, `ruff`, and `pytest`.

## 🚀 Getting Started

### 1. Setup
1.  **Clone this repo** (or use "Use this template").
2.  **Initialize Environment**:
    ```bash
    uv sync
    uv add --dev ruff pytest pytest-cov
    ```
3.  **Configure AI Context**:
    - Open `CLAUDE.md`.
    - Fill out the **Context Initialization** section at the top.

### 2. Development Workflow
- **Add Dependencies**: `uv add pandas`
- **Format Code**: `uv run ruff format .`
- **Lint Code**: `uv run ruff check .`
- **Run Tests**: `uv run pytest`

## 📁 Structure
- `src/`: Source code goes here.
- `tests/`: Test files (must match `src` filenames, prefixed with `test_`).
- `pyproject.toml`: Configuration for all tools.