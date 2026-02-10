"""
ActivityLike model for Activity Stream Feed (Feature 018).

Represents likes on feed activities (TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED).
Separate from likes on trips (Feature 004).
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.activity_feed_item import ActivityFeedItem
    from src.models.user import User


class ActivityLike(Base):
    """
    T041: ActivityLike model for activity feed likes (US2 - FR-009).

    Tracks user likes on feed activities.

    Constraints:
        - Unique (user_id, activity_id): User can like activity only once (FR-010)
        - CASCADE delete when user or activity deleted

    Indexes:
        - activity_id: Fast lookup of activity likes count (FR-012)
        - user_id: Fast lookup of user's liked activities (FR-014)
        - created_at: Chronological ordering
    """

    __tablename__ = "activity_likes"

    like_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("activity_feed_items.activity_id", ondelete="CASCADE"),
        nullable=False,
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
        back_populates="activity_likes",
    )
    activity: Mapped["ActivityFeedItem"] = relationship(
        "ActivityFeedItem",
        foreign_keys=[activity_id],
        back_populates="likes",
    )

    # Constraints and indexes (T042)
    __table_args__ = (
        UniqueConstraint("user_id", "activity_id", name="uq_user_activity_like"),
        Index("idx_activity_likes_activity", "activity_id"),
        Index("idx_activity_likes_user", "user_id"),
        Index("idx_activity_likes_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ActivityLike(like_id={self.like_id}, user_id={self.user_id}, activity_id={self.activity_id})>"
