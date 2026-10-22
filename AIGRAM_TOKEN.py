"""Local credentials are supplied through environment variables."""

import os

AIOGRAM__TOKEN = os.environ["BOT_TOKEN"]
api_key = os.environ.get("API_KEY", "")
