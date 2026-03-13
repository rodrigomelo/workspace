# Palmeiras Data Pipeline Architecture

## Overview

This document outlines the data architecture for the Palmeiras Data Collector (VerdaoTracker). The pipeline collects data from multiple sources, stores it efficiently, and delivers it via Discord notifications and dashboard.

## Data Sources

### 1. football-data.org (API)

| Data Type | Endpoint | Update Frequency | Free Tier |
|-----------|----------|------------------|-----------|
| **Matches** | `/v4/teams/153/matches` | Every 6 hours | ✅ 10 calls/day |
| **Standings** | `/v4/competitions/{id}/standings` | Daily | ✅ |
| **Match Stats** | `/v4/matches/{id}` | On match day | ✅ |
| **Competition Info** | `/v4/competitions/` | Weekly | ✅ |

**Palmeiras Team ID:** `153`

**Data to Collect:**
- Match schedule (date, time, venue, opponent)
- Competition name (Brasileirão, Libertadores, Copa do Brasil, etc.)
- Match status (scheduled, live, finished)
- Score (for finished matches)
- Standings position, points, wins, draws, losses, goals for/against
- Match statistics (possession, shots, corners, fouls)

### 2. ge.globo (Web Scraping)

| Data Type | URL | Update Frequency |
|-----------|-----|------------------|
| **News** | `https://ge.globo.com/futebol/times/palmeiras/` | Every 4 hours |
| **Match Reports** | `https://ge.globo.com/futebol/times/palmeiras/partida/` | On match day |

**Data to Collect:**
- Article title
- Summary/description
- Article URL
- Publication timestamp
- Image thumbnail (if available)
- Category (news, match, interview, etc.)

### 3. Stadium/Venue Info

| Data Type | Source | Update Frequency |
|-----------|--------|------------------|
| **Venue Details** | Static / Wikipedia | Rarely |
| **Match Venue** | football-data.org | Per match |

**Data to Collect:**
- Stadium name (Allianz Parque)
- Address
- Capacity
- Location (city, state)

### 4. TV Broadcast Info

| Data Type | Source | Update Frequency |
|-----------|--------|------------------|
| **Broadcast** | football-data.org + ge.globo | Per match |

**Data to Collect:**
- TV Channel (Globo, Premiere, ESPN, etc.)
- Broadcast time
- Country/region

### 5. Social Media (Future)

| Platform | Data | Source |
|----------|------|--------|
| Twitter/X | Mentions, trends | API (paid) |
| Instagram | Posts | Scraping (limited) |
| YouTube | Highlights | YouTube Data API |

---

## Database Schema (SQLite)

### Schema Overview

```
palmeiras_collector.db
├── matches           # Match schedule and results
├── standings         # Competition standings snapshot
├── match_stats       # Detailed match statistics
├── news              # Scraped news articles
├── venues            # Stadium information
├── broadcast         # TV broadcast info
├── sync_log          # Pipeline execution history
└── cache             # Raw API responses (optional)
```

### Table: matches

```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    external_id TEXT UNIQUE,          -- football-data.org match ID
    date_time TEXT,                   -- ISO 8601
    competition TEXT,                 -- Brasileirão, Libertadores, etc.
    competition_id INTEGER,
    matchday INTEGER,
    season TEXT,                      -- 2024, 2025
    status TEXT,                      -- SCHEDULED, FINISHED, LIVE
    
    -- Opponent
    opponent_name TEXT,
    opponent_id INTEGER,
    is_home BOOLEAN,                  -- True = Palmeiras home
    
    -- Venue
    venue_name TEXT,
    venue_id INTEGER,
    
    -- Score (if finished)
    home_score INTEGER,
    away_score INTEGER,
    half_time_home INTEGER,
    half_time_away INTEGER,
    
    -- Metadata
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_matches_date ON matches(date_time);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_competition ON matches(competition);
```

### Table: standings

```sql
CREATE TABLE standings (
    id INTEGER PRIMARY KEY,
    competition_id INTEGER,
    competition_name TEXT,
    season TEXT,
    
    -- Position
    position INTEGER,
    team_id INTEGER,
    team_name TEXT,
    
    -- Stats
    played INTEGER,
    won INTEGER,
    drawn INTEGER,
    lost INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    points INTEGER,
    
    -- Metadata
    snapshot_date TEXT,               -- When this was captured
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(competition_id, season, team_id, snapshot_date)
);

CREATE INDEX idx_standings_comp_season ON standings(competition_id, season);
```

