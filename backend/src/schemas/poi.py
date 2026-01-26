"""
Point of Interest (POI) schemas.

Feature 003 - User Story 4: Points of Interest along routes

Pydantic models for POI request/response validation in API.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class POITypeEnum(str, Enum):
    """
    POI type enumeration.

    FR-029: Types for categorizing points of interest.
    """

    VIEWPOINT = "viewpoint"  # Mirador
    TOWN = "town"  # Pueblo
    WATER = "water"  # Fuente de agua
    ACCOMMODATION = "accommodation"  # Alojamiento
    RESTAURANT = "restaurant"  # Restaurante
    MOUNTAIN_PASS = "mountain_pass"  # Puerto de montaña
    OTHER = "other"  # Otro


# ============================================================================
# Request Schemas (Input)
# ============================================================================


class POICreateInput(BaseModel):
    """
    Input schema for creating a new POI.

    FR-029: Users can add POIs to published trips
    SC-029: Maximum 20 POIs per trip (enforced at service layer)

    Attributes:
        name: POI name (1-100 chars, e.g., "Mirador del Valle")
        description: Optional description (max 500 chars)
        poi_type: Type of POI (viewpoint, town, water, accommodation, restaurant, other)
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        distance_from_start_km: Optional distance from route start
        photo_url: Optional photo URL (max 500 chars)
        sequence: Order position in trip (0-based index)
    """

    name: str = Field(..., min_length=1, max_length=100, description="Nombre del punto de interés")
    description: str | None = Field(
        None, max_length=500, description="Descripción opcional (max 500 caracteres)"
    )
    poi_type: POITypeEnum = Field(
        ..., description="Tipo de POI (viewpoint, town, water, accommodation, restaurant, mountain_pass, other)"
    )
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitud (-90 a 90 grados)")
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Longitud (-180 a 180 grados)"
    )
    distance_from_start_km: float | None = Field(
        None, ge=0.0, description="Distancia desde el inicio de la ruta (km)"
    )
    photo_url: str | None = Field(None, max_length=500, description="URL de foto opcional")
    sequence: int = Field(..., ge=0, description="Orden del POI en la ruta (índice 0-based)")

    @field_validator("latitude", "longitude")
    @classmethod
    def round_coordinates(cls, v: float | None) -> float | None:
        """Enforce 6 decimal places precision for coordinates (~11cm accuracy)."""
        if v is None:
            return v
        return round(v, 6)

    @field_validator("latitude")
    @classmethod
    def validate_latitude_range(cls, v: float | None) -> float | None:
        """Validate latitude range with Spanish error message."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError("Latitud debe estar entre -90 y 90 grados")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude_range(cls, v: float | None) -> float | None:
        """Validate longitude range with Spanish error message."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError("Longitud debe estar entre -180 y 180 grados")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "Mirador del Valle",
                "description": "Vistas panorámicas de la sierra",
                "poi_type": "viewpoint",
                "latitude": 40.7261,
                "longitude": -4.0245,
                "distance_from_start_km": 8.5,
                "photo_url": None,
                "sequence": 0,
            }
        }


class POIUpdateInput(BaseModel):
    """
    Input schema for updating an existing POI.

    All fields are optional - only provided fields will be updated.

    Attributes:
        name: POI name (1-100 chars)
        description: Optional description (max 500 chars)
        poi_type: Type of POI
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        distance_from_start_km: Optional distance from route start
        photo_url: Optional photo URL (max 500 chars)
        sequence: Order position in trip
    """

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    poi_type: POITypeEnum | None = None
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    distance_from_start_km: float | None = Field(None, ge=0.0)
    photo_url: str | None = Field(None, max_length=500)
    sequence: int | None = Field(None, ge=0)

    @field_validator("latitude", "longitude")
    @classmethod
    def round_coordinates(cls, v: float | None) -> float | None:
        """Enforce 6 decimal places precision for coordinates."""
        if v is None:
            return v
        return round(v, 6)

    @field_validator("latitude")
    @classmethod
    def validate_latitude_range(cls, v: float | None) -> float | None:
        """Validate latitude range with Spanish error message."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError("Latitud debe estar entre -90 y 90 grados")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude_range(cls, v: float | None) -> float | None:
        """Validate longitude range with Spanish error message."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError("Longitud debe estar entre -180 y 180 grados")
        return v


class POIReorderInput(BaseModel):
    """
    Input schema for reordering POIs.

    FR-029: Users can reorder POIs without affecting GPX route

    Attributes:
        poi_ids: Ordered list of POI IDs (must include all POIs from trip)
    """

    poi_ids: list[str] = Field(
        ..., min_length=1, max_length=20, description="Lista ordenada de POI IDs"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "poi_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "550e8400-e29b-41d4-a716-446655440001",
                    "550e8400-e29b-41d4-a716-446655440002",
                ]
            }
        }


# ============================================================================
# Response Schemas (Output)
# ============================================================================


class POIResponse(BaseModel):
    """
    Response schema for a single POI.

    SC-030: POIs display on map with distinctive icons by type
    SC-031: Clicking POI shows popup with name, description, photo, distance

    Attributes:
        poi_id: POI unique identifier
        trip_id: Parent trip ID
        name: POI name
        description: Optional description
        poi_type: Type of POI
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        distance_from_start_km: Distance from route start
        photo_url: Optional photo URL
        sequence: Order position in trip
        created_at: Creation timestamp
    """

    poi_id: str
    trip_id: str
    name: str
    description: str | None
    poi_type: POITypeEnum
    latitude: float
    longitude: float
    distance_from_start_km: float | None
    photo_url: str | None
    sequence: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "poi_id": "550e8400-e29b-41d4-a716-446655440000",
                "trip_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Mirador del Valle",
                "description": "Vistas panorámicas de la sierra",
                "poi_type": "viewpoint",
                "latitude": 40.7261,
                "longitude": -4.0245,
                "distance_from_start_km": 8.5,
                "photo_url": "https://example.com/photos/mirador.jpg",
                "sequence": 0,
                "created_at": "2024-01-26T12:00:00Z",
            }
        }


class POIListResponse(BaseModel):
    """
    Response schema for listing multiple POIs.

    Attributes:
        pois: List of POIs (ordered by sequence)
        total: Total count of POIs
    """

    pois: list[POIResponse]
    total: int

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "pois": [
                    {
                        "poi_id": "550e8400-e29b-41d4-a716-446655440000",
                        "trip_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Mirador del Valle",
                        "description": "Vistas panorámicas",
                        "poi_type": "viewpoint",
                        "latitude": 40.7261,
                        "longitude": -4.0245,
                        "distance_from_start_km": 8.5,
                        "photo_url": None,
                        "sequence": 0,
                        "created_at": "2024-01-26T12:00:00Z",
                    }
                ],
                "total": 1,
            }
        }
