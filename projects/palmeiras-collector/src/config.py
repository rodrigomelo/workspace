"""
Configuration for Palmeiras Data Collector.
Uses environment variables for sensitive data.
"""

import os

# Palmeiras Team ID (from football-data.org)
TEAM_ID = 102

# API Configuration
# Get your free API key at: https://www.football-data.org/
API_KEY = os.environ.get("FOOTBALL_API_KEY", "")

# Discord Webhook URL
# Create a webhook in your Discord server: Server Settings > Integrations > Webhooks
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# Request timeout (seconds)
REQUEST_TIMEOUT = 10
