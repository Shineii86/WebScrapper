"""Validation utilities for WebScrapperBot."""
import re
import urllib.robotparser
from urllib.parse import urlparse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    return bool(URL_PATTERN.match(url))


def normalize_url(url: str) -> str:
    """Normalize a URL by adding scheme if missing."""
    url = url.strip()
    if url.startswith("www."):
        url = f"https://{url}"
    return url


def get_base_url(url: str) -> str:
    """Extract the base URL (scheme + netloc) from a full URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def resolve_url(base_url: str, url: str) -> str:
    """Resolve a relative URL against a base URL."""
    from urllib.parse import urljoin
    return urljoin(base_url, url)


def is_robots_txt_allowed(url: str, user_agent: str = "*") -> bool:
    """Check if a URL is allowed by robots.txt."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        logger.warning(f"Could not check robots.txt for {url}: {e}")
        return True  # Allow if robots.txt cannot be fetched


def is_safe_url(url: str) -> bool:
    """Check if URL is safe (not localhost/private IP)."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return False
    hostname = hostname.lower()
    # Block localhost
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
        return False
    # Block private IP ranges
    if re.match(r"^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)", hostname):
        return False
    return True
