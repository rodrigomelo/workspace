# Project Documentation

## Context

We are building a CLI task manager for developers who spend most of their time in the terminal. The goal is to provide a delightful, visually clear interface for managing tasks without leaving the command line.

## Target Users

- Developers using terminal daily
- People who want quick task capture without GUI
- Fans of minimal, keyboard-driven tools

## Success Metrics

- < 100ms response for all commands
- Clear visual feedback (colors, emojis)
- Zero dependencies on GUI libraries
- Works on macOS, Linux, Windows (cross-platform)

## Dependencies

- Node.js 20+
- No external services required

## Tech Stack Rationale

- **TypeScript**: Catch errors early, better DX
- **Commander**: Battle-tested CLI framework
- **Chalk**: Lightweight colors
- **Vitest**: Fast unit tests

## Open Questions

- Should we support task tags? (v2)
- Should we have undo? (v2 maybe)
- Integrate with calendar? (future)

---