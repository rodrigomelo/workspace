#!/usr/bin/env python3
"""
Palmeiras Data Fetcher
Fetches data from API and saves to JSON files for the frontend to consume.
Run this on a cron job (e.g., every 30 minutes).
"""
import os
import json
import requests
from datetime import datetime

API_KEY = os.environ.get('FOOTBALL_API_KEY', 'eca8b30bb5c34fcfa80ec28ceedf84a0')
TEAM_ID = 1769
API_BASE = 'https://api.football-data.org/v4'
HEADERS = {'X-Auth-Token': API_KEY}

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_and_save(endpoint, filename):
    """Fetch data from API and save to JSON file."""
    url = f"{API_BASE}/{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Saved: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return False


def main():
    print(f"🏆 Palmeiras Data Fetcher - {datetime.now()}")
    
    # Fetch all data
    fetch_and_save(f'teams/{TEAM_ID}/matches?status=SCHEDULED&limit=10', 'matches_scheduled.json')
    fetch_and_save(f'teams/{TEAM_ID}/matches?status=FINISHED&limit=10', 'matches_finished.json')
    fetch_and_save('competitions/BSA/standings', 'standings.json')
    
    print("🎉 Data fetch complete!")


if __name__ == '__main__':
    main()
