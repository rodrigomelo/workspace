# CLI Task Manager — Design Specification

## Overview
A CLI task manager with thoughtful UX — prioritizing clarity, visual hierarchy, and delight.

---

## Commands

| Command | Description |
|---------|-------------|
| `task add <text> [-p priority]` | Add a new task |
| `task list [-s status] [-p priority]` | List tasks |
| `task complete <id>` | Mark task as done |
| `task delete <id>` | Remove a task |
| `task help` | Show help |

---

## Priority Levels

| Priority | Flag | Emoji | Color (ANSI) |
|----------|------|-------|---------------|
| High | `-p high` | 🔴 | Red |
| Medium | `-p medium` | 🟡 | Yellow |
| Low | `-p low` | 🟢 | Green |

Default priority: **medium**

---

## Output Formats

### List View
```
📋 Your Tasks (3 pending)

🔴 [1] Finish project spec
🟡 [2] Review PR #42
🟢 [3] Update documentation

Run "task complete <id>" to finish a task
```

### Empty State
```
📋 No tasks yet!

Run "task add <task>" to create your first task 🚀
```

### Success Feedback
```
✅ Task #1 completed!
```

### Error Feedback
```
❌ Error: Task not found

Available IDs: 1, 2, 3
```

---

## Color Palette (ANSI)

- **Reset:** `\033[0m`
- **Red (High):** `\033[31m`
- **Yellow (Medium):** `\033[33m`
- **Green (Low):** `\033[32m`
- **Cyan (Headers):** `\033[36m`
- **Bright (IDs):** `\033[1m`

---

## UX Principles

1. **Emoji-first** — Visual scanning is faster
2. **Actionable footer** — Always hint next steps
3. **Friendly errors** — Tell user what they CAN do
4. **Consistent spacing** — Aligned, readable output

---

## File Storage

- Location: `~/.tasks.json`
- Format: JSON array

```json
[
  {
    "id": 1,
    "text": "Finish project spec",
    "priority": "high",
    "completed": false,
    "createdAt": "2026-03-12T22:00:00Z"
  }
]
```

---

## Future Ideas (v2)

- [ ] Due dates
- [ ] Tags/categories
- [ ] Export to markdown
- [ ] Sync across devices
