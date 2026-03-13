# Palmeiras Calendar Integration UX Specification

## Event Title Format

**Format:**
```
🏆 Palmeiras vs [OPONENT] - [COMPETIÇÃO]
```

Examples:
- 🏆 Palmeiras vs Corinthians - Brasileirão
- 🏆 Palmeiras vs Flamengo - Copa do Brasil

## Description Template

```markdown
⚽ PARTIDA DO PALMEIRAS

🏟️ Estádio: [STADIUM]
📍 Cidade: [CITY]
🕐Horário: [TIME] (horário de Brasília)

📺 Onde assistir:
• TV: [BROADCASTER]
• Streaming: [STREAM_PLATFORM]

🔄 Competição: [TOURNAMENT_NAME]
📊 Rodada: [ROUND]ªrodada
```

## Color Coding

| Event Type | Color | Hex |
|------------|-------|-----|
| Home Game | 🟢 Green | `#006400` |
| Away Game | 🟡 Yellow | `#FFD700` |
| Derby/Final | 🔴 Red | `#DC143C` |

## Reminder Timing
- Default: 2 hours before match
- Important (derbies): 1 day before + 2h before
