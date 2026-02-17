# AGENTS.md

This file is the canonical instruction contract for agentic coding assistants in this repository.

## Precedence
- This repo’s instructions override any global agent preferences.
- If there is a conflict, follow the nearest repo-local instruction and workflow artifacts.

## Session Start (mandatory)
1) Read:
   - `AGENTS.md`
   - `docs/workflow/PLAN.md`
   - `docs/workflow/DECISIONS.md`
   - `docs/workflow/GATES.md`
2) Run:
   - `./scripts/workflow.sh status`
   - `./scripts/workflow.sh prompt`
3) Do not begin implementation work that violates the current phase scope.

## Project Contract (Phase 1 required)
Populate these fields in `docs/workflow/PLAN.md` (Phase 1) before implementation:
- Objective: What problem are we solving?
- Success criteria: What must be true for this to be done?
- Constraints: Regulatory, runtime, platform, budget, performance, etc.
- Non-goals: What is explicitly out of scope?
- Risks: What can fail and how will we detect it?

## Working Rules
- Prefer small, reviewable changes. Avoid scope creep and drive-by refactors.
- Keep architecture decisions in `docs/workflow/DECISIONS.md` (append-only; mark superseded when needed).
- Keep the active phase and checklist status in `docs/workflow/PLAN.md`.
- Do not advance to a new phase until the current phase gate passes in `docs/workflow/GATES.md`.
- Record assumptions explicitly when requirements are ambiguous.
- Phase discipline:
  - Phase 1: no product feature implementation (except explicitly recorded, isolated investigative spikes).
  - Phase 2+: implementation must match the Phase 1 contract.

## Phase-Gated Workflow
Primary workflow files:
- `docs/workflow/PLAN.md`
- `docs/workflow/DECISIONS.md`
- `docs/workflow/GATES.md`

Validation and status commands:
- `./scripts/workflow.sh status`
- `./scripts/workflow.sh prompt`
- `./scripts/workflow.sh validate`

Before claiming a phase is complete or advancing phases:
- Run `./scripts/workflow.sh validate` and record the result.
- Do not check off checklist/gate items without evidence (tests, command output, or concrete file references).

## Decision Triggers (when to add an ADR entry)
Add an ADR entry in `docs/workflow/DECISIONS.md` when you:
- Add a dependency or change ecosystem tooling
- Change a public interface/contract
- Change persistence/schema semantics
- Choose a non-obvious architectural approach or major tradeoff

## Language Standards Profiles
This core template is language-agnostic.
If a project chooses Python, apply `standards/python.md`.
Add additional profiles under `standards/` for other languages as needed.

## Repository Quality Expectations
- CI must run deterministic, non-interactive checks.
- Lockfiles for active ecosystems should be committed.
- Coverage thresholds must be enforced by CI when a language profile defines them.
- Public behavior changes require matching tests in the selected language profile.

## Safety (non-negotiable)
- Never commit secrets.
- Use synthetic data in examples/tests; do not paste real customer/PII/PHI into logs or tests.