# Language Standards

## Official Language

**English** é a língua oficial do projeto para:

- **Code** — variable names, function names, comments, strings, logs
- **Documentation** — READMEs, SPECs, ADRs, CHANGELOG, API docs
- **Commits** — conventional commits em inglês
- **Issues/PRs** — discussões em inglês

## Exceptions

- Mensagens de erro destinadas ao usuário final podem estar em PT/EN dependendo do público (mas default EN)
- Nomes de domínio/marca em português (ex: `clawlab`) são permitidos

## Why

- Consistência global
- Ferramentas (linters, IDEs) baseadas em English
- Facilita colaboração internacional
- Commits/searchability

## Enforcement

- ESLint rule `comma-dangle` not related — use `eslint-plugin-english`
- PR template reminding: "Please write all text in English"
- Code reviews check for Portuguese words in code/comments

---

*Related: knowledge/standards/code-standards.md*