"""
Authentication-related models.

PasswordReset: Tokens for email verification and password reset
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PasswordReset(Base):
    """
    PasswordReset model for verification and reset tokens.

    Stores hashed tokens for email verification and password reset flows.
    Each token has a type, expiration, and usage tracking.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        token_hash: Hashed token (bcrypt) for security
        token_type: Type of token (email_verification, password_reset)
        expires_at: Token expiration timestamp
        used_at: Timestamp when token was used (null = unused)
        created_at: Token creation timestamp
    """

    __tablename__ = "password_resets"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique token identifier (UUID)",
    )

    # Foreign key to User
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to User",
    )

    # Token data
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed token (bcrypt) for security",
    )

    token_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        doc="Type of token: email_verification, password_reset, refresh_token",
    )

    # Token metadata
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Token expiration timestamp (UTC)",
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when token was used (null = unused)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Token creation timestamp (UTC)",
    )

    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name conflict)
    extra_metadata: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional JSON metadata (e.g., IP address, user agent)",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="password_resets",
        doc="Relationship with User",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<PasswordReset(id={self.id}, user_id={self.user_id}, "
            f"type={self.token_type}, used={'Yes' if self.used_at else 'No'})>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self) -> bool:
        """Check if token has been used."""
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired and not self.is_used
