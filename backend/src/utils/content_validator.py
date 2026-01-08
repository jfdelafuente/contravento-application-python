"""
Content validation utility for spam and inappropriate content detection.

Uses configurable blocked words list and pattern matching to detect:
- Blocked keywords (spam, profanity, inappropriate content)
- Excessive word repetition
- Excessive URLs

Balances spam prevention with false positive avoidance.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from src.config import settings

logger = logging.getLogger(__name__)


class ContentValidator:
    """Validate user-generated content for spam and inappropriate material."""

    def __init__(self) -> None:
        """
        Initialize content validator.

        Loads blocked words from configuration file if spam detection enabled.
        """
        self.blocked_words: list[str] = []
        self._load_blocked_words()

    def _load_blocked_words(self) -> None:
        """Load blocked words from configuration file."""
        if not settings.spam_detection_enabled:
            logger.info("Spam detection disabled - skipping blocked words loading")
            return

        try:
            blocked_file = Path(settings.blocked_words_file)
            if not blocked_file.exists():
                logger.warning(f"Blocked words file not found: {blocked_file}")
                return

            with open(blocked_file, encoding="utf-8") as f:
                self.blocked_words = [
                    line.strip().lower()
                    for line in f
                    if line.strip()  # Not empty
                    and not line.strip().startswith("#")  # Not a comment
                ]

            logger.info(f"Loaded {len(self.blocked_words)} blocked words from {blocked_file}")

        except Exception as e:
            logger.error(f"Error loading blocked words file: {e}")
            # Continue with empty list - don't fail startup

    def validate_content(self, content: str, field_name: str = "contenido") -> Optional[str]:
        """
        Validate content for spam and inappropriate material.

        Args:
            content: Text content to validate (title, description, etc.)
            field_name: Name of field for error messages (default: "contenido")

        Returns:
            Error message (Spanish) if validation fails, None if content is valid

        Examples:
            >>> validator = ContentValidator()
            >>> validator.validate_content("Buy viagra now!")
            "El contenido contiene contenido inapropiado..."

            >>> validator.validate_content("Clean cycling description")
            None
        """
        # Skip validation if disabled
        if not settings.spam_detection_enabled:
            return None

        # Skip validation for empty content
        if not content or not content.strip():
            return None

        # Normalize content for checking (case-insensitive)
        normalized = content.lower()

        # Check 1: Blocked words
        error = self._check_blocked_words(normalized, field_name)
        if error:
            return error

        # Check 2: Excessive repetition
        error = self._check_excessive_repetition(content, field_name)
        if error:
            return error

        # Check 3: Excessive URLs
        error = self._check_excessive_urls(content, field_name)
        if error:
            return error

        # All checks passed
        return None

    def _check_blocked_words(self, normalized_content: str, field_name: str) -> Optional[str]:
        """
        Check if content contains blocked words.

        Uses word boundary regex to avoid false positives on partial matches.
        """
        for word in self.blocked_words:
            # Use word boundary regex for whole word matching
            # This prevents 'spam' from matching 'spamming' or 'gratis' from matching 'graficar'
            pattern = r"\b" + re.escape(word) + r"\b"

            if re.search(pattern, normalized_content):
                logger.warning(f"Blocked word detected in {field_name}: {word}")
                return (
                    f"El {field_name} contiene contenido inapropiado. "
                    "Por favor, revisa el texto y elimina cualquier contenido ofensivo o spam."
                )

        return None

    def _check_excessive_repetition(self, content: str, field_name: str) -> Optional[str]:
        """
        Check for excessive word repetition (same word 10+ times).

        Only checks meaningful words (> 3 characters) to avoid false positives
        on common short words like 'de', 'la', 'el', etc.
        """
        # Threshold: Same word repeated more than 10 times
        MAX_REPETITIONS = 10

        # Count word occurrences (case-insensitive)
        words = content.lower().split()
        word_counts: dict[str, int] = {}

        for word in words:
            # Only check meaningful words (longer than 3 chars)
            if len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1

                if word_counts[word] > MAX_REPETITIONS:
                    logger.warning(
                        f"Excessive repetition detected in {field_name}: "
                        f"'{word}' repeated {word_counts[word]} times"
                    )
                    return (
                        f"El {field_name} contiene repeticiones excesivas. "
                        "Por favor, escribe contenido original y descriptivo."
                    )

        return None

    def _check_excessive_urls(self, content: str, field_name: str) -> Optional[str]:
        """
        Check for excessive URLs (more than 5 URLs in content).

        Prevents link spam while allowing legitimate route references.
        """
        # Threshold: More than 5 URLs
        MAX_URLS = 5

        # Regex pattern for HTTP/HTTPS URLs
        url_pattern = r"https?://\S+"
        urls = re.findall(url_pattern, content)

        if len(urls) > MAX_URLS:
            logger.warning(
                f"Excessive URLs detected in {field_name}: "
                f"{len(urls)} URLs found (max {MAX_URLS})"
            )
            return (
                f"El {field_name} contiene demasiados enlaces ({len(urls)}). "
                "Limita los enlaces a información relevante del viaje."
            )

        return None


# Global singleton instance
# Can be used throughout the application without re-loading blocked words
content_validator = ContentValidator()
