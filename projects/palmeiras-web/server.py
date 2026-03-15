"""
Palmeiras Web Dashboard - Vercel Server (Pure Python)
"""
import os
import json
import requests
from urllib.parse import urlparse, parse_qs

# Football Data API configuration
API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'

API_HEADERS = {
    'X-Auth-Token': API_KEY
}


def handler(request):
    """Vercel Python handler - receives a request object"""
    path = request.url.path
    query = request.url.query
    
    # Parse query params
    params = {}
    if query:
        for key, value in parse_qs(query).items():
            params[key] = value[0] if len(value) == 1 else value
    
    # Root - serve index.html
    if path == '/' or path == '':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': open('index.html').read()
        }
    
    # API: /api/teams/{id}/matches
    if path.startswith('/api/teams/') and '/matches' in path:
        import re
        match = re.match(r'/api/teams/(\d+)/matches', path)
        if match:
            team_id = match.group(1)
            status = params.get('status', 'SCHEDULED')
            limit = params.get('limit', '10')
            
            url = f"{API_BASE}/teams/{team_id}/matches"
            req_params = {'status': status}
            if limit:
                req_params['limit'] = limit
            
            try:
                response = requests.get(url, headers=API_HEADERS, params=req_params, timeout=10)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                data = {'error': str(e)}
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(data)
            }
    
    # API: /api/competitions/{comp}/standings
    if path.startswith('/api/competitions/') and '/standings' in path:
        import re
        match = re.match(r'/api/competitions/(\w+)/standings', path)
        if match:
            comp = match.group(1)
            url = f"{API_BASE}/competitions/{comp}/standings"
            
            try:
                response = requests.get(url, headers=API_HEADERS, timeout=10)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                data = {'error': str(e)}
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(data)
            }
    
    # API: /api/news
    if path == '/api/news':
        return handle_news()
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'})
    }


def handle_news():
    """Scrape news from ge.globo"""
    try:
        url = 'https://ge.globo.com/futebol/times/palmeiras/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        for item in soup.select('.feed-post-item')[:10]:
            link = item.select_one('.feed-post-link')
            if link:
                news_items.append({
                    'title': link.get_text(strip=True)[:200],
                    'url': link.get('href', ''),
                    'source': 'ge.globo'
                })
        
        data = {'articles': news_items}
    except Exception as e:
        data = {'articles': [], 'error': str(e)}
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(data)
    }
