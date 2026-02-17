# Review Gates

Each phase must pass all criteria before advancing.

- `[command]` criteria are machine-verifiable.
- `[manual]` criteria require human judgment.

---

## Phase 1: Problem Framing and Contract

- [ ] `[manual]` Objective, scope, constraints, and non-goals are coherent
- [ ] `[manual]` Interfaces and acceptance criteria are testable
- [ ] `[manual]` Risks and mitigations are documented
- [ ] `[command]` `./scripts/workflow.sh validate` passes

## Phase 2: Implementation and Verification

- [ ] `[manual]` Implementation matches phase 1 contracts
- [ ] `[manual]` Edge cases and failure modes are handled
- [ ] `[command]` `./scripts/workflow.sh validate` passes
- [ ] `[command]` Language-profile checks pass (see selected profile in `standards/`)

## Phase 3: Hardening and Delivery

- [ ] `[manual]` Runbook documents failure scenarios and recovery steps
- [ ] `[manual]` Remaining risks and owners are explicit
- [ ] `[command]` `./scripts/workflow.sh validate` passes
- [ ] `[command]` Release-quality checks pass (from selected language profile)
