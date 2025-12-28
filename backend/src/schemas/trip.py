"""
Trip schemas for Travel Diary feature.

Pydantic models for trip request/response validation in API.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


# ============================================================================
# Request Schemas (Input)
# ============================================================================


class LocationInput(BaseModel):
    """
    Location input for trip creation/update.

    Attributes:
        name: Location name (e.g., "Baeza", "Camino de Santiago")
        country: Country name (optional, e.g., "España")
    """

    name: str = Field(..., min_length=1, max_length=200, description="Location name")
    country: Optional[str] = Field(
        None, max_length=100, description="Country name (optional)"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"name": "Baeza", "country": "España"}
        }


class TripCreateRequest(BaseModel):
    """
    Request schema for creating a new trip.

    **Required fields**: title, description, start_date

    Attributes:
        title: Trip title (1-200 chars)
        description: HTML description (sanitized, max 50000 chars)
        start_date: Start date (cannot be in future)
        end_date: End date (optional, must be >= start_date)
        distance_km: Distance in kilometers (0.1-10000)
        difficulty: Difficulty level (easy, moderate, difficult, very_difficult)
        locations: List of locations visited
        tags: List of tag names (max 10 tags, max 50 chars each)
    """

    title: str = Field(
        ..., min_length=1, max_length=200, description="Trip title"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Trip description (HTML allowed, will be sanitized)",
    )
    start_date: date = Field(
        ..., description="Trip start date (YYYY-MM-DD, cannot be in future)"
    )
    end_date: Optional[date] = Field(
        None, description="Trip end date (must be >= start_date)"
    )
    distance_km: Optional[float] = Field(
        None, ge=0.1, le=10000.0, description="Distance in kilometers"
    )
    difficulty: Optional[str] = Field(
        None,
        description="Difficulty level: easy, moderate, difficult, very_difficult",
    )
    locations: List[LocationInput] = Field(
        default_factory=list,
        max_length=50,
        description="Locations visited during trip",
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Tags for categorization (max 10)",
    )

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty is one of allowed values."""
        if v is None:
            return None
        allowed = ["easy", "moderate", "difficult", "very_difficult"]
        if v not in allowed:
            raise ValueError(
                f"La dificultad debe ser una de: {', '.join(allowed)}"
            )
        return v

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        """Validate start date is not in the future."""
        if v > date.today():
            raise ValueError("La fecha de inicio no puede ser futura")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate each tag length."""
        for tag in v:
            if len(tag) > 50:
                raise ValueError(
                    f"La etiqueta '{tag}' excede 50 caracteres"
                )
            if len(tag.strip()) == 0:
                raise ValueError("Las etiquetas no pueden estar vacías")
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        """Validate end_date is >= start_date."""
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError(
                "La fecha de fin debe ser posterior o igual a la fecha de inicio"
            )
        return self

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "title": "Vía Verde del Aceite",
                "description": "<p>Un recorrido espectacular entre olivos centenarios...</p>",
                "start_date": "2024-05-15",
                "end_date": "2024-05-17",
                "distance_km": 127.3,
                "difficulty": "moderate",
                "locations": [
                    {"name": "Jaén", "country": "España"},
                    {"name": "Baeza", "country": "España"},
                ],
                "tags": ["vías verdes", "andalucía", "olivos"],
            }
        }


class TripUpdateRequest(BaseModel):
    """
    Request schema for updating an existing trip.

    All fields are optional - only provided fields will be updated.

    Attributes:
        title: Trip title (1-200 chars)
        description: HTML description (sanitized, max 50000 chars)
        start_date: Start date
        end_date: End date (must be >= start_date)
        distance_km: Distance in kilometers (0.1-10000)
        difficulty: Difficulty level
        locations: List of locations (replaces existing)
        tags: List of tag names (replaces existing, max 10)
        client_updated_at: Timestamp for optimistic locking
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=50000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    distance_km: Optional[float] = Field(None, ge=0.1, le=10000.0)
    difficulty: Optional[str] = None
    locations: Optional[List[LocationInput]] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(None, max_length=10)
    client_updated_at: Optional[datetime] = Field(
        None, description="Timestamp when client loaded the trip (optimistic locking)"
    )

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty is one of allowed values."""
        if v is None:
            return None
        allowed = ["easy", "moderate", "difficult", "very_difficult"]
        if v not in allowed:
            raise ValueError(
                f"La dificultad debe ser una de: {', '.join(allowed)}"
            )
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate each tag length."""
        if v is None:
            return None
        for tag in v:
            if len(tag) > 50:
                raise ValueError(
                    f"La etiqueta '{tag}' excede 50 caracteres"
                )
            if len(tag.strip()) == 0:
                raise ValueError("Las etiquetas no pueden estar vacías")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "title": "Vía Verde del Aceite - ACTUALIZADO",
                "description": "<p>Actualización con más detalles...</p>",
                "distance_km": 130.5,
                "client_updated_at": "2024-12-24T10:30:00Z",
            }
        }


