"""003_stats_and_achievements

Add statistics and achievements tables for User Story 3.

Creates:
- user_stats: Aggregated user statistics (1-to-1 with users)
- achievements: Achievement/badge definitions
- user_achievements: User-earned achievements (many-to-many join table)

Revision ID: 003
Revises: 002
Create Date: 2025-12-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add statistics and achievements tables."""

    # Create user_stats table
    op.create_table(
        'user_stats',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('total_trips', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_kilometers', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('countries_visited', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('total_photos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('achievements_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_trip_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create index on user_id for faster lookups
    op.create_index('ix_user_stats_user_id', 'user_stats', ['user_id'])

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('badge_icon', sa.String(10), nullable=False),
        sa.Column('requirement_type', sa.String(20), nullable=False),
        sa.Column('requirement_value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create index on code for faster lookups
    op.create_index('ix_achievements_code', 'achievements', ['code'])

    # Create user_achievements table (join table)
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', sa.String(36), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('awarded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for faster queries
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('ix_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])

    # Create unique constraint to prevent duplicate awards
    op.create_unique_constraint(
        'uq_user_achievement',
        'user_achievements',
        ['user_id', 'achievement_id']
    )


def downgrade() -> None:
    """Remove statistics and achievements tables."""

    # Drop tables in reverse order (children first)
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('user_stats')
