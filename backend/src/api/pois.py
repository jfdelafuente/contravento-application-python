"""
POI (Point of Interest) API endpoints for GPS Routes feature.

Feature 003 - User Story 4: Points of Interest along routes

Provides REST API for managing POIs on trip routes.
Functional Requirements: FR-029
Success Criteria: SC-029, SC-030, SC-031
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.api_response import ErrorResponse
from src.schemas.poi import (
    POICreateInput,
    POIListResponse,
    POIReorderInput,
    POIResponse,
    POITypeEnum,
    POIUpdateInput,
)
from src.services.poi_service import POIService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["pois"])


# ============================================================================
# POI CRUD Endpoints
# ============================================================================


@router.post(
    "/trips/{trip_id}/pois",
    response_model=POIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new POI",
    description="Add a Point of Interest to a published trip (FR-029). Maximum 20 POIs per trip (SC-029).",
    responses={
        201: {"description": "POI created successfully"},
        400: {
            "model": ErrorResponse,
            "description": "Validation error (trip not published, max 20 POIs exceeded)",
        },
        403: {"model": ErrorResponse, "description": "User is not trip owner"},
        404: {"model": ErrorResponse, "description": "Trip not found"},
    },
)
async def create_poi(
    trip_id: str,
    data: POICreateInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> POIResponse:
    """
    Create a new Point of Interest for a trip.

    FR-029: Users can add POIs to published trips
    SC-029: Maximum 20 POIs per trip

    **Requirements:**
    - User must be the trip owner
    - Trip must be published
    - Maximum 20 POIs per trip

    **POI Types:**
    - viewpoint (mirador)
    - town (pueblo)
    - water (fuente de agua)
    - accommodation (alojamiento)
    - restaurant (restaurante)
    - other (otro)

    Args:
        trip_id: Parent trip ID
        data: POI creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        POIResponse with created POI
    """
    try:
        poi_service = POIService(db)
        poi = await poi_service.create_poi(trip_id, current_user.id, data)

        return POIResponse.model_validate(poi)

    except PermissionError as e:
        logger.warning(f"Permission denied creating POI for trip {trip_id}: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        logger.warning(f"Validation error creating POI for trip {trip_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/trips/{trip_id}/pois",
    response_model=POIListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get trip POIs",
    description="Get all Points of Interest for a trip, optionally filtered by type (SC-030).",
    responses={
        200: {"description": "POI list retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Trip not found"},
    },
)
async def get_trip_pois(
    trip_id: str,
    poi_type: POITypeEnum | None = Query(None, description="Filter by POI type (optional)"),
    db: AsyncSession = Depends(get_db),
) -> POIListResponse:
    """
    Get all POIs for a trip, optionally filtered by type.

    SC-030: POIs can be filtered by type

    **Type filters:**
    - viewpoint
    - town
    - water
    - accommodation
    - restaurant
    - other

    Args:
        trip_id: Trip ID
        poi_type: Optional type filter
        db: Database session

    Returns:
        POIListResponse with list of POIs (ordered by sequence)
    """
    try:
        poi_service = POIService(db)
        pois = await poi_service.get_trip_pois(trip_id, poi_type)

        poi_responses = [POIResponse.model_validate(poi) for poi in pois]

        return POIListResponse(pois=poi_responses, total=len(poi_responses))

    except ValueError as e:
        logger.warning(f"Error retrieving POIs for trip {trip_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/pois/{poi_id}",
    response_model=POIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get POI by ID",
    description="Get a single Point of Interest by its ID (SC-031).",
    responses={
        200: {"description": "POI retrieved successfully"},
        404: {"model": ErrorResponse, "description": "POI not found"},
    },
)
async def get_poi(
    poi_id: str,
    db: AsyncSession = Depends(get_db),
) -> POIResponse:
    """
    Get a single POI by ID.

    SC-031: Clicking POI shows popup with name, description, photo, distance

    Args:
        poi_id: POI ID
        db: Database session

    Returns:
        POIResponse with POI details
    """
    try:
        poi_service = POIService(db)
        poi = await poi_service.get_poi(poi_id)

        return POIResponse.model_validate(poi)

    except ValueError as e:
        logger.warning(f"POI {poi_id} not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/pois/{poi_id}",
    response_model=POIResponse,
    status_code=status.HTTP_200_OK,
    summary="Update POI",
    description="Update a Point of Interest. Only trip owner can update.",
    responses={
        200: {"description": "POI updated successfully"},
        403: {"model": ErrorResponse, "description": "User is not trip owner"},
        404: {"model": ErrorResponse, "description": "POI not found"},
    },
)
async def update_poi(
    poi_id: str,
    data: POIUpdateInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> POIResponse:
    """
    Update a Point of Interest.

    **Requirements:**
    - User must be the trip owner

    **Updatable fields:**
    - name
    - description
    - poi_type
    - latitude/longitude
    - distance_from_start_km
    - photo_url
    - sequence

    Args:
        poi_id: POI ID
        data: POI update data (only provided fields will be updated)
        db: Database session
        current_user: Authenticated user

    Returns:
        POIResponse with updated POI
    """
    try:
        poi_service = POIService(db)
        poi = await poi_service.update_poi(poi_id, current_user.id, data)

        return POIResponse.model_validate(poi)

    except PermissionError as e:
        logger.warning(f"Permission denied updating POI {poi_id}: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        logger.warning(f"Error updating POI {poi_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/pois/{poi_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete POI",
    description="Delete a Point of Interest. Only trip owner can delete.",
    responses={
        204: {"description": "POI deleted successfully"},
        403: {"model": ErrorResponse, "description": "User is not trip owner"},
        404: {"model": ErrorResponse, "description": "POI not found"},
    },
)
async def delete_poi(
    poi_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a Point of Interest.

    **Requirements:**
    - User must be the trip owner

    Args:
        poi_id: POI ID
        db: Database session
        current_user: Authenticated user

    Returns:
        204 No Content on success
    """
    try:
        poi_service = POIService(db)
        await poi_service.delete_poi(poi_id, current_user.id)

        logger.info(f"POI {poi_id} deleted by user {current_user.id}")

    except PermissionError as e:
        logger.warning(f"Permission denied deleting POI {poi_id}: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        logger.warning(f"Error deleting POI {poi_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/pois/{poi_id}/photo",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Upload photo to POI",
    description="Upload a photo to a Point of Interest (FR-010). Max 5MB per photo. Only trip owner can upload.",
    responses={
        200: {"description": "Photo uploaded successfully"},
        400: {
            "model": ErrorResponse,
            "description": "Validation error (invalid format, file too large)",
        },
        403: {"model": ErrorResponse, "description": "User is not trip owner"},
        404: {"model": ErrorResponse, "description": "POI not found"},
    },
)
async def upload_poi_photo(
    poi_id: str,
    photo: UploadFile = File(..., description="Photo file (JPEG, PNG, WebP, max 5MB)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Upload a photo to a Point of Interest.

    FR-010 (Feature 017): POIs can have photos (max 5MB)

    **Requirements:**
    - User must be the trip owner
    - Photo format: JPEG, PNG, or WebP
    - Max file size: 5MB
    - Only 1 photo per POI (replaces existing photo)

    Args:
        poi_id: POI ID
        photo: Photo file
        db: Database session
        current_user: Authenticated user

    Returns:
        Standardized API response with POI data including photo_url
    """
    try:
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        photo.file.seek(0, 2)  # Seek to end
        file_size = photo.file.tell()
        photo.file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise ValueError("La foto excede el tamaño máximo de 5MB")

        # Upload photo
        poi_service = POIService(db)
        poi = await poi_service.upload_photo(
            poi_id=poi_id,
            user_id=current_user.id,
            photo_file=photo.file,
            filename=photo.filename or "photo.jpg",
            content_type=photo.content_type or "image/jpeg",
        )

        return {
            "success": True,
            "data": {
                "poi_id": poi.poi_id,
                "photo_url": poi.photo_url,
                "name": poi.name,
                "poi_type": poi.poi_type.value,
            },
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied uploading photo to POI {poi_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FORBIDDEN",
                    "message": str(e),
                },
            },
        )

    except ValueError as e:
        error_msg = str(e)
        # Check if it's a not found error or validation error
        if "no encontrado" in error_msg.lower() or "not found" in error_msg.lower():
            status_code = status.HTTP_404_NOT_FOUND
            error_code = "NOT_FOUND"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            error_code = "VALIDATION_ERROR"

        logger.warning(f"Error uploading photo to POI {poi_id}: {e}")
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": error_code,
                    "message": error_msg,
                },
            },
        )

    except Exception as e:
        logger.error(f"Error uploading photo to POI {poi_id}: {e}", exc_info=True)
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


@router.post(
    "/trips/{trip_id}/pois/reorder",
    response_model=POIListResponse,
    status_code=status.HTTP_200_OK,
    summary="Reorder POIs",
    description="Reorder all POIs for a trip without affecting GPX route (FR-029).",
    responses={
        200: {"description": "POIs reordered successfully"},
        400: {"model": ErrorResponse, "description": "Validation error (missing/extra POIs)"},
        403: {"model": ErrorResponse, "description": "User is not trip owner"},
        404: {"model": ErrorResponse, "description": "Trip not found"},
    },
)
async def reorder_pois(
    trip_id: str,
    data: POIReorderInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> POIListResponse:
    """
    Reorder POIs for a trip.

    FR-029: Users can reorder POIs without affecting GPX route

    **Requirements:**
    - User must be the trip owner
    - Must include ALL POI IDs from the trip (no additions or omissions)

    Args:
        trip_id: Trip ID
        data: Ordered list of POI IDs
        db: Database session
        current_user: Authenticated user

    Returns:
        POIListResponse with reordered POI list
    """
    try:
        poi_service = POIService(db)
        pois = await poi_service.reorder_pois(trip_id, current_user.id, data.poi_ids)

        poi_responses = [POIResponse.model_validate(poi) for poi in pois]

        return POIListResponse(pois=poi_responses, total=len(poi_responses))

    except PermissionError as e:
        logger.warning(f"Permission denied reordering POIs for trip {trip_id}: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        logger.warning(f"Validation error reordering POIs for trip {trip_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
