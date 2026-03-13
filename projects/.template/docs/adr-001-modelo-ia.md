# ADR 001: Escolha do Modelo de IA para Agentes

Status: Accepted

Date: 2025-03-12

## Context

Precisamos padronizar o modelo de IA usado por todos os agentes (Hermes, Hefesto, Athena, Apollo) para garantir consistência, reduzir custos e simplificar operações.

Alternativas consideradas:
- Usar modelos diferentes por especialidade
- Cada agente escolher seu próprio
- Um modelo shared para todos

## Decision

Adotamos **MiniMax-M2.5** como modelo padrão para todos os agentes.

Motivos:
- Qualidade técnica sólida para todas as tarefas
- Suporte a multi-agente bem
- Custo razoável
- Disponível via OpenRouter

## Consequences

**Prós:**
- Consistência nas respostas
- Custo previsível
- Fácil config/manter

**Contras:**
- Nem todo modelo é ideal para tudo (ex: código vs design)
- Dependência de um único fornecedor

**Mitigação:**
- Se especialidades divergirem muito, podemos ter modelos diferentes no futuro — mas isso será decidido via ADR.
- Manter avaliação contínua de performance.

---

*Referência: discussão em #general 2025-03-12*