"""
SQLAlchemy models for GPS Routes feature (Feature 003).

Defines GPXFile and TrackPoint models for storing and managing GPS route data.
Supports both PostgreSQL (production) and SQLite (development/testing).
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, relationship

from src.database import Base


def generate_uuid() -> str:
    """Generate UUID string for primary keys."""
    return str(uuid.uuid4())


class GPXFile(Base):
    """
    GPXFile model - Metadata and processing results for uploaded GPX files.

    Represents a GPX file attached to a trip, including:
    - Original file metadata (url, size, name)
    - Processing status (pending, processing, completed, error)
    - Route statistics (distance, elevation, bounds)
    - Track simplification metadata (total_points vs simplified_points)
    """

    __tablename__ = "gpx_files"

    # Primary key
    gpx_file_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Foreign keys
    trip_id = Column(
        String(36),
        ForeignKey("trips.trip_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # File storage metadata
    file_url = Column(String(500), nullable=False)  # Path to original GPX file
    file_size = Column(Integer, nullable=False)  # File size in bytes
    file_name = Column(String(255), nullable=False)  # Original filename

    # Route statistics
    distance_km = Column(Float, nullable=False)  # Total distance in kilometers
    elevation_gain = Column(Float, nullable=True)  # Total elevation gain in meters
    elevation_loss = Column(Float, nullable=True)  # Total elevation loss in meters
    max_elevation = Column(Float, nullable=True)  # Maximum elevation in meters
    min_elevation = Column(Float, nullable=True)  # Minimum elevation in meters

    # Route bounds (first and last coordinates)
    start_lat = Column(Float, nullable=False)  # Starting latitude
    start_lon = Column(Float, nullable=False)  # Starting longitude
    end_lat = Column(Float, nullable=False)  # Ending latitude
    end_lon = Column(Float, nullable=False)  # Ending longitude

    # Track simplification metadata
    total_points = Column(Integer, nullable=False)  # Original trackpoint count
    simplified_points = Column(Integer, nullable=False)  # Simplified trackpoint count

    # GPX content flags
    has_elevation = Column(Boolean, nullable=False)  # Whether GPX includes elevation data
    has_timestamps = Column(Boolean, nullable=False)  # Whether GPX includes timestamps

    # Processing status
    processing_status = Column(
        String(20),
        nullable=False,
        default="pending",
    )  # pending, processing, completed, error
    error_message = Column(Text, nullable=True)  # Error details if processing failed

    # Timestamps
    uploaded_at = Column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
    )  # When file was uploaded
    processed_at = Column(TIMESTAMP, nullable=True)  # When processing completed

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="gpx_file")  # type: ignore
    track_points: Mapped[List["TrackPoint"]] = relationship(
        "TrackPoint",
        back_populates="gpx_file",
        order_by="TrackPoint.sequence",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<GPXFile(gpx_file_id={self.gpx_file_id}, "
            f"trip_id={self.trip_id}, status={self.processing_status})>"
        )


class TrackPoint(Base):
    """
    TrackPoint model - Individual GPS coordinates along the route.

    Stores simplified trackpoints from the GPX file with:
    - Geographic coordinates (latitude, longitude, elevation)
    - Cumulative distance from route start
    - Sequence number for ordering
    - Calculated gradient (% slope)
    """

    __tablename__ = "track_points"

    # Primary key
    point_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Foreign keys
    gpx_file_id = Column(
        String(36),
        ForeignKey("gpx_files.gpx_file_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Geographic coordinates
    latitude = Column(Float, nullable=False)  # Latitude in decimal degrees
    longitude = Column(Float, nullable=False)  # Longitude in decimal degrees
    elevation = Column(Float, nullable=True)  # Elevation in meters (nullable if no elevation data)

    # Route progression
    distance_km = Column(Float, nullable=False)  # Cumulative distance from start in kilometers
    sequence = Column(Integer, nullable=False)  # Order in route (0, 1, 2, ...)

    # Calculated metrics
    gradient = Column(Float, nullable=True)  # Gradient in % (rise/run * 100)

    # Relationships
    gpx_file: Mapped["GPXFile"] = relationship("GPXFile", back_populates="track_points")

    def __repr__(self) -> str:
        return (
            f"<TrackPoint(point_id={self.point_id}, "
            f"gpx_file_id={self.gpx_file_id}, sequence={self.sequence})>"
        )
