# CLI Task Manager — Implementation

Stack: Node.js + TypeScript + Commander + Chalk + Vitest

## Setup

```bash
cd code
npm install
```

## Development

```bash
npm run dev        # watch mode with tsx
npm run build      # compile to dist/
npm start          # run built binary
npm test           # watch tests
npm run test:run   # run tests once
npm run lint       # eslint
```

## Architecture

```
src/
├── index.ts         (CLI entry, commander setup)
├── types.ts         (Task interface, enums)
├── lib/
│   ├── storage.ts   (JSON file ops, CRUD)
│   └── ui.ts        (ANSI colors, formatting)
└── commands/
    ├── add.ts
    ├── list.ts
    ├── complete.ts
    delete.ts
```

## Storage

- Location: `~/.config/clawlab/tasks.json`
- Auto-creates directory if missing
- JSON format (array of Task objects)

## Testing

- Vitest for unit tests
- Test storage functions in isolation
- Mock file system using temp dirs (TODO)

## Building for Distribution

```bash
npm run build
npm link   # globally install locally
```

Then run `task` from anywhere.

## Stack Choices

- **Commander**: industry standard, good help generation
- **Chalk**: simple ANSI colors
- **Vitest**: fast, ESM-native
- **TypeScript**: type safety
- **Conf?**: Not needed — storage path is fixed per spec