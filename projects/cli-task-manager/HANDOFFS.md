# Handoff: Design → Development

**Data:** 2025-03-12
**De:** Athena (Designer)
**Para:** Hefesto (Coder)
**Projeto:** cli-task-manager

## Contexto do Projeto

CLI simples para gerenciar tarefas com UX cuidadosa. Foco em usabilidade visual mesmo em terminal (cores, emojis, feedback claro).

## Problema a Resolver

Pessoas que usam CLI precisam de uma forma rápida e agradável de gerenciar tasks sem sair do terminal.

## Entregas

- [x] Especificação completa (design/SPEC.md)
- [x] Comandos definidos (add, list, complete, delete, help)
- [x] Paleta de cores ANSI
- [x] Formatos de output (lista, vazio, sucesso, erro)
- [x] Prioridades (high/medium/low) com emojis
- [x] Storage location (`~/.config/clawlab/tasks.json`)

## Decisões Tomadas

- **Emoji-first** scanning (melhora reconhecimento rápido)
- **Storage em `~/.config/clawlab/`** (cross-platform, não lixa home)
- **JSON** (simples, legível, editável)
- **Commander** como parser CLI (padrão industria)
- **TypeScript** (type safety)

## Alternativas Consideradas

- **Yargs:** escolhemos commander por ser mais popular e docs melhores
- **~/.tasks.json:** mudado pra ~/.config/clawlab/ por padrão XDG
- **SQLite:** JSON é suficiente pra essa complexidade

## Perguntas Abertas

- Framework de testes: Jest vs Vitest? (sugestão: Vitest)
- Formato de data: ISO8601 vs timestamp? (sugestão: ISO)

## Blockers

Nenhum — spec está completa e pronta pra implementação.

---

**Próximo passo:** Hefesto implementa código, envia PR, Athena valida UX, Apollo testa.