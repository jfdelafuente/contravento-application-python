"""
GPX schemas for GPS Routes feature.

Pydantic models for GPX file request/response validation in API.
Functional Requirements: FR-001 to FR-008, FR-036, FR-039
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Response Schemas (Output)
# ============================================================================


class TrackPointResponse(BaseModel):
    """
    Individual GPS trackpoint in the simplified route.

    Used in track visualization responses.
    """

    point_id: str = Field(..., description="Unique trackpoint identifier (UUID)")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    elevation: float | None = Field(None, description="Altitude in meters (NULL if not available)")
    distance_km: float = Field(..., ge=0.0, description="Cumulative distance from start in km")
    sequence: int = Field(..., ge=0, description="Order in track (0-indexed)")
    gradient: float | None = Field(None, description="Percentage slope (e.g., 5.2 = 5.2% uphill)")

    class Config:
        from_attributes = True


class CoordinateResponse(BaseModel):
    """
    Simple coordinate pair for route bounds.

    Used for start/end point markers.
    """

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class GPXFileMetadata(BaseModel):
    """
    GPX file metadata and processing results.

    Used in GET /trips/{trip_id}/gpx response.
    """

    gpx_file_id: str = Field(..., description="Unique GPX file identifier (UUID)")
    trip_id: str = Field(..., description="Associated trip ID (UUID)")
    file_name: str = Field(..., description="Original filename (e.g., 'Camino_del_Cid.gpx')")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    distance_km: float = Field(..., ge=0.0, description="Total distance in kilometers")
    elevation_gain: float | None = Field(None, description="Total elevation gain in meters")
    elevation_loss: float | None = Field(None, description="Total elevation loss in meters")
    max_elevation: float | None = Field(None, description="Maximum altitude in meters")
    min_elevation: float | None = Field(None, description="Minimum altitude in meters")
    total_points: int = Field(..., ge=0, description="Original trackpoint count")
    simplified_points: int = Field(
        ..., ge=0, description="Reduced trackpoint count after simplification"
    )
    has_elevation: bool = Field(..., description="True if GPX includes elevation data")
    has_timestamps: bool = Field(..., description="True if GPX includes timestamp data")
    processing_status: str = Field(
        ..., description="Current processing status (pending, processing, completed, error)"
    )
    error_message: str | None = Field(None, description="Error details if processing failed")
    uploaded_at: datetime = Field(..., description="Upload timestamp (ISO 8601)")
    processed_at: datetime | None = Field(None, description="Processing completion timestamp")

    class Config:
        from_attributes = True


class GPXUploadResponse(BaseModel):
    """
    Response from GPX upload endpoint.

    Two modes:
    - Synchronous (201): Small files (<1MB) processed immediately
    - Asynchronous (202): Large files (1-10MB) processing in background
    """

    gpx_file_id: str = Field(..., description="Unique GPX file identifier (UUID)")
    trip_id: str = Field(..., description="Associated trip ID (UUID)")
    processing_status: str = Field(
        ..., description="Current processing status (pending, processing, completed, error)"
    )

    # Fields below only present if processing_status = 'completed'
    distance_km: float | None = Field(None, description="Total distance (only if completed)")
    elevation_gain: float | None = Field(
        None, description="Total elevation gain (only if completed)"
    )
    elevation_loss: float | None = Field(
        None, description="Total elevation loss (only if completed)"
    )
    max_elevation: float | None = Field(None, description="Maximum altitude (only if completed)")
    min_elevation: float | None = Field(None, description="Minimum altitude (only if completed)")
    has_elevation: bool | None = Field(
        None, description="True if GPX has elevation (only if completed)"
    )
    has_timestamps: bool | None = Field(
        None, description="True if GPX has timestamps (only if completed)"
    )
    total_points: int | None = Field(
        None, description="Original trackpoint count (only if completed)"
    )
    simplified_points: int | None = Field(
        None, description="Reduced trackpoint count (only if completed)"
    )
    uploaded_at: datetime = Field(..., description="Upload timestamp (ISO 8601)")
    processed_at: datetime | None = Field(
        None, description="Processing completion timestamp (only if completed)"
    )
    error_message: str | None = Field(None, description="Error details (only if status=error)")

    class Config:
        from_attributes = True


class GPXStatusResponse(BaseModel):
    """
    Response from status polling endpoint.

    Used for async uploads to check processing progress.
    """

    gpx_file_id: str = Field(..., description="Unique GPX file identifier (UUID)")
    processing_status: str = Field(..., description="Current processing status")
    distance_km: float | None = Field(None, description="Total distance (only if completed)")
    elevation_gain: float | None = Field(
        None, description="Total elevation gain (only if completed)"
    )
    total_points: int | None = Field(
        None, description="Original trackpoint count (only if completed)"
    )
    simplified_points: int | None = Field(
        None, description="Reduced point count (only if completed)"
    )
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    processed_at: datetime | None = Field(None, description="Processing completion timestamp")
    error_message: str | None = Field(None, description="Error details if processing failed")

    class Config:
        from_attributes = True


class TopClimbResponse(BaseModel):
    """
    Individual climb data in top climbs list.

    Represents a single climb segment with elevation and gradient details.
    Used in RouteStatisticsResponse.
    """

    start_km: float = Field(..., ge=0.0, description="Distance from start where climb begins (km)")
    end_km: float = Field(..., ge=0.0, description="Distance from start where climb ends (km)")
    elevation_gain_m: float = Field(..., ge=0.0, description="Total elevation gain in climb (meters)")
    avg_gradient: float = Field(
        ..., description="Average gradient of climb (percentage, e.g., 8.5 = 8.5% slope)"
    )
    description: str = Field(..., description="Human-readable climb description")

    @field_validator("end_km")
    @classmethod
    def end_km_must_be_greater_than_start(cls, v, info):
        """Validate that end_km > start_km."""
        if "start_km" in info.data and v <= info.data["start_km"]:
            raise ValueError("end_km must be greater than start_km")
        return v


class GradientCategoryResponse(BaseModel):
    """
    Statistics for one gradient category (FR-032).

    Used in gradient distribution visualization.
    """

    distance_km: float = Field(..., ge=0.0, description="Total distance in this category (km)")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of total route distance")


class GradientDistributionResponse(BaseModel):
    """
    Complete gradient distribution breakdown (FR-032).

    Classifies route segments into gradient categories:
    - Llano (flat): 0-3%
    - Moderado (moderate): 3-6%
    - Empinado (steep): 6-10%
    - Muy empinado (very steep): >10%
    """

    llano: GradientCategoryResponse = Field(..., description="Flat terrain: 0-3% gradient")
    moderado: GradientCategoryResponse = Field(..., description="Moderate terrain: 3-6% gradient")
    empinado: GradientCategoryResponse = Field(..., description="Steep terrain: 6-10% gradient")
    muy_empinado: GradientCategoryResponse = Field(
        ..., description="Very steep terrain: >10% gradient"
    )


class RouteStatisticsResponse(BaseModel):
    """
    Advanced route statistics calculated from GPX data.

    Only present if GPX file has timestamps (has_timestamps=True).
    Includes speed metrics, time analysis, gradient analysis, and top climbs.
    """

    stats_id: str = Field(..., description="Unique statistics record ID (UUID)")
    gpx_file_id: str = Field(..., description="Associated GPX file ID (UUID)")
    avg_speed_kmh: float | None = Field(None, ge=0.0, lt=100.0, description="Average speed (km/h)")
    max_speed_kmh: float | None = Field(None, ge=0.0, lt=100.0, description="Maximum speed (km/h)")
    total_time_minutes: float | None = Field(None, ge=0.0, description="Total elapsed time (minutes)")
    moving_time_minutes: float | None = Field(
        None, ge=0.0, description="Time in motion, excludes stops (minutes)"
    )
    avg_gradient: float | None = Field(None, description="Average gradient over route (%)")
    max_gradient: float | None = Field(None, description="Maximum gradient (steepest uphill) (%)")
    top_climbs: list[TopClimbResponse] | None = Field(
        None, max_length=3, description="Top 3 hardest climbs (max 3 items)"
    )
    created_at: datetime = Field(..., description="When statistics were calculated (ISO 8601)")

    @field_validator("moving_time_minutes")
    @classmethod
    def moving_time_must_be_less_than_total(cls, v, info):
        """Validate that moving_time <= total_time."""
        if (
            v is not None
            and "total_time_minutes" in info.data
            and info.data["total_time_minutes"] is not None
        ):
            if v > info.data["total_time_minutes"]:
                raise ValueError("moving_time_minutes must be <= total_time_minutes")
        return v

    class Config:
        from_attributes = True


class RouteStatisticsWithDistributionResponse(RouteStatisticsResponse):
    """
    Extended route statistics with gradient distribution (FR-032).

    Includes all RouteStatisticsResponse fields plus detailed gradient breakdown.
    Used in frontend visualization for gradient distribution charts.
    """

    gradient_distribution: GradientDistributionResponse | None = Field(
        None, description="Gradient distribution breakdown (NULL if no elevation)"
    )


class TrackDataResponse(BaseModel):
    """
    Response from track data endpoint with simplified trackpoints.

    Used for map rendering and elevation profiles.
    Optionally includes advanced route statistics if timestamps are available.
    """

    gpx_file_id: str = Field(..., description="Unique GPX file identifier (UUID)")
    trip_id: str = Field(..., description="Associated trip ID (UUID)")
    distance_km: float = Field(..., ge=0.0, description="Total distance in kilometers")
    elevation_gain: float | None = Field(None, description="Total elevation gain in meters")
    simplified_points_count: int = Field(
        ..., ge=0, description="Number of points in trackpoints array"
    )
    has_elevation: bool = Field(..., description="True if trackpoints contain elevation data")
    start_point: CoordinateResponse = Field(..., description="Route start coordinate")
    end_point: CoordinateResponse = Field(..., description="Route end coordinate")
    trackpoints: list[TrackPointResponse] = Field(
        ..., description="Simplified trackpoints ordered by sequence"
    )
    route_statistics: RouteStatisticsResponse | None = Field(
        None, description="Advanced route statistics (only if GPX has timestamps)"
    )

    class Config:
        from_attributes = True


# ============================================================================
# Wrapper Schemas (Standard API Response Format)
# ============================================================================


class GPXUploadSuccessResponse(BaseModel):
    """
    Standard API response wrapper for GPX upload.

    Used in POST /trips/{trip_id}/gpx response.
    """

    success: bool = Field(True, description="Always true for successful uploads")
    data: GPXUploadResponse = Field(..., description="GPX upload data")
    message: str | None = Field(None, description="Optional message for async uploads")


class GPXMetadataSuccessResponse(BaseModel):
    """
    Standard API response wrapper for GPX metadata.

    Used in GET /trips/{trip_id}/gpx response.
    """

    success: bool = Field(True, description="Always true for successful requests")
    data: GPXFileMetadata = Field(..., description="GPX file metadata")


class GPXStatusSuccessResponse(BaseModel):
    """
    Standard API response wrapper for status polling.

    Used in GET /gpx/{gpx_file_id}/status response.
    """

    success: bool = Field(True, description="Always true for successful status checks")
    data: GPXStatusResponse = Field(..., description="GPX processing status")


class TrackDataSuccessResponse(BaseModel):
    """
    Standard API response wrapper for track data.

    Used in GET /gpx/{gpx_file_id}/track response.
    """

    success: bool = Field(True, description="Always true for successful requests")
    data: TrackDataResponse = Field(..., description="Track data with simplified points")
