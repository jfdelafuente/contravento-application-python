"""
Trip schemas for Travel Diary feature.

Pydantic models for trip request/response validation in API.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

try:
    from typing import Self
except ImportError:
    from typing import Self

from src.schemas.feed import UserSummary  # Feature 004 - Author info in trip detail


# ============================================================================
# Request Schemas (Input)
# ============================================================================


class LocationInput(BaseModel):
    """
    Location input for trip creation/update with optional GPS coordinates.

    Attributes:
        name: Location name (e.g., "Baeza", "Camino de Santiago")
        country: Country name (optional, e.g., "España")
        latitude: Latitude in decimal degrees (optional, -90 to 90)
        longitude: Longitude in decimal degrees (optional, -180 to 180)
    """

    name: str = Field(..., min_length=1, max_length=200, description="Location name")
    country: Optional[str] = Field(None, max_length=100, description="Country name (optional)")
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Latitud en grados decimales (opcional, -90 a 90)",
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Longitud en grados decimales (opcional, -180 a 180)",
    )

    @field_validator("latitude", "longitude")
    @classmethod
    def round_coordinates(cls, v: Optional[float]) -> Optional[float]:
        """Enforce 6 decimal places precision for coordinates."""
        if v is None:
            return v
        return round(v, 6)

    @field_validator("latitude")
    @classmethod
    def validate_latitude_range(cls, v: Optional[float]) -> Optional[float]:
        """Validate latitude range with Spanish error message."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError("Latitud debe estar entre -90 y 90 grados")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude_range(cls, v: Optional[float]) -> Optional[float]:
        """Validate longitude range with Spanish error message."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError("Longitud debe estar entre -180 y 180 grados")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "Baeza",
                "country": "España",
                "latitude": 37.993664,
                "longitude": -3.467208,
            }
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

    title: str = Field(..., min_length=1, max_length=200, description="Trip title")
    description: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Trip description (HTML allowed, will be sanitized)",
    )
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD, cannot be in future)")
    end_date: Optional[date] = Field(None, description="Trip end date (must be >= start_date)")
    distance_km: Optional[float] = Field(
        None, ge=0.1, le=10000.0, description="Distance in kilometers"
    )
    difficulty: Optional[str] = Field(
        None,
        description="Difficulty level: easy, moderate, difficult, very_difficult",
    )
    locations: list[LocationInput] = Field(
        default_factory=list,
        max_length=50,
        description="Locations visited during trip",
    )
    tags: list[str] = Field(
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
            raise ValueError(f"La dificultad debe ser una de: {', '.join(allowed)}")
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
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate each tag length."""
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"La etiqueta '{tag}' excede 50 caracteres")
            if len(tag.strip()) == 0:
                raise ValueError("Las etiquetas no pueden estar vacías")
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        """Validate end_date is >= start_date."""
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("La fecha de fin debe ser posterior o igual a la fecha de inicio")
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
    locations: Optional[list[LocationInput]] = Field(None, max_length=50)
    tags: Optional[list[str]] = Field(None, max_length=10)
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
            raise ValueError(f"La dificultad debe ser una de: {', '.join(allowed)}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate each tag length."""
        if v is None:
            return None
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"La etiqueta '{tag}' excede 50 caracteres")
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
        author: Trip author's profile summary (Feature 004)
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
        like_count: Number of likes (Feature 004 - US2)
        is_liked: Whether current user has liked this trip (Feature 004 - US2, null if not authenticated)
    """

    trip_id: str = Field(..., description="Unique trip identifier")
    user_id: str = Field(..., description="Trip author's user ID")
    author: UserSummary = Field(..., description="Trip author's profile summary (Feature 004)")
    title: str = Field(..., description="Trip title")
    description: str = Field(..., description="Trip description (HTML)")
    status: str = Field(..., description="Trip status (draft/published)")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    distance_km: Optional[float] = Field(None, description="Distance in kilometers")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp (UTC)")
    photos: list[TripPhotoResponse] = Field(default_factory=list, description="List of trip photos")
    locations: list[TripLocationResponse] = Field(
        default_factory=list, description="List of trip locations"
    )
    tags: list[TagResponse] = Field(default_factory=list, description="List of trip tags")
    like_count: int = Field(default=0, description="Number of likes (Feature 004 - US2)")
    is_liked: Optional[bool] = Field(default=None, description="Whether current user has liked this trip (Feature 004 - US2, null if not authenticated)")

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle trip_tags -> tags conversion and dynamic attributes."""
        if hasattr(obj, "trip_tags"):
            # Extract tags from trip_tags relationship
            tags = [trip_tag.tag for trip_tag in obj.trip_tags]

            # Build author UserSummary from trip.user (Feature 004)
            # User model has basic fields (username), UserProfile has extended fields (full_name, photo_url)
            author_data = {
                "user_id": obj.user.id,
                "username": obj.user.username,
                "full_name": obj.user.profile.full_name if obj.user.profile else None,
                "profile_photo_url": obj.user.profile.photo_url if obj.user.profile else None,
                "is_following": getattr(obj.user, "is_following", None),
            }
            author = UserSummary.model_validate(author_data)

            # Create a dict with all attributes
            data = {
                "trip_id": obj.trip_id,
                "user_id": obj.user_id,
                "author": author,
                "title": obj.title,
                "description": obj.description,
                "status": obj.status.value if hasattr(obj.status, "value") else obj.status,
                "start_date": obj.start_date,
                "end_date": obj.end_date,
                "distance_km": obj.distance_km,
                "difficulty": obj.difficulty.value
                if obj.difficulty and hasattr(obj.difficulty, "value")
                else obj.difficulty,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at,
                "published_at": obj.published_at,
                "photos": obj.photos,
                "locations": obj.locations,
                "tags": tags,
                # Feature 004 - US2: Like count and is_liked (dynamic attributes)
                "like_count": getattr(obj, "like_count", 0),
                "is_liked": getattr(obj, "is_liked", None),
            }
            return super().model_validate(data, **kwargs)
        return super().model_validate(obj, **kwargs)

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
    tag_names: list[str] = Field(default_factory=list, description="List of tag names")
    thumbnail_url: Optional[str] = Field(None, description="First photo thumbnail URL")
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

    trips: list[TripListItemResponse] = Field(..., description="List of trips")
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


