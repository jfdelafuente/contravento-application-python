"""
Like model for trip likes.

Simple interaction model tracking which users liked which trips.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.trip import Trip
    from src.models.user import User


class Like(Base):
    """
    T052: Like model for trip likes (FR-009).

    Tracks user likes on published trips.

    Constraints:
        - Unique (user_id, trip_id): User can like trip only once (FR-010)
        - CASCADE delete when user or trip deleted

    Indexes:
        - trip_id: Fast lookup of trip likes count (FR-012)
        - user_id: Fast lookup of user's liked trips (FR-014)
        - created_at: Chronological ordering
    """

    __tablename__ = "likes"

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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="likes",
    )
    trip: Mapped["Trip"] = relationship(
        "Trip",
        foreign_keys=[trip_id],
        back_populates="likes",
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "trip_id", name="uq_user_trip_like"),
        Index("ix_likes_trip_id", "trip_id"),
        Index("ix_likes_user_id", "user_id"),
        Index("ix_likes_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Like(user_id={self.user_id}, trip_id={self.trip_id})>"
