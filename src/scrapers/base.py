"""Base scraper module with common utilities and async request handling."""
import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from functools import wraps
from typing import Optional, Tuple

from src.config import DEFAULT_HEADERS, REQUEST_TIMEOUT, REPO_URL
from src.utils.validators import is_valid_url, normalize_url
from src.utils.ui import get_issue_markup

logger = logging.getLogger(__name__)

# Semaphore to limit concurrent requests
_semaphore = asyncio.Semaphore(10)


async def fetch_url(url: str) -> Tuple[Optional[bytes], Optional[BeautifulSoup]]:
    """Fetch a URL asynchronously and return (content_bytes, soup).
    
    Returns the raw bytes AND parsed soup so callers can use either.
    Both are fully read/created inside the session context.
    """
    try:
        normalized = normalize_url(url)
        if not is_valid_url(normalized):
            raise ValueError(f"Invalid URL: {url}")

        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with _semaphore:
            async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout) as session:
                async with session.get(normalized, ssl=False, allow_redirects=True) as response:
                    response.raise_for_status()
                    # Check content length before reading
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > 50 * 1024 * 1024:
                        logger.warning(f"Response too large: {url} ({content_length} bytes)")
                        return None, None
                    content = await response.read()
                    soup = BeautifulSoup(content, "html.parser")
                    return content, soup
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None, None


async def fetch_json(url: str) -> Optional[dict]:
    """Fetch JSON from a URL."""
    try:
        normalized = normalize_url(url)
        if not is_valid_url(normalized):
            return None

        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with _semaphore:
            async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout) as session:
                async with session.get(normalized, ssl=False, allow_redirects=True) as response:
                    response.raise_for_status()
                    return await response.json(content_type=None)
    except Exception as e:
        logger.error(f"Error fetching JSON from {url}: {e}")
        return None


async def fetch_bytes(url: str, max_size: int = 50 * 1024 * 1024) -> Optional[bytes]:
    """Fetch raw bytes from a URL with size limit."""
    try:
        normalized = normalize_url(url)
        if not is_valid_url(normalized):
            return None

        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with _semaphore:
            async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout) as session:
                async with session.get(normalized, ssl=False, allow_redirects=True) as response:
                    response.raise_for_status()
                    # Check content length before downloading
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > max_size:
                        logger.warning(f"File too large: {url} ({content_length} bytes)")
                        return None
                    content = await response.read()
                    if len(content) > max_size:
                        logger.warning(f"File too large: {url} ({len(content)} bytes)")
                        return None
                    return content
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return None


def handle_errors(func):
    """Decorator to handle scraper errors uniformly."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            # Try to extract message object from args
            message = None
            for arg in args:
                if hasattr(arg, "message") and hasattr(arg.message, "reply_text"):
                    message = arg.message
                elif hasattr(arg, "reply_text"):
                    message = arg

            if message:
                error_text = str(e)[:200]
                text = (
                    "⚠️ <b>Something went wrong!</b>\n\n"
                    f"<code>{error_text}</code>\n\n"
                    "Please report this issue if it persists."
                )
                try:
                    await message.reply_text(
                        text,
                        disable_web_page_preview=True,
                        quote=True,
                        reply_markup=get_issue_markup(error_text),
                    )
                except Exception:
                    pass
            return None
    return wrapper
