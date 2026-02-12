"""create_points_of_interest_table

Feature 003 - User Story 4: Points of Interest along routes

Creates the points_of_interest table for marking locations of interest
along a trip route (viewpoints, towns, water sources, accommodation, restaurants).

Revision ID: eee2b0a9b8cc
Revises: 4144c09f7bc0
Create Date: 2026-01-26 12:00:47.751696+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = "eee2b0a9b8cc"
down_revision: Union[str, None] = "4144c09f7bc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create points_of_interest table."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Detect database dialect
    is_postgresql = conn.dialect.name == "postgresql"

    # Create ENUM type for PostgreSQL only
    if is_postgresql:
        poi_type_enum = postgresql.ENUM(
            "viewpoint",
            "town",
            "water",
            "accommodation",
            "restaurant",
            "other",
            name="poi_type_enum",
            create_type=False,
        )
        # Check if enum type exists
        result = conn.execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'poi_type_enum')"
            )
        )
        enum_exists = result.scalar()

        if not enum_exists:
            poi_type_enum.create(conn, checkfirst=True)

    # Create points_of_interest table
    op.create_table(
        "points_of_interest",
        sa.Column("poi_id", sa.String(36), primary_key=True),
        sa.Column("trip_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column(
            "poi_type",
            postgresql.ENUM(
                "viewpoint",
                "town",
                "water",
                "accommodation",
                "restaurant",
                "other",
                name="poi_type_enum",
                create_type=False,  # Don't auto-create, we handle it manually above
            )
            if is_postgresql
            else sa.String(50),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("distance_from_start_km", sa.Float(), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=is_postgresql),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["trip_id"], ["trips.trip_id"], ondelete="CASCADE"
        ),
        # Add CHECK constraints for SQLite (PostgreSQL inherits from column types)
        sa.CheckConstraint(
            "latitude >= -90 AND latitude <= 90", name="check_poi_latitude_range"
        ),
        sa.CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="check_poi_longitude_range",
        ),
    )

    # Create indexes
    op.create_index("idx_poi_trip", "points_of_interest", ["trip_id"])
    op.create_index(
        "idx_poi_type", "points_of_interest", ["trip_id", "poi_type"]
    )
    op.create_index(
        "idx_poi_sequence", "points_of_interest", ["trip_id", "sequence"]
    )


def downgrade() -> None:
    """Drop points_of_interest table."""
    conn = op.get_bind()
    is_postgresql = conn.dialect.name == "postgresql"

    # Drop indexes first
    op.drop_index("idx_poi_sequence", table_name="points_of_interest")
    op.drop_index("idx_poi_type", table_name="points_of_interest")
    op.drop_index("idx_poi_trip", table_name="points_of_interest")

    # Drop table
    op.drop_table("points_of_interest")

    # Drop ENUM type for PostgreSQL
    if is_postgresql:
        poi_type_enum = postgresql.ENUM(
            "viewpoint",
            "town",
            "water",
            "accommodation",
            "restaurant",
            "other",
            name="poi_type_enum",
        )
        poi_type_enum.drop(conn, checkfirst=True)
