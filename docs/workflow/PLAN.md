# Implementation Plan

**Project:** {{PROJECT_NAME}}
**Current Phase:** 1
**Last Updated:** {{DATE}}

## Blockers
<!-- List anything blocking progress. Remove items when resolved. -->
- None

## Decisions
<!-- Brief summary of key decisions. Full detail in DECISIONS.md. -->
- ADR-000: Adopted phase-gated workflow for structured delivery.

---

## Phase 1: Design & Contract

**Goal:** Define data contracts, schemas, and pipeline architecture before writing implementation code.

### Read First
- `docs/workflow/DECISIONS.md`
- `docs/workflow/GATES.md`

### Scope
- Define source and target data schemas
- Document data flow and transformation logic
- Establish error handling strategy
- Write acceptance criteria for pipeline outputs

### Out of Scope
- Production implementation code
- Performance optimization
- Deployment configuration

### Checklist
- [ ] (1-1) Source data schema documented
- [ ] (1-2) Target data schema documented
- [ ] (1-3) Data flow diagram or description in DECISIONS.md
- [ ] (1-4) Error handling strategy decided (see DECISIONS.md)
- [ ] (1-5) Acceptance criteria written in GATES.md

### Review Gate
See `docs/workflow/GATES.md` Phase 1 section.

---

## Phase 2: Core Pipeline

**Goal:** Build the core data pipeline with tests, following Phase 1 contracts.

### Read First
- `docs/workflow/PLAN.md` (Phase 1 checklist — must be complete)
- `docs/workflow/DECISIONS.md`

### Scope
- Implement extraction logic
- Implement transformation logic
- Implement loading logic
- Unit tests for each stage
- Integration test for end-to-end flow

### Out of Scope
- Deployment automation
- Monitoring and alerting
- Performance tuning beyond correctness

### Checklist
- [ ] (2-1) Extract module implemented and tested
- [ ] (2-2) Transform module implemented and tested
- [ ] (2-3) Load module implemented and tested
- [ ] (2-4) End-to-end integration test passes
- [ ] (2-5) Error handling covers documented failure modes

### Review Gate
See `docs/workflow/GATES.md` Phase 2 section.

---

## Phase 3: Integration & Deployment

**Goal:** Production-ready pipeline with CI, monitoring, and documentation.

### Read First
- `docs/workflow/PLAN.md` (Phase 2 checklist — must be complete)
- `docs/workflow/GATES.md`

### Scope
- CI/CD pipeline configuration
- Data quality assertions
- Logging and error reporting
- README and runbook documentation
- Final cleanup and code review

### Out of Scope
- Feature additions beyond original scope
- Performance optimization beyond SLA requirements

### Checklist
- [ ] (3-1) CI pipeline runs all quality gates
- [ ] (3-2) Data quality assertions implemented
- [ ] (3-3) Logging covers all pipeline stages
- [ ] (3-4) README updated with usage instructions
- [ ] (3-5) Runbook documents common failure scenarios

### Review Gate
See `docs/workflow/GATES.md` Phase 3 section.
