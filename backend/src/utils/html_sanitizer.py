"""
HTML sanitization utility for user-generated content.

Prevents XSS attacks while allowing safe rich text formatting.
Uses Bleach library with strict whitelist of allowed tags and attributes.
"""

import bleach
from typing import List, Dict

# Whitelist of allowed HTML tags for trip descriptions
# Allows basic rich text formatting but prevents dangerous content
ALLOWED_TAGS: List[str] = [
    'p',       # Paragraphs
    'br',      # Line breaks
    'b',       # Bold (deprecated but widely used)
    'strong',  # Bold (semantic)
    'i',       # Italic (deprecated but widely used)
    'em',      # Italic (semantic)
    'ul',      # Unordered lists
    'ol',      # Ordered lists
    'li',      # List items
    'a',       # Links
]

# Whitelist of allowed attributes per tag
# Only safe attributes that cannot execute JavaScript
ALLOWED_ATTRIBUTES: Dict[str, List[str]] = {
    'a': ['href', 'title'],  # Links can have URL and title
}

# Allowed URL protocols for links
# Prevents javascript: and data: URLs which can execute code
ALLOWED_PROTOCOLS: List[str] = [
    'http',
    'https',
    'mailto',
]

# Maximum length for sanitized HTML content (50,000 characters)
# Prevents abuse and ensures reasonable content size
MAX_DESCRIPTION_LENGTH = 50000


def sanitize_html(dirty_html: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Removes all potentially dangerous HTML tags, attributes, and JavaScript.
    Only allows safe formatting tags from the ALLOWED_TAGS whitelist.

    Args:
        dirty_html: Raw HTML content from user input

    Returns:
        Sanitized HTML safe for storage and display

    Raises:
        ValueError: If content exceeds maximum length after sanitization

    Examples:
        >>> sanitize_html('<p>Hello</p><script>alert("XSS")</script>')
        '<p>Hello</p>'

        >>> sanitize_html('<p onclick="alert()">Click</p>')
        '<p>Click</p>'

        >>> sanitize_html('<p>Bold: <b>text</b></p>')
        '<p>Bold: <b>text</b></p>'
    """
    # Handle empty input
    if not dirty_html:
        return ""

    # First: Remove dangerous tags and their content BEFORE bleach processing
    # This ensures script/style content is completely removed, not just tags
    import re
    # Remove script tags and all their content
    preprocessed = re.sub(
        r'<script[^>]*>.*?</script>',
        '',
        dirty_html,
        flags=re.DOTALL | re.IGNORECASE
    )
    # Remove style tags and all their content
    preprocessed = re.sub(
        r'<style[^>]*>.*?</style>',
        '',
        preprocessed,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Now sanitize with Bleach
    # - tags: Only allow whitelisted tags
    # - attributes: Only allow whitelisted attributes per tag
    # - protocols: Only allow safe URL protocols
    # - strip: Remove disallowed tags but keep their text content
    clean = bleach.clean(
        preprocessed,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Remove disallowed tags but keep content
    )

    # Check length AFTER sanitization
    # This prevents users from bypassing limit with lots of tags
    if len(clean) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"La descripción excede el límite de {MAX_DESCRIPTION_LENGTH:,} caracteres "
            f"(actual: {len(clean):,})"
        )

    return clean
