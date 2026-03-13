# Code Standards

Padrões de código que todos os agentes seguem.

## General
- English only em código, commits, mensagens de commit
- Sem cryptic names — seja explícito
- Funções pequenas, responsibility única
- DRY, mas não over-engineer

## Formatação
- Prettier configurado no projeto
- 2 espaços indentação
- Máximo 100 colunas
- ponto-e-vírgula opcional (mas consistente)

## Testing
- Testes unitários para lógica crítica
- Testes de integração para APIs
- Cobertura mínima: 80%

## Security
- Nunca hardcode secrets — usar env vars
- Validação de entrada em todos os endpoints
- Log de ações importantes, sem vazar dados sensíveis

## Commits
- Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`
- Mensagem clara, Imperativo ("Add", "Fix", "Update")
- Escopo opcional: `feat(auth):`

## Branching
- `main` — production
- `develop` — staging
- `feature/nome` — novas features

## Pull Requests
- Descrição clara do "porquê"
- Screenshots para mudanças visuais
- Referenciar issue (se houver)
- Self-review antes de pedir review