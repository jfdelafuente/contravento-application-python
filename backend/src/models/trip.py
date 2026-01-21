"""
SQLAlchemy models for Travel Diary feature.

Defines Trip, TripPhoto, Tag, TripTag, and TripLocation models.
Supports both PostgreSQL (production) and SQLite (development/testing).
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, relationship

from src.database import Base


def generate_uuid() -> str:
    """Generate UUID string for primary keys."""
    return str(uuid.uuid4())


class TripStatus(str, enum.Enum):
    """Trip publication status."""

    DRAFT = "draft"  # Not published, only visible to owner
    PUBLISHED = "published"  # Published, visible to others


class TripDifficulty(str, enum.Enum):
    """Trip difficulty levels."""

    EASY = "easy"  # Fácil
    MODERATE = "moderate"  # Moderada
    DIFFICULT = "difficult"  # Difícil
    VERY_DIFFICULT = "very_difficult"  # Muy Difícil


class Trip(Base):
    """
    Trip model - Main entity for travel diary entries.

    Represents a cycling trip with all its details: route, photos, tags, locations.
    """

    __tablename__ = "trips"

    # Primary key
    trip_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Core fields
    title = Column(String(200), nullable=False)  # Trip title
    description = Column(Text, nullable=False)  # Rich text description (HTML)
    status = Column(
        Enum(TripStatus, native_enum=False, length=20),
        nullable=False,
        default=TripStatus.DRAFT,
    )

    # Trip details
    start_date = Column(Date, nullable=False)  # When trip started
    end_date = Column(Date, nullable=True)  # When trip ended (optional)
    distance_km = Column(Float, nullable=True)  # Distance in kilometers
    difficulty = Column(
        Enum(TripDifficulty, native_enum=False, length=20),
        nullable=True,
    )

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    published_at = Column(DateTime(timezone=True), nullable=True)  # When first published

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="trips")  # type: ignore
    photos: Mapped[list["TripPhoto"]] = relationship(
        "TripPhoto",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripPhoto.order",
    )
    locations: Mapped[list["TripLocation"]] = relationship(
        "TripLocation",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripLocation.sequence",
    )
    trip_tags: Mapped[list["TripTag"]] = relationship(
        "TripTag",
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    # Social network relationships (Feature 004)
    likes: Mapped[list["Like"]] = relationship(
        "Like",
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    shares: Mapped[list["Share"]] = relationship(
        "Share",
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_trip_user_status", "user_id", "status"),  # List user's trips by status
        Index("idx_trip_created", "created_at"),  # Sort by creation date
        Index("idx_trip_published", "published_at"),  # Filter published trips
    )

    def __repr__(self) -> str:
        return f"<Trip(trip_id={self.trip_id}, title={self.title}, status={self.status})>"


class TripPhoto(Base):
    """
    TripPhoto model - Photos attached to trips.

    Stores both optimized and thumbnail versions of trip photos.
    """

    __tablename__ = "trip_photos"

    # Primary key
    photo_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Foreign keys
    trip_id = Column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), nullable=False)

    # Photo storage paths
    photo_url = Column(String(500), nullable=False)  # Path to optimized version
    thumb_url = Column(String(500), nullable=False)  # Path to thumbnail

    # Photo metadata
    caption = Column(String(500), nullable=True)  # Optional caption
    order = Column(
        Integer, nullable=False, default=0
    )  # Order in gallery (renamed from display_order)
    file_size = Column(Integer, nullable=False, default=0)  # File size in bytes
    width = Column(Integer, nullable=False, default=0)  # Image width in pixels
    height = Column(Integer, nullable=False, default=0)  # Image height in pixels

    # Metadata
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="photos")

    # Indexes
    __table_args__ = (
        Index("idx_photo_trip", "trip_id"),  # Find photos by trip
        Index("idx_photo_order", "trip_id", "order"),  # Ordered gallery
    )

    # Property mappings for schema compatibility
    @property
    def id(self) -> str:
        """Map photo_id to id for backward compatibility."""
        return self.photo_id

    @property
    def thumbnail_url(self) -> str:
        """Map thumb_url to thumbnail_url for schema compatibility."""
        return self.thumb_url

    @thumbnail_url.setter
    def thumbnail_url(self, value: str) -> None:
        """Allow setting thumbnail_url by writing to thumb_url."""
        self.thumb_url = value

    @property
    def display_order(self) -> int:
        """Map order to display_order for schema compatibility."""
        return self.order

    @display_order.setter
    def display_order(self, value: int) -> None:
        """Allow setting display_order by writing to order."""
        self.order = value

    def __repr__(self) -> str:
        return f"<TripPhoto(photo_id={self.photo_id}, trip_id={self.trip_id})>"


class Tag(Base):
    """
    Tag model - Tags for categorizing trips.

    Uses normalized lowercase for matching while preserving display format.
    """

    __tablename__ = "tags"

    # Primary key
    tag_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Tag names
    name = Column(String(50), nullable=False, unique=True)  # Display name (original case)
    normalized = Column(String(50), nullable=False, unique=True)  # Lowercase for matching

    # Usage counter
    usage_count = Column(Integer, nullable=False, default=0)  # How many trips use this tag

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    # Relationships
    trip_tags: Mapped[list["TripTag"]] = relationship(
        "TripTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_tag_normalized", "normalized"),  # Fast case-insensitive lookup
        Index("idx_tag_usage", "usage_count"),  # Popular tags
    )

    def __repr__(self) -> str:
        return f"<Tag(tag_id={self.tag_id}, name={self.name}, usage={self.usage_count})>"


class TripTag(Base):
    """
    TripTag model - Many-to-many association between Trips and Tags.

    Junction table linking trips to their tags.
    """

    __tablename__ = "trip_tags"

    # Composite primary key
    trip_id = Column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(String(36), ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="trip_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="trip_tags")

    # Indexes
    __table_args__ = (
        Index("idx_trip_tag_trip", "trip_id"),  # Find tags for a trip
        Index("idx_trip_tag_tag", "tag_id"),  # Find trips with a tag
    )

    def __repr__(self) -> str:
        return f"<TripTag(trip_id={self.trip_id}, tag_id={self.tag_id})>"


class TripLocation(Base):
    """
    TripLocation model - Locations/waypoints along the trip route.

    Stores location name and optional coordinates (if geocoded).
    """

    __tablename__ = "trip_locations"

    # Primary key
    location_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Foreign keys
    trip_id = Column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), nullable=False)

    # Location data
    name = Column(
        String(200), nullable=False
    )  # Location name (e.g., "Madrid", "Camino de Santiago")
    latitude = Column(Float, nullable=True)  # Decimal degrees (optional, from geocoding)
    longitude = Column(Float, nullable=True)  # Decimal degrees (optional, from geocoding)
    sequence = Column(Integer, nullable=False)  # Order along route (0 = start, 1 = next, etc.)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="locations")

    # Indexes
    __table_args__ = (
        Index("idx_location_trip", "trip_id"),  # Find locations for a trip
        Index("idx_location_sequence", "trip_id", "sequence"),  # Ordered route
    )

    def __repr__(self) -> str:
        return (
            f"<TripLocation(location_id={self.location_id}, name={self.name}, seq={self.sequence})>"
        )
