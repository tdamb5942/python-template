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
2. Update `AGENTS.md` with your project objective, constraints, and success criteria.
3. Customize:
   - `docs/workflow/PLAN.md`
   - `docs/workflow/DECISIONS.md`
   - `docs/workflow/GATES.md`
4. Validate workflow docs:
   ```bash
   ./scripts/workflow.sh validate
   ```
5. Run full template checks locally:
   ```bash
   ./scripts/check-template.sh
   ```

## Workflow Commands

```bash
./scripts/workflow.sh status    # Current phase, checklist progress, blockers
./scripts/workflow.sh prompt    # Full markdown block for current phase
./scripts/workflow.sh validate  # Structural validation across workflow docs
```

## Language Standards

- Python profile: `standards/python.md`

Add additional profiles as needed (for example `standards/node.md`, `standards/go.md`).

## CI Policy

The core template CI validates workflow integrity and template quality only.

When you select a language profile, extend CI with that profile's lint/test/coverage gates.
