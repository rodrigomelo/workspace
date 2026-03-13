# OpenClaw Multi-Agent System

## Overview

This is a collaborative AI agent system built on OpenClaw, featuring specialized agents that work together on software projects.

## Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Hermes** | Coordinator | Main assistant, coordinates other agents, handles communication |
| **Hefesto** | Coder | Builds and implements code based on specifications |
| **Athena** | Designer | Creates UX/UI specs, design standards |
| **Apollo** | QA | Tests, validates quality, regression testing |

## Workspace Structure

```
~/.openclaw/workspace/
├── knowledge/           # Shared knowledge base
│   ├── standards/      # Design & code standards
│   ├── decisions/     # ADRs and architectural decisions
│   ├── components/    # Reusable components
│   └── process.md     # Process documentation
├── projects/           # Active projects
│   └── {project}/
│       ├── design/    # Specs, wireframes
│       ├── code/      # Source code
│       ├── qa/        # Test results
│       └── docs/      # Documentation
├── memory/            # Agent memory (daily notes)
└── .gitignore
```

## Process

### Pipeline: Design → Code → QA

1. **Athena** creates specification in `design/SPEC.md`
2. **Athena** creates `HANDOFFS.md` with context and decisions
3. **Hefesto** implements code in `code/`
4. **Apollo** validates in `qa/`
5. **All** document learnings in `knowledge/`

### Handoff Requirements

Each handoff must include:
- Context (what + why)
- Decisions made
- Pending items
- Relevant links

## Language Standards

- **Official Language**: English
- All code, documentation, commits in English
- User-facing messages can be localized

## Communication

- **Discord** for real-time chat
- `requireMention: true` - agents only respond when mentioned
- Mention format: `@AgentName`

## First Project: CLI Task Manager

- **Status**: v0.1.0 released
- **Location**: `projects/cli-task-manager/`
- **Tech**: TypeScript, Commander, Chalk, Vitest

## GitHub Integration

- Repository: https://github.com/rodrigomelo/workspace
- PAT-based authentication
- Push workflow: local commits → GitHub

---

*Last updated: 2026-03-12*
