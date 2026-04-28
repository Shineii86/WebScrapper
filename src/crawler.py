"""Improved web crawler with rate limiting and robots.txt respect."""
import asyncio
import logging
import os
import tempfile
from urllib.parse import urljoin, urlparse, unquote

from src.scrapers.base import fetch_url
from src.config import CRAWL_LOG_CHANNEL, RATE_LIMIT_DELAY, MAX_CRAWL_DEPTH
from src.utils.validators import is_safe_url

logger = logging.getLogger(__name__)


def get_safe_filename(url: str) -> str:
    """Convert a URL to a safe filename."""
    parsed = urlparse(url)
    safe = unquote(parsed.netloc + parsed.path).replace("/", "_").replace(":", "_")
    return safe[:200]  # limit length


async def crawl_page(url: str, depth: int = 0) -> str:
    """Crawl a single page and save its paragraphs to a temp file."""
    temp_path = None
    try:
        _, soup = await fetch_url(url)
        if not soup:
            logger.warning(f"Could not fetch {url}")
            return None

        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
        if not paragraphs:
            return None

        safe_name = get_safe_filename(url)
        fd, temp_path = tempfile.mkstemp(suffix=".txt", prefix=f"Crawl-{safe_name}-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\n")
            f.write("=" * 50 + "\n\n")
            for para in paragraphs:
                f.write(f"{para}\n\n")
        return temp_path
    except Exception as e:
        logger.error(f"Error crawling {url}: {e}")
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return None


async def crawl_web(bot, query):
    """Crawl a website starting from the given URL."""
    message = query.message
    base_url = message.text
    base_domain = urlparse(base_url).netloc

    if not CRAWL_LOG_CHANNEL:
        await message.reply_text(
            "⚠️ <b>Crawl Log Channel not configured!</b>\n\n"
            "Set the <code>CRAWL_LOG_CHANNEL</code> environment variable "
            "to a channel/group ID where crawl results will be sent.",
            quote=True,
        )
        return

    status = await message.reply_text("🕷️ Starting crawl...", quote=True)
    visited_urls = set()
    pending_urls = [base_url]
    crawled_count = 0

    try:
        # Get initial links
        _, soup = await fetch_url(base_url)
        if soup:
            for link in soup.find_all("a", href=True):
                next_url = urljoin(base_url, link["href"])
                if urlparse(next_url).netloc == base_domain and next_url not in visited_urls:
                    pending_urls.append(next_url)

        # Remove duplicates but preserve order
        pending_urls = list(dict.fromkeys(pending_urls))

        for url in pending_urls:
            if url in visited_urls:
                continue
            visited_urls.add(url)

            # Skip unsafe URLs
            if not is_safe_url(url):
                continue

            try:
                await status.edit(
                    f"🕷️ Crawling...\n"
                    f"<b>Current:</b> <code>{url[:60]}...</code>\n"
                    f"<b>Progress:</b> {crawled_count}/{len(pending_urls)}\n"
                    f"<b>Visited:</b> {len(visited_urls)}"
                )
            except Exception:
                pass

            file_path = await crawl_page(url)
            if file_path:
                try:
                    with open(file_path, "rb") as f:
                        await bot.send_document(
                            chat_id=CRAWL_LOG_CHANNEL,
                            document=file_path,
                            caption=f"🕷️ Crawled: {url}",
                        )
                    crawled_count += 1
                except Exception as e:
                    logger.error(f"Failed to send document to log channel: {e}")
                finally:
                    os.remove(file_path)

            # Rate limiting
            await asyncio.sleep(RATE_LIMIT_DELAY)

            if crawled_count >= 20:  # Limit to prevent spam
                break

        await status.edit(
            f"✅ <b>Crawl Complete!</b>\n\n"
            f"<b>Pages visited:</b> {len(visited_urls)}\n"
            f"<b>Pages extracted:</b> {crawled_count}\n"
            f"<b>Log channel:</b> <code>{CRAWL_LOG_CHANNEL}</code>"
        )
    except Exception as e:
        logger.error(f"Error in crawl_web: {e}")
        await status.edit(f"❌ Crawl failed: {str(e)[:200]}")
