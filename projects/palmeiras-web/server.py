"""
Palmeiras Web Dashboard - Flask Server
"""
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
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


if __name__ == '__main__':
    print("🏆 Starting Palmeiras Dashboard...")
    app.run(host='0.0.0.0', port=5001, debug=True)
