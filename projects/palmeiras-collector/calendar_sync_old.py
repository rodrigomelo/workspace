#!/usr/bin/env python3
"""
Palmeiras Calendar Sync - Robust Anti-Duplication Version

Fetches upcoming matches from football-data.org and creates Google Calendar events.
Uses match ID from API as unique identifier and stores Google Calendar Event IDs.

Usage:
    python calendar_sync.py [--dry-run] [--limit N] [--force-update]

Environment:
    FOOTBALL_API_KEY - API key for football-data.org
    TEAM_ID - Team ID for Palmeiras (default: 1769)
"""

import os
import sys
import json
import subprocess
import argparse
import re
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
    return {'events': {}, 'match_map': {}, 'last_sync': None}


def save_cache(cache: dict) -> None:
    """Save the event cache to file."""
    cache['last_sync'] = datetime.now().isoformat()
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def get_match_id(match: dict) -> str:
    """Get unique match ID from API response."""
    return str(match.get('id', ''))


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
    match_id = get_match_id(match)
    
    return f"""⚽ PARTIDA DO PALMEIRAS

🏟️ Estádio: {venue}
📍 Cidade: {city}
🕐 Horário: {match_time} (horário de Brasília)

📺 Onde assistir:
• TV: {broadcast['tv']}
• Streaming: {broadcast['streaming']}

🔄 Competição: {competition}
📊 Rodada: {round_num}ªrodada

🆔 Match ID: {match_id}"""


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


