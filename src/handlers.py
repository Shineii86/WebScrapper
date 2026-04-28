"""Bot handlers for WebScrapperBot."""
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from src.config import BOT_TOKEN, API_ID, API_HASH, CRAWL_LOG_CHANNEL
from src.utils.ui import START_TEXT, START_BUTTON, HELP_TEXT, ABOUT_TEXT, SCRAPERS_TEXT, OPTIONS, BACK_BUTTON
from src.utils.validators import is_valid_url, normalize_url, is_safe_url

from src.scrapers.text import (
    raw_data_scraping,
    html_data_scraping,
    all_links_scraping,
    all_paragraph_scraping,
    all_headings_scraping,
    all_tables_scraping,
    extract_metadata,
)
from src.scrapers.media import (
    all_images_scraping,
    all_audio_scraping,
    all_video_scraping,
    all_pdf_scraping,
)
from src.scrapers.browser import (
    extract_cookies,
    extract_local_storage,
    capture_screenshot,
    record_screen,
)
from src.crawler import crawl_web

logger = logging.getLogger(__name__)

# Initialize Pyrogram Client
app = Client(
    "WebScrapperBot",
    bot_token=BOT_TOKEN,
    api_id=int(API_ID),
    api_hash=API_HASH,
)


@app.on_message(filters.command(["start"]))
async def start_handler(_, message: Message):
    """Handle /start command."""
    await message.reply_text(
        START_TEXT,
        disable_web_page_preview=True,
        quote=True,
        reply_markup=START_BUTTON,
    )


@app.on_message(filters.command(["help"]))
async def help_handler(_, message: Message):
    """Handle /help command."""
    await message.reply_text(
        HELP_TEXT,
        disable_web_page_preview=True,
        quote=True,
        reply_markup=BACK_BUTTON,
    )


@app.on_message(filters.command(["about"]))
async def about_handler(_, message: Message):
    """Handle /about command."""
    await message.reply_text(
        ABOUT_TEXT,
        disable_web_page_preview=True,
        quote=True,
        reply_markup=BACK_BUTTON,
    )


@app.on_message(filters.command(["scrapers"]))
async def scrapers_handler(_, message: Message):
    """Handle /scrapers command."""
    await message.reply_text(
        SCRAPERS_TEXT,
        disable_web_page_preview=True,
        quote=True,
        reply_markup=BACK_BUTTON,
    )


@app.on_callback_query()
async def callback_handler(bot, update):
    """Handle all callback queries from inline keyboards."""
    data = update.data
    message = update.message

    if data == "cb_back":
        await message.edit_text(
            START_TEXT,
            disable_web_page_preview=True,
            reply_markup=START_BUTTON,
        )
        return

    if data == "cbhelp":
        await message.edit_text(
            HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=BACK_BUTTON,
        )
        return

    if data == "cbabout":
        await message.edit_text(
            ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=BACK_BUTTON,
        )
        return

    if data == "cb_cancel":
        try:
            await message.edit_text("❌ Operation cancelled by user.")
        except Exception:
            pass
        return

    # All scraping operations need a URL from the message text
    if not message or not message.text:
        await message.reply_text("❌ No URL found. Please send a URL first.")
        return

    # Validate URL for scraping operations
    url = normalize_url(message.text)
    if not is_valid_url(url):
        await message.reply_text("❌ Invalid URL. Please send a valid http:// or https:// link.")
        return
    if not is_safe_url(url):
        await message.reply_text("❌ This URL is not allowed for safety reasons.")
        return

    # Send typing action for better UX
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass

    # Route to appropriate scraper
    scraper_map = {
        "cbrdata": raw_data_scraping,
        "cbhtmldata": html_data_scraping,
        "cballlinks": all_links_scraping,
        "cballparagraphs": all_paragraph_scraping,
        "cballheadings": all_headings_scraping,
        "cballtables": all_tables_scraping,
        "cballimages": lambda q: all_images_scraping(bot, q),
        "cballaudio": lambda q: all_audio_scraping(bot, q),
        "cballvideo": lambda q: all_video_scraping(bot, q),
        "cballpdf": all_pdf_scraping,
        "cbcookies": extract_cookies,
        "cblocalstorage": extract_local_storage,
        "cbmetadata": extract_metadata,
        "cbscreenshot": capture_screenshot,
        "cbscreenrecord": record_screen,
        "cbcrawl": lambda q: crawl_web(bot, q),
    }

    handler = scraper_map.get(data)
    if handler:
        try:
            await handler(update)
        except Exception as e:
            logger.error(f"Handler error for {data}: {e}", exc_info=True)
            await message.reply_text(
                f"❌ An error occurred while processing your request.\n"
                f"<code>{str(e)[:200]}</code>",
                quote=True,
            )
    else:
        await message.edit_text(
            START_TEXT,
            disable_web_page_preview=True,
            reply_markup=START_BUTTON,
        )


@app.on_message(
    (filters.regex(r"https?://") | filters.regex(r"www\."))
    & filters.private
)
async def url_handler(bot, message: Message):
    """Handle URLs sent by users."""
    url = normalize_url(message.text)

    if not is_valid_url(url):
        await message.reply_text(
            "⚠️ <b>Invalid URL</b>\n\n"
            "Please send a valid URL starting with <code>http://</code> or <code>https://</code>",
            quote=True,
        )
        return

    if not is_safe_url(url):
        await message.reply_text(
            "⚠️ <b>Unsafe URL detected</b>\n\n"
            "This URL points to a private/local address and is not allowed.",
            quote=True,
        )
        return

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await message.reply_text(
        "✅ <b>URL Received!</b>\n\nChoose an option to scrape:",
        quote=True,
    )
    await message.reply_text(
        message.text,
        reply_markup=OPTIONS,
        disable_web_page_preview=True,
        quote=True,
    )
