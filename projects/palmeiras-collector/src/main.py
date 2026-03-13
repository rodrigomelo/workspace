"""
Palmeiras Data Collector - Main Script
Fetches the next Palmeiras match and sends notification to Discord.
"""

import os
import requests
from datetime import datetime
from src.config import API_KEY, WEBHOOK_URL, TEAM_ID


def get_next_match():
    """Fetch the next scheduled match for Palmeiras."""
    url = f"https://api.football-data.org/v4/teams/{TEAM_ID}/matches"
    params = {"status": "SCHEDULED"}
    headers = {"X-Auth-Token": API_KEY}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    matches = data.get("matches", [])
    
    if not matches:
        return None
    
    # Return the next match (first scheduled)
    return matches[0]


def format_match_notification(match):
    """Format match data for Discord webhook."""
    competition = match.get("competition", {}).get("name", "Unknown")
    home_team = match.get("homeTeam", {}).get("name", "Unknown")
    away_team = match.get("awayTeam", {}).get("name", "Unknown")
    utc_date = match.get("utcDate", "")
    
    # Parse and format date
    dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
    match_time = dt.strftime("%d/%m/%Y às %H:%M")
    
    # Determine opponent
    opponent = away_team if home_team == "Palmeiras" else home_team
    is_home = home_team == "Palmeiras"
    venue = "em casa" if is_home else "fora"
    
    embed = {
        "title": "⚽ Próximo Jogo do Palmeiras",
        "description": f"**{competition}**",
        "color": 0x0D7A3D,  # Palmeiras green
        "fields": [
            {
                "name": "🗓️ Data",
                "value": match_time,
                "inline": True
            },
            {
                "name": "📍 Local",
                "value": venue,
                "inline": True
            },
            {
                "name": "👥 Adversário",
                "value": opponent,
                "inline": False
            }
        ],
        "footer": {
            "text": "VerdaoTracker • Dados via football-data.org"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return embed


def send_discord_notification(embed):
    """Send notification to Discord webhook."""
    payload = {"embeds": [embed]}
    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()
    return response.status_code == 204 or response.status_code == 200


def main():
    """Main execution flow."""
    print("🔍 VerdaoTracker - Buscando próximo jogo...")
    
    try:
        match = get_next_match()
        
        if not match:
            print("ℹ️ Nenhum jogo agendado encontrado.")
            return
        
        print(f"✅ Jogo encontrado: {match.get('homeTeam', {}).get('name')} x {match.get('awayTeam', {}).get('name')}")
        
        # Only send to Discord if WEBHOOK_URL is set
        if WEBHOOK_URL and WEBHOOK_URL != "YOUR_DISCORD_WEBHOOK_URL":
            embed = format_match_notification(match)
            send_discord_notification(embed)
            print("✅ Notificação enviada para Discord!")
        else:
            print("ℹ️ WEBHOOK_URL não configurado - pulando envio para Discord")
            print(f"📋 Embed que seria enviado: {format_match_notification(match)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        raise
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise


if __name__ == "__main__":
    main()
