# CLI Task Manager — Web UI

Web interface for the CLI Task Manager. Shares the same JSON storage with the CLI.

## Features

- View tasks (filtered by status/priority)
- Add new tasks with priority
- Complete/delete tasks
- Auto-refresh every 5 seconds
- Dark theme, responsive design

## Prerequisites

- Node.js 18+
- npm

## Setup

```bash
cd web
npm install
```

## Running

```bash
npm start
```

Then open http://localhost:3000 in your browser.

## Development

Project structure:

```
web/
├── server.js           Express server + API routes
├── package.json
├── public/
│   ├── index.html
│   ├── styles.css
│   └── app.js          Frontend logic (vanilla JS)
└── README.md
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Add task (body: `{ text, priority }`) |
| PATCH | `/api/tasks/:id/complete` | Mark task as complete |
| DELETE | `/api/tasks/:id` | Delete task |

## Storage

Tasks are stored in `~/.config/clawlab/tasks.json`.
The CLI and Web UI share the same storage location.

## Tech Stack

- Backend: Express.js + CORS
- Frontend: Vanilla JS (no framework)
- Storage: Shared `clawlab-task-storage` library

---