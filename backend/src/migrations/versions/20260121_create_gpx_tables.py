"""Create GPX tables for Feature 003 - GPS Routes Interactive

Revision ID: f8a7b3c2d491
Revises: 44e29a9f8684
Create Date: 2026-01-21 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = "f8a7b3c2d491"
down_revision: Union[str, None] = "44e29a9f8684"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create gpx_files and track_points tables."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Detect database dialect
    is_postgresql = conn.dialect.name == 'postgresql'

    # Create gpx_files table
    op.create_table(
        'gpx_files',
        sa.Column('gpx_file_id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=False),
        sa.Column('elevation_gain', sa.Float(), nullable=True),
        sa.Column('elevation_loss', sa.Float(), nullable=True),
        sa.Column('max_elevation', sa.Float(), nullable=True),
        sa.Column('min_elevation', sa.Float(), nullable=True),
        sa.Column('start_lat', sa.Float(), nullable=False),
        sa.Column('start_lon', sa.Float(), nullable=False),
        sa.Column('end_lat', sa.Float(), nullable=False),
        sa.Column('end_lon', sa.Float(), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False),
        sa.Column('simplified_points', sa.Integer(), nullable=False),
        sa.Column('has_elevation', sa.Boolean(), nullable=False),
        sa.Column('has_timestamps', sa.Boolean(), nullable=False),
        sa.Column('processing_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.TIMESTAMP(timezone=is_postgresql), nullable=False, server_default=sa.func.now()),
        sa.Column('processed_at', sa.TIMESTAMP(timezone=is_postgresql), nullable=True),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.trip_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('trip_id', name='uq_gpx_files_trip_id')
    )

    op.create_index('idx_gpx_files_trip', 'gpx_files', ['trip_id'])
    op.create_index('idx_gpx_files_status', 'gpx_files', ['processing_status'])

    # Create track_points table
    op.create_table(
        'track_points',
        sa.Column('point_id', sa.String(36), primary_key=True),
        sa.Column('gpx_file_id', sa.String(36), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('elevation', sa.Float(), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('gradient', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['gpx_file_id'], ['gpx_files.gpx_file_id'], ondelete='CASCADE')
    )

    op.create_index('idx_track_points_gpx', 'track_points', ['gpx_file_id'])
    op.create_index('idx_track_points_seq', 'track_points', ['gpx_file_id', 'sequence'])

    if is_postgresql:
        op.create_index(
            'idx_track_points_unique_seq',
            'track_points',
            ['gpx_file_id', 'sequence'],
            unique=True
        )


def downgrade() -> None:
    """Drop GPX tables."""
    op.drop_table('track_points')
    op.drop_table('gpx_files')
