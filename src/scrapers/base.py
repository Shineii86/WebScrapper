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


async def fetch_url(url: str) -> Tuple[Optional[aiohttp.ClientResponse], Optional[BeautifulSoup]]:
    """Fetch a URL asynchronously and return the response and BeautifulSoup object."""
    try:
        normalized = normalize_url(url)
        if not is_valid_url(normalized):
            raise ValueError(f"Invalid URL: {url}")
        
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout) as session:
            async with session.get(normalized, ssl=False) as response:
                response.raise_for_status()
                content = await response.read()
                soup = BeautifulSoup(content, "html.parser")
                return response, soup
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None, None


async def fetch_bytes(url: str, max_size: int = 50 * 1024 * 1024) -> Optional[bytes]:
    """Fetch raw bytes from a URL with size limit."""
    try:
        normalized = normalize_url(url)
        if not is_valid_url(normalized):
            return None
        
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout) as session:
            async with session.get(normalized, ssl=False) as response:
                response.raise_for_status()
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
            query = None
            for arg in args:
                if hasattr(arg, "message"):
                    query = arg
                    message = arg.message
                elif hasattr(arg, "reply_text"):
                    message = arg
            
            if message:
                error_text = str(e)[:100]
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
            return e
    return wrapper
