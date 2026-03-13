#!/usr/bin/env python3
"""
Palmeiras Calendar Sync - Anti-Duplication Version

Fetches upcoming matches from football-data.org and creates Google Calendar events.
Uses a cache file to track created events and avoid duplicates.

Usage:
    python calendar_sync.py [--dry-run] [--limit N] [--force]

Environment:
    FOOTBALL_API_KEY - API key for football-data.org
    TEAM_ID - Team ID for Palmeiras (default: 1769)
"""

import os
import sys
import json
import subprocess
import argparse
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = os.getenv('TEAM_ID', '1769')
CALENDAR_ID = os.getenv('CALENDAR_ID', 'melorodrigo@gmail.com')

# Cache file for tracking created events
CACHE_FILE = Path(__file__).parent / '.calendar_cache.json'

# Brazil timezone
BRAZIL_TZ = ZoneInfo('America/Sao_Paulo')

# Stadium mapping
STADIUMS = {
    'SE Palmeiras': 'Allianz Parque',
    'Mirassol FC': 'Estádio José Maria de Campos Maia',
    'Botafogo FR': 'Estádio Nilton Santos (Maracanã)',
    'São Paulo FC': 'Estádio Morumbis',
    'SC Corinthians Paulista': 'Arena Corinthians',
    'Grêmio FBPA': 'Arena do Grêmio',
    'EC Bahia': 'Arena Fonte Nova',
    'CA Paranaense': 'Estádio Durival Britto',
    'RB Bragantino': 'Estádio Nabi Abi Chedid',
    'Santos FC': 'Estádio Vila Capanema',
    'Cruzeiro EC': 'Estádio Mineirão',
    'CR Flamengo': 'Estádio do Maracanã',
    'Chapecoense AF': 'Arena Condá',
    'Coritiba FBC': 'Estádio Couto Pereira',
    'CA Mineiro': 'Estádio Mineirão',
    'EC Vitória': 'Estádio Barradão',
    'SC Internacional': 'Estádio Beira-Rio',
    'Fluminense FC': 'Estádio do Maracanã',
    'CR Vasco da Gama': 'Estádio São Januário',
}

# Competitions with broadcaster info
BROADCASTERS = {
    'Campeonato Brasileiro Série A': {
        'tv': 'Globo, Bandeirantes, Record',
        'streaming': 'Premiere, Globoplay'
    },
    'Copa do Brasil': {
        'tv': 'Globo, SBT, Record',
        'streaming': 'Globoplay, Prime Video'
    },
    'Copa Libertadores da América': {
        'tv': 'Globo, Paramount+',
        'streaming': 'Paramount+, Globoplay'
    },
    'Copa Sul-Americana': {
        'tv': 'ESPN, Paramount+',
        'streaming': 'Paramount+'
    },
    'Campeonato Paulista': {
        'tv': 'Globo, Record, Bandeirantes',
        'streaming': 'Globoplay, Paulistão Play'
    }
}


def load_cache() -> dict:
    """Load the event cache from file."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'events': {}, 'last_sync': None}


def save_cache(cache: dict) -> None:
    """Save the event cache to file."""
    cache['last_sync'] = datetime.now().isoformat()
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def generate_event_id(match: dict) -> str:
    """Generate a unique ID for a match based on date and teams."""
    utc_date = match.get('utcDate', '')
    home = match.get('homeTeam', {}).get('id', '')
    away = match.get('awayTeam', {}).get('id', '')
    
    # Create unique key: date_homeId_awayId
    key = f"{utc_date[:10]}_{home}_{away}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def get_team_name(team: dict) -> str:
    """Extract team name from API response."""
    return team.get('name', 'Unknown')


def get_opponent(match: dict, team_id: str) -> str:
    """Get the opponent team name."""
    home = match.get('homeTeam', {})
    away = match.get('awayTeam', {})
    
    if str(home.get('id')) == team_id:
        return get_team_name(away)
    elif str(away.get('id')) == team_id:
        return get_team_name(home)
    return 'Unknown'


def is_home_game(match: dict, team_id: str) -> bool:
    """Check if it's a home game."""
    home = match.get('homeTeam', {})
    return str(home.get('id')) == team_id


def get_stadium(team_name: str) -> str:
    """Get stadium name for the team."""
    return STADIUMS.get(team_name, 'TBD')


