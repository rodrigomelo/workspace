"""
Palmeiras Web Dashboard - Flask Server
"""
import os
import requests
from flask import Flask, jsonify, request, send_from_directory, Response
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.')

API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'

API_HEADERS = {'X-Auth-Token': API_KEY}


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
        # Fetch both scheduled and finished matches
        url = f"{API_BASE}/teams/{TEAM_ID}/matches"
        params = {'limit': 50}
        
        response = requests.get(url, headers=API_HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
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
            
            uid = f"{match.get('id')}@palmeiras.vercel.app"
            summary = f"🏆 {home} vs {away}"
            if status == 'FINISHED':
                score = match.get('score', {})
                full_time = score.get('fullTime', {})
                home_goals = full_time.get('home') or 0
                away_goals = full_time.get('away') or 0
                summary = f"🏆 {home} {home_goals} x {away_goals} {away}"
            
            description = f"{competition}\\nStatus: {status}"
            
            ical_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART:{dt}",
                f"DTEND:{dt}",
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
