<p align="center">
  <a href="https://github.com/Shineii86/WebScrapper">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=300&color=gradient&text=𝗪𝗲𝗯%20𝗦𝗰𝗿𝗮𝗽𝗽𝗲𝗿&fontAlignY=30&fontSize=100&desc=𝖯𝗈𝗐𝖾𝗋𝖿𝗎𝗅%20%7C%20𝖵𝖾𝗋𝗌𝖺𝗍𝗂𝗅𝖾%20%7C%20𝖤𝖺𝗌𝗒-𝗍𝗈-𝖴𝗌𝖾&descSize=30" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/Shineii86/WebScrapper/stargazers">
    <img src="https://img.shields.io/github/stars/Shineii86/WebScrapper?style=flat-square&color=yellow" alt="Stars">
  </a>
  <a href="https://github.com/Shineii86/WebScrapper/network/members">
    <img src="https://img.shields.io/github/forks/Shineii86/WebScrapper?style=flat-square&color=green" alt="Forks">
  </a>
  <a href="https://github.com/Shineii86/WebScrapper/issues">
    <img src="https://img.shields.io/github/issues/Shineii86/WebScrapper?style=flat-square&color=red" alt="Issues">
  </a>
  <a href="https://github.com/Shineii86/WebScrapper/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Shineii86/WebScrapper?style=flat-square&color=blue" alt="License">
  </a>
</p>

---

## 🚀 Overview

**WebScrapperBot** is a simple, powerful, and versatile Telegram bot designed to simplify web scraping. Whether you need raw HTML, extracted text, media downloads, browser cookies, or full-page screenshots — this bot handles it all through an intuitive menu-driven interface.

### What's New?

- ✅ **Async Architecture** — Faster, non-blocking requests with `aiohttp`
- ✅ **Modular Codebase** — Clean separation of concerns with organized packages
- ✅ **New Scrapers** — Headings, tables, Open Graph & Twitter Card metadata
- ✅ **Browser Automation** — Full-page screenshots, screen recording, cookies, localStorage
- ✅ **Safety First** — URL validation, robots.txt respect, private IP blocking
- ✅ **Better UX** — Progress bars, typing indicators, cancel buttons, improved menus
- ✅ **Rate Limiting** — Polite crawling with configurable delays
- ✅ **Error Handling** — Centralized error decorator with GitHub issue reporting

---

## 🛠️ Features

### Text & Content Extraction
| Feature | Description |
|---------|-------------|
| 📄 **Full Content** | Raw HTML response from the server |
| 📝 **HTML Data** | Prettified, formatted HTML structure |
| 🔗 **All Links** | Every anchor (`<a>`) tag with resolved URLs |
| 📃 **All Paragraphs** | Extracted text content from `<p>` tags |
| 📌 **All Headings** | H1–H6 headings with hierarchy preserved |
| 📊 **All Tables** | HTML tables formatted as readable text |

### Media Downloads
| Feature | Description |
|---------|-------------|
| 🌄 **All Images** | Download all images as a ZIP archive |
| 🎵 **All Audio** | Download audio files as a ZIP archive |
| 🎥 **All Video** | Download video files as a ZIP archive |
| 📚 **All PDFs** | Download linked PDF documents as ZIP |

### Browser & Data Extraction
| Feature | Description |
|---------|-------------|
| 🍪 **Cookies** | Extract browser cookies via Selenium |
| 📦 **LocalStorage** | Extract HTML5 localStorage data |
| 📊 **Metadata** | Title, description, keywords, Open Graph, Twitter Cards |
| 📷 **Screenshot** | Full-page screenshot (not just viewport) |
| 🎬 **Screen Record** | Scrolling video capture of the entire page |

### Web Crawling
| Feature | Description |
|---------|-------------|
| 🕷️ **Crawl Website** | Follow same-domain links and extract paragraph content |

---

## 🚀 Quick Start

### Run in Google Colab (Free)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Shineii86/WebScrapper/blob/main/notebooks/WebScrapper.ipynb)

---

## 🖥️ Local Installation