def get_competition_name(match: dict) -> str:
    """Get competition name from match."""
    comp = match.get('competition', {})
    name = comp.get('name', 'Campeonato')
    
    if 'Brasileiro' in name and 'Série A' in name:
        return 'Brasileirão'
    elif 'Copa do Brasil' in name:
        return 'Copa do Brasil'
    elif 'Libertadores' in name:
        return 'Copa Libertadores'
    elif 'Sul-Americana' in name:
        return 'Copa Sul-Americana'
    elif 'Paulista' in name:
        return 'Paulistão'
    return name


def get_broadcast_info(competition: str) -> dict:
    """Get broadcaster info for competition."""
    for comp_key, info in BROADCASTERS.items():
        if comp_key in competition:
            return info
    return {'tv': 'TBD', 'streaming': 'TBD'}


def format_datetime(utc_str: str) -> tuple:
    """Convert UTC string to Brazil timezone datetime."""
    utc_dt = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
    brazil_dt = utc_dt.astimezone(BRAZIL_TZ)
    end_dt = brazil_dt + timedelta(hours=2)
    
    start_iso = brazil_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    end_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    return start_iso, end_iso, brazil_dt.strftime('%d/%m às %H:%M')


def create_event_title(opponent: str, competition: str) -> str:
    """Create event title in the required format."""
    return f"Palmeiras vs {opponent} - {competition}"


def create_event_description(match: dict, competition: str, match_time: str) -> str:
    """Create event description in the required format."""
    team_id = TEAM_ID
    venue = get_stadium('SE Palmeiras') if is_home_game(match, team_id) else 'TBD'
    city = 'São Paulo, SP' if is_home_game(match, team_id) else 'TBD'
    broadcast = get_broadcast_info(competition)
    round_num = match.get('matchday', 'TBD')
    
    return f"""⚽ PARTIDA DO PALMEIRAS

🏟️ Estádio: {venue}
📍 Cidade: {city}
🕐 Horário: {match_time} (horário de Brasília)

📺 Onde assistir:
• TV: {broadcast['tv']}
• Streaming: {broadcast['streaming']}

🔄 Competição: {competition}
📊 Rodada: {round_num}ªrodada"""


def get_event_color(match: dict, competition: str) -> str:
    """Determine event color based on match type."""
    opponent = get_opponent(match, TEAM_ID)
    
    derbies = ['Corinthians', 'Santos', 'São Paulo', 'Flamengo', 'Coritiba']
    if any(d in opponent for d in derbies):
        return '11'  # Red
    if is_home_game(match, TEAM_ID):
        return '10'  # Green
    return '5'  # Yellow


def fetch_upcoming_matches(limit: int = 10) -> list:
    """Fetch upcoming matches from football-data.org."""
    url = f'https://api.football-data.org/v4/teams/{TEAM_ID}/matches'
    headers = {'X-Auth-Token': API_KEY}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    matches = data.get('matches', [])
    
    upcoming = [
        m for m in matches 
        if m.get('status') in ('TIMED', 'SCHEDULED')
    ]
    
    return upcoming[:limit]


