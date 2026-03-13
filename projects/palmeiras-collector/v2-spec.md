# Palmeiras Tracker v2 - Technical Specification

## Project Overview

Enhanced Palmeiras tracking with next 5 games, Libertadores standings, match stats, news from ge.globo, and daily digest notifications.

## Features to Implement

### 1. Next 5 Games
- Show next 5 upcoming matches (not just the next one)
- Include: date, time, competition, opponent, venue, home/away
- Display matchweek/round info when available

### 2. Libertadores Standings
- Current CONMEBOL Libertadores group stage standings
- Points, games played, wins, draws, losses, goals for/against
- Position indicator (qualified, eliminated, repechagem)

### 3. Match Stats (Possession, Shots)
- Detailed match statistics for completed games
- Key stats: possession %, shots, shots on target, corners, fouls
- Comparison view: Palmeiras vs opponent

### 4. News from ge.globo
- Scrape latest Palmeiras news from ge.globo
- Headline, summary, link, publication time
- Configurable number of news items (default: 5)

### 5. Daily Digest Notifications
- Scheduled summary sent to Discord
- Includes: next 5 games, Libertadores standing, latest news
- Configurable time (default: 9:00 AM)

## Technical Approach

### Data Sources

| Feature | Source | Free Tier |
|---------|--------|-----------|
| Next 5 games | football-data.org | ✅ (up to 10 calls/day on free) |
| Libertadores standings | football-data.org | ✅ (same API) |
| Match stats | football-data.org | ✅ (same API) |
| News | ge.globo scraping | ✅ (free, no API key) |
| Notifications | Discord Webhooks | ✅ (free) |

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Palmeiras Tracker v2             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐    ┌──────────────┐              │
│  │   Scheduler │    │   Discord    │              │
│  │   (cron)    │───▶│   Webhook    │              │
│  └──────────────┘    └──────────────┘              │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────────────────┐              │
│  │         Data Collector           │              │
│  │  ┌─────────┐ ┌─────────┐ ┌────┐ │              │
│  │  │Football │ │ ge.globo│ │Cache│ │              │
│  │  │  API    │ │ Scraper │ │.json│ │              │
│  │  └─────────┘ └─────────┘ └────┘ │              │
│  └──────────────────────────────────┘              │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────────────────┐              │
│  │        Formatter                  │              │
│  │   (Discord embed builder)        │              │
│  └──────────────────────────────────┘              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Key Technical Decisions

1. **Caching**: Cache API responses for 1 hour to minimize API calls
2. **Rate Limiting**: Implement request delays for ge.globo scraping
3. **Error Handling**: Graceful degradation if any data source fails
4. **Modular Design**: Separate collectors for each data source
5. **Environment Config**: All settings via environment variables

### File Structure

```
palmeiras-collector/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration (env vars)
│   ├── main.py                # Entry point
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── matches.py          # Next 5 games
│   │   ├── libertadores.py    # Standings
│   │   ├── stats.py            # Match stats
│   │   └── news.py             # ge.globo scraper
│   ├── formatter/
│   │   ├── __init__.py
│   │   └── discord.py          # Embed builder
│   └── utils/
│       ├── __init__.py
│       ├── cache.py            # JSON file cache
│       └── http.py             # HTTP client wrapper
├── tests/
│   ├── test_collectors.py
│   └── test_formatter.py
├── .env
├── requirements.txt
└── SPEC.md
```

### Dependencies

```txt
requests>=2.31.0
python-dotenv>=1.0.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

## Implementation Details

### Football Data API Endpoints

- **Fixtures**: `GET /v4/teams/{team_id}/matches` → next 5 matches
- **Standings**: `GET /v4/competitions/{comp_id}/standings` → Libertadores
- **Match Stats**: `GET /v4/matches/{match_id}` → detailed stats

Palmeiras team ID: 153

### ge.globo Scraping

- URL: `https://ge.globo.com/futebol/times/palmeiras/`
- Use BeautifulSoup to parse HTML
- Extract: title, summary, link, timestamp

### Discord Embed Format

```python
{
    "title": "🏆 Palmeiras Tracker - Daily Digest",
    "color": 0x006400,  # Dark green
    "fields": [
        {"name": "📅 Próximos Jogos", "value": "...", "inline": False},
        {"name": "📊 Libertadores", "value": "...", "inline": False},
        {"name": "📰 Últimas Notícias", "value": "...", "inline": False}
    ]
}
```

## Timeline Estimate

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Project setup (venv, deps) | 30 min |
| 2 | Matches collector (next 5) | 1 hour |
| 3 | Libertadores standings | 1 hour |
| 4 | Match stats collector | 1 hour |
| 5 | ge.globo news scraper | 2 hours |
| 6 | Discord formatter | 1 hour |
| 7 | Daily digest cron job | 30 min |
| 8 | Testing & polish | 2 hours |
| **Total** | | **~9 hours** |

## Configuration Variables

```bash
# Football Data API (free)
export FOOTBALL_API_KEY="your-key"

# Discord
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# Settings
export NOTIFICATION_TIME="09:00"
export NEWS_COUNT=5
export CACHE_TTL=3600
```

## Backward Compatibility

- Keep `python -m src.main` working for immediate match check
- Add `--digest` flag for daily digest mode
- Support both scheduled (cron) and manual runs
