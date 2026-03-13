# Code Implementation

Estrutura e padrões de código do projeto.

## Stack

- Linguagem:
- Framework:
- Banco de dados:
- Outros:

## Estrutura de pastas

```
src/
├── components/    (reusable UI)
├── pages/         (rotas/páginas)
├── services/      (API clients, business logic)
├── utils/         (helpers, formatadores)
├── styles/        (tokens, global CSS)
└── tests/         (unit, integration)
```

## Environment

- ` .env.example` — listar variáveis necessárias
- Nunca commitar `.env`

## Scripts

- `npm run dev` — start local
- `npm run build` — produção
- `npm test` — testes
- `npm run lint` — code quality

## Dependencies

Listar principais pacotes e por quê.

## API Integration

- Base URL: ...
- Auth: ...
- Error handling padrão

## Testing

- Framework: Jest/Vitest/etc
- Coverage target: 80%
- Rodar antes de commit

## Deploy

- Branch: `main` → produção
- CI/CD: [descrever]
- rolled back? Como? (git revert, etc)