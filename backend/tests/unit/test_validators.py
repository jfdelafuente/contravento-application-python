"""
Unit tests for custom validators (username, email, password).

Tests validation logic for user input fields.
"""

import pytest

from src.utils.validators import (
    validate_bio,
    validate_cycling_type,
    validate_email,
    validate_password,
    validate_username,
)


@pytest.mark.unit
class TestUsernameValidator:
    """T052: Unit test for username validators."""

    def test_valid_usernames(self):
        """Verify that valid usernames pass validation."""
        valid_usernames = [
            "user123",
            "maria_garcia",
            "John_Doe_99",
            "abc",  # Minimum length (3)
            "a" * 30,  # Maximum length (30)
            "user_name_123",
        ]

        for username in valid_usernames:
            # Should not raise
            result = validate_username(username)
            assert result == username

    def test_username_too_short(self):
        """Verify that usernames shorter than 3 characters are rejected."""
        short_usernames = ["ab", "a", ""]

        for username in short_usernames:
            with pytest.raises(ValueError) as exc_info:
                validate_username(username)
            assert "3 y 30 caracteres" in str(exc_info.value)

    def test_username_too_long(self):
        """Verify that usernames longer than 30 characters are rejected."""
        long_username = "a" * 31

        with pytest.raises(ValueError) as exc_info:
            validate_username(long_username)
        assert "3 y 30 caracteres" in str(exc_info.value)

    def test_username_invalid_characters(self):
        """Verify that usernames with invalid characters are rejected."""
        invalid_usernames = [
            "user-name",  # Hyphen not allowed
            "user.name",  # Dot not allowed
            "user name",  # Space not allowed
            "user@name",  # @ not allowed
            "user#123",  # # not allowed
            "maría",  # Accents not allowed
        ]

        for username in invalid_usernames:
            with pytest.raises(ValueError) as exc_info:
                validate_username(username)
            assert "alfanuméricos y guiones bajos" in str(exc_info.value)

    def test_username_case_preserved(self):
        """Verify that username case is preserved (not normalized)."""
        username = "UserName123"
        result = validate_username(username)
        assert result == "UserName123"


@pytest.mark.unit
class TestEmailValidator:
    """T052: Unit test for email validators."""

    def test_valid_emails(self):
        """Verify that valid email addresses pass validation."""
        valid_emails = [
            "user@example.com",
            "maria.garcia@example.es",
            "test+tag@subdomain.example.com",
            "user123@domain.co.uk",
            "name_123@example.org",
        ]

        for email in valid_emails:
            result = validate_email(email)
            assert result == email.lower()  # Should be normalized to lowercase

    def test_email_normalized_to_lowercase(self):
        """Verify that emails are normalized to lowercase."""
        email = "User@Example.COM"
        result = validate_email(email)
        assert result == "user@example.com"

    def test_invalid_email_format(self):
        """Verify that invalid email formats are rejected."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",  # Space
            "user@exam ple.com",  # Space in domain
            "user..name@example.com",  # Double dot
            "user@.example.com",  # Dot at start of domain
        ]

        for email in invalid_emails:
            with pytest.raises(ValueError) as exc_info:
                validate_email(email)
            assert "email válido" in str(exc_info.value).lower()

    def test_email_too_long(self):
        """Verify that emails longer than 255 characters are rejected."""
        long_email = "a" * 250 + "@example.com"  # > 255 chars

        with pytest.raises(ValueError) as exc_info:
            validate_email(long_email)
        assert "255 caracteres" in str(exc_info.value)


@pytest.mark.unit
class TestPasswordValidator:
    """T053: Unit test for password strength validator."""

    def test_valid_passwords(self):
        """Verify that strong passwords pass validation."""
        valid_passwords = [
            "SecurePass123!",
            "Contraseña1!",
            "P@ssw0rd",
            "MyP@ss123",
            "Testing123!@#",
        ]

        for password in valid_passwords:
            # Should not raise
            result = validate_password(password)
            assert result == password

    def test_password_too_short(self):
        """Verify that passwords shorter than 8 characters are rejected."""
        short_passwords = ["Pass1!", "Ab1!"]

        for password in short_passwords:
            with pytest.raises(ValueError) as exc_info:
                validate_password(password)
            assert "al menos 8 caracteres" in str(exc_info.value)

    def test_password_missing_uppercase(self):
        """Verify that passwords without uppercase are rejected."""
        password = "password123!"

        with pytest.raises(ValueError) as exc_info:
            validate_password(password)
        assert "mayúscula" in str(exc_info.value)

    def test_password_missing_lowercase(self):
        """Verify that passwords without lowercase are rejected."""
        password = "PASSWORD123!"

        with pytest.raises(ValueError) as exc_info:
            validate_password(password)
        assert "minúscula" in str(exc_info.value)

    def test_password_missing_digit(self):
        """Verify that passwords without digits are rejected."""
        password = "Password!"

        with pytest.raises(ValueError) as exc_info:
            validate_password(password)
        assert "número" in str(exc_info.value)

    def test_password_missing_special_character(self):
        """Verify that passwords without special characters are rejected."""
        password = "Password123"

        with pytest.raises(ValueError) as exc_info:
            validate_password(password)
        assert "especial" in str(exc_info.value)

    def test_password_with_unicode_characters(self):
        """Verify that passwords with unicode characters work."""
        password = "Contraseña123!"  # Contains 'ñ'

        # Should pass all requirements
        result = validate_password(password)
        assert result == password


@pytest.mark.unit
class TestBioValidator:
    """Unit test for bio field validator."""

    def test_valid_bios(self):
        """Verify that valid bios pass validation."""
        valid_bios = [
            "Ciclista apasionado de las rutas de montaña",
            "🚴 Amante del ciclismo de ruta",
            "",  # Empty is valid
            None,  # None is valid
            "a" * 500,  # Maximum length
        ]

        for bio in valid_bios:
            result = validate_bio(bio)
            assert result == bio

    def test_bio_too_long(self):
        """Verify that bios longer than 500 characters are rejected."""
        long_bio = "a" * 501

        with pytest.raises(ValueError) as exc_info:
            validate_bio(long_bio)
        assert "500 caracteres" in str(exc_info.value)

    def test_bio_stripped_of_whitespace(self):
        """Verify that bio is stripped of leading/trailing whitespace."""
        bio = "  My bio  "
        result = validate_bio(bio)
        assert result == "My bio"


@pytest.mark.unit
class TestCyclingTypeValidator:
    """Unit test for cycling_type field validator."""

    def test_valid_cycling_types(self):
        """Verify that valid cycling types pass validation."""
        valid_types = ["road", "mountain", "gravel", "touring", "commuting"]

        for cycling_type in valid_types:
            result = validate_cycling_type(cycling_type)
            assert result == cycling_type

    def test_cycling_type_case_insensitive(self):
        """Verify that cycling_type validation is case-insensitive."""
        inputs = ["ROAD", "Road", "rOaD"]

        for input_type in inputs:
            result = validate_cycling_type(input_type)
            assert result == "road"  # Normalized to lowercase

    def test_invalid_cycling_type(self):
        """Verify that invalid cycling types are rejected."""
        invalid_types = ["invalid", "bike", "cycling", ""]

        for cycling_type in invalid_types:
            with pytest.raises(ValueError) as exc_info:
                validate_cycling_type(cycling_type)
            assert "tipo de ciclismo debe ser uno de" in str(exc_info.value).lower()

    def test_cycling_type_none_is_valid(self):
        """Verify that None is a valid cycling_type (optional field)."""
        result = validate_cycling_type(None)
        assert result is None
