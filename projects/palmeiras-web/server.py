"""
Palmeiras Web Dashboard - Flask Server
"""
import os
import json
import time
import requests
from flask import Flask, jsonify, request, send_from_directory, Response
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.')

API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'

API_HEADERS = {'X-Auth-Token': API_KEY}

# Simple cache: {url: (response_json, timestamp)}
_cache = {}
_CACHE_TTL = 1800  # 30 minutes - reduce API calls

# Static fallback data (deployed with site)
import os
FALLBACK_FILE = os.path.join(os.path.dirname(__file__), 'matches_backup.json')

def load_fallback():
    """Load fallback data from static file"""
    try:
        if os.path.exists(FALLBACK_FILE):
            with open(FALLBACK_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None


def get_cached(url, params=None):
    """Get data from cache or fetch from API"""
    cache_key = f"{url}?{params}" if params else url
    now = time.time()
    
    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        if now - timestamp < _CACHE_TTL:
            return data
    
    # Fetch from API
    try:
        response = requests.get(url, headers=API_HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        _cache[cache_key] = (data, now)
        return data
    except Exception as e:
        # Return cached data if available (even if expired)
        if cache_key in _cache:
            data, _ = _cache[cache_key]
            return data
        # Try fallback file
        fallback = load_fallback()
        if fallback:
            return fallback
        raise e


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/teams/<int:team_id>/matches')
def team_matches(team_id):
    """GET /api/teams/1769/matches - reads from JSON cache only"""
    import os
    
    status = request.args.get('status', 'SCHEDULED')
    limit = request.args.get('limit', '10')
    
    # Try multiple paths - Vercel uses /var/task
    for data_dir in ['data', '/var/task/data', os.path.join(os.path.dirname(__file__), 'data')]:
        if os.path.exists(os.path.join(data_dir, 'matches_scheduled.json')):
            try:
                if status == 'SCHEDULED':
                    with open(os.path.join(data_dir, 'matches_scheduled.json'), 'r') as f:
                        data = json.load(f)
                else:
                    with open(os.path.join(data_dir, 'matches_finished.json'), 'r') as f:
                        data = json.load(f)
                
                if limit:
                    data['matches'] = data['matches'][:int(limit)]
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Data not found'}), 500
    
    # Apply limit
    if 'matches' in data and limit:
        data['matches'] = data['matches'][:int(limit)]
    
    return jsonify(data)


@app.route('/api/competitions/<competition>/standings')
def standings(competition):
    """GET /api/competitions/BSA/standings - reads from JSON cache only"""
    import os
    
    # Try multiple paths for local and Vercel
    data_dir = 'data'
    if not os.path.exists(os.path.join(data_dir, 'standings.json')):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    try:
        with open(os.path.join(data_dir, 'standings.json'), 'r') as f:
            data = json.load(f)
    except:
        data = {'error': 'Standings data not available'}
    
    return jsonify(data)


@app.route('/api/news')
def palmeiras_news():
    """GET /api/news - reads from local JSON cache (no live scraping!)"""
    import os
    
    # Try multiple paths for local and Vercel
    data_dir = 'data'
    if not os.path.exists(os.path.join(data_dir, 'news.json')):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    news_file = os.path.join(data_dir, 'news.json')
    
    try:
        if os.path.exists(news_file):
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify({'articles': data.get('news', [])})
    except Exception as e:
        pass
    
    # Fallback: empty response if no local data
    return jsonify({'articles': [], 'error': 'No cached news available'})


@app.route('/api/calendar.ics')
def calendar_ics():
    """Generate iCal feed for Palmeiras matches - reads from JSON cache only"""
    try:
        # Read from local JSON cache - NO external API calls!
        import json
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Try scheduled matches first
        try:
            with open(os.path.join(data_dir, 'matches_scheduled.json'), 'r') as f:
                data = json.load(f)
        except:
            # Fallback to all matches
            try:
                with open(os.path.join(data_dir, 'matches_all.json'), 'r') as f:
                    data = json.load(f)
            except:
                # Ultimate fallback
                data = {'matches': []}
        
        # Stadium info
        stadium = "Allianz Parque"
        
        # Where to watch
        tv_channels = "Transmissão: A confirmar"
        
        ical_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Palmeiras//VerdaoTracker//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Palmeiras - Jogos do Verdão",
            "X-WR-TIMEZONE:America/Sao_Paulo",
        ]
        
        for match in data.get('matches', []):
            utc_date = match.get('utcDate', '')
            if not utc_date:
                continue
                
            # Parse ISO date and create iCal format
            # Format: 2026-03-15T20:00:00Z -> 20260315T200000Z
            dt_start = utc_date.replace('-', '').replace(':', '').replace('Z', 'Z')
            if dt_start.endswith('Z'):
                dt_start = dt_start[:-1] + 'Z'
            
            # Calculate end time (2 hours later for match duration)
            from datetime import datetime, timedelta
            try:
                start_dt = datetime.strptime(utc_date.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
                end_dt = start_dt + timedelta(hours=2)
                dt_end = end_dt.strftime('%Y%m%dT%H%M%S') + 'Z'
            except:
                dt_end = dt_start  # Fallback
            
            home = match.get('homeTeam', {}).get('name', 'Home')
            away = match.get('awayTeam', {}).get('name', 'Away')
            competition = match.get('competition', {}).get('name', 'Football')
            status = match.get('status', 'SCHEDULED')
            
            # Determine location (home games at Allianz Parque)
            location = stadium if "Palmeiras" in home or "SE Palmeiras" in home else "Estádio a definir"
            
            uid = f"{match.get('id')}@palmeiras.vercel.app"
            summary = f"🏆 {home} vs {away}"
            if status == 'FINISHED':
                score = match.get('score', {})
                full_time = score.get('fullTime', {})
                home_goals = full_time.get('home') or 0
                away_goals = full_time.get('away') or 0
                summary = f"🏆 {home} {home_goals} x {away_goals} {away}"
            
            description = f"{competition}\\nStatus: {status}\\n\\n📍 {location}\\n📺 {tv_channels}"
            
            ical_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART:{dt_start}",
                f"DTEND:{dt_end}",
                f"LOCATION:{location}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{description}",
                "END:VEVENT"
            ])
        
        ical_lines.append("END:VCALENDAR")
        
        return Response('\n'.join(ical_lines), mimetype='text/calendar')
    except Exception as e:
        return Response(f"Error generating calendar: {str(e)}", status=500)


if __name__ == '__main__':
    print("🏆 Starting Palmeiras Dashboard...")
    app.run(host='0.0.0.0', port=5001, debug=True)
