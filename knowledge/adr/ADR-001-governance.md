# Governance — ADR-001

## Context
Need clear authority and workflow for the Olympian agent team.

## Decision
Adopt **Hermes-led approval hierarchy** with Rodrigo as final approver.

### Hierarchy
```
Rodrigo (Owner)
    ↑ approves everything
Hermes (Coordinator)
    ↑ approves before any execution
    ├→ Hefesto (Coder)
    ├→ Athena (Designer)
    ├→ Apollo (QA)
    └→ Artemis (Research)
```

### Rules
1. No agent may create/modify/delete files, code, or commits without **Hermes' explicit approval**.
2. Rodrigo's approval flows through Hermes (Hermes decides when to escalate).
3. All work happens in shared workspace: `~/.openclaw/workspace/`.
4. Each agent has defined role memory in `memory/{agent}.md`.
5. Apollo QA required before any commit (even with Hermes approval).
6. Specs from Athena are binding; deviations require Hermes approval.

### Process
```
Idea → Proposal to Hermes → Hermes approves → Agent executes → QA (Apollo) → Hermes authorizes commit
```

### Consequences
- Violation: immediate rollback + review
- Ambiguity: ask Hermes

---

*Status: accepted 2025-03-12*