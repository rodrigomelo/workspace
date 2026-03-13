# Handoff: CLI Task Manager Web UI (Design → Code)

**From:** Athena (UX Designer)  
**To:** Hefesto (Coder)  
**Date:** 2026-03-12  
**Project:** cli-task-manager/web

---

## Deliverables

### ✅ Design Specification
- **File:** `projects/cli-task-manager/web/SPEC.md`
- Contains: UI layout, colors, components, functionality, tech stack

---

## Key Design Decisions

1. **Web UI (not TUI)** — accessible via browser
2. **Plain HTML/CSS/JS** — no framework, simpler to maintain
3. **Same storage** — reads/writes to `~/.config/clawlab/tasks.json`
4. **Color scheme** — matches CLI: 🔴 High (red), 🟡 Medium (yellow), 🟢 Low (green)
5. **Dark theme** — modern, easy on eyes

---

## Tech Stack

- Plain HTML/CSS/JS
- Simple static server (Node.js or Python)
- Port 3000
- Same JSON storage as CLI

---

## Questions for You

1. **Server:** Express? http-server? Python SimpleHTTPServer?
2. **File watching:** Poll for changes or just refresh button?
3. **CORS:** Any concerns reading local JSON file?

---

## Next Steps

1. Review SPEC.md
2. Confirm approach
3. Start coding
4. Test with CLI

---

## Reference

- Full spec: `projects/cli-task-manager/web/SPEC.md`
- CLI spec: `../design/SPEC.md`
