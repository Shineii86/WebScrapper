"""WebScrapperBot configuration module."""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Optional Crawl Log Channel
CRAWL_LOG_CHANNEL = os.getenv("CRAWL_LOG_CHANNEL")

# Validate required credentials
if not all([BOT_TOKEN, API_ID, API_HASH]):
    raise ValueError(
        "Missing required environment variables. "
        "Please set BOT_TOKEN, API_ID, and API_HASH. "
        "Copy .env.example to .env and fill in your credentials."
    )

# Bot metadata
BOT_NAME = "WebScrapperBot"
BOT_VERSION = "2.5.0"
BOT_OWNER = "@Shineii86"
SUPPORT_CHAT = "https://t.me/MaximXGroup"
REPO_URL = "https://github.com/Shineii86/WebScrapper"

# Request settings
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}

REQUEST_TIMEOUT = 30  # seconds
MAX_CRAWL_DEPTH = 2
RATE_LIMIT_DELAY = 1.5  # seconds between requests

# Media settings
MAX_VIDEO_LENGTH = 30  # seconds for screen recording
MAX_SCREENSHOTS = 60  # max frames for screen recording
MAX_DOWNLOAD_SIZE_MB = 50  # max individual file size

# Progress bar settings
FINISHED_PROGRESS_STR = "▓"
UN_FINISHED_PROGRESS_STR = "░"
