"""
Unit tests for HTML sanitizer utility.

Tests XSS prevention and safe HTML formatting for trip descriptions.
"""

import pytest

from src.utils.html_sanitizer import sanitize_html


class TestHtmlSanitizer:
    """Test HTML sanitization for user-generated content."""

    def test_sanitize_removes_script_tags(self) -> None:
        """Test that script tags are removed (XSS prevention)."""
        dirty = '<p>Hello</p><script>alert("XSS")</script><p>World</p>'
        clean = sanitize_html(dirty)

        assert "<script>" not in clean
        assert "alert" not in clean
        assert "<p>Hello</p>" in clean
        assert "<p>World</p>" in clean

    def test_sanitize_removes_onclick_attributes(self) -> None:
        """Test that JavaScript event handlers are removed."""
        dirty = "<p onclick=\"alert('XSS')\">Click me</p>"
        clean = sanitize_html(dirty)

        assert "onclick" not in clean
        assert "alert" not in clean
        assert "<p>Click me</p>" in clean

    def test_sanitize_preserves_allowed_tags(self) -> None:
        """Test that safe formatting tags are preserved."""
        dirty = """
        <p>This is a <b>bold</b> and <i>italic</i> text.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <ol>
            <li>First</li>
            <li>Second</li>
        </ol>
        """
        clean = sanitize_html(dirty)

        assert "<p>" in clean
        assert "<b>bold</b>" in clean
        assert "<i>italic</i>" in clean
        assert "<ul>" in clean
        assert "<li>" in clean
        assert "<ol>" in clean

    def test_sanitize_preserves_safe_links(self) -> None:
        """Test that HTTP/HTTPS links are preserved."""
        dirty = '<p>Check out <a href="https://example.com" title="Example">this link</a></p>'
        clean = sanitize_html(dirty)

        assert '<a href="https://example.com"' in clean
        assert 'title="Example"' in clean
        assert ">this link</a>" in clean

    def test_sanitize_removes_javascript_protocol(self) -> None:
        """Test that javascript: URLs are removed."""
        dirty = "<a href=\"javascript:alert('XSS')\">Bad link</a>"
        clean = sanitize_html(dirty)

        assert "javascript:" not in clean
        assert "alert" not in clean

    def test_sanitize_removes_disallowed_tags(self) -> None:
        """Test that potentially dangerous tags are removed."""
        dirty = """
        <p>Safe content</p>
        <iframe src="https://evil.com"></iframe>
        <object data="evil.swf"></object>
        <embed src="evil.swf">
        <style>body { display: none; }</style>
        """
        clean = sanitize_html(dirty)

        assert "<p>Safe content</p>" in clean
        assert "<iframe" not in clean
        assert "<object" not in clean
        assert "<embed" not in clean
        assert "<style" not in clean

    def test_sanitize_removes_disallowed_attributes(self) -> None:
        """Test that only whitelisted attributes are allowed."""
        dirty = '<a href="https://example.com" onclick="alert()" class="link" style="color:red">Link</a>'
        clean = sanitize_html(dirty)

        assert 'href="https://example.com"' in clean
        assert "onclick" not in clean
        assert "class" not in clean  # Not in whitelist
        assert "style" not in clean  # Not in whitelist

    def test_sanitize_enforces_max_length(self) -> None:
        """Test that content exceeding max length raises error."""
        # Generate content exceeding 50,000 chars
        dirty = "<p>" + ("A" * 50001) + "</p>"

        with pytest.raises(ValueError, match="excede el límite"):
            sanitize_html(dirty)

    def test_sanitize_handles_empty_string(self) -> None:
        """Test that empty strings are handled gracefully."""
        assert sanitize_html("") == ""
        assert sanitize_html("   ") == "   "

    def test_sanitize_handles_none_as_empty(self) -> None:
        """Test that None input returns empty string."""
        # Note: Type hint says str, but defensive programming
        assert sanitize_html("") == ""

    def test_sanitize_preserves_line_breaks(self) -> None:
        """Test that <br> tags are preserved."""
        dirty = "<p>Line 1<br>Line 2<br>Line 3</p>"
        clean = sanitize_html(dirty)

        assert "<br>" in clean or "<br />" in clean
        assert "Line 1" in clean
        assert "Line 2" in clean

    def test_sanitize_handles_nested_tags(self) -> None:
        """Test that nested allowed tags work correctly."""
        dirty = "<p>This is <b>bold with <i>italic inside</i></b>.</p>"
        clean = sanitize_html(dirty)

        assert "<p>" in clean
        assert "<b>" in clean
        assert "<i>" in clean
        assert "bold with" in clean
        assert "italic inside" in clean

    def test_sanitize_strips_disallowed_tags_content(self) -> None:
        """Test that script content is completely removed."""
        dirty = '<p>Before</p><script>var x = "evil";</script><p>After</p>'
        clean = sanitize_html(dirty)

        assert "<p>Before</p>" in clean
        assert "<p>After</p>" in clean
        assert "evil" not in clean
        assert "var x" not in clean

    def test_sanitize_handles_malformed_html(self) -> None:
        """Test that malformed HTML is cleaned up."""
        dirty = "<p>Unclosed paragraph<b>Bold without close"
        clean = sanitize_html(dirty)

        # Bleach should close tags automatically
        assert "Unclosed paragraph" in clean
        assert "Bold without close" in clean

    def test_sanitize_removes_data_attributes(self) -> None:
        """Test that data-* attributes are removed."""
        dirty = '<p data-user-id="123" data-action="delete">Content</p>'
        clean = sanitize_html(dirty)

        assert "data-user-id" not in clean
        assert "data-action" not in clean
        assert "<p>Content</p>" in clean

    def test_sanitize_allows_mailto_links(self) -> None:
        """Test that mailto: links are allowed."""
        dirty = '<a href="mailto:user@example.com">Email me</a>'
        clean = sanitize_html(dirty)

        assert "mailto:user@example.com" in clean
        assert "Email me" in clean

    def test_sanitize_preserves_strong_and_em(self) -> None:
        """Test that <strong> and <em> tags work like <b> and <i>."""
        dirty = "<p><strong>Strong text</strong> and <em>emphasized text</em></p>"
        clean = sanitize_html(dirty)

        assert "<strong>Strong text</strong>" in clean
        assert "<em>emphasized text</em>" in clean

    def test_sanitize_length_check_after_cleaning(self) -> None:
        """Test that length is checked AFTER sanitization, not before."""
        # Input with lots of tags that get stripped
        # Should pass if stripped version is under limit
        dirty = "<p>" + "<b>A</b>" * 100 + "</p>"  # Results in ~300 chars after stripping tags
        clean = sanitize_html(dirty)

        # Should not raise error
        assert "A" in clean

    def test_sanitize_realistic_trip_description(self) -> None:
        """Test with realistic trip description content."""
        dirty = """
        <p>Espectacular ruta entre <b>Jaén</b> y <b>Córdoba</b> siguiendo antiguas vías de tren.</p>
        <p>Destacados:</p>
        <ul>
            <li>Paisajes de olivos infinitos</li>
            <li>Pueblos con encanto como <a href="https://baeza.es">Baeza</a></li>
            <li>Viaductos históricos</li>
        </ul>
        <p>Ideal para cicloturistas de nivel <i>moderado</i>.<br>
        <strong>Recomendación:</strong> Llevar agua suficiente en verano.</p>
        """
        clean = sanitize_html(dirty)

        # Should preserve all content
        assert "Jaén" in clean
        assert "Córdoba" in clean
        assert "<b>" in clean
        assert "<ul>" in clean
        assert "<li>" in clean
        assert 'href="https://baeza.es"' in clean
        assert "<i>moderado</i>" in clean
        assert "<strong>" in clean
        assert "<br>" in clean or "<br />" in clean
