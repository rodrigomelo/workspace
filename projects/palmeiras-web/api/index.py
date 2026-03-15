import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def read_json(filename):
    """Read data from local JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {'error': str(e), 'data': []}


def teams_matches(request):
    """GET /api/teams/1769/matches"""
    status = request.args.get('status', 'SCHEDULED')
    limit = request.args.get('limit', '10')
    
    if status == 'SCHEDULED':
        data = read_json('matches_scheduled.json')
    else:
        data = read_json('matches_finished.json')
    
    # Filter by limit if needed
    if 'matches' in data and limit:
        data['matches'] = data['matches'][:int(limit)]
    
    return data, 200


def competitions(request):
    """GET /api/competitions/BSA/standings"""
    data = read_json('standings.json')
    return data, 200


def news(request):
    """GET /api/news - still uses external API for news"""
    import requests as req
    articles = []
    try:
        r = req.get('https://ge.globo.com/futebol/times/palmeiras/', 
                    headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
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
    return {'articles': articles}, 200


def handler(request):
    """Main Vercel handler."""
    path = request.path
    
    if '/teams/' in path and '/matches' in path:
        return teams_matches(request)
    elif '/competitions/' in path and '/standings' in path:
        return competitions(request)
    elif path == '/api/news':
        return news(request)
    
    return {'error': 'Not found'}, 404
