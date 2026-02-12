"""
Trip Photos API endpoints for Travel Diary feature.

Provides REST API for managing trip photo gallery: upload, delete, and reorder photos.

Functional Requirements: FR-009, FR-010, FR-011, FR-012, FR-013
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["trip-photos"])


# Pydantic schema for photo reorder request
class PhotoReorderRequest(BaseModel):
    """Request schema for reordering photos."""

    photo_order: list[str]


@router.post(
    "/{trip_id}/photos",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Upload photo to trip",
    description="Upload a photo to trip gallery. Max 20 photos per trip, max 10MB per photo.",
)
async def upload_photo(
    trip_id: str,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Upload photo to trip (FR-009, FR-010, FR-011).

    Validates photo format (JPG, PNG, WebP), checks limit (max 20),
    processes image (resize, thumbnail generation), and saves to storage.

    Args:
        trip_id: Trip identifier
        photo: Photo file
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with photo data

    Raises:
        400: Invalid photo format or limit exceeded
        404: Trip not found
        403: Permission denied (not trip owner)
        401: Unauthorized
    """
    try:
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        photo.file.seek(0, 2)  # Seek to end
        file_size = photo.file.tell()
        photo.file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise ValueError("La foto excede el tamaño máximo de 10MB")

        # Upload photo
        service = TripService(db)
        photo_record = await service.upload_photo(
            trip_id=trip_id,
            user_id=current_user.id,
            photo_file=photo.file,
            filename=photo.filename,
            content_type=photo.content_type,
        )

        return {
            "success": True,
            "data": {
                "id": photo_record.photo_id,
                "trip_id": photo_record.trip_id,
                "photo_url": photo_record.photo_url,
                "thumb_url": photo_record.thumb_url,
                "order": photo_record.order,
                "file_size": photo_record.file_size,
                "width": photo_record.width,
                "height": photo_record.height,
                "uploaded_at": photo_record.uploaded_at.isoformat() + "Z"
                if photo_record.uploaded_at
                else None,
            },
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied uploading photo to trip {trip_id}: {e}")
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

        logger.warning(f"Error uploading photo to trip {trip_id}: {e}")
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
        logger.error(f"Error uploading photo to trip {trip_id}: {e}", exc_info=True)
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


@router.delete(
    "/{trip_id}/photos/{photo_id}",
    response_model=dict[str, Any],
    summary="Delete photo from trip",
    description="Remove a photo from trip gallery and delete files from storage.",
)
async def delete_photo(
    trip_id: str,
    photo_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Delete photo from trip (FR-013).

    Removes photo from database and deletes files from storage.

    Args:
        trip_id: Trip identifier
        photo_id: Photo identifier
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with success message

    Raises:
        404: Trip or photo not found
        403: Permission denied (not trip owner)
        401: Unauthorized
    """
    try:
        service = TripService(db)
        result = await service.delete_photo(
            trip_id=trip_id,
            photo_id=photo_id,
            user_id=current_user.id,
        )

        return {
            "success": True,
            "data": result,
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied deleting photo {photo_id} from trip {trip_id}: {e}")
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
        logger.warning(f"Error deleting photo {photo_id} from trip {trip_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": str(e),
                },
            },
        )
    except Exception as e:
        logger.error(f"Error deleting photo {photo_id} from trip {trip_id}: {e}", exc_info=True)
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


@router.put(
    "/{trip_id}/photos/reorder",
    response_model=dict[str, Any],
    summary="Reorder photos in trip gallery",
    description="Update the order of photos in trip gallery.",
)
async def reorder_photos(
    trip_id: str,
    request: PhotoReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Reorder photos in trip gallery (FR-012).

    Updates the order field for each photo based on provided photo_ids list.

    Args:
        trip_id: Trip identifier
        request: Photo reorder request with photo_order list
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with success message

    Raises:
        400: Invalid photo IDs (don't match trip's photos)
        404: Trip not found
        403: Permission denied (not trip owner)
        401: Unauthorized
    """
    try:
        service = TripService(db)
        result = await service.reorder_photos(
            trip_id=trip_id,
            user_id=current_user.id,
            photo_order=request.photo_order,
        )

        return {
            "success": True,
            "data": result,
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied reordering photos for trip {trip_id}: {e}")
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

        logger.warning(f"Error reordering photos for trip {trip_id}: {e}")
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
        logger.error(f"Error reordering photos for trip {trip_id}: {e}", exc_info=True)
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
