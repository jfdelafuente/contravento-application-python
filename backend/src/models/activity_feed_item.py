"""
ActivityFeedItem model for Activity Stream Feed (Feature 018).

Represents activities in the social feed (trip publications, photo uploads, achievements).
Task: T013
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.user import User


class ActivityType(str, enum.Enum):
    """
    Activity type enum (FR-002).

    Types:
        - TRIP_PUBLISHED: User published a trip
        - PHOTO_UPLOADED: User uploaded a photo to a trip
        - ACHIEVEMENT_UNLOCKED: User unlocked an achievement
    """

    TRIP_PUBLISHED = "TRIP_PUBLISHED"
    PHOTO_UPLOADED = "PHOTO_UPLOADED"
    ACHIEVEMENT_UNLOCKED = "ACHIEVEMENT_UNLOCKED"


class ActivityFeedItem(Base):
    """
    T013: ActivityFeedItem model for social activity stream.

    Represents an activity in the feed (trip published, photo uploaded, achievement unlocked).
    Activities are created automatically when users perform actions and are visible to their followers.

    Indexes:
        - (user_id, created_at DESC): Feed generation for user's activities (SC-001)
        - (activity_type, created_at DESC): Filter by activity type (FR-008)
        - (created_at DESC): Global chronological ordering (FR-003)

    Privacy:
        - Activities inherit privacy from source content (trips, photos)
        - Private trip publications don't create feed activities
    """

    __tablename__ = "activity_feed_items"

    activity_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type: Mapped[ActivityType] = mapped_column(
        String(30),
        nullable=False,
    )
    related_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )  # trip_id, photo_id, or user_achievement_id
    activity_metadata: Mapped[dict] = mapped_column(
        "metadata",  # Database column name
        Text,
        nullable=False,
        default="{}",
    )  # Stored as JSON string (SQLite) or JSONB (PostgreSQL)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="activity_feed_items",
    )

    # Indexes for performance (FR-027, SC-001)
    __table_args__ = (
        Index("idx_activities_user_created", "user_id", "created_at"),
        Index("idx_activities_type_created", "activity_type", "created_at"),
        Index("idx_activities_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ActivityFeedItem(activity_id={self.activity_id}, type={self.activity_type}, user_id={self.user_id})>"
