# VerdaoTracker 🟢⚪

Palmeiras Data Collector - Fetches the next match and sends notifications to Discord.

## Features

- Fetches the next scheduled Palmeiras match using football-data.org API
- Sends formatted match notifications to Discord via webhook
- Uses environment variables for sensitive data (API keys)
- Can be run on a schedule using cron

## Prerequisites

- Python 3.8+
- [football-data.org](https://www.football-data.org/) API key (free tier available)
- Discord webhook URL (optional, for notifications)

## Setup

### 1. Clone/Create the project

```bash
cd ~/.openclaw/workspace/projects/
git clone <your-repo> palmeiras-collector
cd palmeiras-collector
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file (optional, for local development):

```bash
# .env
FOOTBALL_API_KEY=your_football_data_api_key
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

Or export them in your shell:

```bash
export FOOTBALL_API_KEY=your_api_key_here
export DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 5. Get your API key

1. Go to [football-data.org](https://www.football-data.org/)
2. Register for a free account
3. Get your API key from the dashboard

### 6. Get Discord Webhook URL

1. Open your Discord server
2. Go to Server Settings > Integrations
3. Create a new Webhook
4. Copy the webhook URL

## Usage

### Run manually

```bash
python -m src.main
```

### Schedule with cron (every hour)

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths)
0 * * * * /path/to/venv/bin/python /path/to/project/src/main.py >> /path/to/project.log 2>&1
```

## Project Structure

```
palmeiras-collector/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── config.py
└── .env (optional)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FOOTBALL_API_KEY` | API key from football-data.org | Yes |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | No* |

*If not set, the script will run but skip sending to Discord and print the notification instead.

## Notes

- The free football-data.org API has a rate limit of 10 requests/minute
- Palmeiras team ID is `102` (fixed)
- Only fetches matches with status `SCHEDULED`

## License

MIT
