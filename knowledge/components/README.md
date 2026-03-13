# Reusable Components

Biblioteca de componentes e utilitários compartilhados.

## UI Components

Reusable visual components (buttons, inputs, cards, etc.) em formato que todos os projetos possam consumir:

- Design tokens já aplicados
- States (hover, focus, disabled) definidos
- Accessibility built-in (ARIA, keyboard nav)

## Utils

Funções utilitárias comuns:
- Validation (email, phone, CPF, etc.)
- Formatting (dates, currency, bytes)
- API helpers (retry, timeout, cache)

## Scripts

Automações CLI para:
- Setup de projetos
- Deploy
- Migrations
- Testing

## Como adicionar

1. Criar componente/utils em formato agnóstico (plain JS/TS, não framework-specific quando possível)
2. Documentar com exemplos
3. Testar
4. Referenciar no `components-index.md`

## Consumo

Nos projetos, importar daqui em vez de reimplementar.