# ============================================================================
# Public Feed Schemas (Feature 013 - Public Trips Feed)
# ============================================================================


class PublicUserSummary(BaseModel):
    """
    User summary for public trip feed (Feature 013).

    Minimal user info displayed on public trip cards - only public profile data.

    Attributes:
        user_id: Unique user identifier
        username: Username (for profile link)
        profile_photo_url: Profile photo URL (optional)
        is_following: Whether current user follows this user (Feature 004 - US1, None if not authenticated)
    """

    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    profile_photo_url: Optional[str] = Field(None, description="Profile photo URL")
    is_following: Optional[bool] = Field(None, description="Whether current user follows this user (Feature 004 - US1)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "maria_ciclista",
                "profile_photo_url": "/storage/profile_photos/2024/12/maria.jpg",
                "is_following": False,
            }
        }


class PublicPhotoSummary(BaseModel):
    """
    Photo summary for public trip feed (Feature 013).

    Minimal photo info for trip cards - only first photo thumbnail.

    Attributes:
        photo_url: URL to optimized photo
        thumbnail_url: URL to thumbnail
    """

    photo_url: str = Field(..., description="URL to optimized photo")
    thumbnail_url: str = Field(..., description="URL to thumbnail")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "photo_url": "/storage/trip_photos/2024/12/550e.../abc123.jpg",
                "thumbnail_url": "/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
            }
        }