### Prerequisites
- Python 3.10 or higher
- Chrome or Firefox (for browser-based features)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- API_ID and API_HASH from [my.telegram.org](https://my.telegram.org/apps)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Shineii86/WebScrapper.git
cd WebScrapper
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
CRAWL_LOG_CHANNEL=-1001234567890  # Optional
```

> 💡 **Tip:** To get a channel ID, forward a message from your channel to [@userinfobot](https://t.me/userinfobot).

### Step 5: Run the Bot

```bash
python -m src.main
```

You should see:

```
==================================================
WebScrapperBot v2.0.0 starting...
==================================================
```

---

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t webscrapper-bot .

# Run with env variables
docker run -e BOT_TOKEN=xxx -e API_ID=xxx -e API_HASH=xxx webscrapper-bot
```

### Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  bot:
    build: .
    container_name: webscrapper-bot
    env_file: .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

Run with:

```bash
docker-compose up -d
```

---

## 🚀 Heroku Deployment

### One-Click Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Manual Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-webscrapper-bot

# Set environment variables
heroku config:set BOT_TOKEN=xxx
heroku config:set API_ID=xxx
heroku config:set API_HASH=xxx

# Deploy
git push heroku main
```

---

## 📁 Project Structure

```
WebScrapper/
├── .github/                    # GitHub templates & funding
│   ├── FUNDING.yml
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── assets/
│   └── demos/                  # Screenshots & demo images
├── notebooks/
│   └── WebScrapper.ipynb       # Google Colab notebook
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Environment & settings
│   ├── handlers.py             # Telegram bot handlers
│   ├── crawler.py              # Web crawler logic
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py             # Base scraper + async fetch + error decorator
│   │   ├── text.py             # Text content scrapers
│   │   ├── media.py            # Media downloaders
│   │   └── browser.py          # Selenium-based scrapers
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py          # Progress bars, formatters
│       ├── ui.py               # Keyboards, buttons, messages
│       └── validators.py       # URL validation, robots.txt
├── tests/                      # Unit tests (future)
├── .env.example                # Environment template
├── .gitignore
├── app.json                    # Heroku configuration
├── CODE_OF_CONDUCT.md
├── Dockerfile
├── LICENSE
├── Procfile
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version
└── SECURITY.md
```

---

## 📖 Usage Guide

### Basic Usage

1. **Start the bot** — Send `/start` to see the welcome menu.
2. **Send a URL** — Paste any `http://` or `https://` link.
3. **Choose an option** — Tap a button from the inline menu.
4. **Receive results** — The bot will process and send files or text.

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Show detailed help message |
| `/about` | About the bot and tech stack |
| `/scrapers` | List all available scrapers |

### Feature-Specific Tips

**Images/Audio/Video/PDFs**
- Files are downloaded and sent as ZIP archives
- Large files show real-time progress bars
- Supports cancel button during upload

**Screenshots**
- Captures the *full page* height, not just viewport
- Requires Chrome or Firefox installed

**Screen Recording**
- Records a scrolling capture of the entire page
- Configurable duration and FPS in `src/config.py`

**Crawling**
- Respects `robots.txt`
- Rate-limited to avoid overloading servers
- Sends results to `CRAWL_LOG_CHANNEL`
- Limited to same-domain links

---

## ⚙️ Configuration

All settings are in `src/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `REQUEST_TIMEOUT` | 30 | HTTP request timeout in seconds |
| `RATE_LIMIT_DELAY` | 1.5 | Delay between crawl requests |
| `MAX_CRAWL_DEPTH` | 2 | Maximum crawl depth |
| `MAX_VIDEO_LENGTH` | 30 | Screen recording duration |
| `MAX_SCREENSHOTS` | 60 | Max frames for screen recording |
| `MAX_DOWNLOAD_SIZE_MB` | 50 | Max individual file size |

---

## 🛡️ Safety & Ethics

WebScrapperBot includes built-in safety measures:

- ✅ **URL Validation** — Only accepts valid HTTP/HTTPS URLs
- ✅ **Private IP Blocking** — Prevents access to localhost/internal networks
- ✅ **robots.txt Respect** — Checks robots.txt before crawling
- ✅ **Rate Limiting** — Configurable delays between requests
- ✅ **File Size Limits** — Prevents excessive memory usage

**Please use responsibly:**
- Don't scrape personal information without consent
- Respect website Terms of Service
- Don't overload servers with aggressive crawling
- Identify yourself with the User-Agent string

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Browser features fail | Install Chrome: `sudo apt install chromium-browser` |
| Session file locked | Delete `*.session` files and restart |
| Heroku build fails | Check `runtime.txt` matches Python version |
| Crawl not sending files | Verify `CRAWL_LOG_CHANNEL` is set correctly |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) and [Security Policy](./SECURITY.md).

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) — Telegram MTProto framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [Selenium](https://www.selenium.dev/) — Browser automation
- [aiohttp](https://docs.aiohttp.org/) — Async HTTP client

---

## 💬 Support

- 📢 **Telegram:** [@BugHunterBots](https://t.me/BugHunterBots)
- 🐛 **Issues:** [GitHub Issues](https://github.com/Shineii86/WebScrapper/issues)
- ⭐ **Star this repo** if you find it useful!

<p align="center">
  <a href="https://github.com/sponsors/Shineii86">
    <img src="https://img.shields.io/badge/Sponsor-GitHub-red?style=for-the-badge&logo=github-sponsors" alt="Sponsor">
  </a>
</p>

---

<p align="center">
  <b>Made with ❤️ by <a href="https://github.com/Shineii86">Shinei Nouzen</a></b>
</p>

<p align="center">
  <img src="https://api.star-history.com/svg?repos=Shineii86/webscrapper&type=Date" alt="Star History">
</p>
