"""
Cursor-based pagination utilities for Activity Stream Feed (Feature 018).

Provides encode/decode functions for opaque cursor strings used in feed pagination.
Task: T016
"""

import base64
import json
from datetime import datetime
from typing import Any


def encode_cursor(created_at: datetime, activity_id: str) -> str:
    """
    Encode pagination cursor from timestamp and activity ID.

    Cursor format: base64-encoded JSON with created_at timestamp and activity_id.
    This allows efficient cursor-based pagination without offset/limit performance issues.

    Args:
        created_at: Activity creation timestamp
        activity_id: Activity unique identifier

    Returns:
        Opaque base64-encoded cursor string

    Example:
        >>> encode_cursor(datetime(2024, 6, 15, 10, 30, 0), "abc123")
        'eyJjcmVhdGVkX2F0IjogIjIwMjQtMDYtMTVUMTA6MzA6MDAiLCAiYWN0aXZpdHlfaWQiOiAiYWJjMTIzIn0='
    """
    cursor_data = {
        "created_at": created_at.isoformat(),
        "activity_id": activity_id,
    }

    # Encode to JSON, then base64
    json_str = json.dumps(cursor_data, separators=(",", ":"))
    cursor_bytes = json_str.encode("utf-8")
    encoded = base64.urlsafe_b64encode(cursor_bytes).decode("utf-8")

    return encoded


def decode_cursor(cursor: str) -> dict[str, Any]:
    """
    Decode pagination cursor to timestamp and activity ID.

    Args:
        cursor: Base64-encoded cursor string from encode_cursor()

    Returns:
        Dictionary with 'created_at' (datetime) and 'activity_id' (str)

    Raises:
        ValueError: If cursor is invalid or malformed

    Example:
        >>> decode_cursor('eyJjcmVhdGVkX2F0IjogIjIwMjQtMDYtMTVUMTA6MzA6MDAiLCAiYWN0aXZpdHlfaWQiOiAiYWJjMTIzIn0=')
        {'created_at': datetime(2024, 6, 15, 10, 30, 0), 'activity_id': 'abc123'}
    """
    try:
        # Decode from base64, then JSON
        cursor_bytes = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        json_str = cursor_bytes.decode("utf-8")
        cursor_data = json.loads(json_str)

        # Parse ISO timestamp back to datetime
        created_at = datetime.fromisoformat(cursor_data["created_at"])

        return {
            "created_at": created_at,
            "activity_id": cursor_data["activity_id"],
        }

    except (KeyError, json.JSONDecodeError, ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid cursor format: {str(e)}")


def validate_cursor(cursor: str | None) -> bool:
    """
    Validate cursor format without raising exceptions.

    Args:
        cursor: Cursor string to validate (or None)

    Returns:
        True if cursor is valid or None, False otherwise

    Example:
        >>> validate_cursor(None)
        True
        >>> validate_cursor('eyJjcmVhdGVkX2F0IjogIjIwMjQtMDYtMTVUMTA6MzA6MDAiLCAiYWN0aXZpdHlfaWQiOiAiYWJjMTIzIn0=')
        True
        >>> validate_cursor('invalid_cursor')
        False
    """
    if cursor is None:
        return True

    try:
        decode_cursor(cursor)
        return True
    except ValueError:
        return False
