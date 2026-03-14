"""
Palmeiras Web Dashboard - Flask Server
Proxies API calls to football-data.org to avoid CORS issues
"""
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.')

# Football Data API configuration
API_KEY = 'eca8b30bb5c34fcfa80ec28ceedf84a0'
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'

# Headers for API requests (hidden from browser)
API_HEADERS = {
    'X-Auth-Token': API_KEY
}


@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')


@app.route('/api/teams/<int:team_id>/matches')
def team_matches(team_id):
    """Proxy endpoint for team matches"""
    status = request.args.get('status', 'SCHEDULED')
    limit = request.args.get('limit', '10')
    
    try:
        url = f"{API_BASE}/teams/{team_id}/matches"
        params = {
            'status': status,
        }
        if limit:
            params['limit'] = limit
        
        response = requests.get(url, headers=API_HEADERS, params=params)
        response.raise_for_status()
        
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/competitions/<competition>/standings')
def standings(competition):
    """Proxy endpoint for competition standings"""
    try:
        url = f"{API_BASE}/competitions/{competition}/standings"
        
        response = requests.get(url, headers=API_HEADERS)
        response.raise_for_status()
        
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/news')
def palmeiras_news():
    """Fetch news from multiple sources"""
    all_news = []
    
    # Source 1: ge.globo
    try:
        url = 'https://ge.globo.com/futebol/times/palmeiras/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.feed-post-item, article, .bastian-feed-item')[:5]:
            link = item.select_one('.feed-post-link, a')
            if link and link.get('href'):
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    all_news.append({
                        'title': title[:150],
                        'url': link.get('href'),
                        'source': 'ge.globo'
                    })
    except Exception as e:
        print(f"ge.globo error: {e}")
    
    # Source 2: Lance! (try RSS or fallback)
    try:
        # Try Lance! search
        url = 'https://www.lance.com.br/palmeiras/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.article-item, .news-item, article')[:5]:
            link = item.select_one('a')
            if link:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                if title and len(title) > 10 and href:
                    all_news.append({
                        'title': title[:150],
                        'url': href if href.startswith('http') else 'https://www.lance.com.br' + href,
                        'source': 'Lance!'
                    })
    except Exception as e:
        print(f"Lance! error: {e}")
    
    # Source 3: Terra
    try:
        url = 'https://www.terra.com.br/esporte/futebol/palmeiras/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.card, .news-item, article')[:5]:
            link = item.select_one('a')
            if link:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                if title and len(title) > 10 and href:
                    all_news.append({
                        'title': title[:150],
                        'url': href if href.startswith('http') else 'https://www.terra.com.br' + href,
                        'source': 'Terra'
                    })
    except Exception as e:
        print(f"Terra error: {e}")
    
    # Remove duplicates
    seen = set()
    unique_news = []
    for n in all_news:
        key = n['title'][:50].lower()
        if key not in seen:
            seen.add(key)
            unique_news.append(n)
    
    return jsonify({
        'success': True,
        'sources': ['ge.globo', 'Lance!', 'Terra'],
        'articles': unique_news[:15]
    })


if __name__ == '__main__':
    print("🏆 Starting Palmeiras Dashboard Server...")
    print("   Open http://localhost:5001 in your browser")
    app.run(host='0.0.0.0', port=5001, debug=True)
