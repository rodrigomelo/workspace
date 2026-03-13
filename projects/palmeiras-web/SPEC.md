# SPEC.md - Palmeiras Dashboard v2

## Paleta de Cores

| Elemento | Cor | Hex |
|----------|-----|-----|
| Primary (Verdão) | Verde Palmeiras | `#007824` |
| Secondary | Branco | `#FFFFFF` |
| Accent | Dourado | `#CEB888` |
| Background Dark | Cinza Escuro | `#1A1A1A` |
| Background Card | Cinza Médio | `#2D2D2D` |
| Text Primary | Branco | `#FFFFFF` |
| Text Secondary | Cinza Claro | `#B0B0B0` |
| Error | Vermelho | `#E53935` |
| Success | Verde Claro | `#4CAF50` |

**Contraste:** Garantir razão mínima 4.5:1 para texto sobre fundo escuro.

## Tipografia

- **Headings:** `Inter` ou `Poppins` (700 weight)
- **Body:** `Inter` (400/500 weight)
- **Tamanhos:**
  - H1: 32px
  - H2: 24px
  - H3: 18px
  - Body: 16px
  - Small: 14px

## Layout dos Cards

### Próximo Jogo (Destaque)
- Card grande e prominence
- Escudo do time grande (80x80px)
- Data e horário em destaque
- Estádio/local
- Borda sutil com cor `#007824`

### Resultados Recentes
- Formato de lista vertical
- Cada item: data, time casa (escudo 32px), placar, time visitante (escudo 32px)
- Fundo alternado para leitura fácil

### Classificação
- Tabela com colunas: Pos, Time, Pts, J, V, E, D, GP, GC, SG
- Linha do Palmeirense destacada com fundo `#007824` com 10% opacidade

## Estado de Carregamento

- **Spinner:** Círculo giratório verde (`#007824`) com 40px
- **Esqueleto:** Cards com efeito "skeleton"

## Estado de Erro

- Ícone de alerta em vermelho
- Mensagem: "Ops! Algo deu errado."
- Botão "Tentar novamente"

## Breakpoints Mobile

| Dispositivo | Largura |
|-------------|---------|
| Mobile | < 768px |
| Desktop | > 1024px |

**Ajustes mobile:**
- Cards em stack vertical
- Padding reduzido
- Tabelas com scroll horizontal
