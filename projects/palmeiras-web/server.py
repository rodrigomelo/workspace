"""
Palmeiras Web Dashboard - Vercel Server
Proxies API calls to football-data.org to avoid CORS issues
"""
import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Football Data API configuration
API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'

API_HEADERS = {
    'X-Auth-Token': API_KEY
}


class handler(BaseHTTPRequestHandler):
    """Vercel Python handler"""
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Root - serve index.html
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                with open('index.html', 'r') as f:
                    self.wfile.write(f.read().encode())
            except:
                self.wfile.write(b'<html><body><h1>Palmeiras Dashboard</h1></body></html>')
            return
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api(path, query)
            return
        
        # Static files
        if path.endswith('.html') or path.endswith('.js') or path.endswith('.css'):
            self.send_response(200)
            if path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            else:
                self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                with open(path.lstrip('/'), 'r') as f:
                    self.wfile.write(f.read().encode())
            except:
                self.wfile.write(b'Not found')
            return
        
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not found')
    
    def handle_api(self, path, query):
        """Handle API proxy requests"""
        
        # /api/teams/{id}/matches
        if '/teams/' in path and '/matches' in path:
            import re
            match = re.match(r'/api/teams/(\d+)/matches', path)
            if match:
                team_id = match.group(1)
                status = query.get('status', ['SCHEDULED'])[0]
                limit = query.get('limit', ['10'])[0]
                
                url = f"{API_BASE}/teams/{team_id}/matches"
                params = {'status': status}
                if limit:
                    params['limit'] = limit
                
                try:
                    response = requests.get(url, headers=API_HEADERS, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                except Exception as e:
                    data = {'error': str(e)}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                return
        
        # /api/competitions/{comp}/standings
        if '/competitions/' in path and '/standings' in path:
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
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                return
        
        # /api/news
        if path == '/api/news':
            self.handle_news()
            return
        
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def handle_news(self):
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
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logging
