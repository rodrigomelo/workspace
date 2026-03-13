# Handoff: Design → Development (Web UI)

**Data:** 2025-03-12
**De:** Athena (Designer)
**Para:** Hefesto (Coder)
**Projeto:** cli-task-manager (Web UI)

## Contexto do Projeto

GUI web para o CLI Task Manager. Mantém mesma UX, cores, e compartilha storage JSON com a CLI.

## Entregas

- [x] Especificação completa (`web/SPEC.md`)
- [x] Layout, paleta de cores, tipografia
- [x] Componentes: header, filtros, cards, modais
- [x] Estados: empty, loading, error
- [x] Fluxo de usuário detalhado
- [x] Critérios de aceitação

## Decisões Tomadas

- **Stack:** Plain HTML/CSS/JS (sem framework) — simplicidade
- **Server:** Express + static files
- **Porta:** 3000
- **API:** RESTful (GET/POST/PATCH/DELETE)
- **Polling:** 5s auto-refresh
- **Cores:** Mesmo scheme do CLI (vermelho/amarelo/verde, dark theme)

## Alternativas Consideradas

- **React/Vue:** descartado por overhead desnecessário
- **WebSocket:** polling é suficiente para uso local
- **Electron/Tauri:** futuramente, mas web-first pra cross-platform

## Perguntas Abertas

- Devo usar um build step (bundle) ou vanilla JS puro? (Decisão: vanilla)
- Devo incluir service worker? (Não, fora de escopo)

## Blockers

Nenhum — spec está completa.

---

**Próximo passo:** Hefesto implementa server + frontend, Apollo valida QA web, Artemis revisa boas práticas de UX web.