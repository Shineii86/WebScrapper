# 🕷️ WebScrapperBot v2.5.0

A powerful and versatile Telegram bot for web scraping with support for content extraction, media downloads, browser automation, and web crawling.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.x-green.svg)](https://docs.pyrogram.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 📄 Text & Content Scraping
- **Raw Data** - Get raw HTML response from any URL
- **HTML Data** - Prettified HTML output
- **All Links** - Extract all anchor links with deduplication
- **Paragraphs** - Extract text paragraphs
- **Headings** - Extract H1-H6 heading tags
- **Tables** - Extract and format HTML tables
- **Clean Text** - Readable text content (strips scripts, styles, nav, footer)
- **Emails** - Extract email addresses from page content
- **Phone Numbers** - Extract phone numbers from page content

### 🌅 Media Downloading
- **Images** - Download all images (including lazy-loaded & CSS backgrounds) as ZIP
- **Audio** - Download audio files (including linked files) as ZIP
- **Video** - Download video files (including linked files) as ZIP
- **PDFs** - Download PDF documents as ZIP

### 🌐 Browser Automation (Selenium)
- **Cookies** - Extract browser cookies with full details
- **LocalStorage** - Extract local storage data
- **Metadata** - Page title, description, keywords, Open Graph, Twitter Card, canonical, favicon
- **Screenshot** - Full-page screenshot capture
- **Screen Record** - Scrolling video capture with frame-by-frame recording
- **Rendered Source** - Get page source after JavaScript execution

### 🕷️ Web Crawling
- Rate-limited crawling with configurable depth
- Respects robots.txt
- Sends extracted content to a configured log channel
- Progress tracking and status updates

### 🔒 Security
- URL validation with comprehensive regex
- Blocks private/local IPs (10.x, 192.168.x, 172.16-31.x, 127.x, link-local)
- Blocks access to internal services (Redis, MongoDB, PostgreSQL, MySQL, etc.)
- Blocks metadata endpoints (169.254.169.254)
- Content-length checks before downloading
- Concurrent request limiting with semaphore

## 🚀 Deploy

### Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Docker

```bash
docker build -t webscrapper .
docker run -d --name webscrapper \
  -e BOT_TOKEN=your_token \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  webscrapper
```

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/Shineii86/WebScrapper.git
cd WebScrapper

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python -m src.main
```

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| `API_ID` | ✅ | API ID from [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | ✅ | API Hash from [my.telegram.org](https://my.telegram.org/apps) |
| `CRAWL_LOG_CHANNEL` | ❌ | Channel/Group ID for crawl logs (e.g., `-1001234567890`) |

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Show help message |
| `/about` | About the bot |
| `/scrapers` | List all available scrapers |
| `/ping` | Check bot responsiveness |

## 🔧 Tech Stack

- **Python 3.12** - Core language
- **Pyrogram 2.x** - Telegram MTProto API framework
- **BeautifulSoup4 + lxml** - HTML parsing
- **Aiohttp** - Async HTTP client
- **Selenium** - Browser automation
- **ImageIO** - Video frame processing
- **TgCrypto** - Encryption for Telegram

## 📁 Project Structure

```
WebScrapper/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py             # Configuration
│   ├── handlers.py           # Bot command & callback handlers
│   ├── crawler.py            # Web crawler
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py           # Base fetch/error handling
│   │   ├── text.py           # Text content scrapers
│   │   ├── media.py          # Media downloaders
│   │   └── browser.py        # Selenium-based scrapers
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py         # Progress bars, formatters
│       ├── ui.py              # UI components, keyboards
│       └── validators.py      # URL validation & safety
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── app.json
├── requirements.txt
├── runtime.txt
├── LICENSE
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- Built with [Pyrogram](https://docs.pyrogram.org)
- HTML parsing by [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- Browser automation by [Selenium](https://www.selenium.dev/)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Shineii86">Shineii86</a>
</p>
