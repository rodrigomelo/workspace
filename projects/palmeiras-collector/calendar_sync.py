"""
Palmeiras Calendar Sync
Syncs Palmeiras matches to Google Calendar.
"""

import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from pathlib import Path

# Load config
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

API_KEY = os.environ.get("FOOTBALL_API_KEY", "")
TEAM_ID = 1769  # Palmeiras
CALENDAR_ID = "primary"  # or custom calendar

BR_TZ = ZoneInfo("America/Sao_Paulo")


def get_matches(status="SCHEDULED", limit=10):
    """Fetch matches from football-data.org."""
    if not API_KEY:
        print("❌ FOOTBALL_API_KEY not set")
        return []
    
    url = f"https://api.football-data.org/v4/teams/{TEAM_ID}/matches"
    params = {"status": status, "limit": limit}
    headers = {"X-Auth-Token": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("matches", [])
    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
        return []


def format_match_event(match):
    """Format match data for calendar event."""
    home = match.get("homeTeam", {}).get("name", "Unknown")
    away = match.get("awayTeam", {}).get("name", "Unknown")
    competition = match.get("competition", {}).get("name", "Match")
    utc_date = match.get("utcDate", "")
    
    # Parse date
    dt_utc = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
    dt_br = dt_utc.astimezone(BR_TZ)
    
    # Determine opponent
    opponent = away if home == "Palmeiras" else home
    is_home = home == "Palmeiras"
    
    # Title
    title = f"🏆 Palmeiras vs {opponent}"
    if not is_home:
        title = f"🏆 {opponent} vs Palmeiras"
    
    # Description
    description = f"""
{competition}

{'🏠 Allianz Parque' if is_home else '⛽ Jogo fora'}

#Palmeiras #Verdao
""".strip()
    
    # Location
    location = "Allianz Parque, São Paulo" if is_home else "Estádio do adversário"
    
    # Start and end times (match is ~2 hours)
    start_iso = dt_br.isoformat()
    end_dt = dt_br + timedelta(hours=2)
    end_iso = end_dt.isoformat()
    
    return {
        "summary": title,
        "description": description,
        "location": location,
        "start": start_iso,
        "end": end_iso,
        "home": is_home,
    }


def create_calendar_event(event_data):
    """Create event using gog CLI."""
    import subprocess
    
    title = event_data["summary"]
    start = event_data["start"]
    end = event_data["end"]
    location = event_data["location"]
    description = event_data["description"]
    
    # gog calendar create command
    cmd = [
        "gog", "calendar", "create", CALENDAR_ID,
        "--summary", title,
        "--from", start,
        "--to", end,
        "--location", location,
        "--description", description,
    ]
    
    # Color: green for home (7), yellow for away (5)
    if event_data["home"]:
        cmd.extend(["--event-color", "7"])
    else:
        cmd.extend(["--event-color", "5"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created: {title}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def list_existing_events():
    """List existing Palmeiras events."""
    import subprocess
    from datetime import datetime, timedelta
    
    # Get events for next 30 days
    now = datetime.now(BR_TZ)
    future = now + timedelta(days=30)
    
    cmd = [
        "gog", "calendar", "events", CALENDAR_ID,
        "--from", now.isoformat(),
        "--to", future.isoformat(),
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            return [l for l in lines if "Palmeiras" in l]
    except:
        pass
    return []


def main():
    print("🏆 Palmeiras Calendar Sync")
    print("=" * 40)
    
    # Get upcoming matches
    print("\n📡 Fetching upcoming matches...")
    matches = get_matches("SCHEDULED", limit=10)
    
    if not matches:
        print("❌ No matches found")
        return
    
    print(f"✅ Found {len(matches)} upcoming matches")
    
    # Check existing events
    print("\n📅 Checking existing events...")
    existing = list_existing_events()
    print(f"📋 {len(existing)} existing Palmeiras events in calendar")
    
    # Create events
    print("\n🎫 Creating calendar events...")
    created = 0
    for match in matches:
        event = format_match_event(match)
        if create_calendar_event(event):
            created += 1
    
    print(f"\n✅ Done! Created {created} calendar events")


if __name__ == "__main__":
    main()
