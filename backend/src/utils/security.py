"""
Security utilities for password hashing and JWT token management.

Implements bcrypt password hashing with configurable rounds and JWT encode/decode
for access and refresh tokens.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings

# Password hashing context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_rounds,
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string (60 characters)

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> len(hashed)
        60
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time, defaults to settings

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "user_id", "username": "maria"})
        >>> # Token valid for 15 minutes (default)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time, defaults to settings

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_refresh_token({"sub": "user_id", "jti": "unique_token_id"})
        >>> # Token valid for 30 days (default)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired

    Example:
        >>> token = create_access_token({"sub": "user_id"})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        'user_id'
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        raise JWTError(f"Could not validate token: {str(e)}")


def get_token_subject(token: str) -> Optional[str]:
    """
    Extract the subject (user ID) from a token.

    Args:
        token: JWT token string

    Returns:
        User ID from token subject, or None if invalid

    Example:
        >>> token = create_access_token({"sub": "user_123"})
        >>> get_token_subject(token)
        'user_123'
    """
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None
