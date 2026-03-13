# Best Practices

Lições aprendidas e recomendações do dia a dia.

## Comunicação entre Agentes

- **Contexto primeiro**: Sempre inclua o "porquê" ao passar trabalho
- **Handoffs estruturados**: Use `HANDOFFs.md` no projeto
- **Ask specificity**: Perguntas específicas → respostas mais rápidas

## Design-to-Code

- Especificar estados (loading, error, empty)
- Fornecer JSON schema se houver APIs
- Discutir edge cases antes de codificar

## Code Quality

- Não merge sem testes passando
- Revisar PRs com foco (não seja perfecionista)
- Refatorar gradualmente, não tudo de uma vez

## Memory

- Usar `memory/` para contexto vivo
- Documentar lições aprendidas em ADRs
- Manter CHANGELOG atualizado

## When Stuck

1. Search knowledge base primeiro
2. Ask specific question to another agent
3. Document what you tried before escalating

---
*Update this file as we learn.*