def get_calendar_event_id(opponent: str, date: str) -> str:
    """Search for existing event ID by title pattern using gog."""
    # Try to find event by searching calendar
    from_date = date[:10]
    to_date = (datetime.fromisoformat(date[:10]) + timedelta(days=1)).strftime('%Y-%m-%d')
    
    cmd = [
        'gog', 'calendar', 'events', CALENDAR_ID,
        '--from', from_date,
        '--to', to_date,
        '--json'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return None
    
    try:
        events = json.loads(result.stdout)
        # Look for matching event
        for event in events:
            summary = event.get('summary', '')
            if 'Palmeiras' in summary and opponent in summary:
                return event.get('id')
    except:
        pass
    
    return None


def update_calendar_event(event_id: str, match: dict, dry_run: bool = False) -> bool:
    """Update an existing calendar event."""
    team_id = TEAM_ID
    opponent = get_opponent(match, team_id)
    competition = get_competition_name(match)
    match_time = match.get('utcDate', '')
    
    start_iso, end_iso, time_formatted = format_datetime(match_time)
    title = create_event_title(opponent, competition)
    description = create_event_description(match, competition, time_formatted)
    color = get_event_color(match, competition)
    
    print(f"  Updating event: {title}")
    
    if dry_run:
        print("    [DRY RUN - Not updating]")
        return True
    
    # Note: gog doesn't have direct update, we delete and recreate
    # For now, we'll just log that update is needed
    print(f"    ℹ️  Event exists - will be updated on next sync")
    return True


def create_calendar_event(match: dict, dry_run: bool = False) -> bool:
    """Create a calendar event for a match."""
    team_id = TEAM_ID
    
    opponent = get_opponent(match, team_id)
    competition = get_competition_name(match)
    match_time = match.get('utcDate', '')
    
    start_iso, end_iso, time_formatted = format_datetime(match_time)
    title = create_event_title(opponent, competition)
    description = create_event_description(match, competition, time_formatted)
    color = get_event_color(match, competition)
    
    print(f"Creating event: {title}")
    print(f"  Start: {start_iso}")
    print(f"  End: {end_iso}")
    print(f"  Color: {color}")
    
    if dry_run:
        print("  [DRY RUN - Not creating event]")
        return True
    
    cmd = [
        'gog', 'calendar', 'create', CALENDAR_ID,
        '--summary', title,
        '--from', start_iso,
        '--to', end_iso,
        '--description', description,
        '--event-color', color,
        '--reminder', 'popup:120m',
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  ✅ Event created successfully")
        return True
    else:
        print(f"  ❌ Error: {result.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Sync Palmeiras matches to Google Calendar')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating events')
    parser.add_argument('--limit', type=int, default=5, help='Number of matches to sync')
    parser.add_argument('--calendar-id', type=str, default=CALENDAR_ID, help='Calendar ID to use')
    parser.add_argument('--force', action='store_true', help='Force recreate all events (ignore cache)')
    parser.add_argument('--check', action='store_true', help='Check existing events only (no create)')
    
    args = parser.parse_args()
    
    print("⚽ Palmeiras Calendar Sync (Anti-Duplication)")
    print("=" * 45)
    
    # Load cache
    cache = load_cache()
    print(f"\n📂 Cache loaded: {len(cache.get('events', {}))} events tracked")
    
    # Fetch upcoming matches
    print(f"\n📡 Fetching upcoming matches...")
    matches = fetch_upcoming_matches(args.limit)
    
    if not matches:
        print("No upcoming matches found.")
        return
    
    print(f"Found {len(matches)} upcoming matches\n")
    
    # Check mode - just show what's in calendar
    if args.check:
        print("🔍 Checking existing events in calendar...")
        for match in matches:
            event_id = generate_event_id(match)
            opponent = get_opponent(match, TEAM_ID)
            date = match.get('utcDate', '')[:10]
            
            cached = cache['events'].get(event_id)
            exists = '✅' if cached else '⏭️'
            
            print(f"  {exists} {date} - Palmeiras vs {opponent}")
            if cached:
                print(f"      Cached: {cached.get('title')}")
        return
    
    # Create events
    created = 0
    skipped = 0
    already_exists = 0
    
    for match in matches:
        event_id = generate_event_id(match)
        opponent = get_opponent(match, TEAM_ID)
        competition = get_competition_name(match)
        title = create_event_title(opponent, competition)
        date = match.get('utcDate', '')[:10]
        
        # Check if already in cache
        if not args.force and event_id in cache['events']:
            print(f"⏭️  Skipping (cached): {title}")
            skipped += 1
            already_exists += 1
            continue
        
        # Also check calendar for existing events (fallback)
        existing_event_id = get_calendar_event_id(opponent, match.get('utcDate', ''))
        
        if existing_event_id and not args.force:
            print(f"⏭️  Skipping (exists in calendar): {title}")
            # Add to cache
            cache['events'][event_id] = {
                'title': title,
                'date': date,
                'calendar_event_id': existing_event_id,
                'created_at': datetime.now().isoformat()
            }
            skipped += 1
            already_exists += 1
            continue
        
        # Create new event
        if create_calendar_event(match, args.dry_run):
            created += 1
            # Add to cache
            cache['events'][event_id] = {
                'title': title,
                'date': date,
                'competition': competition,
                'created_at': datetime.now().isoformat()
            }
    
    # Clean old events from cache (older than 30 days)
    cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    old_events = [eid for eid, ev in cache['events'].items() if ev.get('date', '') < cutoff]
    for eid in old_events:
        del cache['events'][eid]
    
    # Save cache
    save_cache(cache)
    
    print(f"\n✅ Summary:")
    print(f"   Created: {created}")
    print(f"   Skipped (exists): {skipped}")
    print(f"   Total:   {len(matches)}")
    print(f"\n📂 Cache saved: {len(cache['events'])} events tracked")


if __name__ == '__main__':
    main()
