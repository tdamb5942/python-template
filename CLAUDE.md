# CLAUDE.md - Project Guidelines

## 0. Context Initialization (USER: FILL THIS OUT)
> **Instructions for User:** Before starting, please answer the three questions below. This helps me tailor my code generation to your specific role and project goals.

1.  **What is your Role?** (e.g., Junior Data Engineer, Lead Dev, Analyst)
    - Junior Data Engineer
2.  **What is the Core Project Goal?** (e.g., ETL pipeline for wildlife camera trap data)
    - Update this template repo
3.  **Are there specific constraints?** (e.g., Must run on Raspberry Pi, strictly no cloud storage, etc.)
    - None

---

## 1. Development Environment
- **Language:** Python 3.11+
- **Package Manager:** `uv` (Strictly no pip/poetry).
  - Install: `uv add <package>` | `uv add --dev <package>`
  - Sync: `uv sync`
  - Run: `uv run <script>`
- **Linting/Formatting:** `ruff` via `uv run ruff check .` or `format .`
- **Pre-commit:** `uv run pre-commit install` (runs format, lint, tests on commit)
- **Secrets:** `.env` for local development.

## 2. Code Structure & Standards
- **Directory:** Flat structure in `src/`. Scripts named descriptively (e.g., `ingest.py`).
- **Naming:** `lower_snake_case` for Python.
- **Type Hints:** Mandatory for all function signatures.
- **Docstrings:** Google Style (Summary, Args, Returns).
- **Pathing:** Use `pathlib` over `os.path` where possible.

## 3. Testing Philosophy
- **Framework:** `pytest`.
- **Workflow:** Code first, then immediate test coverage.
- **Coverage Target:** 95% for production modules.
- **Mocking:** Minimal. Mock external APIs/DBs only; use fixtures for data logic.
- **AI Requirement:** When generating code, you must provide a corresponding `test_*.py` suite.

## 4. AI Behavior & Junior Mentorship
- **Explain "Why":** If you see inefficient patterns, explain the optimization (O-notation or Pythonic sugar).
- **Security First:** Aggressively warn about hardcoded credentials.
- **Data Integrity:** Suggest validation checks (Pydantic or simple asserts) for data ingest inputs.

## 5. Workflow (Phase-Gated Delivery)
- **Plan:** `docs/workflow/PLAN.md` — current phase, scope boundaries, and checklists.
- **Decisions:** `docs/workflow/DECISIONS.md` — architecture decision log (append-only).
- **Gates:** `docs/workflow/GATES.md` — review criteria per phase (command + manual).
- **CLI:** `uv run scripts/workflow.py status|prompt|validate`
- **Rules:**
  - Read `docs/workflow/PLAN.md` at the start of every session.
  - Do NOT begin work on a phase until the prior phase's review gate passes.
  - When making an architecture decision, append to `docs/workflow/DECISIONS.md` BEFORE implementing.
  - When completing a checklist item, update `docs/workflow/PLAN.md` (`- [ ]` to `- [x]`).
  - Run `uv run scripts/workflow.py validate` before marking a phase complete.