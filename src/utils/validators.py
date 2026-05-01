"""Validation utilities for WebScrapperBot."""
import re
import logging
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)

# Comprehensive URL pattern
URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d{1,5})?"
    r"(?:/[^\s]*)?$",
    re.IGNORECASE,
)

# Private IP ranges
PRIVATE_IP_PATTERNS = [
    re.compile(r"^10\."),
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[01])\."),
    re.compile(r"^192\.168\."),
    re.compile(r"^169\.254\."),  # Link-local
    re.compile(r"^127\."),
    re.compile(r"^0\."),
    re.compile(r"^::1$"),
    re.compile(r"^fc00:"),
    re.compile(r"^fe80:"),
]

# Blocked hostnames
BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal", "169.254.169.254"}


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid HTTP/HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    if not URL_PATTERN.match(url):
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def normalize_url(url: str) -> str:
    """Normalize a URL by adding scheme if missing."""
    if not url:
        return ""
    url = url.strip()
    if url.startswith("www."):
        url = f"https://{url}"
    # Remove trailing whitespace and newlines
    url = url.split("\n")[0].strip()
    return url


def get_base_url(url: str) -> str:
    """Extract the base URL (scheme + netloc) from a full URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def resolve_url(base_url: str, url: str) -> str:
    """Resolve a relative URL against a base URL."""
    from urllib.parse import urljoin
    return urljoin(base_url, url)


def is_safe_url(url: str) -> bool:
    """Check if URL is safe (not localhost/private IP)."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        hostname = hostname.lower().strip(".")

        # Block known dangerous hostnames
        if hostname in BLOCKED_HOSTNAMES:
            return False

        # Block private IP ranges
        for pattern in PRIVATE_IP_PATTERNS:
            if pattern.match(hostname):
                return False

        # Block non-standard ports that might be internal services
        port = parsed.port
        if port and port in {6379, 27017, 5432, 3306, 9200, 11211}:
            # Redis, MongoDB, PostgreSQL, MySQL, Elasticsearch, Memcached
            return False

        return True
    except Exception:
        return False
