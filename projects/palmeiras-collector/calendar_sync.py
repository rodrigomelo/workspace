#!/usr/bin/env python3
"""
Palmeiras Calendar Sync

Fetches upcoming matches from football-data.org and creates Google Calendar events.

Usage:
    python calendar_sync.py [--dry-run] [--limit N]

Environment:
    FOOTBALL_API_KEY - API key for football-data.org
    TEAM_ID - Team ID for Palmeiras (default: 1769)
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = os.getenv('TEAM_ID', '1769')
CALENDAR_ID = os.getenv('CALENDAR_ID', 'melorodrigo@gmail.com')

# Brazil timezone
BRAZIL_TZ = ZoneInfo('America/Sao_Paulo')

# Stadium mapping (can be expanded)
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
    'Clube do Remo': 'Estádio Evandro Almeida',
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
    
    # Simplify competition names
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
    # Try exact match first
    for comp_key, info in BROADCASTERS.items():
        if comp_key in competition:
            return info
    return {'tv': 'TBD', 'streaming': 'TBD'}


def format_datetime(utc_str: str) -> tuple:
    """Convert UTC string to Brazil timezone datetime.
    
    Returns:
        tuple: (start_iso, end_iso) in ISO format
    """
    utc_dt = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
    brazil_dt = utc_dt.astimezone(BRAZIL_TZ)
    
    # Match duration: 90 minutes + 15 min halftime = ~2 hours total
    end_dt = brazil_dt + timedelta(hours=2)
    
    # Format for gog CLI - needs timezone offset
    # e.g., 2026-03-15T21:30:00-03:00
    start_iso = brazil_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    end_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    return start_iso, end_iso, brazil_dt.strftime('%d/%m às %H:%M')


def create_event_title(opponent: str, competition: str) -> str:
    """Create event title in the required format."""
    return f"🏆 Palmeiras vs {opponent} - {competition}"


def create_event_description(match: dict, competition: str, match_time: str) -> str:
    """Create event description in the required format."""
    team_id = TEAM_ID
    venue = get_stadium('SE Palmeiras') if is_home_game(match, team_id) else 'TBD'
    
    # Get city (usually São Paulo for most matches in Brasileirão)
    city = 'São Paulo, SP' if is_home_game(match, team_id) else 'TBD'
    
    broadcast = get_broadcast_info(competition)
    round_num = match.get('matchday', 'TBD')
    
    description = f"""⚽ PARTIDA DO PALMEIRAS

🏟️ Estádio: {venue}
📍 Cidade: {city}
🕐Horário: {match_time} (horário de Brasília)

📺 Onde assistir:
• TV: {broadcast['tv']}
• Streaming: {broadcast['streaming']}

🔄 Competição: {competition}
📊 Rodada: {round_num}ªrodada"""

    return description


def get_event_color(match: dict, competition: str) -> str:
    """Determine event color based on match type."""
    opponent = get_opponent(match, TEAM_ID)
    
    # Derby games - red
    derbies = ['Corinthians', 'Santos', 'São Paulo', 'Flamengo', 'Coritiba']
    if any(d in opponent for d in derbies):
        return '11'  # Red
    
    # Home game - green
    if is_home_game(match, TEAM_ID):
        return '10'  # Green
    
    # Away game - yellow
    return '5'  # Yellow


def fetch_upcoming_matches(limit: int = 10) -> list:
    """Fetch upcoming matches from football-data.org."""
    url = f'https://api.football-data.org/v4/teams/{TEAM_ID}/matches'
    headers = {'X-Auth-Token': API_KEY}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    matches = data.get('matches', [])
    
    # Filter for upcoming matches (TIMED or SCHEDULED)
    upcoming = [
        m for m in matches 
        if m.get('status') in ('TIMED', 'SCHEDULED')
    ]
    
    return upcoming[:limit]


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
    
    # Build gog command
    cmd = [
        'gog', 'calendar', 'create', CALENDAR_ID,
        '--summary', title,
        '--from', start_iso,
        '--to', end_iso,
        '--description', description,
        '--event-color', color,
        '--reminder', 'popup:120m',  # 2 hours before
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  ✅ Event created successfully")
        return True
    else:
        print(f"  ❌ Error: {result.stderr}")
        return False


def list_existing_events(calendar_id: str, days: int = 30) -> list:
    """List existing Palmeiras events in calendar."""
    from_date = datetime.now().strftime('%Y-%m-%d')
    to_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    cmd = [
        'gog', 'calendar', 'events', calendar_id,
        '--from', from_date,
        '--to', to_date,
        '--json'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return []
    
    try:
        events = json.loads(result.stdout)
        # Filter for Palmeiras events
        return [e for e in events if 'Palmeiras' in e.get('summary', '')]
    except:
        return []


def main():
    parser = argparse.ArgumentParser(description='Sync Palmeiras matches to Google Calendar')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating events')
    parser.add_argument('--limit', type=int, default=5, help='Number of matches to sync')
    parser.add_argument('--calendar-id', type=str, default=CALENDAR_ID, help='Calendar ID to use')
    parser.add_argument('--check-existing', action='store_true', help='Check for existing events before creating')
    
    args = parser.parse_args()
    
    print("⚽ Palmeiras Calendar Sync")
    print("=" * 40)
    
    # Fetch upcoming matches
    print(f"\n📡 Fetching upcoming matches...")
    matches = fetch_upcoming_matches(args.limit)
    
    if not matches:
        print("No upcoming matches found.")
        return
    
    print(f"Found {len(matches)} upcoming matches\n")
    
    # Check for existing events if requested
    existing_events = []
    if args.check_existing:
        print("🔍 Checking for existing events...")
        existing_events = list_existing_events(args.calendar_id)
        print(f"Found {len(existing_events)} existing Palmeiras events\n")
    
    # Create events
    created = 0
    skipped = 0
    
    for match in matches:
        opponent = get_opponent(match, TEAM_ID)
        competition = get_competition_name(match)
        title = create_event_title(opponent, competition)
        
        # Check if event already exists
        if args.check_existing and any(title in e.get('summary', '') for e in existing_events):
            print(f"⏭️  Skipping (already exists): {title}")
            skipped += 1
            continue
        
        if create_calendar_event(match, args.dry_run):
            created += 1
    
    print(f"\n✅ Summary:")
    print(f"   Created: {created}")
    print(f"   Skipped: {skipped}")
    print(f"   Total:   {len(matches)}")


if __name__ == '__main__':
    main()