# ============================================================================
# Response Schemas (Output)
# ============================================================================


class TagResponse(BaseModel):
    """
    Tag data in API responses.

    Attributes:
        tag_id: Unique tag identifier
        name: Display name (preserves original casing)
        normalized: Normalized name for matching
        usage_count: Number of trips using this tag
    """

    tag_id: str = Field(..., description="Unique tag identifier")
    name: str = Field(..., description="Tag display name")
    normalized: str = Field(..., description="Normalized name for matching")
    usage_count: int = Field(..., description="Number of trips using this tag")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "tag_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Vías Verdes",
                "normalized": "vias verdes",
                "usage_count": 125,
            }
        }


class TripLocationResponse(BaseModel):
    """
    Trip location data in API responses.

    Attributes:
        location_id: Unique location identifier
        name: Location name
        latitude: Latitude coordinate (from geocoding, optional)
        longitude: Longitude coordinate (from geocoding, optional)
        sequence: Order in route (0-based)
    """

    location_id: str = Field(..., description="Unique location identifier")
    name: str = Field(..., description="Location name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    sequence: int = Field(..., description="Order in route (0-based)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "location_id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Baeza",
                "latitude": 37.9963,
                "longitude": -3.4669,
                "sequence": 0,
            }
        }


class TripPhotoResponse(BaseModel):
    """
    Trip photo data in API responses.

    Attributes:
        photo_id: Unique photo identifier
        photo_url: URL to optimized photo
        thumbnail_url: URL to thumbnail
        caption: Photo caption (optional)
        display_order: Display order (0-based)
        width: Original photo width in pixels
        height: Original photo height in pixels
    """

    photo_id: str = Field(..., description="Unique photo identifier")
    photo_url: str = Field(..., description="URL to optimized photo")
    thumbnail_url: str = Field(..., description="URL to thumbnail")
    caption: Optional[str] = Field(None, description="Photo caption")
    display_order: int = Field(..., description="Display order (0-based)")
    width: Optional[int] = Field(None, description="Original photo width")
    height: Optional[int] = Field(None, description="Original photo height")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "photo_id": "770e8400-e29b-41d4-a716-446655440002",
                "photo_url": "/storage/trip_photos/2024/12/550e.../abc123.jpg",
                "thumbnail_url": "/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
                "caption": "Vista desde el viaducto",
                "display_order": 0,
                "width": 2000,
                "height": 1500,
            }
        }


