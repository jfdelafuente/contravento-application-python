"""
Unit tests for security utilities (password hashing, JWT tokens).

Tests the core security functions used for authentication.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from src.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.config import settings


@pytest.mark.unit
class TestPasswordHashing:
    """T050: Unit test for password hashing and verification."""

    def test_hash_password_returns_different_hash_each_time(self):
        """Verify that hashing the same password twice produces different hashes (salt)."""
        password = "SecurePass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0

    def test_verify_password_correct_password(self):
        """Verify that correct password validates against its hash."""
        password = "SecurePass123!"
        password_hash = hash_password(password)

        assert verify_password(password, password_hash) is True

    def test_verify_password_incorrect_password(self):
        """Verify that incorrect password fails validation."""
        password = "SecurePass123!"
        wrong_password = "WrongPass456!"
        password_hash = hash_password(password)

        assert verify_password(wrong_password, password_hash) is False

    def test_verify_password_empty_password(self):
        """Verify that empty password fails validation."""
        password = "SecurePass123!"
        password_hash = hash_password(password)

        assert verify_password("", password_hash) is False

    def test_verify_password_case_sensitive(self):
        """Verify that password verification is case-sensitive."""
        password = "SecurePass123!"
        password_hash = hash_password(password)

        assert verify_password("securepass123!", password_hash) is False
        assert verify_password("SECUREPASS123!", password_hash) is False

    def test_hash_password_with_special_characters(self):
        """Verify that passwords with special characters are hashed correctly."""
        special_passwords = [
            "P@ssw0rd!",
            "Contraseña123!",
            "пароль123!",
            "密码123!",
        ]

        for password in special_passwords:
            password_hash = hash_password(password)
            assert verify_password(password, password_hash) is True


@pytest.mark.unit
class TestJWTTokens:
    """T051: Unit test for JWT token creation and validation."""

    def test_create_access_token_default_expiration(self):
        """Verify access token is created with default 15-minute expiration."""
        data = {"sub": "user123", "username": "test_user"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "user123"
        assert payload["username"] == "test_user"
        assert payload["type"] == "access"

        # Verify expiration is ~15 minutes
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        diff = exp - now
        assert 890 <= diff.total_seconds() <= 910  # ~900 seconds (15 min)

    def test_create_access_token_custom_expiration(self):
        """Verify access token can be created with custom expiration."""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        # Verify expiration is ~30 minutes
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        diff = exp - now
        assert 1790 <= diff.total_seconds() <= 1810  # ~1800 seconds (30 min)

    def test_create_refresh_token_default_expiration(self):
        """Verify refresh token is created with default 30-day expiration."""
        data = {"sub": "user123"}
        token = create_refresh_token(data)

        assert token is not None
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

        # Verify expiration is ~30 days
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        diff = exp - now
        expected_seconds = 30 * 24 * 60 * 60  # 30 days
        assert expected_seconds - 10 <= diff.total_seconds() <= expected_seconds + 10

    def test_decode_token_valid_access_token(self):
        """Verify that decode_token correctly decodes valid access token."""
        data = {"sub": "user123", "username": "test_user"}
        token = create_access_token(data)

        payload = decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["username"] == "test_user"
        assert payload["type"] == "access"

    def test_decode_token_valid_refresh_token(self):
        """Verify that decode_token correctly decodes valid refresh token."""
        data = {"sub": "user123"}
        token = create_refresh_token(data)

        payload = decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_decode_token_expired_token(self):
        """Verify that decode_token raises exception for expired token."""
        data = {"sub": "user123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta=expires_delta)

        with pytest.raises(JWTError):
            decode_token(token)

    def test_decode_token_invalid_token(self):
        """Verify that decode_token raises exception for invalid token."""
        with pytest.raises(JWTError):
            decode_token("invalid.token.here")

    def test_decode_token_tampered_token(self):
        """Verify that decode_token raises exception for tampered token."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        # Tamper with token
        parts = token.split(".")
        parts[1] = parts[1][:-1] + "X"  # Change last character of payload
        tampered_token = ".".join(parts)

        with pytest.raises(JWTError):
            decode_token(tampered_token)

    def test_decode_token_wrong_secret(self):
        """Verify that token signed with different secret is rejected."""
        data = {"sub": "user123"}
        wrong_secret = "wrong_secret_key_here_1234567890"

        # Create token with wrong secret
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire, "type": "access"})
        token = jwt.encode(to_encode, wrong_secret, algorithm=settings.algorithm)

        # Should fail to decode
        with pytest.raises(JWTError):
            decode_token(token)

    def test_token_contains_required_claims(self):
        """Verify that tokens contain all required claims."""
        data = {"sub": "user123", "username": "test_user", "custom": "data"}
        token = create_access_token(data)

        payload = decode_token(token)

        # Required claims
        assert "sub" in payload
        assert "exp" in payload
        assert "type" in payload

        # Custom claims preserved
        assert payload["username"] == "test_user"
        assert payload["custom"] == "data"

    def test_access_and_refresh_tokens_are_different_types(self):
        """Verify that access and refresh tokens have different 'type' claims."""
        data = {"sub": "user123"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
        assert access_payload["type"] != refresh_payload["type"]
