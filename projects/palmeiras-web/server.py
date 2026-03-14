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


if __name__ == '__main__':
    print("🏆 Starting Palmeiras Dashboard Server...")
    print("   Open http://localhost:5001 in your browser")
    app.run(host='0.0.0.0', port=5001, debug=True)


@app.route('/api/news')
def palmeiras_news():
    """Scrape news from ge.globo about Palmeiras"""
    try:
        url = 'https://ge.globo.com/futebol/times/palmeiras/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        
        # Try multiple selectors for ge.globo news
        # Main featured article
        featured = soup.select_one('.feed-post-link, .bastian-feed-item .feed-post-link, article a')
        if featured:
            title = featured.get_text(strip=True)
            link = featured.get('href', '')
            if title and link:
                news_items.append({
                    'title': title[:200],
                    'url': link,
                    'type': 'featured'
                })
        
        # Feed post items
        for item in soup.select('.feed-post-item, .bastian-feed-item, .post-item, article'):
            link_elem = item.select_one('.feed-post-link, .feed-post-body a, a')
            if link_elem:
                title = link_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                if title and len(title) > 10 and link and link not in [n['url'] for n in news_items]:
                    news_items.append({
                        'title': title[:200],
                        'url': link,
                        'type': 'article'
                    })
            if len(news_items) >= 10:
                break
        
        # If no news found via parsing, try JSON-LD
        if len(news_items) == 0:
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    if data.get('@type') == 'NewsArticle' or 'article' in str(data).lower():
                        news_items.append({
                            'title': data.get('headline', '')[:200],
                            'url': data.get('url', ''),
                            'type': 'json-ld'
                        })
                except:
                    pass
        
        return jsonify({
            'success': True,
            'source': 'ge.globo.com',
            'articles': news_items[:10]
        })
        
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'articles': []
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'articles': []
        }), 500
