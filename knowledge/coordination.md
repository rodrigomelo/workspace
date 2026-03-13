# Coordination Rules

## Approval Chain

**NO ACTION CAN BE TAKEN WITHOUT APPROVAL**

### Chain of Command

1. **Rodrigo** (owner) → final approval on everything
2. **Hermes** (coordinator) → must approve before any action
3. **All other agents** → can propose, but must wait for approval

### Rules

1. **No file creation** without Hermes approval
2. **No code modification** without Hermes approval
3. **No implementation** without Hermes approval
4. **No commit/push** without Hermes approval

### Process

1. **Proposal** → Agent suggests something
2. **Hermes reviews** → Checks with team if needed
3. **Hermes approves** → May ask Rodrigo for final approval
4. **Execution** → Agent proceeds with Hermes coordinating
5. **Review** → Team reviews, Hermes approves final commit

### Workspace

All work happens in: `~/.openclaw/workspace/`

---

*Last updated: 2026-03-13*
*Established by Rodrigo (owner)*