class PublicLocationSummary(BaseModel):
    """
    Location summary for public trip feed (Feature 013).

    Minimal location info for trip cards - only first location name.

    Attributes:
        name: Location name
    """

    name: str = Field(..., description="Location name")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {"example": {"name": "Baeza, España"}}


class PublicTripSummary(BaseModel):
    """
    Trip summary for public feed (Feature 013).

    Optimized for homepage display - shows only essential trip data.

    Requirements (FR-002):
    - título, foto, distancia, location (primera), fecha, autor

    Attributes:
        trip_id: Unique trip identifier
        title: Trip title
        start_date: Trip start date
        distance_km: Distance in kilometers (optional)
        photo: First photo (optional)
        location: First location (optional)
        author: Trip author summary
        published_at: Publication timestamp (for sorting)
    """

    trip_id: str = Field(..., description="Unique trip identifier")
    title: str = Field(..., description="Trip title")
    start_date: date = Field(..., description="Trip start date")
    distance_km: Optional[float] = Field(None, description="Distance in kilometers")
    photo: Optional[PublicPhotoSummary] = Field(None, description="First photo thumbnail")
    location: Optional[PublicLocationSummary] = Field(None, description="First location")
    author: PublicUserSummary = Field(..., description="Trip author")
    published_at: datetime = Field(..., description="Publication timestamp (UTC)")
    like_count: int = Field(default=0, description="Number of likes (Feature 004 - US2)")
    is_liked: Optional[bool] = Field(default=None, description="Whether current user has liked this trip (Feature 004 - US2, null if not authenticated)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Vía Verde del Aceite",
                "start_date": "2024-05-15",
                "distance_km": 127.3,
                "photo": {
                    "photo_url": "/storage/trip_photos/2024/12/550e.../abc123.jpg",
                    "thumbnail_url": "/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
                },
                "location": {"name": "Baeza, España"},
                "author": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "maria_ciclista",
                    "profile_photo_url": "/storage/profile_photos/2024/12/maria.jpg",
                },
                "published_at": "2024-12-22T15:45:00Z",
                "like_count": 15,
                "is_liked": None,
            }
        }


class PaginationInfo(BaseModel):
    """
    Pagination metadata for public feed (Feature 013).

    Provides information for client-side pagination controls.

    Attributes:
        total: Total number of trips matching filter
        page: Current page number (1-indexed)
        limit: Page size (trips per page)
        total_pages: Total number of pages
    """

    total: int = Field(..., description="Total trips matching filter", ge=0)
    page: int = Field(..., description="Current page (1-indexed)", ge=1)
    limit: int = Field(..., description="Page size", ge=1, le=50)
    total_pages: int = Field(..., description="Total pages", ge=0)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total": 127,
                "page": 1,
                "limit": 20,
                "total_pages": 7,
            }
        }


class PublicTripListResponse(BaseModel):
    """
    Paginated response for public trips feed (Feature 013).

    Main response schema for GET /trips/public endpoint.

    Attributes:
        trips: List of public trip summaries
        pagination: Pagination metadata
    """

    trips: list[PublicTripSummary] = Field(..., description="List of public trips")
    pagination: PaginationInfo = Field(..., description="Pagination metadata")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "trips": [
                    {
                        "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Vía Verde del Aceite",
                        "start_date": "2024-05-15",
                        "distance_km": 127.3,
                        "photo": {
                            "photo_url": "/storage/trip_photos/2024/12/abc.jpg",
                            "thumbnail_url": "/storage/trip_photos/2024/12/abc_thumb.jpg",
                        },
                        "location": {"name": "Baeza, España"},
                        "author": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "maria_ciclista",
                            "profile_photo_url": "/storage/profile_photos/maria.jpg",
                        },
                        "published_at": "2024-12-22T15:45:00Z",
                    }
                ],
                "pagination": {
                    "total": 127,
                    "page": 1,
                    "limit": 20,
                    "total_pages": 7,
                },
            }
        }
