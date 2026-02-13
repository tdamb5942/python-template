# Review Gates

> Each phase must pass ALL criteria before advancing to the next phase.
> Criteria marked `[command]` are verified automatically by CI.
> Criteria marked `[manual]` require human judgment.

---

## Phase 1: Design & Contract

- [ ] `[manual]` Source and target schemas are documented and reviewed
- [ ] `[manual]` Data flow is described in DECISIONS.md
- [ ] `[manual]` Error handling strategy is decided in DECISIONS.md
- [ ] `[command]` `uv run scripts/workflow.py validate` passes

## Phase 2: Core Pipeline

- [ ] `[command]` `uv run pytest` passes with no failures
- [ ] `[command]` `uv run ruff check .` passes
- [ ] `[command]` `uv run ruff format --check .` passes
- [ ] `[manual]` Error handling covers all failure modes from Phase 1 design
- [ ] `[manual]` Integration test demonstrates end-to-end correctness
- [ ] `[command]` `uv run scripts/workflow.py validate` passes

## Phase 3: Integration & Deployment

- [ ] `[command]` `uv run pytest` passes
- [ ] `[command]` `uv run ruff check .` passes
- [ ] `[manual]` README includes usage instructions
- [ ] `[manual]` Runbook documents failure scenarios and recovery steps
- [ ] `[manual]` Data quality assertions cover critical fields
- [ ] `[command]` `uv run scripts/workflow.py validate` passes
