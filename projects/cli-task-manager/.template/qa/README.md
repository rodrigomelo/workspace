# Quality Assurance

Plano de testes e critérios de aceitação.

## Test Plan

- [ ] Unit tests (lógica pura)
- [ ] Integration tests (API, DB)
- [ ] E2E tests (fluxos completos)
- [ ] Visual regression (pixel perfect)
- [ ] Accessibility audit (axe, Lighthouse)

## Acceptance Criteria

Cada feature deve ter:
- Cenário feliz
- Edge cases
- Mensagens de erro amigáveis
- Performance esperada (< 2s load, etc)

## Testing Environment

- URL de staging: ...
- Credenciais de teste: ...
- Dados de exemplo: ...

## Bug Reporting

Template:
```
Passos para reproduzir:
1. ...
2. ...

Resultado esperado:
Resultado atual:

Ambiente: (dev/staging/prod)
Device/OS:
Screenshot/Video:
Severidade: (critical/major/minor)
```

## QA Sign-off

Após passar em todos os testes above, marcar em `HANDOFFS.md` que o projeto está pronto para deploy.