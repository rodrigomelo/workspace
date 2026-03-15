#!/usr/bin/env python3
"""
Palmeiras News Fetcher
Fetches news from ge.globo and saves to JSON file for the frontend to consume.
Run this on a cron job (e.g., every 30 minutes).
"""
import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_news():
    """Fetch news from ge.globo and return list of articles."""
    articles = []
    try:
        url = 'https://ge.globo.com/futebol/times/palmeiras/'
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            },
            timeout=30
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors for different page layouts
        items = soup.select('.feed-post-item')
        if not items:
            items = soup.select('.bastian-feed-item')
        if not items:
            items = soup.select('article')
        
        for item in items[:10]:
            # Try multiple selectors for title and link
            link = (
                item.select_one('.feed-post-link') or
                item.select_one('.bastian-feed-item-link') or
                item.select_one('a') or
                item.select_one('h2 a') or
                item.select_one('h3 a')
            )
            
            if link:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                if title and len(title) > 10 and href and 'ge.globo.com' in href:
                    # Clean up title
                    title = title[:200].strip()
                    articles.append({
                        'title': title,
                        'url': href,
                        'source': 'ge.globo',
                        'fetched_at': datetime.now().isoformat()
                    })
        
        print(f"✅ Fetched {len(articles)} news articles from ge.globo")
        
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
    
    return articles


def main():
    print(f"📰 Palmeiras News Fetcher - {datetime.now()}")
    
    articles = fetch_news()
    
    if articles:
        filepath = os.path.join(DATA_DIR, 'news.json')
        with open(filepath, 'w') as f:
            json.dump({'articles': articles, 'updated_at': datetime.now().isoformat()}, f, indent=2)
        print(f"✅ Saved: news.json ({len(articles)} articles)")
    else:
        print("⚠️ No articles fetched, keeping existing news.json if available")
        # Still write empty to indicate attempted fetch
        filepath = os.path.join(DATA_DIR, 'news.json')
        with open(filepath, 'w') as f:
            json.dump({'articles': [], 'updated_at': datetime.now().isoformat(), 'error': 'fetch_failed'}, f, indent=2)
    
    print("🎉 News fetch complete!")


if __name__ == '__main__':
    main()
