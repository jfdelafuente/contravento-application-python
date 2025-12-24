"""
Custom Pydantic validators for user input.

Provides validation functions for username, email, and other user-submitted data.
"""

import re
from typing import Any

from pydantic import field_validator


# Username validation pattern: 3-30 alphanumeric characters and underscores
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

# Email validation pattern (basic)
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Password minimum requirements
PASSWORD_MIN_LENGTH = 8


def validate_username(value: str) -> str:
    """
    Validate username format.

    Rules (FR-003):
    - 3-30 characters
    - Only alphanumeric and underscores
    - No spaces or special characters

    Args:
        value: Username to validate

    Returns:
        Validated username (lowercase)

    Raises:
        ValueError: If username doesn't meet requirements

    Example:
        >>> validate_username("maria_garcia")
        'maria_garcia'
        >>> validate_username("ab")
        ValueError: El nombre de usuario debe tener entre 3 y 30 caracteres
    """
    if not value:
        raise ValueError("El nombre de usuario es requerido")

    if len(value) < 3:
        raise ValueError("El nombre de usuario debe tener entre 3 y 30 caracteres")

    if len(value) > 30:
        raise ValueError("El nombre de usuario debe tener entre 3 y 30 caracteres")

    if not USERNAME_PATTERN.match(value):
        raise ValueError(
            "El nombre de usuario solo puede contener letras, números y guiones bajos"
        )

    return value.lower()


def validate_email(value: str) -> str:
    """
    Validate email format.

    Rules (FR-002):
    - Valid email format
    - Case-insensitive

    Args:
        value: Email to validate

    Returns:
        Validated email (lowercase)

    Raises:
        ValueError: If email format is invalid

    Example:
        >>> validate_email("maria@example.com")
        'maria@example.com'
        >>> validate_email("invalid-email")
        ValueError: El formato del email no es válido
    """
    if not value:
        raise ValueError("El email es requerido")

    if not EMAIL_PATTERN.match(value):
        raise ValueError("El formato del email no es válido")

    return value.lower()


def validate_password(value: str) -> str:
    """
    Validate password strength.

    Rules (FR-004):
    - Minimum 8 characters
    - Maximum 72 bytes (bcrypt limitation)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    Args:
        value: Password to validate

    Returns:
        Validated password (unchanged)

    Raises:
        ValueError: If password doesn't meet requirements

    Example:
        >>> validate_password("SecurePass123")
        'SecurePass123'
        >>> validate_password("weak")
        ValueError: La contraseña debe tener al menos 8 caracteres
    """
    if not value:
        raise ValueError("La contraseña es requerida")

    if len(value) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres")

    # Bcrypt has a 72-byte limitation
    if len(value.encode('utf-8')) > 72:
        raise ValueError("La contraseña no puede exceder 72 bytes")

    if not re.search(r"[A-Z]", value):
        raise ValueError("La contraseña debe contener al menos una letra mayúscula")

    if not re.search(r"[a-z]", value):
        raise ValueError("La contraseña debe contener al menos una letra minúscula")

    if not re.search(r"[0-9]", value):
        raise ValueError("La contraseña debe contener al menos un número")

    return value


def validate_bio(value: str) -> str:
    """
    Validate biography text.

    Rules (FR-014):
    - Maximum 500 characters

    Args:
        value: Bio text to validate

    Returns:
        Validated bio (stripped)

    Raises:
        ValueError: If bio exceeds limit

    Example:
        >>> validate_bio("Amante del ciclismo de montaña")
        'Amante del ciclismo de montaña'
    """
    if not value:
        return ""

    value = value.strip()

    if len(value) > 500:
        raise ValueError("La biografía no puede superar 500 caracteres")

    return value


def validate_cycling_type(value: str) -> str:
    """
    Validate cycling type.

    Rules (FR-015):
    - Must be one of: road, mountain, gravel, touring, commuting

    Args:
        value: Cycling type to validate

    Returns:
        Validated cycling type (lowercase)

    Raises:
        ValueError: If cycling type is invalid

    Example:
        >>> validate_cycling_type("mountain")
        'mountain'
    """
    if not value:
        return None

    allowed_types = {"road", "mountain", "gravel", "touring", "commuting"}
    value_lower = value.lower()

    if value_lower not in allowed_types:
        raise ValueError(
            f"El tipo de ciclismo debe ser uno de: {', '.join(allowed_types)}"
        )

    return value_lower
