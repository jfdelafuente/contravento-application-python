"""
Profile API endpoints.

Handles user profile management including viewing, updating, photo upload, and privacy settings.

Endpoints:
- GET /users/{username}/profile: View public profile (optional auth)
- PUT /users/{username}/profile: Update profile (authenticated, owner-only)
- POST /users/{username}/profile/photo: Upload profile photo (authenticated, owner-only)
- DELETE /users/{username}/profile/photo: Delete profile photo (authenticated, owner-only)
- PUT /users/{username}/profile/privacy: Update privacy settings (authenticated, owner-only)
"""

from typing import Dict, Any, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_user, get_optional_current_user
from src.services.profile_service import ProfileService
from src.schemas.profile import (
    ProfileResponse,
    ProfileUpdateRequest,
    PrivacySettings,
    PhotoUploadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["profile"])


def create_response(success: bool, data: Any = None, error: Dict = None, message: str = None) -> Dict:
    """
    Create standardized JSON response.

    Args:
        success: Success flag
        data: Response data
        error: Error details
        message: Optional success message

    Returns:
        Standardized response dict
    """
    response = {"success": success, "data": data, "error": error}
    if message:
        response["message"] = message
    return response


def check_owner_authorization(current_user: dict, username: str) -> None:
    """
    Check if current user is the owner of the profile.

    Args:
        current_user: Current authenticated user
        username: Profile username being accessed

    Raises:
        HTTPException 403: If user is not the owner
    """
    if current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "No tienes permiso para modificar este perfil",
            },
        )


@router.get("/{username}/profile", response_model=ProfileResponse)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_current_user),
) -> ProfileResponse:
    """
    T123: Get user profile (public endpoint with optional authentication).

    Returns public profile data respecting privacy settings.
    If authenticated, may show additional information if viewing own profile.

    **Functional Requirements**: FR-014

    Args:
        username: Username of profile to retrieve
        db: Database session
        current_user: Optional current user (if authenticated)

    Returns:
        ProfileResponse with public profile data

    Raises:
        HTTPException 404: If user not found
    """
    try:
        profile_service = ProfileService(db)
        viewer_username = current_user["username"] if current_user else None

        profile = await profile_service.get_profile(
            username=username,
            viewer_username=viewer_username
        )

        return profile

    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(f"Error retrieving profile for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener el perfil",
            },
        )


@router.put("/{username}/profile")
async def update_user_profile(
    username: str,
    update_data: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """
    T124: Update user profile (authenticated, owner-only).

    Updates profile fields like bio, location, cycling type, and privacy settings.

    **Functional Requirements**: FR-015, FR-016

    Args:
        username: Username of profile to update
        update_data: Profile update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated profile data

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not the profile owner
        HTTPException 404: If user not found
        HTTPException 400: If validation fails
    """
    # T131: Check owner authorization
    check_owner_authorization(current_user, username)

    try:
        profile_service = ProfileService(db)
        profile = await profile_service.update_profile(
            username=username,
            update_data=update_data
        )

        return create_response(
            success=True,
            data=profile.model_dump(),
            message="Perfil actualizado correctamente"
        )

    except ValueError as e:
        # T133, T134: Validation errors (bio length, cycling_type)
        error_msg = str(e)

        if "no existe" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": error_msg,
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": error_msg,
                },
            )

    except Exception as e:
        logger.error(f"Error updating profile for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al actualizar el perfil",
            },
        )


@router.post("/{username}/profile/photo")
async def upload_profile_photo(
    username: str,
    photo: UploadFile = File(..., description="Profile photo (JPEG, PNG, or WebP, max 5MB)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """
    T125: Upload profile photo (authenticated, owner-only).

    Uploads and processes profile photo. Photo is validated, resized to 400x400px,
    and stored. Old photo is replaced if exists.

    **Functional Requirements**: FR-012, FR-013

    Args:
        username: Username of profile
        photo: Uploaded photo file
        db: Database session
        current_user: Current authenticated user

    Returns:
        Photo URL and dimensions

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not the profile owner
        HTTPException 404: If user not found
        HTTPException 400: If photo validation fails
    """
    # T131: Check owner authorization
    check_owner_authorization(current_user, username)

    try:
        profile_service = ProfileService(db)
        result = await profile_service.upload_photo(
            username=username,
            photo_file=photo
        )

        return create_response(
            success=True,
            data=result,
            message="Foto de perfil actualizada correctamente"
        )

    except ValueError as e:
        # T135, T136: Photo validation errors (size, format)
        error_msg = str(e)

        if "no existe" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": error_msg,
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": error_msg,
                },
            )

    except IOError as e:
        logger.error(f"IO error uploading photo for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "FILE_SAVE_ERROR",
                "message": "Error al guardar la foto",
            },
        )

    except Exception as e:
        logger.error(f"Error uploading photo for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al subir la foto",
            },
        )


@router.delete("/{username}/profile/photo")
async def delete_profile_photo(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """
    T126: Delete profile photo (authenticated, owner-only).

    Removes profile photo from storage and database.

    **Functional Requirements**: FR-013

    Args:
        username: Username of profile
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success confirmation

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not the profile owner
        HTTPException 404: If user not found
    """
    # T131: Check owner authorization
    check_owner_authorization(current_user, username)

    try:
        profile_service = ProfileService(db)
        await profile_service.delete_photo(username=username)

        return create_response(
            success=True,
            data=None,
            message="Foto de perfil eliminada correctamente"
        )

    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Error deleting photo for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al eliminar la foto",
            },
        )


@router.put("/{username}/profile/privacy")
async def update_privacy_settings(
    username: str,
    privacy_settings: PrivacySettings,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """
    T127: Update privacy settings (authenticated, owner-only).

    Updates show_email and show_location privacy preferences.

    **Functional Requirements**: FR-017

    Args:
        username: Username of profile
        privacy_settings: Privacy settings to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated privacy settings

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not the profile owner
        HTTPException 404: If user not found
    """
    # T131: Check owner authorization
    check_owner_authorization(current_user, username)

    try:
        profile_service = ProfileService(db)
        result = await profile_service.update_privacy(
            username=username,
            privacy_settings=privacy_settings
        )

        return create_response(
            success=True,
            data=result,
            message="Configuración de privacidad actualizada"
        )

    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Error updating privacy for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al actualizar la privacidad",
            },
        )
