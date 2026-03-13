# Palmeiras Calendar Integration Plan

## Overview

This document outlines the Google Calendar integration for Palmeiras matches. The system will automatically create, update, and delete calendar events based on match data from football-data.org, using the gog CLI for Google Calendar operations.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Calendar Integration Architecture                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────┐         ┌─────────────────┐                       │
│   │ football-data.org│         │  gog CLI        │                       │
│   │     API          │         │  (Calendar)     │                       │
│   └────────┬────────┘         └────────┬────────┘                       │
│            │                           │                                  │
│            ▼                           ▼                                  │
│   ┌─────────────────────────────────────────────────────┐                │
│   │              calendar_sync.py                       │                │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │                │
│   │  │ Fetcher  │→ │ Transformer│→ │ Sync     │         │                │
│   │  │ (API)    │  │           │  │ Engine   │         │                │
│   │  └──────────┘  └──────────┘  └────┬─────┘         │                │
│   └────────────────────────────────────┼────────────────┘                │
│                                          │                               │
│                     ┌─────────────────────┼─────────────────────┐        │
│                     │                     │                     │        │
│                     ▼                     ▼                     ▼        │
│            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│            │ Create Events│      │Update Events │      │Delete Events │ │
│            │  (new match) │      │ (score update)│     │ (old match)  │ │
│            └──────────────┘      └──────────────┘      └──────────────┘ │
│                     │                     │                     │        │
│                     └─────────────────────┼─────────────────────┘        │
│                                           ▼                              │
│                              ┌──────────────────────┐                    │
│                              │  Google Calendar      │                    │
│                              │  (Palmeiras Calendar) │                    │
│                              └──────────────────────┘                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data to Sync

### 1. Upcoming Matches (Create Events)

| Field | Source | Calendar Field |
|-------|--------|----------------|
| Match Date/Time | football-data.org | `startTime` |
| Competition | football-data.org | `summary` (e.g., "Brasileirão - Palmeiras vs Corinthians") |
| Opponent | football-data.org | `description` |
| Venue | football-data.org | `location` |
| Match Day/Round | football-data.org | `description` |
| TV Broadcast | football-data.org | `description` |

### 2. Live/Finished Matches (Update Events)

| Field | Source | Action |
|-------|--------|--------|
| Score | football-data.org | Update event title: "Palmeiras 2 x 1 Corinthians - Brasileirão" |
| Status | football-data.org | Add "🔴 LIVE" or "✅ FINAL" to description |
| Match Stats | football-data.org | Add to description (goals, cards) |

### 3. Past Results (Keep for Reference)

- Keep events for **7 days** after match
- Move to "Past Matches" calendar or delete
- Option to archive in separate calendar

---

## Calendar Structure

### Option A: Single Calendar (Recommended)

**Single Calendar:** "Palmeiras - Jogos"
- All matches (upcoming + recent)
- Simple to manage
- One sync job

| Event Pattern | Example |
|--------------|---------|
| Upcoming | "Palmeiras x Corinthians - Brasileirão" |
| Live | "🔴 Palmeira 2 x 1 Corinthians - Brasileirão" |
| Finished | "✅ Palmeiras 2 x 1 Corinthians - Brasileirão" |

### Option B: Multiple Calendars

| Calendar | Purpose | Retention |
|----------|---------|-----------|
| "Palmeiras - Próximos" | Upcoming matches | 30 days forward |
| "Palmeiras - Ao Vivo" | Live matches | Until final |
| "Palmeiras - Resultados" | Past results | 7 days |

### Option C: Hybrid (With Tags/Labels)

- Single calendar + color coding by competition:
  - 🟢 Green: Brasileirão
  - 🟡 Yellow: Libertadores
  - 🔵 Blue: Copa do Brasil
  - ⚪ White: Friendlies

### Recommendation: Option A (Single Calendar)

Simpler, cleaner, easier to sync. Use event title to distinguish status.

---

## Naming Convention

### Event Title Format

```
# Upcoming (more than 24h before)
Palmeiras x [Opponent] - [Competition]

# Day of match
🟡 Palmeiras x [Opponent] - [Competition]

# Live
🔴 Palmeiras [Score]-[Score] [Opponent] - [Competition]

# Finished
✅ Palmeiras [Score]-[Score] [Opponent] - [Competition]
```

### Event Description Template

```
🆚 Adversário: [Opponent]
🏆 Competição: [Competition]
📅 Rodada: [Matchday]
📍 Estádio: [Venue Name]
📺 Transmissão: [TV Channel]

[Status: AGENDADO / AO VIVO / ENCERRADO]
```

### Location Format

```
Allianz Parque, São Paulo
Estádio Monumental, Buenos Aires
```

---

## File Structure

