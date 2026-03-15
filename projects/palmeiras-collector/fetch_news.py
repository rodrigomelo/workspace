#!/usr/bin/env python3
"""
Palmeiras News Collector
Fetches news from ge.globo and saves to local JSON for the dashboard.
This replaces the real-time scraping with pre-collected data.

Usage:
    python fetch_news.py [--limit N]

Cron setup (every 15 minutes):
    */15 * * * * cd ~/workspace/projects/palmeiras-collector && source venv/bin/activate && python fetch_news.py >> news.log 2>&1
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configuration
DATA_DIR = Path(__file__).parent / "data"
NEWS_FILE = DATA_DIR / "news.json"
BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")

# ge.globo URL for Palmeiras news
GE_GLOBO_URL = "https://ge.globo.com/futebol/times/palmeiras/"

# User agent to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(exist_ok=True)


def fetch_ge_globo_news(limit: int = 10) -> list:
    """Fetch news from ge.globo."""
    print(f"  Fetching from {GE_GLOBO_URL}...")
    
    try:
        response = requests.get(GE_GLOBO_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ❌ Error fetching ge.globo: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []
    
    # Find news articles - ge.globo uses various selectors
    articles = soup.select("div.feed-post-body") or soup.select("article") or soup.select(".bastian-feed-item")
    
    for article in articles[:limit]:
        try:
            # Try different selectors for title and link
            title_elem = (
                article.select_one("a.feed-post-link") or 
                article.select_one("h2") or
                article.select_one("h3") or
                article.select_one("a")
            )
            
            link_elem = (
                article.select_one("a.feed-post-link") or
                article.select_one("a")
            )
            
            # Try to get image
            img_elem = article.select_one("img")
            
            # Try to get summary/description
            summary_elem = (
                article.select_one("p") or
                article.select_one(".feed-post-body-resumo")
            )
            
            title = title_elem.get_text(strip=True) if title_elem else ""
            link = link_elem.get("href", "") if link_elem else ""
            image = img_elem.get("src", "") or img_elem.get("data-src", "") if img_elem else ""
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            if title and link:
                news_items.append({
                    "title": title,
                    "link": link,
                    "image": image,
                    "summary": summary[:200] if summary else "",  # Limit summary length
                    "source": "ge.globo",
                    "collected_at": datetime.now(BRAZIL_TZ).isoformat()
                })
                
        except Exception as e:
            print(f"  ⚠️ Error parsing article: {e}")
            continue
    
    print(f"  ✅ Found {len(news_items)} articles")
    return news_items


def fetch_lance_news(limit: int = 5) -> list:
    """Fetch news from Lance!."""
    print(f"  Fetching from lance.com.br...")
    
    LANCE_URL = "https://www.lance.com.br/palmeiras/"
    
    try:
        response = requests.get(LANCE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠️ Error fetching lance.com.br: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []
    
    articles = soup.select("article") or soup.select(".article-item")
    
    for article in articles[:limit]:
        try:
            title_elem = article.select_one("h2") or article.select_one("h3") or article.select_one("a")
            link_elem = article.select_one("a")
            img_elem = article.select_one("img")
            
            title = title_elem.get_text(strip=True) if title_elem else ""
            link = link_elem.get("href", "") if link_elem else ""
            if link and not link.startswith("http"):
                link = "https://www.lance.com.br" + link
            
            image = img_elem.get("src", "") or img_elem.get("data-src", "") if img_elem else ""
            
            if title and link:
                news_items.append({
                    "title": title,
                    "link": link,
                    "image": image,
                    "summary": "",
                    "source": "Lance!",
                    "collected_at": datetime.now(BRAZIL_TZ).isoformat()
                })
                
        except Exception as e:
            continue
    
    print(f"  ✅ Found {len(news_items)} articles from Lance!")
    return news_items


def save_news(news: list) -> None:
    """Save news to JSON file."""
    ensure_data_dir()
    
    data = {
        "news": news,
        "last_updated": datetime.now(BRAZIL_TZ).isoformat(),
        "sources": ["ge.globo", "lance.com.br"]
    }
    
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 Saved to {NEWS_FILE}")


def load_news() -> dict:
    """Load existing news from JSON file."""
    if NEWS_FILE.exists():
        try:
            with open(NEWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠️ Error loading existing news: {e}")
    
    return {"news": [], "last_updated": None}


def main():
    parser = argparse.ArgumentParser(description="Palmeiras News Collector")
    parser.add_argument("--limit", type=int, default=10, help="Number of news to fetch per source")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected without saving")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print(" 🗞️ Palmeiras News Collector")
    print("=" * 50)
    
    all_news = []
    
    # Fetch from ge.globo
    print("\n📡 Fetching news from sources...")
    ge_news = fetch_ge_globo_news(args.limit)
    all_news.extend(ge_news)
    
    # Fetch from Lance!
    lance_news = fetch_lance_news(args.limit)
    all_news.extend(lance_news)
    
    if not all_news:
        print("\n❌ No news collected!")
        
        # Check if we have old data
        existing = load_news()
        if existing.get("news"):
            print(f"  📋 Using existing data from {existing.get('last_updated')}")
            return
        
        sys.exit(1)
    
    # Remove duplicates based on title
    seen = set()
    unique_news = []
    for item in all_news:
        title_key = item["title"].lower().strip()
        if title_key not in seen:
            seen.add(title_key)
            unique_news.append(item)
    
    print(f"\n📊 Total unique articles: {len(unique_news)}")
    
    if args.dry_run:
        print("\n[DRY RUN - Not saving]")
        for item in unique_news[:5]:
            print(f"  - {item['title'][:60]}...")
        return
    
    # Save to file
    save_news(unique_news)
    
    print("\n✅ News collection complete!")
    print(f"   File: {NEWS_FILE}")
    print(f"   Articles: {len(unique_news)}")


if __name__ == "__main__":
    main()
