"""
FastAPI application entry point for ContraVento backend.

Initializes the FastAPI app with middleware, error handling, and routing.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings


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
    error: Dict[str, str] = None,
    message: str = None,
) -> Dict[str, Any]:
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
    # Extract error details
    if isinstance(exc.detail, dict):
        error = exc.detail
    else:
        error = {
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=create_response(success=False, error=error),
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
    response.headers["X-Timestamp"] = datetime.utcnow().isoformat() + "Z"
    return response


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
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
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


# Root endpoint
@app.get("/", tags=["System"])
async def root() -> Dict[str, Any]:
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
from src.api import auth, profile, stats, social
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(stats.router)
app.include_router(stats.achievements_router)
app.include_router(social.router)
