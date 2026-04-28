"""
WebScrapperBot - A powerful Telegram bot for web scraping.

Entry point for the bot application.
"""
import logging
import sys

# Configure logging before importing anything else
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

from src.handlers import app

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("WebScrapperBot v2.0.0 starting...")
    logger.info("=" * 50)
    app.run()
