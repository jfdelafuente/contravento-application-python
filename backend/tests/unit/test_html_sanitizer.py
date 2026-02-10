"""
Unit tests for HTML Sanitizer utility (Feature 004 - US3: Comentarios).

Tests cover:
- T076: HTML sanitization to prevent XSS attacks

Following TDD: These tests are written BEFORE implementation.
"""


from src.utils.html_sanitizer import sanitize_html

# ============================================================
# T076: Test HTML sanitization
# ============================================================


def test_sanitize_html_removes_script_tags():
    """
    Test T076: sanitize_html() removes <script> tags to prevent XSS.

    Verifies:
    - <script> tags are completely removed (tag stripped, content remains as plain text)
    - Script content cannot execute (no HTML tags)
    """
    # Test basic script tag
    malicious = "<script>alert('XSS')</script>Hello"
    result = sanitize_html(malicious)
    assert "<script>" not in result
    assert "</script>" not in result
    # bleach strips tags but leaves text content (safe - won't execute)
    assert "Hello" in result

    # Test script with attributes
    malicious2 = '<script src="evil.js">alert("XSS")</script>Comment'
    result2 = sanitize_html(malicious2)
    assert "<script" not in result2
    assert "Comment" in result2


def test_sanitize_html_removes_event_handlers():
    """
    Test T076: sanitize_html() removes event handler attributes (onclick, onerror, etc).

    Verifies:
    - onclick, onerror, onload attributes are removed
    - Other inline JavaScript is stripped
    """
    # Test onclick
    malicious = "<div onclick=\"alert('XSS')\">Click me</div>"
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
    malicious = "<a href=\"javascript:alert('XSS')\">Link</a>"
    result = sanitize_html(malicious)
    assert "javascript:" not in result
    assert "alert" not in result
    assert "Link" in result

    # Test data: protocol
    malicious2 = "<a href=\"data:text/html,<script>alert('XSS')</script>\">Data Link</a>"
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
    - <style> tags are removed (tag stripped, CSS content remains as text - safe)
    - style attributes are removed (can contain expression())
    - <div> tags are removed (not in allowed list)
    """
    # Test style tag
    malicious = "<style>body { background: url('javascript:alert(1)') }</style>Text"
    result = sanitize_html(malicious)
    assert "<style>" not in result
    assert "</style>" not in result
    assert "Text" in result

    # Test style attribute and div tag removal
    malicious2 = "<div style=\"background: url('javascript:alert(1)')\">Text</div>"
    result2 = sanitize_html(malicious2)
    assert 'style="' not in result2
    assert "<div" not in result2
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
    - Nested script tags are removed (tags stripped, safe text remains)
    - Complex XSS payloads are neutralized
    - Safe tags like <p> are preserved
    """
    # Test nested scripts
    malicious = "<div><script>alert('XSS')</script><p>Text</p></div>"
    result = sanitize_html(malicious)
    assert "<script>" not in result
    assert "</script>" not in result
    assert "<div>" not in result  # div not in allowed tags
    assert "<p>Text</p>" in result  # <p> is allowed

    # Test obfuscated XSS
    malicious2 = "<<script>script>alert('XSS')<</script>/script>"
    result2 = sanitize_html(malicious2)
    assert "<script>" not in result2
    assert "</script>" not in result2


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
    Test T076: sanitize_html() doesn't modify safe content length.

    Verifies:
    - Safe content length is preserved exactly
    - Malicious tags are stripped (content may remain as text)
    """
    # Long safe content
    long_safe = "A" * 500
    result = sanitize_html(long_safe)
    assert len(result) == 500
    assert result == long_safe

    # Long content with malicious tag
    long_malicious = "A" * 250 + "<script>alert('XSS')</script>" + "B" * 250
    result2 = sanitize_html(long_malicious)
    # nh3 strips <script> tags but leaves text content
    # Length will be: 250 + len("alert('XSS')") + 250 = ~520 chars
    assert "A" * 250 in result2
    assert "B" * 250 in result2
    assert "<script>" not in result2
    assert "</script>" not in result2


# ============================================================
# T018: nh3 Performance Benchmarks (Feature 018)
# ============================================================


def test_nh3_performance_benchmark():
    """
    Test T018: Benchmark nh3 sanitization speed (20x faster than bleach target).

    Verifies:
    - nh3 can process 100 iterations of moderately complex HTML in < 1 second
    - This demonstrates significant performance improvement over bleach
    """
    import time

    test_html = """
    <p>This is a <b>test</b> paragraph with <em>emphasis</em>.</p>
    <script>alert('XSS')</script>
    <a href="https://example.com">Safe link</a>
    <a href="javascript:alert(1)">Malicious link</a>
    """ * 100  # Repeat 100 times for meaningful benchmark

    start_time = time.perf_counter()
    for _ in range(100):
        sanitize_html(test_html)
    end_time = time.perf_counter()

    elapsed = end_time - start_time
    avg_time = elapsed / 100

    # nh3 should process 100 iterations in < 1 second (very fast)
    assert elapsed < 1.0, f"nh3 took {elapsed:.3f}s for 100 iterations (expected < 1.0s)"

    print(f"\nnh3 performance: {avg_time * 1000:.2f}ms per iteration")


def test_nh3_large_document_performance():
    """
    Test T018: Benchmark nh3 with large HTML documents.

    Verifies:
    - nh3 can process ~50KB HTML document in < 100ms
    - Demonstrates scalability for large comment/description fields
    """
    import time

    large_html = """
    <p>Paragraph text</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    <blockquote>Quote text</blockquote>
    """ * 1000  # 1000 repetitions (~50KB of HTML)

    start_time = time.perf_counter()
    result = sanitize_html(large_html)
    end_time = time.perf_counter()

    elapsed = end_time - start_time

    # Should process 50KB document in < 100ms
    assert elapsed < 0.1, f"Large document took {elapsed * 1000:.2f}ms (expected < 100ms)"
    assert len(result) > 0

    print(f"\nnh3 large document performance: {elapsed * 1000:.2f}ms for ~50KB HTML")


def test_nh3_comment_use_case():
    """
    Test T018: Real-world comment sanitization for Activity Stream (Feature 018).

    Verifies:
    - nh3 handles typical user comments with formatting
    - Safe links are preserved
    - XSS attempts are blocked
    """
    # Comment with safe formatting
    comment1 = "¡Increíble ruta! Me encantó el <b>tramo de montaña</b>. 🚴‍♂️"
    result1 = sanitize_html(comment1)

    assert "<b>tramo de montaña</b>" in result1
    assert "🚴‍♂️" in result1

    # Comment with safe link
    comment2 = 'Más info aquí: <a href="https://contravento.com">ContraVento</a>'
    result2 = sanitize_html(comment2)

    assert '<a href="https://contravento.com"' in result2

    # Comment with XSS attempt
    malicious_comment = 'Great trip! <script>stealCookies()</script>'
    result3 = sanitize_html(malicious_comment)

    assert "Great trip!" in result3
    assert "<script>" not in result3
    assert "stealCookies" not in result3