```
palmeiras-collector/
├── src/
│   ├── collectors/
│   │   ├── matches.py          # Fetch matches from API
│   │   └── broadcast.py        # Fetch TV info
│   ├── sync/
│   │   ├── calendar_sync.py   # Main sync logic
│   │   ├── gog_client.py       # gog CLI wrapper
│   │   ├── event_mapper.py    # Transform match → event
│   │   └── deduplicator.py    # Prevent duplicate events
│   └── utils/
│       ├── logger.py
│       └── config.py
├── config/
│   └── calendar.yaml          # Calendar config
├── logs/
│   └── calendar_sync.log
├── data/
│   └── calendar_events.json   # Local event cache
└── scripts/
    └── sync_calendar.sh       # Cron wrapper
```

### Key Files

**config/calendar.yaml**
```yaml
calendar:
  name: "Palmeiras - Jogos"
  timezone: "America/Sao_Paulo"
  
sync:
  # How far ahead to create events (days)
  look_ahead_days: 30
  
  # How far back to keep results (days)
  keep_results_days: 7
  
  # Update frequency for live scores (minutes)
  live_update_interval: 15
  
  # Full sync interval (hours)
  full_sync_interval: 6

competitions:
  # Color coding by competition
  Brasileirão: "#00C853"       # Green
  "Copa Libertadores": "#FFD600" # Yellow
  "Copa do Brasil": "#2962FF"  # Blue
  Friendlies: "#9E9E9E"        # Gray

fields:
  # Field mappings
  venue_map:
    "Allianz Parque": "Av. Francisco Matarazzo, 1705 - Água Branca, São Paulo"
    "Arena Corinthians": "Av. Concópio, 891 - Parque Industrial, São Paulo"
```

**src/sync/calendar_sync.py** (Core Logic)
```python
class CalendarSync:
    def __init__(self, config):
        self.gog = GogClient()
        self.fetcher = MatchFetcher()
        self.mapper = EventMapper(config)
        self.dedup = Deduplicator()
    
    def sync(self):
        """Main sync operation"""
        matches = self.fetcher.get_upcoming_matches()
        
        for match in matches:
            event = self.mapper.match_to_event(match)
            
            existing = self.dedup.find_existing(event)
            
            if existing:
                if self.needs_update(existing, event):
                    self.gog.update_event(existing.id, event)
            else:
                self.gog.create_event(event)
        
        # Cleanup old events
        self.cleanup_old_events()
```

---

## Automation (Cron Jobs)

### Cron Schedule

| Job | Frequency | Time | Purpose |
|-----|-----------|------|---------|
| **Full Sync** | Every 6 hours | 06:00, 12:00, 18:00, 00:00 | Create new events |
| **Live Updates** | Every 15 min | Match days only | Update scores |
| **Cleanup** | Daily | 01:00 | Delete old events |

### Crontab Configuration

```bash
# Palmeiras Calendar Sync

# Full sync - every 6 hours
0 6,12,18,0 * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.sync.calendar_sync >> logs/calendar_sync.log 2>&1

# Live match updates - every 15 minutes (only on match days)
*/15 * * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.sync.calendar_sync --live >> logs/calendar_live.log 2>&1

# Cleanup old events - daily at 1am
0 1 * * * cd ~/projects/palmeiras-collector && ./venv/bin/python -m src.sync.calendar_sync --cleanup >> logs/calendar_cleanup.log 2>&1
```

### Live Match Detection

```python
# Only run live updates when there's a match
def is_match_day():
    matches = fetcher.get_today_matches()
    return any(m.status in ['IN_PLAY', 'PAUSED', 'LIVE'])
```

---

## gog CLI Commands

### Setup/Authentication

```bash
# Check gog status
gog calendar list

# Authorize (if needed)
gog auth status
```

### Event Operations

```bash
# List events from Palmeiras calendar
gog calendar events --calendar "Palmeiras - Jogos" \
  --from 2024-01-01 --to 2024-12-31

# Create new event
gog calendar create \
  --calendar "Palmeiras - Jogos" \
  --title "Palmeiras x Corinthians - Brasileirão" \
  --start "2024-07-15T16:00:00" \
  --end "2024-07-15T18:00:00" \
  --location "Allianz Parque, São Paulo" \
  --description "🏆 Brasileirão - Rodada 15"

# Update event (by ID)
gog calendar update "abc123xyz" \
  --title "✅ Palmeiras 2 x 1 Corinthians - Brasileirão"

# Delete event
gog calendar delete "abc123xyz"

# Find event by title
gog calendar events --search "Palmeiras x Corinthians"
```

### Python Wrapper (gog_client.py)