def find_calendar_event_by_match(opponent: str, match_date: str) -> str:
    """Search for existing event by title pattern using gog calendar events.
    
    Returns the Google Calendar Event ID if found, None otherwise.
    """
    from_date = match_date[:10]
    to_date = (datetime.fromisoformat(match_date[:10]) + timedelta(days=1)).strftime('%Y-%m-%d')
    
    cmd = [
        'gog', 'calendar', 'events', CALENDAR_ID,
        '--from', from_date,
        '--to', to_date,
        '--json'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode != 0:
        print(f"    ⚠️  Error searching calendar: {result.stderr.strip()}")
        return None
    
    try:
        events = json.loads(result.stdout) if result.stdout.strip() else []
        # Look for matching event with "Palmeiras vs {opponent}"
        for event in events:
            summary = event.get('summary', '')
            # Match pattern like "Palmeiras vs Corinthians - Brasileirão"
            if 'Palmeiras vs' in summary and opponent in summary:
                event_id = event.get('id')
                print(f"    ✅ Found existing event: {event_id}")
                return event_id
    except json.JSONDecodeError as e:
        print(f"    ⚠️  Error parsing calendar events: {e}")
    except Exception as e:
        print(f"    ⚠️  Error checking calendar: {e}")
    
    return None


def find_calendar_event_by_id(google_event_id: str) -> bool:
    """Check if a specific Google Calendar event ID still exists."""
    cmd = [
        'gog', 'calendar', 'event', CALENDAR_ID,
        '--id', google_event_id,
        '--json'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0


def delete_calendar_event(event_id: str, dry_run: bool = False) -> bool:
    """Delete a calendar event."""
    print(f"    🗑️  Deleting old event: {event_id}")
    
    if dry_run:
        print(f"    [DRY RUN - Not deleting]")
        return True
    
    cmd = [
        'gog', 'calendar', 'delete', CALENDAR_ID,
        '--id', event_id,
        '--yes'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print(f"    ✅ Event deleted")
        return True
    else:
        print(f"    ❌ Error deleting: {result.stderr.strip()}")
        return False


def create_calendar_event(match: dict, dry_run: bool = False) -> str:
    """Create a calendar event for a match.
    
    Returns the Google Calendar Event ID if successful, None otherwise.
    """
    team_id = TEAM_ID
    
    opponent = get_opponent(match, team_id)
    competition = get_competition_name(match)
    match_time = match.get('utcDate', '')
    match_id = get_match_id(match)
    
    start_iso, end_iso, time_formatted = format_datetime(match_time)
    title = create_event_title(opponent, competition)
    description = create_event_description(match, competition, time_formatted)
    color = get_event_color(match, competition)
    
    print(f"  Creating event: {title}")
    print(f"    Match ID: {match_id}")
    print(f"    Start: {start_iso}")
    print(f"    End: {end_iso}")
    print(f"    Color: {color}")
    
    if dry_run:
        print(f"    [DRY RUN - Not creating event]")
        return "dry-run-event-id"
    
    cmd = [
        'gog', 'calendar', 'create', CALENDAR_ID,
        '--summary', title,
        '--from', start_iso,
        '--to', end_iso,
        '--description', description,
        '--event-color', color,
        '--reminder', 'popup:120m',
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        # Try to extract event ID from output
        # gog calendar create returns the event ID in stdout or a link
        output = result.stdout.strip()
        
        # Try to parse as JSON first
        try:
            data = json.loads(output)
            event_id = data.get('id') or data.get('eventId')
            if event_id:
                print(f"    ✅ Event created: {event_id}")
                return event_id
        except:
            pass
        
        # Try to extract ID from URL pattern in output
        # Pattern: https://calendar.google.com/calendar/event?eid=XXXXX
        match = re.search(r'eid=([a-zA-Z0-9_-]+)', output)
        if match:
            event_id = match.group(1)
            print(f"    ✅ Event created: {event_id}")
            return event_id
        
        # Last resort: return a placeholder and let the caller search for it
        print(f"    ✅ Event created (ID extraction pending)")
        return "created_pending_id"
    else:
        print(f"    ❌ Error: {result.stderr.strip()}")
        return None


def update_calendar_event(google_event_id: str, match: dict, dry_run: bool = False) -> bool:
    """Update an existing calendar event by deleting and recreating."""
    team_id = TEAM_ID
    
    opponent = get_opponent(match, team_id)
    competition = get_competition_name(match)
    match_id = get_match_id(match)
    
    print(f"  🔄 Updating event: {google_event_id}")
    print(f"    Match ID: {match_id}")
    
    # Delete existing event
    if not delete_calendar_event(google_event_id, dry_run):
        return False
    
    # Create new event (this will return the new ID)
    new_event_id = create_calendar_event(match, dry_run)
    
    if new_event_id and new_event_id != "dry-run-event-id":
        return True
    
    return new_event_id is not None


def sync_match_to_calendar(match: dict, cache: dict, force_update: bool = False, dry_run: bool = False) -> tuple:
    """Sync a single match to calendar with anti-duplication logic.
    
    Returns: (status, event_id) where status is 'created', 'updated', 'skipped', or 'error'
    """
    match_id = get_match_id(match)
    opponent = get_opponent(match, TEAM_ID)
    competition = get_competition_name(match)
    title = create_event_title(opponent, competition)
    match_date = match.get('utcDate', '')
    
    print(f"\n📋 Processing: {title}")
    print(f"    Match ID (API): {match_id}")
    
    # Step 1: Check if we have this match_id in our cache with a Google Event ID
    cached_event = cache.get('events', {}).get(match_id)
    
    if cached_event and cached_event.get('google_event_id'):
        stored_google_id = cached_event['google_event_id']
        print(f"    Cached Google Event ID: {stored_google_id}")
        
        # Verify it still exists in Google Calendar
        if find_calendar_event_by_id(stored_google_id):
            if force_update:
                print(f"    🔄 Force update enabled - updating event")
                event_id = update_calendar_event(stored_google_id, match, dry_run)
                if event_id:
                    # Update cache with new ID
                    cache['events'][match_id]['google_event_id'] = event_id if event_id != "dry-run-event-id" else stored_google_id
                    return ('updated', event_id)
                return ('error', None)
            else:
                print(f"    ⏭️  Event exists in calendar - skipping (use --force-update to update)")
                return ('skipped', stored_google_id)
        else:
            print(f"    ⚠️  Cached event not found in calendar - will create new")
            # Remove stale cache entry
            del cache['events'][match_id]
    
    # Step 2: Search Google Calendar for existing event by title
    print(f"    🔍 Searching calendar for existing event...")
    existing_google_id = find_calendar_event_by_match(opponent, match_date)
    
    if existing_google_id:
        print(f"    Found existing event: {existing_google_id}")
        
        if force_update:
            event_id = update_calendar_event(existing_google_id, match, dry_run)
            if event_id:
                cache['events'][match_id] = {
                    'title': title,
                    'google_event_id': event_id if event_id != "dry-run-event-id" else existing_google_id,
                    'competition': competition,
                    'date': match_date[:10],
                    'created_at': datetime.now().isoformat()
                }
                return ('updated', event_id)
            return ('error', None)
        else:
            # Store the found event ID in cache
            cache['events'][match_id] = {
                'title': title,
                'google_event_id': existing_google_id,
                'competition': competition,
                'date': match_date[:10],
                'created_at': datetime.now().isoformat()
            }
            print(f"    ⏭️  Event exists - using existing ID (use --force-update to update)")
            return ('skipped', existing_google_id)
    
    # Step 3: Create new event
    print(f"    ➕ Creating new event...")
    event_id = create_calendar_event(match, dry_run)
    
    if event_id:
        # Store in cache with match_id as key
        actual_event_id = event_id if event_id != "dry-run-event-id" else None
        cache['events'][match_id] = {
            'title': title,
            'google_event_id': actual_event_id,
            'competition': competition,
            'date': match_date[:10],
            'created_at': datetime.now().isoformat()
        }
        
        # Also map the google_event_id for reverse lookup
        if actual_event_id:
            cache['match_map'][actual_event_id] = match_id
        
        return ('created', event_id)
    
    return ('error', None)


def main():
    parser = argparse.ArgumentParser(description='Sync Palmeiras matches to Google Calendar')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating events')
    parser.add_argument('--limit', type=int, default=5, help='Number of matches to sync')
    parser.add_argument('--calendar-id', type=str, default=CALENDAR_ID, help='Calendar ID to use')
    parser.add_argument('--force-update', action='store_true', help='Force update existing events instead of skipping')
    parser.add_argument('--check', action='store_true', help='Check existing events only (no create)')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before syncing')
    
    args = parser.parse_args()
    
    print("⚽ Palmeiras Calendar Sync (Robust Anti-Duplication)")
    print("=" * 50)
    print(f"Using match ID from football-data.org as unique identifier")
    print(f"Calendar: {args.calendar_id}")
    
    # Load cache
    cache = load_cache()
    
    if args.clear_cache:
        print(f"\n🧹 Clearing cache...")
        cache = {'events': {}, 'match_map': {}, 'last_sync': None}
    
    print(f"\n📂 Cache loaded: {len(cache.get('events', {}))} events tracked")
    
    # Fetch upcoming matches
    print(f"\n📡 Fetching upcoming matches...")
    matches = fetch_upcoming_matches(args.limit)
    
    if not matches:
        print("No upcoming matches found.")
        return
    
    print(f"Found {len(matches)} upcoming matches\n")
    
    # Check mode - just show what's in calendar vs cache
    if args.check:
        print("🔍 Checking matches vs calendar...\n")
        for match in matches:
            match_id = get_match_id(match)
            opponent = get_opponent(match, TEAM_ID)
            date = match.get('utcDate', '')[:10]
            
            cached = cache['events'].get(match_id)
            if cached:
                google_id = cached.get('google_event_id')
                exists = find_calendar_event_by_id(google_id) if google_id else False
                status = '✅' if exists else '⚠️ stale'
                print(f"  {status} {date} - Palmeiras vs {opponent}")
                print(f"      Match ID: {match_id}")
                print(f"      Google Event ID: {google_id}")
            else:
                print(f"  ⏭️  {date} - Palmeiras vs {opponent}")
                print(f"      Match ID: {match_id} (not in calendar)")
        return
    
    # Sync matches
    created = 0
    updated = 0
    skipped = 0
    errors = 0
    
    for match in matches:
        status, event_id = sync_match_to_calendar(
            match, cache, 
            force_update=args.force_update, 
            dry_run=args.dry_run
        )
        
        if status == 'created':
            created += 1
        elif status == 'updated':
            updated += 1
        elif status == 'skipped':
            skipped += 1
        elif status == 'error':
            errors += 1
    
    # Clean old events from cache (older than 30 days)
    cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    old_events = [
        mid for mid, ev in cache.get('events', {}).items() 
        if ev.get('date', '') < cutoff
    ]
    for mid in old_events:
        del cache['events'][mid]
    if old_events:
        print(f"\n🧹 Cleaned {len(old_events)} old events from cache")
    
    # Save cache
    save_cache(cache)
    
    print(f"\n" + "=" * 50)
    print(f"✅ Summary:")
    print(f"   Created:  {created}")
    print(f"   Updated:  {updated}")
    print(f"   Skipped:  {skipped}")
    print(f"   Errors:   {errors}")
    print(f"   Total:    {len(matches)}")
    print(f"\n📂 Cache saved: {len(cache['events'])} events tracked")
    
    if args.dry_run:
        print(f"\n⚠️  DRY RUN - No actual changes made")


if __name__ == '__main__':
    main()
