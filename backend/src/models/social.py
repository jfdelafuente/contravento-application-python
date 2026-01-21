"""
Social features models.

Models for follow relationships and social interactions.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.user import User


class Follow(Base):
    """
    T198: Follow relationship model.

    Represents a follower-following relationship between users.

    Constraints:
    - Unique (follower_id, following_id): No duplicate follows
    - CHECK: follower_id != following_id (prevent self-follow)

    Indexes:
    - follower_id: Fast lookup of who a user follows
    - following_id: Fast lookup of a user's followers
    - created_at: Chronological ordering
    """

    __tablename__ = "follows"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    follower_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    following_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following",
    )
    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "follower_id",
            "following_id",
            name="uq_follower_following",
        ),
        CheckConstraint(
            "follower_id != following_id",
            name="ck_no_self_follow",
        ),
        Index("ix_follows_follower_id", "follower_id"),
        Index("ix_follows_following_id", "following_id"),
        Index("ix_follows_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Follow(follower_id={self.follower_id}, following_id={self.following_id})>"
