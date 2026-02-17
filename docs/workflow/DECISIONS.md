# Architecture Decisions

Append new decisions below. Do not rewrite history; mark old decisions as superseded when needed.

---

## ADR-000: Adopt phase-gated delivery as the execution contract
- **Date:** 2026-02-17
- **Phase:** Setup
- **Status:** Accepted
- **Context:** Agentic sessions are fast but can drift without explicit scope, gates, and decision records.
- **Decision:** Use `PLAN.md`, `GATES.md`, and `DECISIONS.md` as mandatory workflow artifacts.
- **Rationale:** Keeps execution aligned across human and agent collaborators with low ceremony.
- **Consequences:** Teams must maintain phase checklists, gate status, and ADR updates before implementation changes.

---

<!-- TEMPLATE
## ADR-NNN: [Title]
- **Date:** YYYY-MM-DD
- **Phase:** [Phase number and name]
- **Status:** Accepted | Superseded by ADR-NNN
- **Context:** [Problem statement]
- **Decision:** [Chosen approach]
- **Rationale:** [Why this option]
- **Consequences:** [Ongoing impact]
-->
