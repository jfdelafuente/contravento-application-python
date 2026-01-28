"""
Point of Interest (POI) Model

Feature 003 - User Story 4: Points of Interest along routes

Defines markers for interesting locations along trip routes (viewpoints, towns,
water sources, accommodation, restaurants).
"""

import uuid
from datetime import UTC, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.trip import Trip


class POIType(str, PyEnum):
    """Enumeration of Point of Interest types.

    FR-029: POI types for categorization and filtering.
    """

    VIEWPOINT = "viewpoint"  # Mirador
    TOWN = "town"  # Pueblo
    WATER = "water"  # Fuente de agua
    ACCOMMODATION = "accommodation"  # Alojamiento
    RESTAURANT = "restaurant"  # Restaurante
    MOUNTAIN_PASS = "mountain_pass"  # Puerto de montaña
    OTHER = "other"  # Otro


class PointOfInterest(Base):
    """Point of Interest (POI) along a trip route.

    Represents a location marked by the user as interesting or useful along
    their cycling route (e.g., viewpoint, water source, accommodation).

    FR-029: POIs can be added to published trips
    SC-029: Maximum 20 POIs per trip (enforced at service layer)
    SC-030: POIs display on map with distinctive icons by type
    SC-031: Clicking POI shows popup with details
    """

    __tablename__ = "points_of_interest"

    poi_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(
        String(36),
        ForeignKey("trips.trip_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # POI details
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    poi_type = Column(
        Enum(
            POIType,
            name="poi_type_enum",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )

    # Geospatial coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    distance_from_start_km = Column(Float, nullable=True)

    # Optional photo
    photo_url = Column(String(500), nullable=True)

    # Ordering
    sequence = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="points_of_interest")

    # Table constraints
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="check_poi_latitude_range"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="check_poi_longitude_range"),
    )

    def __repr__(self) -> str:
        return (
            f"<PointOfInterest(poi_id={self.poi_id}, "
            f"trip_id={self.trip_id}, "
            f"name='{self.name}', "
            f"type={self.poi_type.value}, "
            f"lat={self.latitude}, lng={self.longitude})>"
        )
