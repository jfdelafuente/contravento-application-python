"""
FastAPI application entry point for ContraVento backend.

Initializes the FastAPI app with middleware, error handling, and routing.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.models.comment import Comment  # noqa: F401
from src.models.cycling_type import CyclingType  # noqa: F401
from src.models.like import Like  # noqa: F401
from src.models.notification import Notification, NotificationArchive  # noqa: F401
from src.models.share import Share  # noqa: F401
from src.models.social import Follow  # noqa: F401
from src.models.stats import Achievement, UserAchievement, UserStats  # noqa: F401
from src.models.trip import Tag, Trip, TripLocation, TripPhoto, TripTag  # noqa: F401

# Import all models to ensure SQLAlchemy relationships are resolved
# This must happen before any route handlers are registered
from src.models.user import User, UserProfile  # noqa: F401

# Create FastAPI application
app = FastAPI(
    title="ContraVento API",
    description="API backend para ContraVento - Plataforma social de cicloturismo",
    version="0.1.0",
    docs_url="/docs" if settings.is_development or settings.is_testing else None,
    redoc_url="/redoc" if settings.is_development or settings.is_testing else None,
)


# CORS Middleware (T025)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standardized JSON response format per constitution
def create_response(
    success: bool,
    data: Any = None,
    error: dict[str, str] = None,
    message: str = None,
) -> dict[str, Any]:
    """
    Create standardized API response.

    Format per constitution III:
    {
        "success": true/false,
        "data": {...},
        "error": {"code": "...", "message": "..."}
    }

    Args:
        success: Whether the request was successful
        data: Response data (if successful)
        error: Error details (if failed)
        message: Optional message

    Returns:
        Standardized response dictionary
    """
    response = {
        "success": success,
        "data": data,
        "error": error,
    }

    if message:
        response["message"] = message

    return response


# Error handling middleware (T026)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with standardized JSON response.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        Standardized error response
    """
    # Check if detail is already in the standardized format
    if isinstance(exc.detail, dict) and "success" in exc.detail and "error" in exc.detail:
        # Already formatted, return as-is
        content = exc.detail
    elif isinstance(exc.detail, dict):
        # Has some structure but not standardized, wrap the error
        error = exc.detail
        content = create_response(success=False, error=error)
    else:
        # Plain string, create error structure
        error = {
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
        }
        content = create_response(success=False, error=error)

    # Build response headers - include CORS headers for preflight/error responses
    response_headers = {}

    # Get origin from request
    origin = request.headers.get("origin")
    if origin and origin in settings.cors_origins:
        response_headers["Access-Control-Allow-Origin"] = origin
        response_headers["Access-Control-Allow-Credentials"] = "true"

    # Preserve WWW-Authenticate header if present
    if hasattr(exc, "headers") and exc.headers:
        response_headers.update(exc.headers)

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=response_headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors with Spanish field-specific messages.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        Standardized validation error response
    """
    # Extract first validation error
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = ".".join(str(loc) for loc in first_error["loc"] if loc != "body")
        message = first_error["msg"]

        error = {
            "code": "VALIDATION_ERROR",
            "message": f"Error de validación en el campo '{field}': {message}",
            "field": field,
        }
    else:
        error = {
            "code": "VALIDATION_ERROR",
            "message": "Error de validación en la solicitud",
        }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=create_response(success=False, error=error),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions with generic error message.

    Never expose stack traces to users per constitution.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        Generic error response
    """
    # Log the actual error for debugging
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    error = {
        "code": "INTERNAL_ERROR",
        "message": "Ha ocurrido un error interno. Por favor intenta de nuevo más tarde.",
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_response(success=False, error=error),
    )


# Timezone-aware UTC timestamp handling (T027)
@app.middleware("http")
async def add_timestamp_header(request: Request, call_next):
    """
    Add UTC timestamp to all responses.

    Args:
        request: FastAPI request
        call_next: Next middleware

    Returns:
        Response with timestamp header
    """
    response = await call_next(request)
    response.headers["X-Timestamp"] = datetime.now(UTC).isoformat() + "Z"
    return response


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        System health status
    """
    return create_response(
        success=True,
        data={
            "status": "healthy",
            "environment": settings.app_env,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
        },
    )


# Root endpoint
@app.get("/", tags=["System"])
async def root() -> dict[str, Any]:
    """
    Root endpoint.

    Returns:
        API welcome message
    """
    return create_response(
        success=True,
        data={
            "message": "ContraVento API",
            "version": "0.1.0",
            "docs": "/docs" if settings.is_development or settings.is_testing else None,
        },
    )


# Include routers (T028)
from src.api import auth, cycling_types, feed, likes, profile, social, stats, trips

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(stats.router)
app.include_router(stats.achievements_router)
app.include_router(social.router)
app.include_router(feed.router)  # Feature 004: Personalized feed
app.include_router(likes.router)  # Feature 004: Likes/Me Gusta
app.include_router(trips.router)
app.include_router(trips.user_router)  # Phase 6: User-facing trip endpoints
app.include_router(cycling_types.router)  # Public cycling types endpoint
app.include_router(cycling_types.admin_router)  # Admin cycling types endpoints

# Mount static files for uploaded content (profile photos, trip photos, etc.)
storage_path = Path(settings.storage_path)
if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")
else:
    # Create storage directory if it doesn't exist
    storage_path.mkdir(parents=True, exist_ok=True)
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")
