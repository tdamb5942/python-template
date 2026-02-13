# Architecture Decisions

> Append new decisions below. Do not edit past decisions (mark as "Superseded" instead).
> Claude Code: When making an architecture choice, append an entry here BEFORE implementing.

---

## ADR-000: Adopt phase-gated workflow
- **Date:** {{DATE}}
- **Phase:** Setup
- **Status:** Accepted
- **Context:** Sequential prompting without written scope boundaries leads to scope creep and lost architectural context between sessions.
- **Decision:** Use a lightweight phase-gated workflow with PLAN.md as source of truth, review gates enforced by CI, and decisions captured in this file.
- **Rationale:** Captures the value of heavyweight workflow systems at a fraction of the ceremony. Markdown is readable by both humans and Claude Code.
- **Consequences:** Each phase must pass its review gate before the next begins. Architecture decisions must be recorded before implementation.

---

<!-- TEMPLATE: Copy the block below for new decisions.

## ADR-NNN: [Title]
- **Date:** YYYY-MM-DD
- **Phase:** [Phase number and name]
- **Status:** Accepted | Superseded by ADR-NNN
- **Context:** [What problem prompted this decision?]
- **Decision:** [What did we choose?]
- **Rationale:** [Why this over alternatives?]
- **Consequences:** [What does this mean going forward?]

-->
