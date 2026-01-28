"""Utility functions for URL shortener."""

import string
import secrets
import re
from urllib.parse import urlparse, urlunparse

# Base62 character set
BASE62_CHARS = string.ascii_letters + string.digits


def generate_short_code(length: int = 6) -> str:
    """
    Generate a random Base62 short code.
    
    Args:
        length: Length of the short code (default: 6)
    
    Returns:
        Random string of specified length using Base62 characters
    """
    return ''.join(secrets.choice(BASE62_CHARS) for _ in range(length))


def is_valid_url(url: str) -> bool:
    """
    Validate if the given string is a valid URL.
    
    Args:
        url: URL string to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent storage.
    
    Args:
        url: URL string to normalize
    
    Returns:
        Normalized URL string
    """
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse and reconstruct
    parsed = urlparse(url)
    
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Remove default ports
    if netloc.endswith(':80') and scheme == 'http':
        netloc = netloc[:-3]
    elif netloc.endswith(':443') and scheme == 'https':
        netloc = netloc[:-4]
    
    # Remove trailing slash from path if it's just "/"
    path = parsed.path
    if path == '/':
        path = ''
    
    # Reconstruct URL
    normalized = urlunparse((
        scheme,
        netloc,
        path,
        parsed.params,
        parsed.query,
        ''  # Remove fragment
    ))
    
    return normalized
