"""Add profile_visibility and public feed indexes for Feature 013

Revision ID: 287f9f5c0f3a
Revises: 9676fc72ca21
Create Date: 2026-01-13 10:09:28.461548+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "287f9f5c0f3a"
down_revision: Union[str, None] = "9676fc72ca21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add profile_visibility field to users table and create indexes for public feed queries.

    Changes:
    1. Add profile_visibility column to users table (default='public')
    2. Create index on users.profile_visibility
    3. Create composite index on trips (status, published_at DESC) for efficient public feed queries
    """
    # Add profile_visibility column to users table
    op.add_column(
        "users",
        sa.Column(
            "profile_visibility",
            sa.String(20),
            nullable=False,
            server_default="public",
        ),
    )

    # Create index on profile_visibility
    op.create_index(
        "idx_users_profile_visibility", "users", ["profile_visibility"], unique=False
    )

    # Create composite index for public feed queries (status, published_at DESC)
    # This supports: WHERE status='PUBLISHED' AND user.profile_visibility='public' ORDER BY published_at DESC
    op.create_index(
        "idx_trips_public_feed",
        "trips",
        ["status", sa.text("published_at DESC")],
        unique=False,
        postgresql_where=sa.text("status = 'PUBLISHED'"),  # Partial index for PostgreSQL
    )


def downgrade() -> None:
    """
    Revert changes: remove profile_visibility field and indexes.
    """
    # Drop composite index
    op.drop_index("idx_trips_public_feed", table_name="trips")

    # Drop profile_visibility index
    op.drop_index("idx_users_profile_visibility", table_name="users")

    # Drop profile_visibility column
    op.drop_column("users", "profile_visibility")
