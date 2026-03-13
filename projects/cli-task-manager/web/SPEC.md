# CLI Task Manager Web UI — Design Specification

## Overview
A web-based GUI for the CLI Task Manager. Users can manage tasks via browser while maintaining the same UX as the CLI.

**Access:** `http://localhost:3000` (local server)  
**Storage:** Reads/writes to `~/.config/clawlab/tasks.json`

---

## UI/UX Specification

### Color Palette

| Priority | Color | Hex |
|----------|-------|-----|
| High | Red | `#EF4444` |
| Medium | Yellow | `#F59E0B` |
| Low | Green | `#10B981` |
| Background | Dark | `#1F2937` |
| Surface | Gray | `#374151` |
| Text | White | `#F9FAFB` |
| Muted | Gray | `#9CA3AF` |

### Typography

- **Font:** System UI / Inter / -apple-system
- **Headings:** Bold, 24px (h1), 18px (h2)
- **Body:** Regular, 16px
- **Small:** 14px

### Layout

```
┌─────────────────────────────────────────────┐
│  🗂️  CLI Task Manager        [+ Add Task]  │
├─────────────────────────────────────────────┤
│  [All] [Pending] [Completed]   [High/Med/Low] │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ 🔴 [1] Finish project spec    [✓] 🗑️ │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ 🟡 [2] Review PR #42         [✓] 🗑️ │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ 🟢 [3] Update documentation  [✓] 🗑️ │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Components

#### Header
- App title with emoji 🗂️
- "Add Task" button (primary)

#### Filters
- Status tabs: All | Pending | Completed
- Priority filter dropdown

#### Task Card
- Priority indicator (colored dot + emoji)
- Task ID (small, muted)
- Task text
- Complete button (checkbox)
- Delete button (trash icon)
- Hover: subtle background change

#### Add Task Modal
- Input field for task text
- Priority selector (High/Medium/Low)
- Cancel / Add buttons

### States

| State | Visual |
|-------|--------|
| Empty | "📋 No tasks yet! Add your first task" |
| Loading | Spinner |
| Error | Red toast with message |

---

## Functionality

### Features
1. **List tasks** — show all, filter by status/priority
2. **Add task** — modal with text + priority
3. **Complete task** — toggle completion status
4. **Delete task** — remove with confirmation
5. **Real-time sync** — reads same JSON file as CLI

### User Flow
1. Open browser → see task list
2. Click "Add Task" → modal opens
3. Enter text, select priority → click Add
4. Task appears in list
5. Click checkbox to complete
6. Click trash to delete

### Data Handling
- **Read:** On load, fetch from `~/.config/clawlab/tasks.json`
- **Write:** After each action, write to same file
- **Refresh:** Auto-refresh or manual button

---

## Technical

- **Stack:** Plain HTML/CSS/JS (no framework for simplicity)
- **Server:** Simple Node.js static server or Python http.server
- **File Access:** Same JSON file as CLI
- **Port:** 3000

---

## Acceptance Criteria

- [ ] Web UI loads at localhost:3000
- [ ] Shows same tasks as CLI
- [ ] Add task works → appears in CLI too
- [ ] Complete task → toggles status
- [ ] Delete task → removes from list
- [ ] Filters work (status + priority)
- [ ] Colors match priority scheme
- [ ] Responsive (works on mobile)