### Table: match_stats

```sql
CREATE TABLE match_stats (
    id INTEGER PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    external_id TEXT,
    
    -- possession
    home_possession REAL,
    away_possession REAL,
    
    -- shots
    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,
    
    -- corners
    home_corners INTEGER,
    away_corners INTEGER,
    
    -- fouls
    home_fouls INTEGER,
    away_fouls INTEGER,
    
    -- cards
    home_yellow_cards INTEGER,
    away_yellow_cards INTEGER,
    home_red_cards INTEGER,
    away_red_cards INTEGER,
    
    -- extra (JSON for flexibility)
    extra_stats TEXT,                 -- JSON blob
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_match_stats_match ON match_stats(match_id);
```

### Table: news

```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    external_id TEXT,                  -- URL or internal ID
    title TEXT NOT NULL,
    summary TEXT,
    url TEXT UNIQUE,
    image_url TEXT,
    category TEXT,                    -- news, match, interview
    published_at TEXT,
    source TEXT DEFAULT 'ge.globo',
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_published ON news(published_at DESC);
CREATE INDEX idx_news_category ON news(category);
```

### Table: venues

```sql
CREATE TABLE venues (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'Brazil',
    capacity INTEGER,
    
    -- Geo coordinates (optional)
    latitude REAL,
    longitude REAL,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Table: broadcast

```sql
CREATE TABLE broadcast (
    id INTEGER PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    channel TEXT,                     -- Globo, Premiere, ESPN, etc.
    region TEXT,                      -- Nacional, SP, RJ
    broadcast_time TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_broadcast_match ON broadcast(match_id);
```

### Table: sync_log

```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY,
    source TEXT,                      -- football_data, ge_globo
    sync_type TEXT,                   -- matches, standings, news
    status TEXT,                      -- SUCCESS, FAILED, PARTIAL
    records_updated INTEGER,
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    duration_ms INTEGER
);

CREATE INDEX idx_sync_log_source ON sync_log(source);
CREATE INDEX idx_sync_log_started ON sync_log(started_at DESC);
```

---

## Data Storage (JSON Files)

For scraped data and raw API responses, use JSON files:

```
data/
├── cache/
│   ├── matches_2024.json
│   ├── standings_2024.json
│   └── news_latest.json
├── raw/
│   ├── football_api_response_2024-01-15.json
│   └── ge_globo_scrape_2024-01-15.json
└── exports/
    └── daily_digest_2024-01-15.json
```

### JSON Schema: news_latest.json

```json
{
  "version": "1.0",
  "fetched_at": "2024-01-15T10:30:00Z",
  "count": 10,
  "articles": [
    {
      "id": "news_12345",
      "title": "Palmeiras announces new signing",
      "summary": "Club signs midfielder from...",
      "url": "https://ge.globo.com/...",
      "image_url": "https://s.glbimg.com/...",
      "published_at": "2024-01-15T09:00:00Z",
      "category": "news"
    }
  ]
}
```

---

## Update Schedule (Cron Jobs)

### Recommended Schedule

| Job | Frequency | Time | Purpose |
|-----|-----------|------|---------|
| **Match Schedule** | Every 6 hours | 06:00, 12:00, 18:00, 00:00 | Next matches |
| **Live Scores** | Every 15 min* | During match days | Live updates |
| **Standings** | Daily | 08:00 | Libertadores/Brasileirão |
| **News** | Every 4 hours | 06:00, 10:00, 14:00, 18:00, 22:00 | Latest news |
| **Broadcast** | On match day | 10:00 | TV info |
| **Daily Digest** | Daily | 09:00 | Discord notification |

*Only during live matches

### Crontab Configuration

```bash
# Palmeiras Data Pipeline Cron Jobs

# Match schedule (every 6 hours)
0 6,12,18,0 * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.collectors.matches >> logs/matches.log 2>&1

# Standings (daily at 8am)
0 8 * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.collectors.standings >> logs/standings.log 2>&1

# News (every 4 hours)
0 6,10,14,18,22 * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.collectors.news >> logs/news.log 2>&1

# Daily digest (daily at 9am)
0 9 * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.main --digest >> logs/digest.log 2>&1

