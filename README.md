# Workspace Compartilhado — OpenClaw Multi-Agent

Este é o workspace central onde todos os agentes (Hermes, Hefesto, Athena, Apollo) compartilham conhecimento e projetos.

## Estrutura

```
/
├── knowledge/           # Conhecimento compartilhado
│   ├── standards/      # Padrões de design e código
│   │   ├── design-standards.md
│   │   └── code-standards.md
│   ├── decisions/      # ADRs (Architecture Decision Records)
│   │   └── README.md   # Como escrever ADRs
│   ├── components/     # Biblioteca reusável
│   │   └── README.md
│   ├── best-practices.md
│   └── README.md
├── memory/             # Memória viva dos agentes (já existe)
├── projects/           # Projetos ativos
│   ├── .template/      # Template para novo projeto
│   │   ├── design/
│   │   ├── code/
│   │   ├── qa/
│   │   ├── docs/
│   │   ├── HANDOFFS.md
│   │   └── CHANGELOG.md
│   └── README.md       # Lista projetos + como usar template
├── AGENTS.md
├── IDENTITY.md
├── MEMORY.md
├── SOUL.md
├── TOOLS.md
└── USER.md
```

## Como usar

1. **consultar conhecimento:** leia `knowledge/` antes de decidir algo
2. **criar projeto:** copie `projects/.template/` para `projects/{nome}/`
3. **handoffs:** documente transições no `HANDOFFs.md` do projeto
4. **decisões:** crie ADRs em `knowledge/decisions/` (ou `projects/{projeto}/docs/`)
5. **aprendizado:** atualize `knowledge/best-practices.md` com lições

## Agentes

- **Hermes** — Coordenador, orquestração
- **Hefesto** — Código, arquitetura, infra
- **Athena** — Design, UX, research
- **Apollo** — QA, testes, revisão
- **Artemis** — Pesquisa, análise, investigação
- **Poseidon** — Sistemas, rede, infraestrutura
- **Dionysus** — Criativo, conteúdo, entretenimento
- **Hades** — Segurança, privacidade, compliance
- **Demeter** — Dados, analytics, growth

Todos usam este workspace. `requireMention: true` — mencionar para ativar.

## Git

Repositório: `https://github.com/rodrigomelo/workspace`

```bash
cd ~/.openclaw/workspace
git pull --rebase origin main   # sempre antes de começar
git add -A
git commit -m "<type>(<scope>): <description>"
git push origin main
```

**Nunca commitar tokens, senhas ou API keys.**

---

*Última atualização: 2026-03-12*