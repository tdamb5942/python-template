# Implementation Plan

**Project:** Template Project  
**Current Phase:** 1  
**Last Updated:** 2026-02-17  

## Project Contract (Phase 1 required)

Fill this in *before* implementation. Treat this block as the primary source for Phase 1 scope and acceptance; use `DECISIONS.md` for architecture decisions and `GATES.md` for advancement criteria.

### Required
- **Objective:** Provide a language-agnostic template for phase-gated agentic software delivery.
- **Success criteria:** Workflow docs validate, template checks pass, and language standards can be applied via profiles.
- **Constraints:** Core template stays language-agnostic; language-specific enforcement belongs in `standards/` profiles.
- **Non-goals:** Shipping full implementation scaffolds for every language in core.
- **Risks:** Teams may skip profile selection or keep ambiguous scope; detect via workflow validation and gate reviews.

### Strongly recommended (to make Phase 1 gates unambiguous)
- **Assumptions:** [TBD — Inputs you’re assuming to be true]
- **Key interfaces / contracts:** [TBD — APIs, CLI, schemas, file formats, SLAs]
- **Acceptance checks:** [TBD — How we will verify success (tests, commands, scenarios)]
- **Risks & mitigations:** [TBD — Map risks to concrete mitigations/owners]
- **Phase 2 scope boundary:** [TBD — What Phase 2 will implement vs defer]

## Blockers
- None

## Decisions
- ADR-000: Use a phase-gated workflow as the execution contract.

---

## Phase 1: Problem Framing and Contract

**Goal:** Lock scope, interface expectations, and acceptance criteria before implementation.

### Read First
- `AGENTS.md`
- `docs/workflow/DECISIONS.md`
- `docs/workflow/GATES.md`

### Scope
- Define target user or system outcome
- Define success criteria and measurable acceptance checks
- Document constraints, assumptions, and non-goals
- Identify high-risk unknowns and mitigation strategy

### Out of Scope
- Feature implementation
- Performance tuning
- Deployment automation

### Checklist
- [ ] (1-1) Objective and success criteria are explicit
- [ ] (1-2) Constraints and non-goals are explicit
- [ ] (1-3) Key interfaces/contracts are documented
- [ ] (1-4) Major risks and mitigations are documented
- [ ] (1-5) Phase 2 scope is clearly bounded

### Review Gate
See `docs/workflow/GATES.md` Phase 1 section.

---

## Phase 2: Implementation and Verification

**Goal:** Build the scoped solution and verify correctness against phase 1 contracts.

### Read First
- `docs/workflow/PLAN.md` (phase 1 checklist)
- `docs/workflow/DECISIONS.md`
- Selected language profile in `standards/`

### Scope
- Implement agreed interfaces and behavior
- Add tests for core behavior and edge cases
- Resolve review findings that block correctness

### Out of Scope
- New feature requests outside phase 1 scope
- Broad refactors not justified by scope or risk

### Checklist
- [ ] (2-1) Implementation matches phase 1 contracts
- [ ] (2-2) Tests cover core behavior and edge cases
- [ ] (2-3) Defined quality gates pass locally
- [ ] (2-4) Blocking review findings are resolved
- [ ] (2-5) Phase 3 hardening scope is documented

### Review Gate
See `docs/workflow/GATES.md` Phase 2 section.

---

## Phase 3: Hardening and Delivery

**Goal:** Make the solution production-ready with operational confidence.

### Read First
- `docs/workflow/PLAN.md` (phase 2 checklist)
- `docs/workflow/GATES.md`
- Selected language profile in `standards/`

### Scope
- Finalize CI/CD and release checks
- Add operational runbook and failure handling guidance
- Confirm observability and recovery expectations
- Final documentation and handoff notes

### Out of Scope
- Net-new features unrelated to original objective
- Redesigning architecture without a new ADR

### Checklist
- [ ] (3-1) CI gates are stable and deterministic
- [ ] (3-2) Operational runbook covers common failures
- [ ] (3-3) Observability and alerting expectations are documented
- [ ] (3-4) Release notes and usage docs are complete
- [ ] (3-5) Open risks are tracked with owners

### Review Gate
See `docs/workflow/GATES.md` Phase 3 section.
