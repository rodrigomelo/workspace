"""
Palmeiras Web Dashboard - Flask Server
"""
import os
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
_CACHE_TTL = 300  # 5 minutes


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
        # Return cached data if available, even if expired
        if cache_key in _cache:
            data, _ = _cache[cache_key]
            return data
        raise e


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/teams/<int:team_id>/matches')
def team_matches(team_id):
    status = request.args.get('status', 'SCHEDULED')
    limit = request.args.get('limit', '10')
    
    url = f"{API_BASE}/teams/{team_id}/matches"
    params = {'status': status}
    if limit:
        params['limit'] = limit
    
    try:
        response = requests.get(url, headers=API_HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/competitions/<competition>/standings')
def standings(competition):
    try:
        url = f"{API_BASE}/competitions/{competition}/standings"
        response = requests.get(url, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/news')
def palmeiras_news():
    all_news = []
    
    try:
        url = 'https://ge.globo.com/futebol/times/palmeiras/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.feed-post-item')[:8]:
            link = item.select_one('.feed-post-link')
            if link:
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    all_news.append({
                        'title': title[:150],
                        'url': link.get('href', ''),
                        'source': 'ge.globo'
                    })
    except Exception as e:
        pass
    
    return jsonify({'articles': all_news})


@app.route('/api/calendar.ics')
def calendar_ics():
    """Generate iCal feed for Palmeiras matches"""
    try:
        # Fetch matches with caching (5 min TTL)
        url = f"{API_BASE}/teams/{TEAM_ID}/matches"
        params = {'limit': 50}
        
        data = get_cached(url, params)
        
        # Stadium info
        stadium = "Allianz Parque"
        stadium_address = "Rua Palestra Itália, 200 - Água Branca, São Paulo, SP"
        
        # Where to watch
        tv_channels = "TV: Globo, SporTV, Premiere | Streaming: Amazon Prime Video, Globoplay"
        
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
            dt = utc_date.replace('-', '').replace(':', '').replace('Z', 'Z')
            if dt.endswith('Z'):
                dt = dt[:-1] + 'Z'
            
            home = match.get('homeTeam', {}).get('name', 'Home')
            away = match.get('awayTeam', {}).get('name', 'Away')
            competition = match.get('competition', {}).get('name', 'Football')
            status = match.get('status', 'SCHEDULED')
            
            # Determine location (home games at Allianz Parque)
            location = stadium_address if "Palmeiras" in home or "SE Palmeiras" in home else "Estádio a definir"
            
            uid = f"{match.get('id')}@palmeiras.vercel.app"
            summary = f"🏆 {home} vs {away}"
            if status == 'FINISHED':
                score = match.get('score', {})
                full_time = score.get('fullTime', {})
                home_goals = full_time.get('home') or 0
                away_goals = full_time.get('away') or 0
                summary = f"🏆 {home} {home_goals} x {away_goals} {away}"
            
            description = f"{competition}\\nStatus: {status}\\n\\n📍 {location}\\n\\n📺 {tv_channels}"
            
            ical_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART:{dt}",
                f"DTEND:{dt}",
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
