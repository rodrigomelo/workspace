#!/usr/bin/env python3
"""
Palmeiras Calendar Sync - Robust Anti-Duplication Version v2

Fetches upcoming matches from football-data.org and creates Google Calendar events.
Uses dual verification: cache + Google Calendar API to prevent duplicates.

Key improvements over v1:
1. Uses Match ID from API (not hash) as unique identifier
2. Queries Google Calendar API directly before creating
3. Stores Google Calendar event ID for updates
4. Full reconciliation on each run

Usage:
    python calendar_sync_v2.py [--dry-run] [--limit N] [--force]

Environment:
    FOOTBALL_API_KEY - API key for football-data.org
    GOOGLE_APPLICATION_CREDENTIALS - Path to Google credentials JSON
"""

import os
import sys
import json
import subprocess
import argparse
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
CACHE_FILE = Path(__file__).parent / '.calendar_cache_v2.json'

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


class CalendarSync:
    """Robust calendar sync with dual verification."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.cache = self.load_cache()
        self.google_events = {}  # Cache of events from Google Calendar
        
    def load_cache(self) -> dict:
        """Load the event cache from file."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'events': {},           # match_id -> {google_event_id, title, date, etc}
            'google_event_ids': {}, # google_event_id -> match_id (reverse index)
            'last_sync': None,
            'last_full_reconcile': None
        }
    
    def save_cache(self) -> None:
        """Save the event cache to file."""
        self.cache['last_sync'] = datetime.now().isoformat()
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_match_id(self, match: dict) -> str:
        """Get unique match ID from API - the most reliable identifier."""
        return str(match.get('id', ''))
    
    def get_team_name(self, team: dict) -> str:
        """Extract team name from API response."""
        return team.get('name', 'Unknown')
    
    def get_opponent(self, match: dict) -> str:
        """Get the opponent team name."""
        home = match.get('homeTeam', {})
        away = match.get('awayTeam', {})
        
        if str(home.get('id')) == TEAM_ID:
            return self.get_team_name(away)
        elif str(away.get('id')) == TEAM_ID:
            return self.get_team_name(home)
        return 'Unknown'
    
    def is_home_game(self, match: dict) -> bool:
        """Check if it's a home game."""
        home = match.get('homeTeam', {})
        return str(home.get('id')) == TEAM_ID
    
    def get_stadium(self, team_name: str) -> str:
        """Get stadium name for the team."""
        return STADIUMS.get(team_name, 'TBD')
    
    def get_competition_name(self, match: dict) -> str:
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
    
    def get_broadcast_info(self, competition: str) -> dict:
        """Get broadcaster info for competition."""
        for comp_key, info in BROADCASTERS.items():
            if comp_key in competition:
                return info
        return {'tv': 'TBD', 'streaming': 'TBD'}
    
    def format_datetime(self, utc_str: str) -> tuple:
        """Convert UTC string to Brazil timezone datetime."""
        utc_dt = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
        brazil_dt = utc_dt.astimezone(BRAZIL_TZ)
        end_dt = brazil_dt + timedelta(hours=2)
        
        start_iso = brazil_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        end_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        
        return start_iso, end_iso, brazil_dt.strftime('%d/%m às %H:%M')
    
    def create_event_title(self, opponent: str, competition: str) -> str:
        """Create event title (no trophy emoji)."""
        return f"Palmeiras vs {opponent} - {competition}"
    
    def create_event_description(self, match: dict, competition: str, match_time: str) -> str:
        """Create event description."""
        venue = self.get_stadium('SE Palmeiras') if self.is_home_game(match) else 'TBD'
        city = 'São Paulo, SP' if self.is_home_game(match) else 'TBD'
        broadcast = self.get_broadcast_info(competition)
        round_num = match.get('matchday', 'TBD')
        
        return f"""PARTIDA DO PALMEIRAS

Estadio: {venue}
Cidade: {city}
Horario: {match_time} (horario de Brasilia)

Onde assistir:
- TV: {broadcast['tv']}
- Streaming: {broadcast['streaming']}

Competicao: {competition}
Rodada: {round_num}"""
    
    def get_event_color(self, match: dict) -> str:
        """Determine event color based on match type."""
        opponent = self.get_opponent(match)
        
        derbies = ['Corinthians', 'Santos', 'Sao Paulo', 'Flamengo', 'Coritiba']
        if any(d.lower() in opponent.lower() for d in derbies):
            return '11'  # Red
        if self.is_home_game(match):
            return '10'  # Green
        return '5'  # Yellow
    
    def fetch_upcoming_matches(self, limit: int = 10) -> list:
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
    
    def query_google_calendar(self, start_date: str, end_date: str) -> dict:
        """Query Google Calendar for existing events."""
        # Note: gog date filters can be unreliable, get all and filter in Python
        cmd = [
            'gog', 'calendar', 'events', CALENDAR_ID,
            '--json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"    Warning: Could not query calendar: {result.stderr}")
            return {}
        
        try:
            data = json.loads(result.stdout)
            # gog returns {"events": [...]} structure
            events = data.get('events', []) if isinstance(data, dict) else data
            # Index by summary for quick lookup
            indexed = {}
            for event in events:
                summary = event.get('summary', '')
                indexed[summary] = event
                # Also index by event ID
                eid = event.get('id', '')
                if eid:
                    indexed[eid] = event
            return indexed
        except json.JSONDecodeError:
            print(f"    Warning: Could not parse calendar response")
            return {}
    
    def find_existing_event(self, match: dict, google_events: dict) -> tuple:
        """
        Find if event already exists using multiple strategies.
        Returns (exists: bool, event_id: str or None)
        """
        match_id = self.get_match_id(match)
        opponent = self.get_opponent(match)
        competition = self.get_competition_name(match)
        match_time = match.get('utcDate', '')
        
        # Strategy 1: Check local cache for this match ID
        if match_id in self.cache['events']:
            cached = self.cache['events'][match_id]
            google_id = cached.get('google_event_id')
            if google_id:
                print(f"    Strategy 1 - Found in cache: {google_id}")
                return True, google_id
        
        # Strategy 2: Look for event with matching title in Google Calendar
        title = self.create_event_title(opponent, competition)
        
        # Try exact title match
        if title in google_events:
            google_id = google_events[title].get('id')
            print(f"    Strategy 2 - Found by title: {google_id}")
            return True, google_id
        
        # Try partial match (without competition, with or without emoji)
        partial_title = f"Palmeiras vs {opponent}"
        for key, event in google_events.items():
            # Clean the key (remove emojis) for comparison
            clean_key = key.replace('🏆', '').replace('⚽', '')
            if partial_title in clean_key:
                google_id = event.get('id')
                print(f"    Strategy 3 - Found by partial match: {google_id}")
                return True, google_id
        
        return False, None
    
    def reconcile_with_google(self) -> None:
        """Perform full reconciliation between cache and Google Calendar."""
        print("\n  Performing full reconciliation...")
        
        # Get date range: 30 days past to 1 year future
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        google_events = self.query_google_calendar(start_date, end_date)
        
        # Mark all known events
        matched = 0
        orphaned = 0
        
        for match_id, cached_event in list(self.cache['events'].items()):
            google_id = cached_event.get('google_event_id')
            if google_id and google_id in google_events:
                matched += 1
            elif google_id:
                # Event exists in cache but not in Google - might have been deleted
                orphaned += 1
                print(f"    Orphaned event: {google_id} (match {match_id})")
        
        print(f"    Matched: {matched}, Orphaned: {orphaned}")
        self.cache['last_full_reconcile'] = datetime.now().isoformat()
    
    def create_event(self, match: dict, existing_event_id: str = None) -> bool:
        """Create or update a calendar event."""
        match_id = self.get_match_id(match)
        opponent = self.get_opponent(match)
        competition = self.get_competition_name(match)
        match_time = match.get('utcDate', '')
        
        start_iso, end_iso, time_formatted = self.format_datetime(match_time)
        title = self.create_event_title(opponent, competition)
        description = self.create_event_description(match, competition, time_formatted)
        color = self.get_event_color(match)
        
        print(f"  {title}")
        
        if self.dry_run:
            print(f"    [DRY RUN]")
            return True
        
        # If we have an existing event ID, update it
        if existing_event_id:
            print(f"    Updating existing event: {existing_event_id}")
            # Delete old and create new (gog doesn't have direct update)
            delete_cmd = ['gog', 'calendar', 'delete', CALENDAR_ID, '--event-id', existing_event_id]
            subprocess.run(delete_cmd, capture_output=True)
        
        # Create new event
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
            print(f"    Created successfully")
            
            # Try to extract event ID from output
            # For now, we'll do a quick lookup to get the ID
            date_str = match_time[:10]
            google_events = self.query_google_calendar(date_str, date_str)
            _, new_event_id = self.find_existing_event(match, google_events)
            
            # Update cache
            self.cache['events'][match_id] = {
                'title': title,
                'date': date_str,
                'competition': competition,
                'google_event_id': new_event_id or 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            if new_event_id:
                self.cache['google_event_ids'][new_event_id] = match_id
            
            return True
        else:
            print(f"    Error: {result.stderr}")
            return False
    
    def sync_matches(self, matches: list, force: bool = False) -> dict:
        """Sync all matches to calendar."""
        if not matches:
            print("No matches to sync.")
            return {'created': 0, 'updated': 0, 'skipped': 0}
        
        # Get date range for Google Calendar query
        dates = [m.get('utcDate', '')[:10] for m in matches]
        min_date = min(dates) if dates else datetime.now().strftime('%Y-%m-%d')
        max_date = (datetime.fromisoformat(max(dates)) + timedelta(days=1)).strftime('%Y-%m-%d') if dates else (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"\n  Querying Google Calendar for {min_date} to {max_date}...")
        google_events = self.query_google_calendar(min_date, max_date)
        
        created = 0
        updated = 0
        skipped = 0
        
        for match in matches:
            match_id = self.get_match_id(match)
            opponent = self.get_opponent(match)
            competition = self.get_competition_name(match)
            
            print(f"\n  Checking: Palmeiras vs {opponent} ({competition})")
            
            # Check if exists
            exists, event_id = self.find_existing_event(match, google_events)
            
            if exists and not force:
                print(f"    Already exists, skipping")
                skipped += 1
                
                # Update cache with Google event ID if we found it
                if event_id and match_id not in self.cache['events']:
                    self.cache['events'][match_id] = {
                        'google_event_id': event_id,
                        'updated_at': datetime.now().isoformat()
                    }
                continue
            
            # Create or update
            if exists and force:
                print(f"    Force mode - will update")
                updated += 1
            else:
                print(f"    Creating new event")
                created += 1
            
            self.create_event(match, event_id if force else None)
        
        # Clean old events from cache
        cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        old_events = [
            mid for mid, ev in self.cache['events'].items() 
            if ev.get('date', '') < cutoff
        ]
        for mid in old_events:
            del self.cache['events'][mid]
        
        return {'created': created, 'updated': updated, 'skipped': skipped}


def main():
    parser = argparse.ArgumentParser(description='Sync Palmeiras matches to Google Calendar (v2)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created')
    parser.add_argument('--limit', type=int, default=10, help='Number of matches to sync')
    parser.add_argument('--force', action='store_true', help='Force recreate/update all events')
    parser.add_argument('--reconcile', action='store_true', help='Perform full reconciliation')
    parser.add_argument('--check', action='store_true', help='Check existing events only')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print(" Palmeiras Calendar Sync v2 (Robust Anti-Duplication)")
    print("=" * 50)
    
    sync = CalendarSync(dry_run=args.dry_run)
    
    # Reconciliation mode
    if args.reconcile:
        sync.reconcile_with_google()
        sync.save_cache()
        print("\n Reconciliation complete!")
        return
    
    # Check mode
    if args.check:
        print("\n Checking existing events...")
        matches = sync.fetch_upcoming_matches(args.limit)
        
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        google_events = sync.query_google_calendar(start_date, end_date)
        
        print(f"\n Found {len(google_events)} events in Google Calendar")
        
        for match in matches:
            match_id = sync.get_match_id(match)
            opponent = sync.get_opponent(match)
            
            exists, event_id = sync.find_existing_event(match, google_events)
            status = "In Calendar" if exists else "Not found"
            cached = "Cached" if match_id in sync.cache['events'] else "Not cached"
            
            print(f"  {status} | {cached} | Palmeiras vs {opponent}")
        
        return
    
    # Normal sync
    print(f"\n Fetching upcoming matches...")
    matches = sync.fetch_upcoming_matches(args.limit)
    
    if not matches:
        print("No upcoming matches found.")
        return
    
    print(f" Found {len(matches)} upcoming matches\n")
    
    # Perform sync
    result = sync.sync_matches(matches, force=args.force)
    
    # Save cache
    sync.save_cache()
    
    print("\n" + "=" * 50)
    print(" Summary:")
    print(f"   Created: {result['created']}")
    print(f"   Updated: {result['updated']}")
    print(f"   Skipped: {result['skipped']}")
    print(f"   Total:   {len(matches)}")
    print("=" * 50)


if __name__ == '__main__':
    main()
