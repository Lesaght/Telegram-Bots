import os
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Все секреты задаются только через переменные окружения.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN не установлен")

BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
SPECIAL_PASSWORD = os.environ.get("BOT_SPECIAL_PASSWORD", "")
BOT_ADMIN_ID = os.environ.get("BOT_ADMIN_ID")
SAVE_FOLDER = "saved_files"
USER_FILES_BASE_FOLDER = os.path.join(SAVE_FOLDER, "users")
SUPPORTED_PHOTO_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
FILES_PER_PAGE = 5
SHARE_LINK_TTL = 24
