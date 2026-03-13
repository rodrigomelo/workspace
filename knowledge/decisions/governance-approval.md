# Governance & Approval Process

## Authority Hierarchy

**Hermes (Coordinator)** is the ultimate approver for all work.

### Rules

1. **No work without Hermes' approval**
   - No file creation
   - No code modifications
   - No implementations
   - No commits

2. **Rodrigo's approval flows through Hermes**
   - Hermes is the intermediary
   - All decisions need Hermes' green light
   - Rodrigo approves Hermes' approvals

3. **Official Process**
   ```
   Idea → Proposal → Hermes Approval (with/without Rodrigo) → Execution → Commit
   ```

4. **Workspace**
   - All work happens in `~/.openclaw/workspace/`
   - No individual agent workspaces

### Agents Responsibilities

- **Hermes**: Coordinator, gatekeeper, orchestrator
- **Hefesto**: Code implementation (needs Hermes approval)
- **Athena**: Design specs (needs Hermes approval)
- **Apollo**: QA validation (runs after Hermes approves)
- **Artemis**: Research (provides input, but implementation still needs Hermes approval)

### Approval Channels

- Discord mentions to Hermes
- Explicit "Approved" or "Yes" from Hermes
- No approval = no action

---

*Established 2025-03-12 by RodrigoMelo*