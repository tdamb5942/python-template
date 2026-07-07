# Agentic Coding Template (Language-Agnostic)

A reusable template for structured, phase-gated software delivery with agentic coding assistants.

The default template is intentionally language-agnostic. Language-specific engineering standards live in `standards/`.

## What This Template Provides

- Canonical assistant contract in `AGENTS.md`
- Phase-gated planning and delivery workflow in `docs/workflow/`
- A shell workflow CLI for status, prompt rendering, and doc validation
- CI checks that enforce template integrity

## Quick Start

1. Use this repository as a template.
2. Fill in the Project Contract (objective, success criteria, constraints, non-goals, risks) in `docs/workflow/PLAN.md`. The shipped contract describes this template itself — replace every field with your project's contract. Update `AGENTS.md` only with repo-specific conventions and safety constraints.
3. Customize:
   - `docs/workflow/PLAN.md`
   - `docs/workflow/DECISIONS.md` — ADR-000 records the template's adoption of the phase-gated workflow; keep, re-date, or supersede it as your project's first decision (the log is append-only — do not delete entries)
   - `docs/workflow/GATES.md`
4. Update `LICENSE` with your own copyright holder and year (the shipped notice names the template author).
5. Select a language profile (recommended): apply `standards/<language>.md`, extend `.github/workflows/ci.yml` with its lint/test/coverage gates, and record the choice as an ADR in `docs/workflow/DECISIONS.md`.
6. Validate workflow docs:
   ```bash
   ./scripts/workflow.sh validate
   ```
7. Run full template checks locally:
   ```bash
   ./scripts/check-template.sh
   ```

## Workflow Commands

```bash
./scripts/workflow.sh status    # Current phase, checklist progress, blockers
./scripts/workflow.sh prompt    # Full markdown block for current phase
./scripts/workflow.sh validate  # Structural validation across workflow docs
```

Checklist items are standard markdown task boxes (`- [ ] ...`) inside each `## Phase N:` section of `PLAN.md` and `GATES.md`; the `(1-1)`-style ids are optional labels for cross-referencing. `validate` blocks phase advancement while any prior-phase checklist item or gate criterion is unchecked.

## Language Standards

- Python profile: `standards/python.md`

Add additional profiles as needed (for example `standards/node.md`, `standards/go.md`).

## CI Policy

The core template CI validates workflow integrity and template quality only.

When you select a language profile, extend CI with that profile's lint/test/coverage gates.
