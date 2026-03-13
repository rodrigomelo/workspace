# Palmeiras Data Collector (VerdaoTracker)

Collects and notifies about Palmeiras matches.

## Data Sources

- **football-data.org** — API de futebol (gratuita com API key)

## Features

- ✅ Next match finder
- ✅ Discord webhook notifications
- ✅ Match details (competition, date, opponent, venue)

## Setup

```bash
# Clone project
cd ~/workspace/projects/palmeiras-collector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
# Get free API key at: https://www.football-data.org/
export FOOTBALL_API_KEY="your-api-key"

# Create Discord webhook: Server Settings > Integrations > Webhooks
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## Running

```bash
python -m src.main
```

## Cron (optional)

Run every day at 9am:

```bash
crontab -e
0 9 * * * cd /path/to/palmeiras-collector && /path/to/venv/bin/python -m src.main >> /tmp/verdao.log 2>&1
```

## Project Structure

```
palmeiras-collector/
├── src/
│   ├── config.py       # Configuration
│   └── main.py         # Main script
├── SPEC.md
└── README.md
```

## Tech Stack

- Python 3.10+
- requests
- football-data.org API
- Discord Webhooks