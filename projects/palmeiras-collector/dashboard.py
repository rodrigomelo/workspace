"""
Palmeiras Dashboard - Web Interface
Simple Flask app to display Palmeiras data.
"""

from flask import Flask, render_template_string, jsonify
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from pathlib import Path

# Load config
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from src.config import API_KEY, TEAM_ID

app = Flask(__name__)

TEAM_ID = 102  # Palmeiras


def get_matches(status="SCHEDULED"):
    """Fetch matches from football-data.org."""
    if not API_KEY:
        return []
        
    url = f"https://api.football-data.org/v4/teams/{TEAM_ID}/matches"
    params = {"status": status}
    headers = {"X-Auth-Token": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("matches", [])[:10]  # Limit to 10
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []


def get_standings():
    """Fetch Serie A standings."""
    url = "https://api.football-data.org/v4/competitions/BSA/standings"
    headers = {"X-Auth-Token": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Find Palmeiras position
        for table in data.get("standings", []):
            if table.get("type") == "TOTAL":
                for entry in table.get("table", []):
                    if entry.get("team", {}).get("id") == TEAM_ID:
                        return {
                            "position": entry.get("position"),
                            "played": entry.get("playedGames"),
                            "won": entry.get("won"),
                            "drawn": entry.get("drawn"),
                            "lost": entry.get("lost"),
                            "points": entry.get("points"),
                            "goalsFor": entry.get("goalsFor"),
                            "goalsAgainst": entry.get("goalsAgainst"),
                        }
        return None
    except Exception as e:
        print(f"Error fetching standings: {e}")
        return None


def format_match(match, is_next=True):
    """Format match for display."""
    home = match.get("homeTeam", {}).get("name", "Unknown")
    away = match.get("awayTeam", {}).get("name", "Unknown")
    competition = match.get("competition", {}).get("name", "Unknown")
    utc_date = match.get("utcDate", "")
    
    # Convert to Brazil timezone
    dt_utc = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
    dt_br = dt_utc.astimezone(ZoneInfo("America/Sao_Paulo"))
    
    if is_next:
        match_time = dt_br.strftime("%d/%m às %H:%M")
    else:
        score = f"{match.get('score', {}).get('fullTime', {}).get('home', '-')} x {match.get('score', {}).get('fullTime', {}).get('away', '-')}"
        match_time = f"{dt_br.strftime('%d/%m')} - {score}"
    
    return {
        "home": home,
        "away": away,
        "competition": competition,
        "time": match_time,
        "is_home": home == "Palmeiras",
    }


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏆 Palmeiras Dashboard</title>
    <style>
        :root {
            --palmeiras-green: #0D7A3D;
            --palmeiras-dark: #054D26;
            --bg: #1a1a1a;
            --card-bg: #2d2d2d;
            --text: #ffffff;
            --text-muted: #a0a0a0;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, var(--palmeiras-green), var(--palmeiras-dark));
            padding: 30px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header .shield {
            font-size: 4rem;
            margin-bottom: 10px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h2 {
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--palmeiras-green);
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card.next {
            border-left: 4px solid var(--palmeiras-green);
        }
        
        .team {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .team.home { text-align: left; }
        .team.away { text-align: right; }
        
        .vs {
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        .match-info {
            text-align: center;
        }
        
        .match-time {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--palmeiras-green);
        }
        
        .competition {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 5px;
        }
        
        .standings-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            text-align: center;
        }
        
        .stat-box {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--palmeiras-green);
        }
        
        .stat-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 5px;
        }
        
        .position-badge {
            background: var(--palmeiras-green);
            color: white;
            padding: 15px 30px;
            border-radius: 50%;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .error {
            background: #3d2d2d;
            border: 1px solid #ff4444;
            border-radius: 8px;
            padding: 15px;
            color: #ff6666;
        }
        
        .last-updated {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="shield">🏆</div>
        <h1>Palmeiras</h1>
        <p>Dashboard Verde-Amarelo</p>
    </div>
    
    <div class="container">
        <!-- Next Match -->
        <div class="section">
            <h2>📅 Próximo Jogo</h2>
            {% if next_matches %}
                {% for match in next_matches %}
                <div class="card next">
                    <div class="team home">{{ match.home }}</div>
                    <div class="match-info">
                        <div class="match-time">vs</div>
                        <div class="competition">{{ match.competition }}</div>
                    </div>
                    <div class="team away">{{ match.away }}</div>
                </div>
                <div style="text-align: center; margin-bottom: 20px;">
                    <div class="match-time">{{ match.time }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="error">Nenhum jogo agendado encontrado</div>
            {% endif %}
        </div>
        
        <!-- Standings -->
        <div class="section">
            <h2>📊 Classificação - Brasileirão</h2>
            {% if standings %}
            <div style="display: flex; align-items: center; gap: 30px; justify-content: center;">
                <div class="position-badge">{{ standings.position }}º</div>
                <div class="standings-grid">
                    <div class="stat-box">
                        <div class="stat-value">{{ standings.played }}</div>
                        <div class="stat-label">Jogos</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ standings.won }}</div>
                        <div class="stat-label">Vitórias</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ standings.points }}</div>
                        <div class="stat-label">Pontos</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ standings.goalsFor }}:{{ standings.goalsAgainst }}</div>
                        <div class="stat-label">Gols</div>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="error">Erro ao carregar classificação</div>
            {% endif %}
        </div>
        
        <!-- Recent Results -->
        <div class="section">
            <h2>✅ Últimos Resultados</h2>
            {% if recent_matches %}
                {% for match in recent_matches %}
                <div class="card">
                    <div class="team home">{{ match.home }}</div>
                    <div class="match-info">
                        <div class="match-time">{{ match.time }}</div>
                        <div class="competition">{{ match.competition }}</div>
                    </div>
                    <div class="team away">{{ match.away }}</div>
                </div>
                {% endfor %}
            {% else %}
            <div class="error">Nenhum resultado encontrado</div>
            {% endif %}
        </div>
        
        <div class="last-updated">
            Atualizado: {{ last_updated }}
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    """Main dashboard page."""
    # Get data
    try:
        next_matches_raw = get_matches("SCHEDULED")
        recent_matches_raw = get_matches("FINISHED")
        standings = get_standings()
    except Exception as e:
        return f"<h1>Error loading data</h1><p>{e}</p>"
    
    # Format matches
    next_matches = [format_match(m, True) for m in next_matches_raw[:1]] if next_matches_raw else []
    recent_matches = [format_match(m, False) for m in recent_matches_raw[:5]] if recent_matches_raw else []
    
    last_updated = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y às %H:%M")
    
    return render_template_string(
        HTML_TEMPLATE,
        next_matches=next_matches,
        recent_matches=recent_matches,
        standings=standings,
        last_updated=last_updated
    )

@app.route("/health")
def health():
    """Health check."""
    return jsonify({"status": "ok", "api_key": bool(API_KEY)})
    
    # Format matches
    next_matches = [format_match(m, True) for m in next_matches_raw[:1]] if next_matches_raw else []
    recent_matches = [format_match(m, False) for m in recent_matches_raw[:5]] if recent_matches_raw else []
    
    last_updated = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y às %H:%M")
    
    return render_template_string(
        HTML_TEMPLATE,
        next_matches=next_matches,
        recent_matches=recent_matches,
        standings=standings,
        last_updated=last_updated
    )


if __name__ == "__main__":
    print("🏆 Palmeiras Dashboard starting...")
    print("Open http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
