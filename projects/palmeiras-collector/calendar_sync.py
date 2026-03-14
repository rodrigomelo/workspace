#!/usr/bin/env python3
"""
Palmeiras Calendar Sync v3 - With proper error handling and logging

...

(same as before but with better logging)
"""
import os
import sys
import json
import subprocess
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/palmeiras_calendar.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = os.getenv('TEAM_ID', '1769')
CALENDAR_ID = os.getenv('CALENDAR_ID', 'melorodrigo@gmail.com')
CACHE_FILE = Path(__file__).parent / '.calendar_cache.json'
BRAZIL_TZ = ZoneInfo('America/Sao_Paulo')

STADIUMS = {
    'SE Palmeiras': 'Allianz Parque',
    'Mirassol FC': 'Estádio José Maria de Campos Maia',
    'Botafogo FR': 'Estádio Nilton Santos',
    'São Paulo FC': 'Estádio Morumbis',
    'SC Corinthians Paulista': 'Arena Corinthians',
    'Grêmio FBPA': 'Arena do Grêmio',
    'EC Bahia': 'Arena Fonte Nova',
}

BROADCASTERS = {
    'Campeonato Brasileiro Série A': {'tv': 'Globo, Premiere', 'streaming': 'Premiere, Globoplay'},
    'Copa do Brasil': {'tv': 'Globo, SBT', 'streaming': 'Globoplay'},
    'Copa Libertadores': {'tv': 'Globo, Paramount+', 'streaming': 'Paramount+'},
}


def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'events': {}, 'last_sync': None, 'google_event_ids': {}}


def save_cache(cache):
    cache['last_sync'] = datetime.now().isoformat()
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def get_team_name(team):
    return team.get('name', 'Unknown')


def get_opponent(match, team_id):
    home = match.get('homeTeam', {})
    away = match.get('awayTeam', {})
    if str(home.get('id')) == team_id:
        return get_team_name(away)
    elif str(away.get('id')) == team_id:
        return get_team_name(home)
    return 'Unknown'


def is_home_game(match, team_id):
    return str(match.get('homeTeam', {}).get('id')) == team_id


def get_competition_name(match):
    name = match.get('competition', {}).get('name', 'Campeonato')
    if 'Brasileiro' in name and 'Série A' in name:
        return 'Brasileirão'
    elif 'Copa do Brasil' in name:
        return 'Copa do Brasil'
    elif 'Libertadores' in name:
        return 'Copa Libertadores'
    return name


def format_datetime(utc_str):
    utc_dt = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
    brazil_dt = utc_dt.astimezone(BRAZIL_TZ)
    end_dt = brazil_dt + timedelta(hours=2)
    start_iso = brazil_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    end_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    return start_iso, end_iso, brazil_dt.strftime('%d/%m às %H:%M')


def create_event_title(opponent, competition):
    return f"Palmeiras vs {opponent} - {competition}"


def create_event_description(match, competition, match_time):
    team_id = TEAM_ID
    venue = get_stadium('SE Palmeiras') if is_home_game(match, team_id) else 'TBD'
    city = 'São Paulo, SP' if is_home_game(match, team_id) else 'TBD'
    broadcast = BROADCASTERS.get(competition, {'tv': 'TBD', 'streaming': 'TBD'})
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


def get_stadium(team_name):
    return STADIUMS.get(team_name, 'TBD')


def get_event_color(match):
    opponent = get_opponent(match, TEAM_ID)
    derbies = ['Corinthians', 'Santos', 'São Paulo', 'Flamengo']
    if any(d in opponent for d in derbies):
        return '11'
    return '10' if is_home_game(match, TEAM_ID) else '5'


def fetch_upcoming_matches(limit=10):
    url = f'https://api.football-data.org/v4/teams/{TEAM_ID}/matches'
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        upcoming = [m for m in matches if m.get('status') in ('TIMED', 'SCHEDULED')]
        logger.info(f"Fetched {len(upcoming)} upcoming matches")
        return upcoming[:limit]
    except Exception as e:
        logger.error(f"Failed to fetch matches: {e}")
        return []


