"""
Statistics and Achievements models.

UserStats: Aggregated user cycling statistics
Achievement: Achievement/badge definitions
UserAchievement: User-earned achievements (join table)
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, String, Text, DateTime, Integer, Float, ForeignKey, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class UserStats(Base):
    """
    UserStats model for aggregated user statistics.

    Automatically updated when trips are published, edited, or deleted.
    1-to-1 relationship with User.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User (1-to-1)
        total_trips: Number of published trips
        total_kilometers: Total distance in kilometers
        countries_visited: List of ISO country codes (stored as JSON)
        total_photos: Total photos uploaded across all trips
        achievements_count: Number of achievements earned
        last_trip_date: Date of most recent trip
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "user_stats"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique stats record identifier (UUID)",
    )

    # Foreign key (1-to-1 with User)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Foreign key to User (1-to-1)",
    )

    # Stats fields
    total_trips: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of published trips",
    )

    total_kilometers: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Total kilometers accumulated across all trips",
    )

    countries_visited: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="List of ISO country codes visited (e.g., ['ES', 'FR', 'IT'])",
    )

    total_photos: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total photos uploaded across all trips",
    )

    achievements_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of achievements earned",
    )

    last_trip_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date of most recent trip",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Record creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp (UTC)",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="stats",
        doc="1-to-1 relationship with User",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<UserStats(id={self.id}, user_id={self.user_id}, "
            f"trips={self.total_trips}, km={self.total_kilometers})>"
        )


class Achievement(Base):
    """
    Achievement model for badge/achievement definitions.

    Defines all available achievements in the system.
    Achievements are awarded based on reaching specific milestones.

    Attributes:
        id: Primary key (UUID)
        code: Unique achievement code (e.g., FIRST_TRIP, CENTURY)
        name: Display name in Spanish (e.g., "Primer Viaje")
        description: Achievement description (e.g., "Publicaste tu primer viaje")
        badge_icon: Emoji or icon for the badge (e.g., "🚴")
        requirement_type: Type of milestone (distance, trips, countries, photos, followers)
        requirement_value: Value required to unlock (e.g., 100 for 100km)
        created_at: Record creation timestamp
    """

    __tablename__ = "achievements"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique achievement identifier (UUID)",
    )

    # Achievement definition
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique achievement code (FIRST_TRIP, CENTURY, etc.)",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Achievement display name in Spanish",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Achievement description explaining how to earn it",
    )

    badge_icon: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="Emoji or icon for the badge (e.g., 🚴, 💯)",
    )

    requirement_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Type of requirement: distance, trips, countries, photos, followers",
    )

    requirement_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Value required to unlock achievement",
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Achievement creation timestamp (UTC)",
    )

    # Relationships
    user_achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
        doc="Users who have earned this achievement",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Achievement(code={self.code}, name={self.name}, "
            f"requirement={self.requirement_type}:{self.requirement_value})>"
        )


class UserAchievement(Base):
    """
    UserAchievement model for user-earned achievements (join table).

    Tracks when users earn specific achievements.
    Many-to-many relationship between User and Achievement.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        achievement_id: Foreign key to Achievement
        awarded_at: Timestamp when achievement was earned
    """

    __tablename__ = "user_achievements"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique user achievement record identifier (UUID)",
    )

    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to User",
    )

    achievement_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to Achievement",
    )

    # Award timestamp
    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp when achievement was earned (UTC)",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_achievements",
        doc="User who earned this achievement",
    )

    achievement: Mapped["Achievement"] = relationship(
        "Achievement",
        back_populates="user_achievements",
        doc="Achievement definition",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<UserAchievement(user_id={self.user_id}, "
            f"achievement_id={self.achievement_id}, awarded_at={self.awarded_at})>"
        )
