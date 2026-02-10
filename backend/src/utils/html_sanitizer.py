"""
HTML Sanitizer utility for preventing XSS attacks (Feature 004 - US3: Comentarios).

Uses nh3 library (Rust-based, 20x faster than bleach) to sanitize user-generated HTML content.
Migrated from bleach to nh3 in Feature 018 (Task: T008).
"""

import nh3

# Allowed HTML tags (safe formatting tags only)
# Note: nh3 requires set instead of list for tags
ALLOWED_TAGS = {
    "p",
    "br",
    "b",
    "i",
    "em",
    "strong",
    "u",
    "ul",
    "ol",
    "li",
    "a",
    "blockquote",
}

# Allowed attributes for specific tags
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},  # Links with href and title only (set for nh3)
}

# Allowed URL schemes (protocols) - no javascript:, data:, etc.
# nh3 uses 'url_schemes' parameter instead of 'protocols'
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks using nh3 (Rust-based, 20x faster than bleach).

    Migrated from bleach to nh3 in Feature 018 (Task: T008).

    Removes:
    - <script> tags and content
    - Event handlers (onclick, onerror, onload, etc.)
    - javascript: and data: protocols
    - <iframe>, <object>, <embed> tags
    - <style> tags and style attributes
    - All other dangerous HTML

    Preserves:
    - Safe formatting tags (p, b, i, em, strong, ul, ol, li, br)
    - Safe links with http/https protocols
    - Plain text content

    Args:
        content: Raw HTML string from user input

    Returns:
        Sanitized HTML string safe for display

    Examples:
        >>> sanitize_html("<script>alert('XSS')</script>Hello")
        'Hello'
        >>> sanitize_html('<p>This is <b>bold</b> text.</p>')
        '<p>This is <b>bold</b> text.</p>'
        >>> sanitize_html('<a href="javascript:alert(1)">Click</a>')
        '<a>Click</a>'
    """
    if not content:
        return ""

    # Clean the HTML using nh3 (Rust-based sanitizer)
    cleaned = nh3.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
    )

    return cleaned