def query_google_calendar():
    cmd = ['gog', 'calendar', 'events', CALENDAR_ID, '--json']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.warning(f"Could not query calendar: {result.stderr}")
            return {}
        
        data = json.loads(result.stdout)
        events = data.get('events', []) if isinstance(data, dict) else data
        
        indexed = {}
        for event in events:
            summary = event.get('summary', '')
            indexed[summary] = event
        
        logger.info(f"Found {len(indexed)} events in Google Calendar")
        return indexed
    except Exception as e:
        logger.error(f"Error querying calendar: {e}")
        return {}


def find_existing_event(opponent, google_events):
    title = f"Palmeiras vs {opponent}"
    
    if title in google_events:
        return google_events[title].get('id')
    
    # Partial match
    for key, event in google_events.items():
        if f"Palmeiras vs {opponent}" in key.replace('🏆', '').replace('⚽', ''):
            return event.get('id')
    
    return None


def create_calendar_event(match):
    team_id = TEAM_ID
    opponent = get_opponent(match, team_id)
    competition = get_competition_name(match)
    match_time = match.get('utcDate', '')
    
    start_iso, end_iso, time_formatted = format_datetime(match_time)
    title = create_event_title(opponent, competition)
    description = create_event_description(match, competition, time_formatted)
    color = get_event_color(match)
    
    logger.info(f"Creating: {title}")
    
    cmd = [
        'gog', 'calendar', 'create', CALENDAR_ID,
        '--summary', title,
        '--from', start_iso,
        '--to', end_iso,
        '--description', description,
        '--event-color', color,
        '--reminder', 'popup:120m',
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info(f"✅ Created: {title}")
            # Try to extract event ID from output
            try:
                output = json.loads(result.stdout)
                event_id = output.get('id')
                return event_id
            except:
                return True
        else:
            logger.error(f"❌ Failed: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return None


def sync_matches(matches, cache, google_events, dry_run=False):
    created = 0
    skipped = 0
    
    for match in matches:
        opponent = get_opponent(match, TEAM_ID)
        competition = get_competition_name(match)
        match_id = str(match.get('id', ''))
        title = create_event_title(opponent, competition)
        
        # Check if already in cache
        if match_id in cache['events']:
            logger.info(f"⏭️ Skipping (cached): {title}")
            skipped += 1
            continue
        
        # Check if exists in Google
        existing_id = find_existing_event(opponent, google_events)
        if existing_id:
            logger.info(f"⏭️ Skipping (exists in Google): {title}")
            cache['events'][match_id] = {
                'title': title,
                'date': match.get('utcDate', '')[:10],
                'competition': competition,
                'google_event_id': existing_id,
                'created_at': datetime.now().isoformat()
            }
            skipped += 1
            continue
        
        # Create new event
        if not dry_run:
            event_id = create_calendar_event(match)
            if event_id:
                cache['events'][match_id] = {
                    'title': title,
                    'date': match.get('utcDate', '')[:10],
                    'competition': competition,
                    'google_event_id': event_id if event_id != True else None,
                    'created_at': datetime.now().isoformat()
                }
                created += 1
            else:
                logger.error(f"Failed to create: {title}")
        else:
            logger.info(f"[DRY RUN] Would create: {title}")
            created += 1
    
    return created, skipped


def main():
    parser = argparse.ArgumentParser(description='Sync Palmeiras matches to Google Calendar')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("Palmeiras Calendar Sync v3")
    logger.info("=" * 50)
    
    # Load cache
    cache = load_cache()
    logger.info(f"Cache loaded: {len(cache.get('events', {}))} events")
    
    # Fetch matches
    matches = fetch_upcoming_matches(args.limit)
    if not matches:
        logger.warning("No upcoming matches found")
        return
    
    logger.info(f"Found {len(matches)} upcoming matches")
    
    # Query Google Calendar
    google_events = query_google_calendar()
    
    # Sync
    created, skipped = sync_matches(matches, cache, google_events, args.dry_run)
    
    # Save cache
    save_cache(cache)
    
    logger.info("=" * 50)
    logger.info(f"Summary: Created={created}, Skipped={skipped}")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
