"""
Comment model for trip comments.

Allows users to comment on published trips with moderation capabilities.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.trip import Trip
    from src.models.user import User


class Comment(Base):
    """
    T084: Comment model for trip comments (FR-016).

    Tracks user comments on published trips with edit history.

    Fields:
        - content: Comment text (1-500 chars after sanitization, FR-017)
        - is_edited: Flag indicating if comment was modified (FR-020)
        - updated_at: Timestamp of last edit (FR-019)

    Constraints:
        - CASCADE delete when user or trip deleted
        - Content must not be empty after trimming

    Indexes:
        - trip_id: Fast lookup of trip comments (FR-018)
        - user_id: Fast lookup of user's comments
        - created_at: Chronological ordering (oldest first, FR-018)
    """

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trip_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("trips.trip_id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )  # Sanitized plain text (no HTML)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="comments",
    )
    trip: Mapped["Trip"] = relationship(
        "Trip",
        foreign_keys=[trip_id],
        back_populates="comments",
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_comments_trip_id", "trip_id"),
        Index("ix_comments_user_id", "user_id"),
        Index("ix_comments_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, trip_id={self.trip_id}, user_id={self.user_id})>"
