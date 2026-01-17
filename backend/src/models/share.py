"""
Share model for trip sharing.

Allows users to share trips with optional commentary.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.trip import Trip
    from src.models.user import User


class Share(Base):
    """
    T115: Share model for trip sharing (FR-026).

    Tracks users sharing trips with optional commentary.

    Fields:
        - comment: Optional share commentary (0-200 chars, FR-027)

    Constraints:
        - CASCADE delete when user or trip deleted

    Indexes:
        - trip_id: Fast lookup of trip shares count (FR-030)
        - user_id: Fast lookup of user's shares
        - created_at: Chronological ordering
    """

    __tablename__ = "shares"

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
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Optional commentary (max 200 chars)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="shares",
    )
    trip: Mapped["Trip"] = relationship(
        "Trip",
        foreign_keys=[trip_id],
        back_populates="shares",
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_shares_trip_id", "trip_id"),
        Index("ix_shares_user_id", "user_id"),
        Index("ix_shares_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Share(id={self.id}, user_id={self.user_id}, trip_id={self.trip_id})>"