class TripResponse(BaseModel):
    """
    Complete trip data in API responses.

    Attributes:
        trip_id: Unique trip identifier
        user_id: Trip author's user ID
        title: Trip title
        description: HTML description (sanitized)
        status: Trip status (draft/published)
        start_date: Start date
        end_date: End date (optional)
        distance_km: Distance in kilometers (optional)
        difficulty: Difficulty level (optional)
        created_at: Creation timestamp (UTC)
        updated_at: Last update timestamp (UTC)
        published_at: Publication timestamp (UTC, null if draft)
        photos: List of trip photos
        locations: List of trip locations
        tags: List of trip tags
    """

    trip_id: str = Field(..., description="Unique trip identifier")
    user_id: str = Field(..., description="Trip author's user ID")
    title: str = Field(..., description="Trip title")
    description: str = Field(..., description="Trip description (HTML)")
    status: str = Field(..., description="Trip status (draft/published)")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    distance_km: Optional[float] = Field(None, description="Distance in kilometers")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
    published_at: Optional[datetime] = Field(
        None, description="Publication timestamp (UTC)"
    )
    photos: List[TripPhotoResponse] = Field(
        default_factory=list, description="List of trip photos"
    )
    locations: List[TripLocationResponse] = Field(
        default_factory=list, description="List of trip locations"
    )
    tags: List[TagResponse] = Field(
        default_factory=list, description="List of trip tags"
    )

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Vía Verde del Aceite",
                "description": "<p>Ruta espectacular...</p>",
                "status": "published",
                "start_date": "2024-05-15",
                "end_date": "2024-05-17",
                "distance_km": 127.3,
                "difficulty": "moderate",
                "created_at": "2024-12-20T10:30:00Z",
                "updated_at": "2024-12-22T15:45:00Z",
                "published_at": "2024-12-22T15:45:00Z",
                "photos": [],
                "locations": [],
                "tags": [],
            }
        }


class TripListItemResponse(BaseModel):
    """
    Trip summary for list views.

    Lighter response for pagination - doesn't include full photos/locations/tags.

    Attributes:
        trip_id: Unique trip identifier
        user_id: Trip author's user ID
        title: Trip title
        start_date: Start date
        distance_km: Distance in kilometers (optional)
        status: Trip status (draft/published)
        photo_count: Number of photos
        tag_names: List of tag names only
        thumbnail_url: First photo thumbnail (optional)
        created_at: Creation timestamp (UTC)
    """

    trip_id: str = Field(..., description="Unique trip identifier")
    user_id: str = Field(..., description="Trip author's user ID")
    title: str = Field(..., description="Trip title")
    start_date: date = Field(..., description="Start date")
    distance_km: Optional[float] = Field(None, description="Distance in kilometers")
    status: str = Field(..., description="Trip status")
    photo_count: int = Field(..., description="Number of photos")
    tag_names: List[str] = Field(
        default_factory=list, description="List of tag names"
    )
    thumbnail_url: Optional[str] = Field(
        None, description="First photo thumbnail URL"
    )
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Vía Verde del Aceite",
                "start_date": "2024-05-15",
                "distance_km": 127.3,
                "status": "published",
                "photo_count": 12,
                "tag_names": ["vías verdes", "andalucía"],
                "thumbnail_url": "/storage/trip_photos/2024/12/550e.../thumb.jpg",
                "created_at": "2024-12-20T10:30:00Z",
            }
        }


class TripListResponse(BaseModel):
    """
    Paginated list of trips.

    Attributes:
        trips: List of trip summaries
        total: Total number of trips matching filter
        limit: Page size
        offset: Pagination offset
    """

    trips: List[TripListItemResponse] = Field(..., description="List of trips")
    total: int = Field(..., description="Total trips matching filter")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Pagination offset")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "trips": [
                    {
                        "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Vía Verde del Aceite",
                        "start_date": "2024-05-15",
                        "distance_km": 127.3,
                        "status": "published",
                        "photo_count": 12,
                        "tag_names": ["vías verdes", "andalucía"],
                        "thumbnail_url": "/storage/.../thumb.jpg",
                        "created_at": "2024-12-20T10:30:00Z",
                    }
                ],
                "total": 15,
                "limit": 20,
                "offset": 0,
            }
        }
