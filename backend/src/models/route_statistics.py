"""
SQLAlchemy model for Route Statistics (Feature 003 - User Story 5).

Defines RouteStatistics model for storing advanced statistics from GPS routes,
including speed metrics, time analysis, gradient distribution, and top climbs.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.types import JSON, TypeDecorator

from src.database import Base


def generate_uuid() -> str:
    """Generate UUID string for primary keys."""
    return str(uuid.uuid4())


class JSONType(TypeDecorator):
    """
    Cross-database JSON type.

    Uses PostgreSQL JSONB for efficiency in production.
    Falls back to JSON (stored as TEXT) in SQLite for development/testing.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class RouteStatistics(Base):
    """
    RouteStatistics model - Advanced analytics for GPS routes.

    Stores calculated statistics for GPX files including:
    - Speed metrics (average, maximum)
    - Time analysis (total time, moving time)
    - Gradient analysis (average, maximum)
    - Top climbs (hardest 3 climbs with details)

    Requirements:
    - Only calculated if GPX file has timestamps (has_timestamps=True)
    - One-to-one relationship with GPXFile
    - Automatically deleted when parent GPXFile is deleted (CASCADE)

    Validation rules:
    - avg_speed_kmh: < 100 km/h (cycling realistic average speeds)
    - max_speed_kmh: < 200 km/h (allows for steep descents)
    - total_time_minutes >= moving_time_minutes
    - top_climbs: max 3 climbs, JSON array format
    """

    __tablename__ = "route_statistics"

    # Primary key
    stats_id = Column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key (one-to-one relationship with GPXFile)
    gpx_file_id = Column(
        String(36),
        ForeignKey("gpx_files.gpx_file_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Speed metrics (km/h)
    avg_speed_kmh = Column(Float, nullable=True)  # Average speed over entire route
    max_speed_kmh = Column(Float, nullable=True)  # Maximum speed reached

    # Time metrics (minutes)
    total_time_minutes = Column(Float, nullable=True)  # Total elapsed time
    moving_time_minutes = Column(Float, nullable=True)  # Time in motion (excludes stops)

    # Gradient metrics (percentage)
    avg_gradient = Column(Float, nullable=True)  # Average gradient over route
    max_gradient = Column(Float, nullable=True)  # Maximum gradient (steepest uphill)

    # Top climbs (JSON array of climb objects)
    # Format: [{"start_km": 10.5, "end_km": 12.3, "elevation_gain_m": 150.0, "avg_gradient": 8.5, "description": "Climb 1"}]
    top_climbs = Column(JSONType, nullable=True)  # Top 3 hardest climbs

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )  # When statistics were calculated

    # Relationships
    gpx_file: Mapped["GPXFile"] = relationship(
        "GPXFile",
        back_populates="route_statistics",
    )  # type: ignore

    def __repr__(self) -> str:
        return (
            f"<RouteStatistics(stats_id={self.stats_id}, "
            f"gpx_file_id={self.gpx_file_id}, avg_speed={self.avg_speed_kmh})>"
        )
