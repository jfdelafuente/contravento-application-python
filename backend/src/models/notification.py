"""
Notification models for social interactions.

Tracks user notifications for likes, comments, and shares.
Implements archiving strategy for old notifications (30-day retention).
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.trip import Trip
    from src.models.user import User


class NotificationType(str, enum.Enum):
    """
    Notification type enum (FR-034).

    Types:
        - LIKE: User liked a trip
        - COMMENT: User commented on a trip
        - SHARE: User shared a trip
    """

    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"


class Notification(Base):
    """
    T142: Notification model for social interactions.

    Tracks notifications sent to users when others interact with their trips.
    Notifications are archived after 30 days (FR-041).

    Indexes:
        - (user_id, is_read): Fast unread count queries (SC-030: <100ms)
        - created_at: Chronological ordering (FR-037)
    """

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[NotificationType] = mapped_column(
        String(20),
        nullable=False,
    )
    actor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trip_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("trips.trip_id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Comment excerpt for type=COMMENT (FR-035)
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="notifications",
    )
    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_id],
    )
    trip: Mapped["Trip"] = relationship(
        "Trip",
        foreign_keys=[trip_id],
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"


class NotificationArchive(Base):
    """
    T143: Archived notifications (30+ days old).

    Same structure as Notification but for historical data.
    Archived notifications are moved here via background job (FR-041).
    """

    __tablename__ = "notifications_archive"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trip_id: Mapped[str] = mapped_column(String(36), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    archived_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Indexes for querying archived notifications
    __table_args__ = (
        Index("ix_notifications_archive_user", "user_id"),
        Index("ix_notifications_archive_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<NotificationArchive(id={self.id}, archived_at={self.archived_at})>"
