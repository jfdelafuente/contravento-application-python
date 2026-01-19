"""
Pydantic schemas for Comment API endpoints (Feature 004 - US3: Comentarios).

Schemas:
- CommentCreateInput: Input for creating comments (T085)
- CommentUpdateInput: Input for updating comments (T086)
- CommentResponse: Response for comment operations (T087)
- CommentsListResponse: Paginated list of comments (T088)
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CommentCreateInput(BaseModel):
    """
    Input schema for POST /trips/{id}/comments (T085).

    Validation:
    - content: 1-500 chars after trimming (FR-017)
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Comment text (1-500 characters)",
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty after trimming."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("El contenido del comentario no puede estar vacío")
        if len(trimmed) > 500:
            raise ValueError(
                "El comentario debe tener entre 1 y 500 caracteres después de eliminar espacios"
            )
        return trimmed


class CommentUpdateInput(BaseModel):
    """
    Input schema for PUT /comments/{id} (T086).

    Validation:
    - content: 1-500 chars after trimming (FR-017)
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Updated comment text (1-500 characters)",
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty after trimming."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("El contenido del comentario no puede estar vacío")
        if len(trimmed) > 500:
            raise ValueError(
                "El comentario debe tener entre 1 y 500 caracteres después de eliminar espacios"
            )
        return trimmed


class UserSummaryForComment(BaseModel):
    """Minimal user details for comments list."""

    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    full_name: str | None = Field(None, description="Full name (nullable)")
    profile_photo_url: str | None = Field(
        None, description="Profile photo URL (nullable)"
    )


class CommentResponse(BaseModel):
    """
    Response schema for comment operations (T087).

    Used for:
    - POST /trips/{id}/comments (create)
    - PUT /comments/{id} (update)
    - GET /trips/{id}/comments (list item)
    """

    id: str = Field(..., description="Comment ID (UUID)")
    user_id: str = Field(..., description="ID of user who commented")
    trip_id: str = Field(..., description="ID of trip being commented on")
    content: str = Field(..., description="Comment text (sanitized HTML)")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    updated_at: datetime | None = Field(
        None, description="Last edit timestamp (null if not edited)"
    )
    is_edited: bool = Field(
        ..., description="True if comment was edited (FR-019, FR-020)"
    )

    # Optional: Include user details in response
    author: UserSummaryForComment | None = Field(
        None, description="Comment author details (optional)"
    )

    model_config = {"from_attributes": True}


class CommentsListResponse(BaseModel):
    """
    Response schema for GET /trips/{id}/comments (T088).

    Pagination:
    - Default limit: 50 items (FR-024)
    - Chronological order: oldest first (FR-018)
    """

    items: list[CommentResponse] = Field(..., description="List of comments")
    total: int = Field(..., ge=0, description="Total number of comments on trip")
    limit: int = Field(..., ge=1, le=50, description="Items per page (max 50)")
    offset: int = Field(..., ge=0, description="Number of items skipped")

    model_config = {"from_attributes": True}
