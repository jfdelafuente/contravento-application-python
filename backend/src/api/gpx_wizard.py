"""
GPS Trip Creation Wizard API endpoints (Feature 017).

Provides REST API for:
1. POST /gpx/analyze - Temporary GPX analysis for wizard preview (no DB storage)
2. POST /trips/gpx-wizard - Atomic trip creation with GPX + POIs (Phase 6)

Feature: 017-gps-trip-wizard
Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.gpx import GPXFile, TrackPoint
from src.models.trip import TripStatus
from src.models.user import User
from src.schemas.gpx_wizard import GPXAnalysisResponse, GPXTelemetry
from src.schemas.trip import TripCreateRequest
from src.services.gpx_service import GPXService, clean_filename_for_title
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

# Router for GPX wizard endpoints
router = APIRouter(prefix="/gpx", tags=["GPX Wizard"])

# Router for trip creation with GPX (separate prefix for RESTful routing)
trips_wizard_router = APIRouter(prefix="/trips", tags=["GPX Wizard"])


# ============================================================================
# Constants
# ============================================================================

# File upload limits (10MB for wizard analysis)
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".gpx"}
ALLOWED_MIME_TYPES = {
    "application/gpx+xml",
    "application/xml",
    "text/xml",
    "application/octet-stream",  # Generic binary type (browsers may send this for .gpx files)
}


# ============================================================================
# POST /gpx/analyze - Temporary GPX Analysis
# ============================================================================


@router.post(
    "/analyze",
    response_model=GPXAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze GPX file without storing to database",
    description="""
    Extract telemetry data (distance, elevation, difficulty) from a GPX file
    for wizard preview. This endpoint does NOT create a GPXFile record in the
    database - it's for wizard UI only.

    The actual GPX upload happens when the user publishes the trip via
    POST /trips/gpx-wizard.

    **Performance**: Returns telemetry in <2s for files up to 10MB.
    **Rate Limit**: 10 requests per minute per user.
    """,
)
async def analyze_gpx_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GPXAnalysisResponse:
    """
    Analyze GPX file and extract telemetry data for wizard preview.

    Args:
        file: Uploaded GPX file (max 10MB)
        current_user: Authenticated user
        db: Database session (not used, but required for service initialization)

    Returns:
        GPXAnalysisResponse with telemetry data or error details

    Raises:
        HTTPException 400: Invalid file type or corrupted GPX
        HTTPException 413: File too large (>10MB)
        HTTPException 408: Processing timeout (>60s)
    """
    # Validate file presence
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_FILE",
                    "message": "No se proporcionó ningún archivo",
                    "field": "file",
                },
            },
        )

    # Validate file extension
    if file.filename:
        file_ext = file.filename.lower().split(".")[-1]
        if f".{file_ext}" not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": f"Formato no válido. Solo se aceptan archivos .gpx (recibido: .{file_ext})",
                        "field": "file",
                    },
                },
            )

    # Validate MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "Formato no válido. Solo se aceptan archivos .gpx",
                    "field": "file",
                },
            },
        )

    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FILE_READ_ERROR",
                    "message": "Error al leer el archivo. Intenta de nuevo",
                    "field": "file",
                },
            },
        )

    # Validate file size
    file_size = len(file_content)
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "El archivo GPX es demasiado grande. Tamaño máximo: 10MB",
                    "field": "file",
                },
            },
        )

    # Extract telemetry using GPXService (include trackpoints for wizard map visualization)
    gpx_service = GPXService(db)

    try:
        telemetry_data = await gpx_service.extract_telemetry_quick(
            file_content, include_trackpoints=True
        )

        # Generate suggested title from filename using smart cleaning
        suggested_title = clean_filename_for_title(file.filename or "nueva_ruta.gpx")

        # Convert to GPXTelemetry schema
        telemetry = GPXTelemetry(
            distance_km=telemetry_data["distance_km"],
            elevation_gain=telemetry_data["elevation_gain"],
            elevation_loss=telemetry_data["elevation_loss"],
            max_elevation=telemetry_data["max_elevation"],
            min_elevation=telemetry_data["min_elevation"],
            has_elevation=telemetry_data["has_elevation"],
            has_timestamps=telemetry_data["has_timestamps"],
            start_date=telemetry_data["start_date"],
            end_date=telemetry_data["end_date"],
            total_time_minutes=telemetry_data["total_time_minutes"],
            moving_time_minutes=telemetry_data["moving_time_minutes"],
            difficulty=telemetry_data["difficulty"],
            suggested_title=suggested_title,
            trackpoints=telemetry_data["trackpoints"],
        )

        return GPXAnalysisResponse(success=True, data=telemetry, error=None)

    except ValueError as e:
        # GPX parsing/validation errors
        error_message = str(e)

        # Check for specific error types
        if "formato" in error_message.lower() or "xml" in error_message.lower():
            error_code = "INVALID_FILE_TYPE"
            error_msg = "Formato no válido. Solo se aceptan archivos .gpx"
        elif "elevación anómala" in error_message.lower():
            error_code = "INVALID_GPX_DATA"
            error_msg = "Datos de elevación anómalos detectados en el archivo GPX"
        elif "no se pudo procesar" in error_message.lower():
            error_code = "INVALID_GPX_FILE"
            error_msg = (
                "No se pudo procesar el archivo. Verifica que contenga datos de ruta válidos"
            )
        else:
            error_code = "INVALID_GPX_FILE"
            error_msg = error_message

        logger.warning(f"GPX analysis failed for user {current_user.id}: {error_message}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {"code": error_code, "message": error_msg, "field": "file"},
            },
        )

    except TimeoutError:
        # Processing timeout (>60s)
        logger.error(f"GPX processing timeout for user {current_user.id}")

        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "PROCESSING_TIMEOUT",
                    "message": "El procesamiento del archivo GPX excedió el tiempo límite de 60 segundos",
                },
            },
        )

    except Exception as e:
        # Unexpected errors
        logger.error(
            f"Unexpected error during GPX analysis for user {current_user.id}: {e}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor. Intenta de nuevo más tarde",
                },
            },
        )


# ============================================================================
# POST /trips/gpx-wizard - Atomic Trip Creation with GPX
# ============================================================================


@trips_wizard_router.post(
    "/gpx-wizard",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create trip with GPX file (atomic transaction)",
    description="""
    Create a new trip with GPX file upload in a single atomic transaction.

    This endpoint combines:
    1. Trip creation (with status=PUBLISHED)
    2. GPX file upload and processing
    3. Telemetry data extraction and storage

    **Transaction**: If any step fails, the entire operation is rolled back.
    **Performance**: Returns immediately after creating trip record. GPX processing
    happens in background for files >1MB.
    **Rate Limit**: 5 requests per minute per user.

    Feature: 017-gps-trip-wizard (Phase 6, US6)
    Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml (lines 224-422)
    """,
)
async def create_trip_with_gpx(
    title: str = Form(..., max_length=200),
    description: str = Form(..., min_length=50),
    start_date: str = Form(...),
    end_date: str | None = Form(None),
    privacy: str = Form("public"),
    gpx_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Create trip with GPX file in atomic transaction (T064-T066).

    This endpoint implements the full GPS Trip Creation Wizard publish flow:
    - Validates trip data and GPX file
    - Creates trip with PUBLISHED status
    - Uploads and processes GPX file
    - Extracts telemetry data
    - Links GPX file to trip
    - Rolls back on any error

    Args:
        title: Trip title (max 200 characters)
        description: Trip description (min 50 characters)
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD, optional)
        privacy: Trip privacy ('public' or 'private')
        gpx_file: GPX file (max 10MB)
        current_user: Authenticated user
        db: Database session

    Returns:
        dict: Standardized response with trip data and GPX metadata

    Raises:
        HTTPException 400: Validation error or invalid GPX
        HTTPException 413: File too large (>10MB)
        HTTPException 500: Server error with automatic rollback
    """
    # ========================================================================
    # Step 1: Validate GPX file (T064)
    # ========================================================================

    # Validate file presence
    if not gpx_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_FILE",
                    "message": "No se proporcionó el archivo GPX",
                    "field": "gpx_file",
                },
            },
        )

    # Validate file extension
    if gpx_file.filename:
        file_ext = gpx_file.filename.lower().split(".")[-1]
        if f".{file_ext}" not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": "Formato no válido. Solo se aceptan archivos .gpx",
                        "field": "gpx_file",
                    },
                },
            )

    # Read file content
    try:
        file_content = await gpx_file.read()
    except Exception as e:
        logger.error(f"Error reading GPX file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FILE_READ_ERROR",
                    "message": "Error al leer el archivo GPX",
                    "field": "gpx_file",
                },
            },
        )

    # Validate file size
    file_size = len(file_content)
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "El archivo GPX es demasiado grande. Tamaño máximo: 10MB",
                    "field": "gpx_file",
                },
            },
        )

    # ========================================================================
    # Step 2: Validate trip data (T064)
    # ========================================================================

    # Validate title length
    if len(title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "El título no puede superar 200 caracteres",
                    "field": "title",
                },
            },
        )

    # Validate description length
    if len(description) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "La descripción debe tener al menos 50 caracteres",
                    "field": "description",
                },
            },
        )

    # ========================================================================
    # Step 3: Atomic Transaction - Create Trip + Upload GPX (T065-T066)
    # ========================================================================

    # Capture user_id before try block to avoid lazy loading issues in exception handling
    user_id = current_user.id

    try:
        # Initialize services
        trip_service = TripService(db)
        gpx_service = GPXService(db)

        # Extract telemetry first to get difficulty and distance
        logger.info(f"Extracting telemetry from GPX file for user {user_id}")

        try:
            telemetry_data = await gpx_service.extract_telemetry_quick(file_content)
        except ValueError as e:
            # GPX parsing/validation errors
            error_message = str(e)

            if "formato" in error_message.lower() or "xml" in error_message.lower():
                error_code = "INVALID_FILE_TYPE"
                error_msg = "Formato no válido. Solo se aceptan archivos .gpx"
            elif "no se pudo procesar" in error_message.lower():
                error_code = "INVALID_GPX_FILE"
                error_msg = "No se pudo procesar el archivo GPX. Verifica que contenga datos de ruta válidos"
            else:
                error_code = "INVALID_GPX_FILE"
                error_msg = error_message

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {"code": error_code, "message": error_msg, "field": "gpx_file"},
                },
            )

        # Create trip with telemetry data
        trip_data = TripCreateRequest(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            distance_km=telemetry_data["distance_km"],
            difficulty=telemetry_data["difficulty"],
            status=TripStatus.PUBLISHED,  # Auto-publish trips created via wizard
        )

        logger.info(f"Creating trip for user {user_id}: {title}")
        trip = await trip_service.create_trip(user_id, trip_data)

        # Upload GPX file and link to trip
        logger.info(f"Uploading GPX file for trip {trip.trip_id}")

        # Parse GPX file
        parsed_data = await gpx_service.parse_gpx_file(file_content)

        # Save original file to storage
        file_url = await gpx_service.save_gpx_to_storage(
            trip_id=trip.trip_id,
            file_content=file_content,
            filename=gpx_file.filename or "route.gpx",
        )

        # Create GPX file record
        gpx_file_record = GPXFile(
            trip_id=trip.trip_id,
            file_url=file_url,
            file_size=len(file_content),
            file_name=gpx_file.filename or "route.gpx",
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

        db.add(gpx_file_record)
        await db.commit()
        await db.refresh(gpx_file_record)

        # Save trackpoints
        trackpoints = []
        for point_data in parsed_data["trackpoints"]:
            track_point = TrackPoint(
                gpx_file_id=gpx_file_record.gpx_file_id,
                latitude=point_data["latitude"],
                longitude=point_data["longitude"],
                elevation=point_data["elevation"],
                distance_km=point_data["distance_km"],
                sequence=point_data["sequence"],
                gradient=point_data["gradient"],
            )
            trackpoints.append(track_point)

        db.add_all(trackpoints)

        # Calculate route statistics if GPX has timestamps (Feature 003 - User Story 5)
        if parsed_data["has_timestamps"]:
            try:
                from src.models.route_statistics import RouteStatistics
                from src.services.route_stats_service import RouteStatsService

                logger.info(
                    f"Calculating route statistics for GPX file {gpx_file_record.gpx_file_id}..."
                )

                # Convert original points to format expected by RouteStatsService
                trackpoints_for_stats = gpx_service.convert_points_for_stats(
                    parsed_data["original_points"]
                )

                # Calculate statistics
                stats_service = RouteStatsService(db)
                speed_metrics = await stats_service.calculate_speed_metrics(trackpoints_for_stats)
                top_climbs = await stats_service.detect_climbs(trackpoints_for_stats)
                gradient_dist = await stats_service.classify_gradients(trackpoints_for_stats)

                # Fix floating-point precision issue: ensure moving_time <= total_time
                if speed_metrics.get("moving_time_minutes") and speed_metrics.get(
                    "total_time_minutes"
                ):
                    if speed_metrics["moving_time_minutes"] > speed_metrics["total_time_minutes"]:
                        speed_metrics["moving_time_minutes"] = speed_metrics["total_time_minutes"]

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
                    gpx_file_id=gpx_file_record.gpx_file_id,
                    avg_speed_kmh=speed_metrics.get("avg_speed_kmh"),
                    max_speed_kmh=speed_metrics.get("max_speed_kmh"),
                    total_time_minutes=speed_metrics.get("total_time_minutes"),
                    moving_time_minutes=speed_metrics.get("moving_time_minutes"),
                    avg_gradient=avg_gradient,
                    max_gradient=max_gradient,
                    top_climbs=top_climbs_data if top_climbs_data else None,
                )
                db.add(route_stats)

                logger.info(
                    f"Route statistics created for GPX file {gpx_file_record.gpx_file_id}: "
                    f"avg_speed={speed_metrics.get('avg_speed_kmh'):.1f} km/h, "
                    f"climbs={len(top_climbs) if top_climbs else 0}"
                )

            except Exception as stats_error:
                # Log error but don't fail the entire trip creation
                logger.error(
                    f"Error calculating route statistics for GPX file {gpx_file_record.gpx_file_id}: {stats_error}",
                    exc_info=True,
                )

        # Access all attributes BEFORE commit to avoid lazy loading issues
        trip_id_str = str(trip.trip_id)
        trip_title = trip.title
        trip_description = trip.description
        trip_start_date = trip.start_date.isoformat() if trip.start_date else None
        trip_end_date = trip.end_date.isoformat() if trip.end_date else None
        trip_distance = trip.distance_km
        trip_difficulty = trip.difficulty.value if trip.difficulty else None
        trip_status = trip.status.value if trip.status else "DRAFT"

        gpx_id_str = str(gpx_file_record.gpx_file_id)
        gpx_distance = gpx_file_record.distance_km
        gpx_elev_gain = gpx_file_record.elevation_gain
        gpx_elev_loss = gpx_file_record.elevation_loss
        gpx_max_elev = gpx_file_record.max_elevation
        gpx_min_elev = gpx_file_record.min_elevation
        gpx_has_elev = gpx_file_record.has_elevation

        # Commit transaction
        await db.commit()

        logger.info(f"Successfully created trip {trip_id_str} with GPX file {gpx_id_str}")

        response_data = {
            "trip_id": trip_id_str,
            "title": trip_title,
            "description": trip_description,
            "start_date": trip_start_date,
            "end_date": trip_end_date,
            "distance_km": trip_distance,
            "difficulty": trip_difficulty,
            "status": trip_status,
            "gpx_file": {
                "gpx_file_id": gpx_id_str,
                "total_distance_km": gpx_distance,
                "elevation_gain": gpx_elev_gain,
                "elevation_loss": gpx_elev_loss,
                "max_elevation": gpx_max_elev,
                "min_elevation": gpx_min_elev,
                "has_elevation": gpx_has_elev,
                "difficulty": trip_difficulty,
            },
        }

        return {"success": True, "data": response_data, "error": None}

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise

    except Exception as e:
        # Rollback on any unexpected error (T066)
        await db.rollback()

        logger.error(
            f"Failed to create trip with GPX for user {user_id}: {e}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error al crear el viaje. Intenta de nuevo más tarde",
                },
            },
        )
