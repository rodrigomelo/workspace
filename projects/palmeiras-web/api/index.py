"""
Palmeiras API - Vercel Serverless
"""
import os
import json
import requests

API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
HEADERS = {'X-Auth-Token': API_KEY}


def teams_matches(request):
    """GET /api/teams/1769/matches?status=SCHEDULED&limit=5"""
    team_id = 1769
    status = request.args.get('status', 'SCHEDULED')
    limit = request.args.get('limit', '10')
    
    url = f"https://api.football-data.org/v4/teams/{team_id}/matches"
    params = {'status': status, 'limit': limit}
    
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {'error': str(e)}, 500


def competitions(request):
    """GET /api/competitions/BSA/standings"""
    path = request.path
    import re
    m = re.search(r'/competitions/(\w+)', path)
    comp = m.group(1) if m else 'BSA'
    
    url = f"https://api.football-data.org/v4/competitions/{comp}/standings"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {'error': str(e)}, 500


def news(request):
    """GET /api/news"""
    articles = []
    try:
        r = requests.get(
            'https://ge.globo.com/futebol/times/palmeiras/',
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        from bs4 import BeautifulSoup
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
    return {'articles': articles}


def handler(request):
    """Main Vercel handler"""
    path = request.path
    
    if '/teams/' in path and '/matches' in path:
        return teams_matches(request)
    elif '/competitions/' in path and '/standings' in path:
        return competitions(request)
    elif path == '/api/news':
        return news(request)
    
    return {'error': 'Not found'}, 404
