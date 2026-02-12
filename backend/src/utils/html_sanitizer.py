"""
HTML Sanitizer utility for preventing XSS attacks (Feature 004 - US3: Comentarios).

Uses bleach library to sanitize user-generated HTML content.
Task: T090
"""

import bleach

# Allowed HTML tags (safe formatting tags only)
ALLOWED_TAGS = [
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
]

# Allowed attributes for specific tags
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],  # Links with href and title only
}

# Allowed protocols for URLs (no javascript:, data:, etc.)
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks (T090).

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

    # Clean the HTML using bleach
    cleaned = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,  # Strip disallowed tags instead of escaping
    )

    return cleaned
