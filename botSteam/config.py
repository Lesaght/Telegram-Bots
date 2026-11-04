import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
STEAM_API_KEY: str = os.getenv("STEAM_API_KEY", "")
STEAM_API = "https://api.steampowered.com"
