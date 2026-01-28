"""
GPX Routes API endpoints (Feature 003 - GPS Routes Interactive).

Provides REST API for uploading, processing, and retrieving GPX track data.
Functional Requirements: FR-001 to FR-039
Success Criteria: SC-002, SC-003, SC-007, SC-016, SC-021 to SC-028
"""

import logging
import re
from datetime import UTC, datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.deps import get_current_user, get_db
from src.models.gpx import GPXFile, TrackPoint
from src.models.trip import Trip
from src.models.user import User
from src.schemas.gpx import (
    GPXMetadataSuccessResponse,
    GPXStatusSuccessResponse,
    GPXUploadSuccessResponse,
    TrackDataSuccessResponse,
)
from src.services.gpx_service import GPXService

logger = logging.getLogger(__name__)

# Router for trip-scoped GPX endpoints (/trips/{trip_id}/gpx)
trip_gpx_router = APIRouter(prefix="/trips", tags=["gpx"])

# Router for standalone GPX endpoints (/gpx/{gpx_file_id}/...)
gpx_router = APIRouter(prefix="/gpx", tags=["gpx"])


# ============================================================================
# Background Processing Helper
# ============================================================================


async def process_gpx_background(
    gpx_file_id: str,
    trip_id: str,
    file_content: bytes,
    filename: str,
) -> None:
    """
    Background task to process large GPX files (>1MB).

    This function runs asynchronously after returning 202 Accepted to the client.
    It performs the same processing as sync mode but without blocking the HTTP response.

    Args:
        gpx_file_id: GPX file record ID to update
        trip_id: Trip identifier
        file_content: Raw GPX file bytes
        filename: Original filename

    Updates GPX record status to "completed" or "failed"
    """
    from src.database import get_db

    # Get database session using the application's session factory
    async for db in get_db():
        try:
            # Fetch GPX file record
            result = await db.execute(select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id))
            gpx_file = result.scalar_one_or_none()

            if not gpx_file:
                logger.error(f"GPX file {gpx_file_id} not found in background task")
                return

            # Initialize GPX service
            gpx_service = GPXService(db)

            # Parse GPX file
            parsed_data = await gpx_service.parse_gpx_file(file_content)

            # Save original file to storage
            file_url = await gpx_service.save_gpx_to_storage(
                trip_id=trip_id, file_content=file_content, filename=filename
            )

            # Update GPX file record with parsed data
            gpx_file.file_url = file_url
            gpx_file.distance_km = parsed_data["distance_km"]
            gpx_file.elevation_gain = parsed_data["elevation_gain"]
            gpx_file.elevation_loss = parsed_data["elevation_loss"]
            gpx_file.max_elevation = parsed_data["max_elevation"]
            gpx_file.min_elevation = parsed_data["min_elevation"]
            gpx_file.start_lat = parsed_data["start_lat"]
            gpx_file.start_lon = parsed_data["start_lon"]
            gpx_file.end_lat = parsed_data["end_lat"]
            gpx_file.end_lon = parsed_data["end_lon"]
            gpx_file.total_points = parsed_data["total_points"]
            gpx_file.simplified_points = parsed_data["simplified_points_count"]
            gpx_file.has_elevation = parsed_data["has_elevation"]
            gpx_file.has_timestamps = parsed_data["has_timestamps"]
            gpx_file.processing_status = "completed"
            gpx_file.processed_at = datetime.now(UTC)

            await db.commit()

            # Save trackpoints
            trackpoints = []
            for point_data in parsed_data["trackpoints"]:
                track_point = TrackPoint(
                    gpx_file_id=gpx_file.gpx_file_id,
                    latitude=point_data["latitude"],
                    longitude=point_data["longitude"],
                    elevation=point_data["elevation"],
                    distance_km=point_data["distance_km"],
                    sequence=point_data["sequence"],
                    gradient=point_data["gradient"],
                )
                trackpoints.append(track_point)

            db.add_all(trackpoints)
            await db.commit()

            logger.info(
                f"Background GPX processing completed for file {gpx_file_id} "
                f"({len(trackpoints)} points, {parsed_data['distance_km']:.2f} km)"
            )

            # Calculate route statistics if GPX has timestamps (T134 - User Story 5)
            if parsed_data["has_timestamps"]:
                try:
                    from src.models.route_statistics import RouteStatistics
                    from src.services.route_stats_service import RouteStatsService

                    logger.info(f"Calculating route statistics for GPX file {gpx_file_id}...")

                    # Convert original points to format expected by RouteStatsService
                    trackpoints_for_stats = gpx_service.convert_points_for_stats(
                        parsed_data["original_points"]
                    )

                    # Calculate statistics
                    stats_service = RouteStatsService(db)
                    speed_metrics = await stats_service.calculate_speed_metrics(
                        trackpoints_for_stats
                    )
                    top_climbs = await stats_service.detect_climbs(trackpoints_for_stats)
                    gradient_dist = await stats_service.classify_gradients(trackpoints_for_stats)

                    # Fix floating-point precision issue: ensure moving_time <= total_time
                    if speed_metrics.get("moving_time_minutes") and speed_metrics.get(
                        "total_time_minutes"
                    ):
                        if (
                            speed_metrics["moving_time_minutes"]
                            > speed_metrics["total_time_minutes"]
                        ):
                            # Clamp moving_time to total_time (precision error fix)
                            speed_metrics["moving_time_minutes"] = speed_metrics[
                                "total_time_minutes"
                            ]

                    # Calculate weighted average gradient from distribution
                    total_distance = (
                        gradient_dist["llano"]["distance_km"]
                        + gradient_dist["moderado"]["distance_km"]
                        + gradient_dist["empinado"]["distance_km"]
                        + gradient_dist["muy_empinado"]["distance_km"]
                    )

                    if total_distance > 0:
                        avg_gradient = (
                            (gradient_dist["llano"]["distance_km"] * 1.5)
                            + (gradient_dist["moderado"]["distance_km"] * 4.5)
                            + (gradient_dist["empinado"]["distance_km"] * 8.0)
                            + (gradient_dist["muy_empinado"]["distance_km"] * 12.0)
                        ) / total_distance
                    else:
                        avg_gradient = None

                    # Find max gradient from trackpoints
                    max_gradient = None
                    if parsed_data["has_elevation"]:
                        gradients = [
                            p.get("gradient")
                            for p in trackpoints_for_stats
                            if p.get("gradient") is not None
                        ]
                        max_gradient = max(gradients) if gradients else None

                    # Convert top climbs to JSON format
                    top_climbs_data = (
                        [
                            {
                                "start_km": climb["start_km"],
                                "end_km": climb["end_km"],
                                "elevation_gain_m": climb["elevation_gain_m"],
                                "avg_gradient": climb["avg_gradient"],
                                "description": f"Subida {i+1}: {climb['elevation_gain_m']:.0f}m gain, {climb['avg_gradient']:.1f}% avg gradient",
                            }
                            for i, climb in enumerate(top_climbs[:3])
                        ]
                        if top_climbs
                        else None
                    )

                    # Create RouteStatistics record
                    route_stats = RouteStatistics(
                        gpx_file_id=gpx_file.gpx_file_id,
                        avg_speed_kmh=speed_metrics.get("avg_speed_kmh"),
                        max_speed_kmh=speed_metrics.get("max_speed_kmh"),
                        total_time_minutes=speed_metrics.get("total_time_minutes"),
                        moving_time_minutes=speed_metrics.get("moving_time_minutes"),
                        avg_gradient=avg_gradient,
                        max_gradient=max_gradient,
                        top_climbs=top_climbs_data if top_climbs_data else None,
                    )
                    db.add(route_stats)
                    await db.commit()
                    await db.refresh(route_stats)

                    logger.info(
                        f"Route statistics created for GPX file {gpx_file_id}: "
                        f"avg_speed={speed_metrics.get('avg_speed_kmh'):.1f} km/h, "
                        f"climbs={len(top_climbs) if top_climbs else 0}"
                    )

                except Exception as stats_error:
                    # Log error but don't fail the entire GPX processing
                    logger.error(
                        f"Error calculating route statistics for GPX file {gpx_file_id}: {stats_error}",
                        exc_info=True,
                    )

        except ValueError as e:
            # GPX parsing error - mark as failed
            logger.error(f"GPX parsing error in background task for {gpx_file_id}: {e}")
            if gpx_file:
                gpx_file.processing_status = "failed"
                gpx_file.error_message = str(e)
                await db.commit()

        except Exception as e:
            # Unexpected error - mark as failed
            logger.error(
                f"Unexpected error in background GPX processing for {gpx_file_id}: {e}",
                exc_info=True,
            )
            if gpx_file:
                gpx_file.processing_status = "failed"
                gpx_file.error_message = "Error interno al procesar el archivo GPX"
                await db.commit()

        # Session will be automatically closed by async context manager
        break  # Exit after first (and only) session iteration


