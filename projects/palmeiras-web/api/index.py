"""
Palmeiras Web Dashboard - Vercel API Handler
"""
import os
import json
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'
HEADERS = {'X-Auth-Token': API_KEY}

app = Flask(__name__)


@app.route('/api/teams/<int:team_id>/matches')
def matches(team_id):
    status = request.args.get('status', 'SCHEDULED')
    limit = request.args.get('limit', '10')
    
    url = f"{API_BASE}/teams/{team_id}/matches"
    params = {'status': status, 'limit': limit}
    
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/competitions/<comp>/standings')
def standings(comp):
    try:
        url = f"{API_BASE}/competitions/{comp}/standings"
        r = requests.get(url, headers=HEADERS, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/news')
def news():
    articles = []
    try:
        r = requests.get('https://ge.globo.com/futebol/times/palmeiras/', 
                       headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.feed-post-item')[:8]:
            link = item.select_one('.feed-post-link')
            if link:
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    articles.append({
                        'title': title[:150],
                        'url': link.get('href', ''),
                        'source': 'ge.globo'
                    })
    except:
        pass
    return jsonify({'articles': articles})


def handler(event, context):
    return app(event, context)
