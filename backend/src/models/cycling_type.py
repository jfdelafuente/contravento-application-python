"""
CyclingType model for managing cycling type categories.

Allows dynamic management of cycling types through database instead of hardcoded values.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CyclingType(Base):
    """
    CyclingType model - Dynamic cycling type categories.

    Stores available cycling types that users can select for their profile.
    Supports soft deletion via is_active flag.

    Attributes:
        id: Unique identifier (UUID)
        code: Unique code (e.g., 'bikepacking', 'mountain')
        display_name: Display name for UI (e.g., 'Bikepacking', 'Montaña (MTB)')
        description: Detailed description of the cycling type
        is_active: Whether this type is currently active/available
        created_at: When this type was created
        updated_at: When this type was last updated
    """

    __tablename__ = "cycling_types"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique cycling type identifier (UUID)",
    )

    # Unique code (used in API and database references)
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique code (lowercase, e.g., 'bikepacking')",
    )

    # Display fields
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name for UI (e.g., 'Bikepacking')",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed description of this cycling type",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether this type is active and available for selection",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp (UTC)",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CyclingType(code={self.code}, display_name={self.display_name}, active={self.is_active})>"