# ============================================================================
# Trip-Scoped GPX Endpoints (/trips/{trip_id}/gpx)
# ============================================================================


@trip_gpx_router.post(
    "/{trip_id}/gpx",
    response_model=GPXUploadSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload GPX file to trip",
    description="Upload a GPX file to a trip. Files <1MB processed sync, >1MB async.",
)
async def upload_gpx_file(
    trip_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GPXUploadSuccessResponse:
    """
    T029: Upload GPX file to trip (FR-001, FR-002, SC-002, SC-003).

    Processing modes:
    - Files <1MB: Synchronous (201 Created with full data)
    - Files >1MB: Asynchronous (202 Accepted, poll /gpx/{gpx_id}/status)

    Requirements:
    - User must be trip owner
    - File must be .gpx format
    - File size ≤10MB (FR-001)
    - Trip can have at most 1 GPX file

    Performance:
    - SC-002: <3s for files <1MB
    - SC-003: <15s for files 5-10MB

    Args:
        trip_id: Trip identifier
        file: GPX file upload
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session

    Returns:
        GPXUploadSuccessResponse with upload status and data

    Raises:
        400: Validation error (file too large, invalid format, trip already has GPX)
        401: Unauthorized
        403: Forbidden (not trip owner)
        404: Trip not found
    """
    try:
        # Validate file extension (T034)
        if not file.filename or not file.filename.lower().endswith(".gpx"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": "Solo se permiten archivos .gpx",
                    },
                },
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size (max 10MB) - T034, FR-001
        MAX_SIZE_MB = 10
        max_size_bytes = MAX_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"El archivo GPX no puede exceder {MAX_SIZE_MB}MB. Tamaño actual: {file_size / (1024 * 1024):.1f}MB",
                    },
                },
            )

        # Verify trip exists
        trip_result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Viaje no encontrado",
                    },
                },
            )

        # Check ownership
        if trip.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Solo el propietario del viaje puede subir archivos GPX",
                    },
                },
            )

        # Check if trip already has GPX file - T034
        existing_gpx = await db.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        if existing_gpx.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "TRIP_ALREADY_HAS_GPX",
                        "message": "Este viaje ya tiene un archivo GPX. Elimínalo primero si deseas subir uno nuevo.",
                    },
                },
            )

        # Initialize GPX service
        gpx_service = GPXService(db)

        # Determine processing mode based on file size
        ASYNC_THRESHOLD_MB = 1
        async_threshold_bytes = ASYNC_THRESHOLD_MB * 1024 * 1024

        if file_size <= async_threshold_bytes:
            # Synchronous processing (<1MB files) - SC-002
            try:
                # Parse GPX file (T023)
                parsed_data = await gpx_service.parse_gpx_file(file_content)

                # Save original file to storage (T026)
                file_url = await gpx_service.save_gpx_to_storage(
                    trip_id=trip_id, file_content=file_content, filename=file.filename
                )

                # Create GPX file record
                gpx_file = GPXFile(
                    trip_id=trip_id,
                    file_url=file_url,
                    file_size=file_size,
                    file_name=file.filename,
                    distance_km=parsed_data["distance_km"],
                    elevation_gain=parsed_data["elevation_gain"],
                    elevation_loss=parsed_data["elevation_loss"],
                    max_elevation=parsed_data["max_elevation"],
                    min_elevation=parsed_data["min_elevation"],
                    start_lat=parsed_data["start_lat"],
                    start_lon=parsed_data["start_lon"],
                    end_lat=parsed_data["end_lat"],
                    end_lon=parsed_data["end_lon"],
                    total_points=parsed_data["total_points"],
                    simplified_points=parsed_data["simplified_points_count"],
                    has_elevation=parsed_data["has_elevation"],
                    has_timestamps=parsed_data["has_timestamps"],
                    processing_status="completed",
                    processed_at=datetime.now(UTC),
                )

                db.add(gpx_file)
                await db.commit()
                await db.refresh(gpx_file)

                # Save trackpoints
                trackpoints = []
                for point_data in parsed_data["trackpoints"]:
                    track_point = TrackPoint(
                        gpx_file_id=gpx_file.gpx_file_id,
                        latitude=point_data["latitude"],
                        longitude=point_data["longitude"],
                        elevation=point_data["elevation"],
                        distance_km=point_data["distance_km"],
                        sequence=point_data["sequence"],
                        gradient=point_data["gradient"],
                    )
                    trackpoints.append(track_point)

                db.add_all(trackpoints)
                await db.commit()

                # Calculate advanced route statistics if timestamps available (User Story 5)
                # FR-030 to FR-034, SC-021 to SC-024
                if parsed_data["has_timestamps"]:
                    from src.models.route_statistics import RouteStatistics
                    from src.services.route_stats_service import RouteStatsService

                    try:
                        # Convert GPX trackpoints to dict format for RouteStatsService
                        trackpoints_for_stats = gpx_service.convert_points_for_stats(
                            parsed_data["original_points"]
                        )

                        # Initialize RouteStatsService
                        stats_service = RouteStatsService(db)

                        # Calculate speed metrics (FR-030)
                        speed_metrics = await stats_service.calculate_speed_metrics(
                            trackpoints_for_stats
                        )

                        # Fix floating-point precision issue: ensure moving_time <= total_time
                        if speed_metrics.get("moving_time_minutes") and speed_metrics.get(
                            "total_time_minutes"
                        ):
                            if (
                                speed_metrics["moving_time_minutes"]
                                > speed_metrics["total_time_minutes"]
                            ):
                                # Clamp moving_time to total_time (precision error fix)
                                speed_metrics["moving_time_minutes"] = speed_metrics[
                                    "total_time_minutes"
                                ]

                        # Detect top 3 climbs (FR-031)
                        top_climbs = await stats_service.detect_climbs(trackpoints_for_stats)

                        # Calculate gradient metrics (avg/max)
                        gradient_distribution = await stats_service.classify_gradients(
                            trackpoints_for_stats
                        )

                        # Calculate avg/max gradient from distribution
                        # (avg gradient = weighted average of all categories)
                        # (max gradient = steepest segment in muy_empinado category)
                        avg_gradient = None
                        max_gradient = None
                        if parsed_data["has_elevation"]:
                            # Weighted average of uphill gradients
                            total_distance = sum(
                                cat["distance_km"]
                                for cat in gradient_distribution.values()
                                if cat["distance_km"] > 0
                            )
                            if total_distance > 0:
                                # Weight each category by its midpoint gradient
                                # llano: 1.5%, moderado: 4.5%, empinado: 8%, muy_empinado: 12%
                                weighted_sum = (
                                    gradient_distribution["llano"]["distance_km"] * 1.5
                                    + gradient_distribution["moderado"]["distance_km"] * 4.5
                                    + gradient_distribution["empinado"]["distance_km"] * 8.0
                                    + gradient_distribution["muy_empinado"]["distance_km"] * 12.0
                                )
                                avg_gradient = round(weighted_sum / total_distance, 1)

                            # Max gradient is assumed from muy_empinado category
                            if gradient_distribution["muy_empinado"]["distance_km"] > 0:
                                max_gradient = 15.0  # Conservative estimate for muy_empinado

                        # Convert top climbs to JSON format with description field
                        top_climbs_data = (
                            [
                                {
                                    "start_km": climb["start_km"],
                                    "end_km": climb["end_km"],
                                    "elevation_gain_m": climb["elevation_gain_m"],
                                    "avg_gradient": climb["avg_gradient"],
                                    "description": f"Subida {i+1}: {climb['elevation_gain_m']:.0f}m gain, {climb['avg_gradient']:.1f}% avg gradient",
                                }
                                for i, climb in enumerate(top_climbs[:3])
                            ]
                            if top_climbs
                            else None
                        )

                        # Create RouteStatistics record
                        route_stats = RouteStatistics(
                            gpx_file_id=gpx_file.gpx_file_id,
                            avg_speed_kmh=speed_metrics["avg_speed_kmh"],
                            max_speed_kmh=speed_metrics["max_speed_kmh"],
                            total_time_minutes=speed_metrics["total_time_minutes"],
                            moving_time_minutes=speed_metrics["moving_time_minutes"],
                            avg_gradient=avg_gradient,
                            max_gradient=max_gradient,
                            top_climbs=top_climbs_data if top_climbs_data else None,
                        )
                        db.add(route_stats)
                        await db.commit()
                        logger.info(
                            f"Route statistics calculated for GPX {gpx_file.gpx_file_id}: "
                            f"avg_speed={speed_metrics['avg_speed_kmh']} km/h, "
                            f"{len(top_climbs_data)} climbs"
                        )
                    except Exception as e:
                        # Log error but don't fail the upload
                        logger.error(f"Failed to calculate route statistics: {e}")

                # Return full response (201 Created)
                from src.schemas.gpx import GPXUploadResponse

                response_data = GPXUploadResponse(
                    gpx_file_id=gpx_file.gpx_file_id,
                    trip_id=gpx_file.trip_id,
                    processing_status=gpx_file.processing_status,
                    distance_km=gpx_file.distance_km,
                    elevation_gain=gpx_file.elevation_gain,
                    elevation_loss=gpx_file.elevation_loss,
                    max_elevation=gpx_file.max_elevation,
                    min_elevation=gpx_file.min_elevation,
                    has_elevation=gpx_file.has_elevation,
                    has_timestamps=gpx_file.has_timestamps,
                    total_points=gpx_file.total_points,
                    simplified_points=gpx_file.simplified_points,
                    uploaded_at=gpx_file.uploaded_at,
                    processed_at=gpx_file.processed_at,
                )

                return GPXUploadSuccessResponse(success=True, data=response_data)

            except ValueError as e:
                # GPX parsing error (T035 - Spanish error messages)
                logger.warning(f"GPX parsing error for trip {trip_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "INVALID_GPX_FORMAT",
                            "message": str(e),
                        },
                    },
                )

        else:
            # Asynchronous processing (>1MB files) - SC-003
            from src.config import settings

            # IN TESTING MODE: Process synchronously to avoid SQLite :memory: isolation issues
            if settings.app_env == "testing":
                # Process synchronously (same behavior as <1MB files for testing)
                try:
                    # Parse GPX file
                    parsed_data = await gpx_service.parse_gpx_file(file_content)

                    # Save original file to storage
                    file_url = await gpx_service.save_gpx_to_storage(
                        trip_id=trip_id, file_content=file_content, filename=file.filename
                    )

                    # Create GPX file record with completed status
                    gpx_file = GPXFile(
                        trip_id=trip_id,
                        file_url=file_url,
                        file_size=file_size,
                        file_name=file.filename,
                        distance_km=parsed_data["distance_km"],
                        elevation_gain=parsed_data["elevation_gain"],
                        elevation_loss=parsed_data["elevation_loss"],
                        max_elevation=parsed_data["max_elevation"],
                        min_elevation=parsed_data["min_elevation"],
                        start_lat=parsed_data["start_lat"],
                        start_lon=parsed_data["start_lon"],
                        end_lat=parsed_data["end_lat"],
                        end_lon=parsed_data["end_lon"],
                        total_points=parsed_data["total_points"],
                        simplified_points=parsed_data["simplified_points_count"],
                        has_elevation=parsed_data["has_elevation"],
                        has_timestamps=parsed_data["has_timestamps"],
                        processing_status="completed",
                        processed_at=datetime.now(UTC),
                    )

                    db.add(gpx_file)
                    await db.commit()
                    await db.refresh(gpx_file)

                    # Save trackpoints
                    trackpoints = []
                    for point_data in parsed_data["trackpoints"]:
                        track_point = TrackPoint(
                            gpx_file_id=gpx_file.gpx_file_id,
                            latitude=point_data["latitude"],
                            longitude=point_data["longitude"],
                            elevation=point_data["elevation"],
                            distance_km=point_data["distance_km"],
                            sequence=point_data["sequence"],
                            gradient=point_data["gradient"],
                        )
                        trackpoints.append(track_point)

                    db.add_all(trackpoints)
                    await db.commit()

                    # Calculate advanced route statistics if timestamps available (User Story 5)
                    # FR-030 to FR-034, SC-021 to SC-024
                    if parsed_data["has_timestamps"]:
                        from src.models.route_statistics import RouteStatistics
                        from src.services.route_stats_service import RouteStatsService

                        try:
                            # Convert GPX trackpoints to dict format for RouteStatsService
                            trackpoints_for_stats = gpx_service.convert_points_for_stats(
                                parsed_data["original_points"]
                            )

                            # Initialize RouteStatsService
                            stats_service = RouteStatsService(db)

                            # Calculate speed metrics (FR-030)
                            speed_metrics = await stats_service.calculate_speed_metrics(
                                trackpoints_for_stats
                            )

                            # Fix floating-point precision issue: ensure moving_time <= total_time
                            if speed_metrics.get("moving_time_minutes") and speed_metrics.get(
                                "total_time_minutes"
                            ):
                                if (
                                    speed_metrics["moving_time_minutes"]
                                    > speed_metrics["total_time_minutes"]
                                ):
                                    # Clamp moving_time to total_time (precision error fix)
                                    speed_metrics["moving_time_minutes"] = speed_metrics[
                                        "total_time_minutes"
                                    ]

                            # Detect top 3 climbs (FR-031)
                            top_climbs = await stats_service.detect_climbs(trackpoints_for_stats)

                            # Calculate gradient metrics (avg/max)
                            gradient_distribution = await stats_service.classify_gradients(
                                trackpoints_for_stats
                            )

                            # Calculate avg/max gradient from distribution
                            avg_gradient = None
                            max_gradient = None
                            if parsed_data["has_elevation"]:
                                # Weighted average of uphill gradients
                                total_distance = sum(
                                    cat["distance_km"]
                                    for cat in gradient_distribution.values()
                                    if cat["distance_km"] > 0
                                )
                                if total_distance > 0:
                                    weighted_sum = (
                                        gradient_distribution["llano"]["distance_km"] * 1.5
                                        + gradient_distribution["moderado"]["distance_km"] * 4.5
                                        + gradient_distribution["empinado"]["distance_km"] * 8.0
                                        + gradient_distribution["muy_empinado"]["distance_km"]
                                        * 12.0
                                    )
                                    avg_gradient = round(weighted_sum / total_distance, 1)

                                if gradient_distribution["muy_empinado"]["distance_km"] > 0:
                                    max_gradient = 15.0  # Conservative estimate

                            # Convert top climbs to JSON format with description field
                            top_climbs_data = (
                                [
                                    {
                                        "start_km": climb["start_km"],
                                        "end_km": climb["end_km"],
                                        "elevation_gain_m": climb["elevation_gain_m"],
                                        "avg_gradient": climb["avg_gradient"],
                                        "description": f"Subida {i+1}: {climb['elevation_gain_m']:.0f}m gain, {climb['avg_gradient']:.1f}% avg gradient",
                                    }
                                    for i, climb in enumerate(top_climbs[:3])
                                ]
                                if top_climbs
                                else None
                            )

                            # Create RouteStatistics record
                            route_stats = RouteStatistics(
                                gpx_file_id=gpx_file.gpx_file_id,
                                avg_speed_kmh=speed_metrics["avg_speed_kmh"],
                                max_speed_kmh=speed_metrics["max_speed_kmh"],
                                total_time_minutes=speed_metrics["total_time_minutes"],
                                moving_time_minutes=speed_metrics["moving_time_minutes"],
                                avg_gradient=avg_gradient,
                                max_gradient=max_gradient,
                                top_climbs=top_climbs_data if top_climbs_data else None,
                            )
                            db.add(route_stats)
                            await db.commit()
                            logger.info(
                                f"Route statistics calculated for GPX {gpx_file.gpx_file_id}: "
                                f"avg_speed={speed_metrics['avg_speed_kmh']} km/h, "
                                f"{len(top_climbs_data)} climbs"
                            )
                        except Exception as e:
                            # Log error but don't fail the upload
                            logger.error(f"Failed to calculate route statistics: {e}")

                    # Return 201 Created (synchronous)
                    from src.schemas.gpx import GPXUploadResponse

                    response_data = GPXUploadResponse(
                        gpx_file_id=gpx_file.gpx_file_id,
                        trip_id=gpx_file.trip_id,
                        processing_status=gpx_file.processing_status,
                        distance_km=gpx_file.distance_km,
                        elevation_gain=gpx_file.elevation_gain,
                        elevation_loss=gpx_file.elevation_loss,
                        max_elevation=gpx_file.max_elevation,
                        min_elevation=gpx_file.min_elevation,
                        has_elevation=gpx_file.has_elevation,
                        has_timestamps=gpx_file.has_timestamps,
                        total_points=gpx_file.total_points,
                        simplified_points=gpx_file.simplified_points,
                        uploaded_at=gpx_file.uploaded_at,
                        processed_at=gpx_file.processed_at,
                    )

                    return GPXUploadSuccessResponse(success=True, data=response_data)

                except ValueError as e:
                    # GPX parsing error
                    logger.warning(f"GPX parsing error for trip {trip_id}: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "success": False,
                            "data": None,
                            "error": {
                                "code": "INVALID_GPX_FORMAT",
                                "message": str(e),
                            },
                        },
                    )

            else:
                # PRODUCTION MODE: Process asynchronously with BackgroundTasks
                # Create GPX file record with "processing" status
                gpx_file = GPXFile(
                    trip_id=trip_id,
                    file_url="",  # Will be set after file is saved in background
                    file_size=file_size,
                    file_name=file.filename,
                    distance_km=0.0,  # Will be updated after processing
                    elevation_gain=0.0,
                    elevation_loss=0.0,
                    max_elevation=0.0,
                    min_elevation=0.0,
                    start_lat=0.0,  # Will be updated after parsing
                    start_lon=0.0,
                    end_lat=0.0,
                    end_lon=0.0,
                    total_points=0,  # Will be updated after parsing
                    simplified_points=0,
                    has_elevation=False,  # Will be updated after parsing
                    has_timestamps=False,
                    processing_status="processing",
                    uploaded_at=datetime.now(UTC),
                )

                db.add(gpx_file)
                await db.commit()
                await db.refresh(gpx_file)

                # Add background task to process GPX file
                if background_tasks is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "success": False,
                            "data": None,
                            "error": {
                                "code": "INTERNAL_ERROR",
                                "message": "BackgroundTasks no disponible para procesamiento asíncrono",
                            },
                        },
                    )

                background_tasks.add_task(
                    process_gpx_background,
                    gpx_file_id=str(gpx_file.gpx_file_id),
                    trip_id=trip_id,
                    file_content=file_content,
                    filename=file.filename,
                )

                # Return 202 Accepted with gpx_file_id for polling
                from src.schemas.gpx import GPXUploadResponse

                response_data = GPXUploadResponse(
                    gpx_file_id=gpx_file.gpx_file_id,
                    trip_id=gpx_file.trip_id,
                    processing_status="processing",
                    distance_km=None,
                    elevation_gain=None,
                    elevation_loss=None,
                    max_elevation=None,
                    min_elevation=None,
                    has_elevation=None,
                    has_timestamps=None,
                    total_points=None,
                    simplified_points=None,
                    uploaded_at=gpx_file.uploaded_at,
                    processed_at=None,
                )

                return JSONResponse(
                    status_code=status.HTTP_202_ACCEPTED,
                    content={
                        "success": True,
                        "data": response_data.model_dump(mode="json"),
                        "error": None,
                    },
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading GPX file to trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@trip_gpx_router.get(
    "/{trip_id}/gpx",
    response_model=GPXMetadataSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get GPX file metadata for trip",
    description="Retrieve metadata about the GPX file associated with a trip.",
)
async def get_gpx_metadata(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
) -> GPXMetadataSuccessResponse:
    """
    T031: Get GPX file metadata for trip.

    Public endpoint - No authentication required.

    Args:
        trip_id: Trip identifier
        db: Database session

    Returns:
        GPXMetadataSuccessResponse with GPX file metadata

    Raises:
        404: Trip not found or trip has no GPX file
    """
    try:
        # Get GPX file for trip
        result = await db.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "No se encontró archivo GPX para este viaje",
                    },
                },
            )

        # Convert to response schema
        from src.schemas.gpx import GPXFileMetadata

        metadata = GPXFileMetadata.model_validate(gpx_file)

        return GPXMetadataSuccessResponse(success=True, data=metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving GPX metadata for trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@trip_gpx_router.delete(
    "/{trip_id}/gpx",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete GPX file from trip",
    description="Remove GPX file and all associated trackpoints from a trip.",
)
async def delete_gpx_file(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    T033: Delete GPX file from trip (FR-036).

    Cascade deletes:
    - Trackpoints
    - Original GPX file from storage

    Args:
        trip_id: Trip identifier
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        401: Unauthorized
        403: Forbidden (not trip owner)
        404: Trip not found or trip has no GPX file
    """
    try:
        # Verify trip exists
        trip_result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Viaje no encontrado",
                    },
                },
            )

        # Check ownership
        if trip.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Solo el propietario del viaje puede eliminar archivos GPX",
                    },
                },
            )

        # Get GPX file
        gpx_result = await db.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        gpx_file = gpx_result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "No se encontró archivo GPX para este viaje",
                    },
                },
            )

        # Delete physical file from storage
        try:
            file_path = Path(gpx_file.file_url)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted GPX file from storage: {gpx_file.file_url}")
        except Exception as e:
            logger.warning(f"Failed to delete GPX file from storage: {e}")

        # Delete from database (cascade will delete trackpoints)
        await db.delete(gpx_file)
        await db.commit()

        logger.info(f"Deleted GPX file {gpx_file.gpx_file_id} from trip {trip_id}")

        # Return 204 No Content
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting GPX file from trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


# ============================================================================
# Standalone GPX Endpoints (/gpx/{gpx_file_id}/...)
# ============================================================================


@gpx_router.get(
    "/{gpx_file_id}/status",
    response_model=GPXStatusSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get GPX processing status",
    description="Poll processing status of uploaded GPX file (for async uploads).",
)
async def get_gpx_status(
    gpx_file_id: str,
    db: AsyncSession = Depends(get_db),
) -> GPXStatusSuccessResponse:
    """
    T030: Get GPX processing status.

    Used for polling async uploads (files >1MB).

    Args:
        gpx_file_id: GPX file identifier
        db: Database session

    Returns:
        GPXStatusSuccessResponse with processing status

    Raises:
        404: GPX file not found
    """
    try:
        # Get GPX file
        result = await db.execute(select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id))
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Archivo GPX no encontrado",
                    },
                },
            )

        # Convert to response schema
        from src.schemas.gpx import GPXStatusResponse

        status_data = GPXStatusResponse(
            gpx_file_id=gpx_file.gpx_file_id,
            processing_status=gpx_file.processing_status,
            distance_km=gpx_file.distance_km if gpx_file.processing_status == "completed" else None,
            elevation_gain=gpx_file.elevation_gain
            if gpx_file.processing_status == "completed"
            else None,
            total_points=gpx_file.total_points
            if gpx_file.processing_status == "completed"
            else None,
            simplified_points=gpx_file.simplified_points
            if gpx_file.processing_status == "completed"
            else None,
            uploaded_at=gpx_file.uploaded_at,
            processed_at=gpx_file.processed_at,
            error_message=gpx_file.error_message,
        )

        return GPXStatusSuccessResponse(success=True, data=status_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving GPX status {gpx_file_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@gpx_router.get(
    "/{gpx_file_id}/track",
    response_model=TrackDataSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get simplified trackpoints for map rendering",
    description="Retrieve simplified GPS trackpoints for route visualization.",
)
async def get_track_data(
    gpx_file_id: str,
    db: AsyncSession = Depends(get_db),
) -> TrackDataSuccessResponse:
    """
    Get trackpoints for map rendering (FR-009, SC-007).

    Returns simplified trackpoints (Douglas-Peucker algorithm).

    Public endpoint - No authentication required.

    Args:
        gpx_file_id: GPX file identifier
        db: Database session

    Returns:
        TrackDataSuccessResponse with simplified trackpoints

    Raises:
        404: GPX file not found or not yet processed
    """
    try:
        # Get GPX file
        result = await db.execute(select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id))
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Archivo GPX no encontrado",
                    },
                },
            )

        # Check processing status
        if gpx_file.processing_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_PROCESSED",
                        "message": f"Archivo GPX aún no procesado. Estado: {gpx_file.processing_status}",
                    },
                },
            )

        # Get trackpoints
        trackpoints_result = await db.execute(
            select(TrackPoint)
            .where(TrackPoint.gpx_file_id == gpx_file_id)
            .order_by(TrackPoint.sequence)
        )
        trackpoints = trackpoints_result.scalars().all()

        # Get route statistics (User Story 5) if available
        from src.models.route_statistics import RouteStatistics

        stats_result = await db.execute(
            select(RouteStatistics).where(RouteStatistics.gpx_file_id == gpx_file_id)
        )
        route_statistics = stats_result.scalar_one_or_none()

        # Calculate gradient distribution (FR-032) if statistics exist
        gradient_distribution = None
        if route_statistics and gpx_file.has_elevation:
            from src.services.route_stats_service import RouteStatsService

            # Convert trackpoints to dict format for stats service
            trackpoints_for_stats = []
            for tp in trackpoints:
                trackpoints_for_stats.append(
                    {
                        "latitude": tp.latitude,
                        "longitude": tp.longitude,
                        "elevation": tp.elevation,
                        "distance_km": tp.distance_km,
                        "timestamp": None,  # Not needed for gradient classification
                        "sequence": tp.sequence,
                    }
                )

            # Calculate gradient distribution
            stats_service = RouteStatsService(db)
            gradient_distribution = await stats_service.classify_gradients(trackpoints_for_stats)

        # Convert to response schema
        from src.schemas.gpx import (
            CoordinateResponse,
            GradientCategoryResponse,
            GradientDistributionResponse,
            RouteStatisticsResponse,
            RouteStatisticsWithDistributionResponse,
            TrackDataResponse,
            TrackPointResponse,
        )

        # Build route statistics response with gradient distribution (FR-032)
        route_stats_response = None
        if route_statistics:
            if gradient_distribution:
                # Use extended response with gradient distribution
                route_stats_response = RouteStatisticsWithDistributionResponse(
                    stats_id=str(route_statistics.stats_id),
                    gpx_file_id=str(route_statistics.gpx_file_id),
                    avg_speed_kmh=route_statistics.avg_speed_kmh,
                    max_speed_kmh=route_statistics.max_speed_kmh,
                    total_time_minutes=route_statistics.total_time_minutes,
                    moving_time_minutes=route_statistics.moving_time_minutes,
                    avg_gradient=route_statistics.avg_gradient,
                    max_gradient=route_statistics.max_gradient,
                    top_climbs=route_statistics.top_climbs,
                    created_at=route_statistics.created_at.isoformat(),
                    gradient_distribution=GradientDistributionResponse(
                        llano=GradientCategoryResponse(**gradient_distribution["llano"]),
                        moderado=GradientCategoryResponse(**gradient_distribution["moderado"]),
                        empinado=GradientCategoryResponse(**gradient_distribution["empinado"]),
                        muy_empinado=GradientCategoryResponse(
                            **gradient_distribution["muy_empinado"]
                        ),
                    ),
                )
            else:
                # Use standard response without gradient distribution
                route_stats_response = RouteStatisticsResponse.model_validate(route_statistics)

        track_data = TrackDataResponse(
            gpx_file_id=gpx_file.gpx_file_id,
            trip_id=gpx_file.trip_id,
            distance_km=gpx_file.distance_km,
            elevation_gain=gpx_file.elevation_gain,
            simplified_points_count=len(trackpoints),
            has_elevation=gpx_file.has_elevation,
            start_point=CoordinateResponse(
                latitude=gpx_file.start_lat, longitude=gpx_file.start_lon
            ),
            end_point=CoordinateResponse(latitude=gpx_file.end_lat, longitude=gpx_file.end_lon),
            trackpoints=[TrackPointResponse.model_validate(tp) for tp in trackpoints],
            route_statistics=route_stats_response,
        )

        return TrackDataSuccessResponse(success=True, data=track_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving track data {gpx_file_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@gpx_router.get(
    "/{gpx_file_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download original GPX file",
    description="Download the original unmodified GPX file.",
)
async def download_gpx_file(
    gpx_file_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    T032: Download original GPX file (FR-039, SC-028).

    Public endpoint - Anyone can download GPX files.

    Args:
        gpx_file_id: GPX file identifier
        db: Database session

    Returns:
        FileResponse with GPX file

    Raises:
        404: GPX file not found
    """
    try:
        # Get GPX file with associated trip (eager loading)
        result = await db.execute(
            select(GPXFile)
            .options(selectinload(GPXFile.trip))
            .where(GPXFile.gpx_file_id == gpx_file_id)
        )
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Archivo GPX no encontrado",
                    },
                },
            )

        # Check if file exists
        file_path = Path(gpx_file.file_url)
        if not file_path.exists():
            logger.error(f"GPX file not found in storage: {gpx_file.file_url}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": "Archivo GPX no encontrado en almacenamiento",
                    },
                },
            )

        # Generate filename from trip title (T048: Download as {trip_title}.gpx)
        # Sanitize trip title for filename (remove special characters)
        sanitized_title = re.sub(r"[^\w\s-]", "", gpx_file.trip.title)
        sanitized_title = re.sub(r"[-\s]+", "-", sanitized_title).strip("-")
        download_filename = f"{sanitized_title}.gpx"

        # Return file
        return FileResponse(
            path=str(file_path),
            media_type="application/gpx+xml",
            filename=download_filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading GPX file {gpx_file_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )
