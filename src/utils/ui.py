"""UI components for WebScrapperBot."""
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import REPO_URL, SUPPORT_CHAT, BOT_VERSION

START_TEXT = (
    f"👋 <b>Welcome to WebScrapperBot v{BOT_VERSION}</b>\n\n"
    "I'm a powerful and versatile web scraping bot designed to extract data from websites.\n\n"
    "📌 <b>How to use:</b>\n"
    "1️⃣ Send me any valid URL (starting with http/https)\n"
    "2️⃣ Choose what you want to scrape from the menu\n"
    "3️⃣ I'll handle the rest and send you the results!\n\n"
    "🛠 <b>Supported Operations:</b>\n"
    "• 📄 Full Content / 📝 HTML Data\n"
    "• 🔗 Links / 📃 Paragraphs / 📌 Headings / 📊 Tables\n"
    "• 🌅 Images / 🎵 Audio / 🎥 Video / 📚 PDFs\n"
    "• 🍪 Cookies / 📦 LocalStorage / 📊 Metadata\n"
    "• 📷 Screenshot / 🎬 Screen Recording\n"
    "• 📧 Emails / 📞 Phone Numbers / 📄 Clean Text\n"
    "• 🕷️ Web Crawling\n\n"
    f"📢 Support: {SUPPORT_CHAT}"
)

HELP_TEXT = (
    "<b>📖 WebScrapperBot Help</b>\n\n"
    "<b>Commands:</b>\n"
    "• /start - Start the bot\n"
    "• /help - Show this help message\n"
    "• /about - About the bot\n"
    "• /scrapers - List all available scrapers\n"
    "• /ping - Check bot responsiveness\n\n"
    "<b>How to Scrape:</b>\n"
    "Simply send any URL and select an option from the menu.\n\n"
    "<b>💡 Tips:</b>\n"
    "• Ensure URLs start with http:// or https://\n"
    "• Some sites may block scraping (respect robots.txt)\n"
    "• Large media files may take time to process\n"
    "• Browser features require Chrome/Firefox on the server\n"
    "• Crawling requires a configured log channel\n\n"
    f"❓ Need help? Contact {SUPPORT_CHAT}"
)

ABOUT_TEXT = (
    f"<b>🤖 WebScrapperBot v{BOT_VERSION}</b>\n\n"
    "A simple, powerful, and versatile web scraping tool built with Python.\n\n"
    "<b>✨ Features:</b>\n"
    "• User-friendly menu-driven interface\n"
    "• Comprehensive data extraction\n"
    "• Browser automation with Selenium\n"
    "• Async web crawling with rate limiting\n"
    "• Email & phone number extraction\n"
    "• Clean text content extraction\n"
    "• Rendered page source capture\n"
    "• Robust error handling\n\n"
    "<b>🔧 Tech Stack:</b>\n"
    "• Python 3.12\n"
    "• Pyrogram (Telegram MTProto)\n"
    "• BeautifulSoup4 + lxml\n"
    "• Selenium WebDriver\n"
    "• Aiohttp (async HTTP)\n"
    "• ImageIO (video processing)\n\n"
    f"📂 <a href='{REPO_URL}'>Source Code</a>\n"
    f"⭐ Star us on GitHub!"
)

SCRAPERS_TEXT = (
    "<b>🔧 Available Scrapers</b>\n\n"
    "<b>📄 Text & Content:</b>\n"
    "• Raw Data - Raw HTML response\n"
    "• HTML Data - Prettified HTML\n"
    "• All Links - Extract anchor links\n"
    "• Paragraphs - Extract text paragraphs\n"
    "• Headings - Extract H1-H6 headings\n"
    "• Tables - Extract HTML tables\n"
    "• Clean Text - Readable text without HTML\n"
    "• Emails - Extract email addresses\n"
    "• Phone Numbers - Extract phone numbers\n\n"
    "<b>🌅 Media:</b>\n"
    "• Images - Download as ZIP archive\n"
    "• Audio - Download audio files\n"
    "• Video - Download video files\n"
    "• PDFs - Download PDF documents\n\n"
    "<b>🌐 Browser & Data:</b>\n"
    "• Cookies - Browser cookies\n"
    "• LocalStorage - Local storage data\n"
    "• Metadata - Page meta information\n"
    "• Screenshot - Full page capture\n"
    "• Screen Record - Scrolling video\n"
    "• Rendered Source - JS-rendered HTML\n\n"
    "<b>🕷️ Crawling:</b>\n"
    "• Crawl Website - Follow links & extract content"
)

# Back button for sub-menus
BACK_BUTTON = InlineKeyboardMarkup(
    [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="cb_back")]]
)

# Cancel button for ongoing operations
CANCEL_BUTTON = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🚫 Cancel", callback_data="cb_cancel")]]
)

# Start menu keyboard
START_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📄 Raw Data", callback_data="cbrdata"),
            InlineKeyboardButton("📝 HTML Data", callback_data="cbhtmldata"),
        ],
        [
            InlineKeyboardButton("🔗 All Links", callback_data="cballlinks"),
            InlineKeyboardButton("📃 Paragraphs", callback_data="cballparagraphs"),
        ],
        [
            InlineKeyboardButton("📌 Headings", callback_data="cballheadings"),
            InlineKeyboardButton("📊 Tables", callback_data="cballtables"),
        ],
        [
            InlineKeyboardButton("📄 Clean Text", callback_data="cbtextcontent"),
            InlineKeyboardButton("📊 Metadata", callback_data="cbmetadata"),
        ],
        [
            InlineKeyboardButton("📧 Emails", callback_data="cbemails"),
            InlineKeyboardButton("📞 Phones", callback_data="cbphones"),
        ],
        [
            InlineKeyboardButton("🌅 Images", callback_data="cballimages"),
            InlineKeyboardButton("🎵 Audio", callback_data="cballaudio"),
        ],
        [
            InlineKeyboardButton("🎥 Video", callback_data="cballvideo"),
            InlineKeyboardButton("📚 PDFs", callback_data="cballpdf"),
        ],
        [
            InlineKeyboardButton("🍪 Cookies", callback_data="cbcookies"),
            InlineKeyboardButton("📦 LocalStorage", callback_data="cblocalstorage"),
        ],
        [
            InlineKeyboardButton("📷 Screenshot", callback_data="cbscreenshot"),
            InlineKeyboardButton("🎬 Screen Record", callback_data="cbscreenrecord"),
        ],
        [
            InlineKeyboardButton("📄 Rendered Source", callback_data="cbsource"),
        ],
        [
            InlineKeyboardButton("🕷️ Crawl Website", callback_data="cbcrawl"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="cbhelp"),
            InlineKeyboardButton("📋 Scrapers", callback_data="cbscrapers"),
            InlineKeyboardButton("ℹ️ About", callback_data="cbabout"),
        ],
    ]
)

# Main options keyboard (shown after sending a URL)
OPTIONS = START_BUTTON


# Inline buttons for issue reporting
def get_issue_markup(error_text: str) -> InlineKeyboardMarkup:
    """Generate an inline keyboard with a link to create a GitHub issue."""
    from urllib.parse import quote
    error_link = (
        f"{REPO_URL}/issues/new?"
        f"title={quote(f'ERROR: {error_text[:100]}')}&"
        f"body={quote(f'Describe the issue here...\\n\\nError: {error_text}')}"
    )
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🐛 Report Issue", url=error_link)],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cb_back")],
        ]
    )
