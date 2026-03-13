"""
Palmeiras Web Dashboard - Flask Server
Proxies API calls to football-data.org to avoid CORS issues
"""
import os
import requests
from flask import Flask, jsonify, request, send_from_directory

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
