"""
Unit tests for HTML Sanitizer utility (Feature 004 - US3: Comentarios).

Tests cover:
- T076: HTML sanitization to prevent XSS attacks

Following TDD: These tests are written BEFORE implementation.
"""

import pytest

from src.utils.html_sanitizer import sanitize_html


# ============================================================
# T076: Test HTML sanitization
# ============================================================


def test_sanitize_html_removes_script_tags():
    """
    Test T076: sanitize_html() removes <script> tags to prevent XSS.

    Verifies:
    - <script> tags are completely removed
    - Malicious JavaScript is stripped
    """
    # Test basic script tag
    malicious = "<script>alert('XSS')</script>Hello"
    result = sanitize_html(malicious)
    assert "<script>" not in result
    assert "alert" not in result
    assert "Hello" in result

    # Test script with attributes
    malicious2 = '<script src="evil.js">alert("XSS")</script>Comment'
    result2 = sanitize_html(malicious2)
    assert "<script" not in result2
    assert "evil.js" not in result2
    assert "Comment" in result2


def test_sanitize_html_removes_event_handlers():
    """
    Test T076: sanitize_html() removes event handler attributes (onclick, onerror, etc).

    Verifies:
    - onclick, onerror, onload attributes are removed
    - Other inline JavaScript is stripped
    """
    # Test onclick
    malicious = '<div onclick="alert(\'XSS\')">Click me</div>'
    result = sanitize_html(malicious)
    assert "onclick" not in result
    assert "alert" not in result
    assert "Click me" in result

    # Test onerror
    malicious2 = '<img src="x" onerror="alert(\'XSS\')">Image'
    result2 = sanitize_html(malicious2)
    assert "onerror" not in result2
    assert "alert" not in result2

    # Test onload
    malicious3 = '<body onload="stealCookies()">Text</body>'
    result3 = sanitize_html(malicious3)
    assert "onload" not in result3
    assert "stealCookies" not in result3
    assert "Text" in result3


def test_sanitize_html_removes_javascript_protocol():
    """
    Test T076: sanitize_html() removes javascript: protocol in URLs.

    Verifies:
    - javascript: URLs are stripped
    - data: URLs are stripped (can execute JS)
    """
    # Test javascript: protocol
    malicious = '<a href="javascript:alert(\'XSS\')">Link</a>'
    result = sanitize_html(malicious)
    assert "javascript:" not in result
    assert "alert" not in result
    assert "Link" in result

    # Test data: protocol
    malicious2 = '<a href="data:text/html,<script>alert(\'XSS\')</script>">Data Link</a>'
    result2 = sanitize_html(malicious2)
    assert "data:" not in result2
    assert "<script>" not in result2
    assert "Data Link" in result2


def test_sanitize_html_allows_safe_tags():
    """
    Test T076: sanitize_html() allows safe HTML tags.

    Verifies:
    - Common formatting tags are preserved (p, b, i, em, strong, ul, ol, li, br)
    - Links with safe URLs are preserved
    - Safe content is not modified
    """
    # Test paragraph and formatting
    safe = "<p>This is <b>bold</b> and <i>italic</i> text.</p>"
    result = sanitize_html(safe)
    assert result == safe

    # Test lists
    safe_list = "<ul><li>Item 1</li><li>Item 2</li></ul>"
    result_list = sanitize_html(safe_list)
    assert result_list == safe_list

    # Test safe link
    safe_link = '<a href="https://example.com">Safe Link</a>'
    result_link = sanitize_html(safe_link)
    assert "https://example.com" in result_link
    assert "Safe Link" in result_link

    # Test line breaks
    safe_br = "Line 1<br>Line 2"
    result_br = sanitize_html(safe_br)
    assert "<br" in result_br


def test_sanitize_html_removes_iframe_and_object():
    """
    Test T076: sanitize_html() removes <iframe> and <object> tags.

    Verifies:
    - <iframe> tags are removed (can load external content)
    - <object> and <embed> tags are removed
    """
    # Test iframe
    malicious = '<iframe src="https://evil.com/steal.html"></iframe>Text'
    result = sanitize_html(malicious)
    assert "<iframe" not in result
    assert "evil.com" not in result
    assert "Text" in result

    # Test object
    malicious2 = '<object data="evil.swf"></object>Content'
    result2 = sanitize_html(malicious2)
    assert "<object" not in result2
    assert "evil.swf" not in result2
    assert "Content" in result2

    # Test embed
    malicious3 = '<embed src="evil.swf">Text</embed>'
    result3 = sanitize_html(malicious3)
    assert "<embed" not in result3
    assert "Text" in result3


def test_sanitize_html_removes_style_tags():
    """
    Test T076: sanitize_html() removes <style> tags and style attributes.

    Verifies:
    - <style> tags are removed (can contain CSS injection)
    - style attributes are removed (can contain expression())
    """
    # Test style tag
    malicious = "<style>body { background: url('javascript:alert(1)') }</style>Text"
    result = sanitize_html(malicious)
    assert "<style>" not in result
    assert "javascript:" not in result
    assert "Text" in result

    # Test style attribute
    malicious2 = '<div style="background: url(\'javascript:alert(1)\')">Text</div>'
    result2 = sanitize_html(malicious2)
    assert 'style="' not in result2
    assert "javascript:" not in result2
    assert "Text" in result2


def test_sanitize_html_plain_text_unchanged():
    """
    Test T076: sanitize_html() leaves plain text unchanged.

    Verifies:
    - Plain text without HTML is preserved
    - No modifications to safe content
    """
    plain = "This is a simple comment with no HTML."
    result = sanitize_html(plain)
    assert result == plain

    # Test with special characters (but not HTML)
    plain2 = "Price: $100 < $200 & taxes > 0"
    result2 = sanitize_html(plain2)
    # Special chars may be escaped, but content preserved
    assert "$100" in result2
    assert "$200" in result2


def test_sanitize_html_nested_malicious_tags():
    """
    Test T076: sanitize_html() handles nested malicious tags.

    Verifies:
    - Nested script tags are removed
    - Complex XSS payloads are neutralized
    """
    # Test nested scripts
    malicious = "<div><script>alert('XSS')</script><p>Text</p></div>"
    result = sanitize_html(malicious)
    assert "<script>" not in result
    assert "alert" not in result
    assert "Text" in result

    # Test obfuscated XSS
    malicious2 = "<<script>script>alert('XSS')<</script>/script>"
    result2 = sanitize_html(malicious2)
    assert "<script>" not in result2
    assert "alert" not in result2


def test_sanitize_html_handles_empty_and_whitespace():
    """
    Test T076: sanitize_html() handles edge cases.

    Verifies:
    - Empty string returns empty
    - Whitespace-only content is preserved
    - None handling (if applicable)
    """
    # Empty string
    assert sanitize_html("") == ""

    # Whitespace
    whitespace = "   \n\t   "
    result = sanitize_html(whitespace)
    assert result.strip() == ""


def test_sanitize_html_max_length_preserved():
    """
    Test T076: sanitize_html() doesn't modify content length significantly.

    Verifies:
    - Safe content length is preserved
    - Only malicious parts are removed
    """
    # Long safe content
    long_safe = "A" * 500
    result = sanitize_html(long_safe)
    assert len(result) == 500
    assert result == long_safe

    # Long content with malicious tag
    long_malicious = "A" * 250 + "<script>alert('XSS')</script>" + "B" * 250
    result2 = sanitize_html(long_malicious)
    # Should be ~500 chars (malicious part removed)
    assert len(result2) == 500
    assert "A" * 250 in result2
    assert "B" * 250 in result2
    assert "<script>" not in result2
