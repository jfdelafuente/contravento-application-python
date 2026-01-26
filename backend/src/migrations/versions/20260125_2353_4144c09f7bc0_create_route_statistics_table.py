"""create route_statistics table

Revision ID: 4144c09f7bc0
Revises: f8a7b3c2d491
Create Date: 2026-01-25 23:53:21.582221+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4144c09f7bc0"
down_revision: Union[str, None] = "f8a7b3c2d491"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create route_statistics table for User Story 5 (Advanced Statistics)."""
    # Detect database dialect
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        # PostgreSQL DDL
        op.execute(
            """
            CREATE TABLE route_statistics (
                stats_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                gpx_file_id UUID UNIQUE NOT NULL,
                avg_speed_kmh DOUBLE PRECISION,
                max_speed_kmh DOUBLE PRECISION,
                total_time_minutes DOUBLE PRECISION,
                moving_time_minutes DOUBLE PRECISION,
                avg_gradient DOUBLE PRECISION,
                max_gradient DOUBLE PRECISION,
                top_climbs JSONB,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

                FOREIGN KEY (gpx_file_id) REFERENCES gpx_files(gpx_file_id) ON DELETE CASCADE
            )
            """
        )

        op.execute(
            """
            CREATE INDEX idx_route_stats_gpx ON route_statistics(gpx_file_id)
            """
        )
    else:
        # SQLite DDL
        op.execute(
            """
            CREATE TABLE route_statistics (
                stats_id TEXT PRIMARY KEY,
                gpx_file_id TEXT UNIQUE NOT NULL,
                avg_speed_kmh REAL,
                max_speed_kmh REAL,
                total_time_minutes REAL,
                moving_time_minutes REAL,
                avg_gradient REAL,
                max_gradient REAL,
                top_climbs TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (gpx_file_id) REFERENCES gpx_files(gpx_file_id) ON DELETE CASCADE
            )
            """
        )

        op.execute(
            """
            CREATE INDEX idx_route_stats_gpx ON route_statistics(gpx_file_id)
            """
        )


def downgrade() -> None:
    """Drop route_statistics table."""
    op.drop_index("idx_route_stats_gpx", table_name="route_statistics")
    op.drop_table("route_statistics")