```python
import subprocess
import json

class GogClient:
    def __init__(self, calendar_name="Palmeiras - Jogos"):
        self.calendar = calendar_name
    
    def create_event(self, title, start, end, location=None, description=None):
        cmd = [
            "gog", "calendar", "create",
            "--calendar", self.calendar,
            "--title", title,
            "--start", start,
            "--end", end
        ]
        if location:
            cmd.extend(["--location", location])
        if description:
            cmd.extend(["--description", description])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    def update_event(self, event_id, **kwargs):
        cmd = ["gog", "calendar", "update", event_id]
        for key, value in kwargs.items():
            cmd.extend([f"--{key}", str(value)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    def delete_event(self, event_id):
        cmd = ["gog", "calendar", "delete", event_id]
        subprocess.run(cmd, capture_output=True)
    
    def list_events(self, start_date, end_date):
        cmd = [
            "gog", "calendar", "events",
            "--calendar", self.calendar,
            "--from", start_date,
            "--to", end_date,
            "--json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
```

---

## Features

### 1. Create Events ✅

- Fetch upcoming matches from football-data.org
- Transform to Google Calendar event format
- Create event in calendar
- Store event ID mapping for updates

### 2. Update with Scores ✅

- On live match days, fetch current scores
- Update event title with live score
- Update description with match stats
- Color-code by competition

### 3. Delete Old Events ✅

- Delete events older than X days
- Or move to "Archive" calendar

### 4. Additional Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Reminder** | Add 30-min notification before match | High |
| **Multiple Calendars** | Support competition-specific calendars | Medium |
| **Color Coding** | Different colors per competition | Medium |
| **Recurring** | Handle stadium address changes | Low |
| **Conflict Detection** | Warn if two matches at same time | Low |

### Event Reminders

```python
# Add reminder to event
gog calendar create \
  --reminder 30m \
  --title "Palmeiras x Corinthians"
```

---

## Error Handling

### Error Types & Handling

| Error | Handling | Retry |
|-------|----------|-------|
| gog not authenticated | Prompt user to run `gog auth login` | No |
| API rate limit | Wait and retry | Yes (3x) |
| Network timeout | Retry | Yes (3x) |
| Event not found (update) | Log warning, skip | No |
| Duplicate event | Use existing, skip create | No |
| Invalid date format | Log error, skip | No |

### Local Event Cache

```python
# data/calendar_events.json
{
  "last_sync": "2024-07-15T10:00:00Z",
  "events": [
    {
      "match_id": "12345",
      "event_id": "abc123xyz",
      "title": "Palmeiras x Corinthians - Brasileirão",
      "created_at": "2024-07-10T08:00:00Z"
    }
  ]
}
```

### Logging

```python
# Log format
2024-07-15 10:00:00 INFO Created event: Palmeiras x Corinthians (event_id: abc123)
2024-07-15 10:00:00 INFO Updated event: Palmeiras 2 x 1 Corinthians (event_id: abc123)
2024-07-15 10:00:00 WARNING Event not found for match 12345, creating new
2024-07-15 10:00:00 ERROR Failed to create event: Rate limit exceeded
```

---

## Implementation Steps

### Phase 1: Basic Sync (Week 1)

- [ ] Set up gog CLI authentication
- [ ] Create config/calendar.yaml
- [ ] Implement gog_client.py wrapper
- [ ] Implement event_mapper.py
- [ ] Test create event manually
- [ ] Create full sync script

### Phase 2: Update Logic (Week 2)

- [ ] Implement deduplicator.py
- [ ] Add event ID to local cache
- [ ] Implement update logic
- [ ] Add live match detection
- [ ] Test update on fake live match

### Phase 3: Cleanup & Polish (Week 3)

- [ ] Implement cleanup logic
- [ ] Add error handling
- [ ] Set up cron jobs
- [ ] Add logging
- [ ] Test full cycle

---

## Configuration Summary

```yaml
# calendar.yaml - Complete Config

calendar:
  name: "Palmeiras - Jogos"
  timezone: "America/Sao_Paulo"
  
api:
  football_data:
    team_id: 153  # Palmeiras
    api_key_env: "FOOTBALL_DATA_API_KEY"
  
sync:
  look_ahead_days: 30
  keep_results_days: 7
  full_sync_hours: 6
  live_update_minutes: 15

reminders:
  default_minutes: 30
  
competitions:
  colors:
    Brasileirão: "#00C853"
    "Copa Libertadores": "#FFD600"
    "Copa do Brasil": "#2962FF"
```

---

## Summary

| Component | Implementation |
|-----------|----------------|
| **Data Source** | football-data.org API |
| **Calendar Tool** | gog CLI |
| **Calendar Structure** | Single calendar with status in title |
| **Sync Frequency** | Every 6 hours (full), 15 min (live) |
| **Event Format** | "Palmeiras x [Opponent] - [Competition]" |
| **Updates** | Title with score, description with stats |
| **Cleanup** | Delete events older than 7 days |
| **Error Handling** | Retry logic + local cache |

This plan provides a complete roadmap for integrating Palmeiras matches into Google Calendar with automatic updates and minimal maintenance.
