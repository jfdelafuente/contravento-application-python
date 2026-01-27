"""
Route Statistics schemas for GPS Routes feature (User Story 5).

Pydantic models for advanced statistics request/response validation in API.
Functional Requirements: FR-030 to FR-034
Success Criteria: SC-021 to SC-024
"""

from pydantic import BaseModel, Field


# ============================================================================
# Response Schemas (Output)
# ============================================================================


class TopClimbResponse(BaseModel):
    """
    Individual climb information.

    Represents one of the top 3 hardest climbs on the route.
    Used in route statistics visualization.

    Functional Requirement: FR-031 (Identify hardest climbs)
    """

    start_km: float = Field(..., ge=0.0, description="Distance where climb starts (km from start)")
    end_km: float = Field(..., ge=0.0, description="Distance where climb ends (km from start)")
    elevation_gain_m: float = Field(
        ..., ge=0.0, description="Total elevation gain during climb (meters)"
    )
    avg_gradient: float = Field(
        ..., description="Average gradient of climb (percentage, e.g., 8.5 = 8.5%)"
    )
    description: str | None = Field(None, description="Optional climb name/description")


class GradientCategoryResponse(BaseModel):
    """
    Statistics for one gradient category.

    Used in gradient distribution analysis.

    Functional Requirement: FR-032 (Gradient distribution visualization)
    """

    distance_km: float = Field(..., ge=0.0, description="Total distance in this category (km)")
    percentage: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of total route distance"
    )


class GradientDistributionResponse(BaseModel):
    """
    Complete gradient distribution breakdown.

    Classifies route segments into gradient categories:
    - Llano (flat): 0-3%
    - Moderado (moderate): 3-6%
    - Empinado (steep): 6-10%
    - Muy empinado (very steep): >10%

    Functional Requirement: FR-032 (Gradient distribution visualization)
    """

    llano: GradientCategoryResponse = Field(..., description="Flat terrain: 0-3% gradient")
    moderado: GradientCategoryResponse = Field(..., description="Moderate terrain: 3-6% gradient")
    empinado: GradientCategoryResponse = Field(..., description="Steep terrain: 6-10% gradient")
    muy_empinado: GradientCategoryResponse = Field(
        ..., description="Very steep terrain: >10% gradient"
    )


class RouteStatisticsResponse(BaseModel):
    """
    Complete route statistics response.

    Advanced analytics for GPS routes including speed, time, and gradient metrics.

    Requirements:
    - Only populated if GPX file has timestamps (has_timestamps=True)
    - All speed/time fields are None if no timestamps available
    - Gradient metrics work regardless of timestamps

    Functional Requirements: FR-030 to FR-034
    Success Criteria: SC-021 to SC-024
    """

    stats_id: str = Field(..., description="Unique statistics record ID (UUID)")
    gpx_file_id: str = Field(..., description="Associated GPX file ID (UUID)")

    # Speed metrics (km/h)
    # NULL if GPX has no timestamps (FR-033)
    avg_speed_kmh: float | None = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Average speed over entire route (km/h, NULL if no timestamps)",
    )
    max_speed_kmh: float | None = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Maximum speed reached (km/h, NULL if no timestamps)",
    )

    # Time metrics (minutes)
    # NULL if GPX has no timestamps (FR-033)
    total_time_minutes: float | None = Field(
        None, ge=0.0, description="Total elapsed time (minutes, NULL if no timestamps)"
    )
    moving_time_minutes: float | None = Field(
        None,
        ge=0.0,
        description="Time in motion, excludes stops >5min (minutes, NULL if no timestamps)",
    )

    # Gradient metrics (percentage)
    # Available regardless of timestamps (only requires elevation)
    avg_gradient: float | None = Field(None, description="Average gradient over route (%)")
    max_gradient: float | None = Field(None, description="Maximum gradient (steepest uphill, %)")

    # Top climbs (array of max 3 climbs)
    # NULL if GPX has no elevation data
    top_climbs: list[TopClimbResponse] | None = Field(
        None, max_length=3, description="Top 3 hardest climbs (NULL if no elevation)"
    )

    class Config:
        from_attributes = True


class RouteStatisticsWithDistributionResponse(RouteStatisticsResponse):
    """
    Extended route statistics with gradient distribution.

    Includes all RouteStatisticsResponse fields plus detailed gradient breakdown.

    Used in frontend visualization for gradient distribution charts.
    Functional Requirement: FR-032 (Gradient distribution visualization)
    """

    gradient_distribution: GradientDistributionResponse | None = Field(
        None, description="Gradient distribution breakdown (NULL if no elevation)"
    )