# Live match updates (every 15 min during match days - advanced)
# Managed by separate script with match-day detection
```

### Update Strategy

1. **Incremental Updates**: Only fetch data that changed
2. **Caching**: Cache API responses (TTL: 1 hour for matches, 6 hours for standings)
3. **Rate Limiting**: Respect API limits (football-data.org: 10 calls/minute free tier)
4. **Backfill**: On first run, load last 30 days of matches, last 10 standings snapshots
5. **Deduplication**: Use external_id to avoid duplicates

---

## Dashboard Integration

### Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Palmeiras Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Next Match │  │  Standings  │  │   News      │         │
│  │   Widget    │  │   Widget    │  │   Widget    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Match Stats (last 5)               │        │
│  └─────────────────────────────────────────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   SQLite    │
              │  Database   │
              └─────────────┘
```

### Dashboard Data Queries

```python
# Next 5 matches
SELECT * FROM matches 
WHERE date_time > datetime('now') 
ORDER BY date_time ASC 
LIMIT 5;

# Current standings (Libertadores)
SELECT * FROM standings 
WHERE competition_name = 'Copa Libertadores' 
AND snapshot_date = (SELECT MAX(snapshot_date) FROM standings)
ORDER BY position;

# Recent news (last 10)
SELECT * FROM news 
ORDER BY published_at DESC 
LIMIT 10;

# Recent match stats
SELECT ms.*, m.date_time, m.opponent_name, m.home_score, m.away_score
FROM match_stats ms
JOIN matches m ON ms.match_id = m.id
WHERE m.status = 'FINISHED'
ORDER BY m.date_time DESC
LIMIT 5;
```

### Dashboard Implementation Options

1. **Simple (dashboard.py)**: Already exists, uses Flask + SQLite
2. **Streamlit**: Fast prototyping for data apps
3. ** Grafana**: Full-featured dashboards with SQLite plugin
4. **Custom**: React/Next.js frontend with API backend

### API Endpoints (for Dashboard)

```python
# /api/matches/next - Next matches
# /api/matches/last - Last N matches with scores
# /api/standings - Current standings
# /api/news - Latest news
# /api/stats/{match_id} - Match statistics
# /api/dashboard - Full dashboard data (single call)
```

---

## Data Flow Diagram

```
                           ┌─────────────────┐
                           │   Cron Jobs     │
                           │  (scheduler)    │
                           └────────┬────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
   │ football-   │          │   ge.globo  │          │   Static    │
   │ data.org    │          │   (scraper) │          │   (venues)  │
   └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
          │                        │                        │
          ▼                        ▼                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                     Data Collectors                          │
   │   (matches.py, standings.py, news.py, broadcast.py)         │
   └─────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                    Data Transformers                         │
   │   (normalize, validate, enrich)                             │
   └─────────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
            ┌──────────────┐            ┌──────────────┐
            │   SQLite     │            │   JSON       │
            │  Database    │            │   Files      │
            └──────────────┘            └──────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                      Outputs                                 │
   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
   │   │  Discord    │  │  Dashboard  │  │    API      │       │
   │   │  Webhooks  │  │   (Flask)   │  │  (REST)     │       │
   │   └─────────────┘  └─────────────┘  └─────────────┘       │
   └─────────────────────────────────────────────────────────────┘
```

---

## Error Handling & Monitoring

### Error Types

| Error | Handling | Notification |
|-------|----------|--------------|
| API rate limit | Retry with exponential backoff | Log only |
| API timeout | Retry 3x, then cache fallback | Log + alert |
| Scraping parse fail | Log error, skip item | Log only |
| Database error | Rollback transaction | Alert |
| Invalid data | Validate, reject bad records | Log + alert |

### Monitoring

```sql
-- Check sync status
SELECT source, sync_type, status, records_updated, error_message 
FROM sync_log 
ORDER BY started_at DESC 
LIMIT 10;

-- Failed syncs in last 24 hours
SELECT COUNT(*) FROM sync_log 
WHERE status = 'FAILED' 
AND started_at > datetime('now', '-24 hours');
```

---

## Migration Path (Future)

### Phase 1: Current (SQLite + JSON)
- Simple, portable, no external dependencies
- Good for personal use

### Phase 2: PostGIS + TimescaleDB
- Time-series optimization for stats
- Geo queries for venue analysis

### Phase 3: Data Warehouse
- BigQuery/Snowflake for analytics
- Historical data retention
- Advanced queries

---

## Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Database** | SQLite | Match data, standings, news, logs |
| **Cache** | JSON files | Raw API responses, exports |
| **Scheduler** | Cron | Automated updates |
| **Collectors** | Python scripts | API + scraping |
| **Output** | Discord + Dashboard | Notifications + visualization |

This architecture provides a solid foundation that can start simple (SQLite + JSON) and scale to more complex systems as needed.