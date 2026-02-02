"""
Pydantic schemas for GPS Trip Creation Wizard feature.

Feature: 017-gps-trip-wizard
Endpoints: POST /gpx/analyze, POST /trips/gpx-wizard
"""

from pydantic import BaseModel, Field

from src.models.trip import TripDifficulty


class GPXTelemetry(BaseModel):
    """
    Telemetry data extracted from GPX file for wizard preview.

    This schema represents the data returned by POST /gpx/analyze.
    It provides essential route metrics for difficulty calculation without
    storing data to the database.

    See: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml (lines 424-483)
    """

    distance_km: float = Field(
        ...,
        ge=0,
        description="Total route distance in kilometers",
        json_schema_extra={"example": 42.5},
    )

    elevation_gain: float | None = Field(
        None,
        ge=0,
        description="Cumulative uphill elevation in meters (None if no elevation data)",
        json_schema_extra={"example": 1250.0},
    )

    elevation_loss: float | None = Field(
        None,
        ge=0,
        description="Cumulative downhill elevation in meters (None if no elevation data)",
        json_schema_extra={"example": 1100.0},
    )

    max_elevation: float | None = Field(
        None,
        description="Maximum altitude in meters (None if no elevation data)",
        json_schema_extra={"example": 1850.0},
    )

    min_elevation: float | None = Field(
        None,
        description="Minimum altitude in meters (None if no elevation data)",
        json_schema_extra={"example": 450.0},
    )

    has_elevation: bool = Field(
        ..., description="Whether GPX contains elevation data", json_schema_extra={"example": True}
    )

    has_timestamps: bool = Field(
        default=False,
        description="Whether GPX contains timestamp data",
        json_schema_extra={"example": True},
    )

    start_date: str | None = Field(
        None,
        description="Start date from GPS timestamps (YYYY-MM-DD, None if no timestamps)",
        json_schema_extra={"example": "2024-06-01"},
    )

    end_date: str | None = Field(
        None,
        description="End date from GPS timestamps (YYYY-MM-DD, None if same day or no timestamps)",
        json_schema_extra={"example": "2024-06-05"},
    )

    difficulty: TripDifficulty = Field(
        ...,
        description="Auto-calculated trip difficulty from distance and elevation",
        json_schema_extra={"example": "difficult"},
    )

    suggested_title: str = Field(
        ...,
        max_length=200,
        description="Auto-generated title from GPX filename (cleaned and formatted)",
        json_schema_extra={"example": "Ruta Pirineos"},
    )

    trackpoints: list[dict] | None = Field(
        None,
        description="Simplified trackpoints for map visualization in wizard (null for lightweight telemetry)",
        json_schema_extra={
            "example": [
                {"latitude": 40.7128, "longitude": -74.0060, "elevation": 10.0, "distance_km": 0.0},
                {"latitude": 40.7129, "longitude": -74.0061, "elevation": 11.0, "distance_km": 0.1},
            ]
        },
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "distance_km": 42.5,
                "elevation_gain": 1250.0,
                "elevation_loss": 1100.0,
                "max_elevation": 1850.0,
                "min_elevation": 450.0,
                "has_elevation": True,
                "has_timestamps": True,
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "difficulty": "difficult",
                "suggested_title": "Ruta Pirineos",
                "trackpoints": [
                    {
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "elevation": 10.0,
                        "distance_km": 0.0,
                    },
                    {
                        "latitude": 40.7129,
                        "longitude": -74.0061,
                        "elevation": 11.0,
                        "distance_km": 0.1,
                    },
                ],
            }
        }


class GPXAnalysisResponse(BaseModel):
    """
    Response schema for POST /gpx/analyze endpoint.

    Standardized JSON response with success/data/error structure.

    See: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml (lines 485-514)
    """

    success: bool = Field(..., description="Whether the request was successful")

    data: GPXTelemetry | None = Field(None, description="Telemetry data if successful")

    error: dict[str, str] | None = Field(
        None,
        description="Error details if failed",
        json_schema_extra={
            "example": {
                "code": "INVALID_GPX_FILE",
                "message": "No se pudo procesar el archivo. Verifica que contenga datos de ruta válidos",
                "field": "file",
            }
        },
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example_success": {
                "success": True,
                "data": {
                    "distance_km": 42.5,
                    "elevation_gain": 1250.0,
                    "elevation_loss": 1100.0,
                    "max_elevation": 1850.0,
                    "min_elevation": 450.0,
                    "has_elevation": True,
                    "difficulty": "difficult",
                    "suggested_title": "Ruta Pirineos",
                    "trackpoints": [
                        {
                            "latitude": 40.7128,
                            "longitude": -74.0060,
                            "elevation": 10.0,
                            "distance_km": 0.0,
                        },
                        {
                            "latitude": 40.7129,
                            "longitude": -74.0061,
                            "elevation": 11.0,
                            "distance_km": 0.1,
                        },
                    ],
                },
                "error": None,
            },
            "example_error": {
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_GPX_FILE",
                    "message": "No se pudo procesar el archivo. Verifica que contenga datos de ruta válidos",
                    "field": "file",
                },
            },
        }


class GPXTripCreateInput(BaseModel):
    """
    Request schema for POST /trips/gpx-wizard endpoint.

    This schema represents the multipart/form-data request for atomic trip creation
    with GPX file and POIs. The actual file upload is handled separately by FastAPI's
    UploadFile, so this schema only includes non-file fields.

    Note: The gpx_file and pois are handled in the API endpoint via multipart/form-data:
    - gpx_file: UploadFile (binary)
    - pois: JSON string (parsed to list[POICreateInput])

    See: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml (lines 224-289)
    """

    title: str = Field(
        ...,
        max_length=200,
        description="Trip title",
        json_schema_extra={"example": "Ruta Bikepacking Pirineos"},
    )

    description: str = Field(
        ...,
        min_length=50,
        description="Trip description (minimum 50 characters)",
        json_schema_extra={
            "example": "Viaje de 5 días por los Pirineos con más de 300km recorridos y 5000m de desnivel acumulado. Ruta circular desde Jaca con pernoctas en refugios de montaña."
        },
    )

    start_date: str = Field(
        ...,
        description="Trip start date (YYYY-MM-DD format)",
        json_schema_extra={"example": "2024-06-01"},
    )

    end_date: str | None = Field(
        None,
        description="Trip end date (YYYY-MM-DD format, optional)",
        json_schema_extra={"example": "2024-06-05"},
    )

    privacy: str = Field(
        "public",
        description="Trip privacy setting",
        json_schema_extra={"example": "public"},
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "title": "Ruta Bikepacking Pirineos",
                "description": "Viaje de 5 días por los Pirineos con más de 300km recorridos y 5000m de desnivel acumulado.",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "privacy": "public",
            }
        }
