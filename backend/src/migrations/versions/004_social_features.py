"""
T200: Add social features tables and counters.

Creates:
- follows table for follow relationships
- followers_count and following_count in user_profiles

Revision ID: 004
Revises: 003
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade database schema.

    Creates:
    1. follows table with follower_id, following_id, created_at
    2. Unique constraint on (follower_id, following_id)
    3. CHECK constraint to prevent self-follows
    4. Indexes on follower_id, following_id, created_at
    5. followers_count and following_count columns in user_profiles
    """
    # Create follows table
    op.create_table(
        'follows',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('follower_id', sa.String(length=36), nullable=False),
        sa.Column('following_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['following_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('follower_id', 'following_id', name='uq_follower_following'),
        sa.CheckConstraint('follower_id != following_id', name='ck_no_self_follow'),
    )

    # Create indexes on follows table
    op.create_index('ix_follows_follower_id', 'follows', ['follower_id'])
    op.create_index('ix_follows_following_id', 'follows', ['following_id'])
    op.create_index('ix_follows_created_at', 'follows', ['created_at'])

    # Add follower/following counters to user_profiles
    op.add_column('user_profiles', sa.Column('followers_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_profiles', sa.Column('following_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """
    Downgrade database schema.

    Removes:
    1. followers_count and following_count columns from user_profiles
    2. follows table (cascades delete follow relationships)
    """
    # Remove counters from user_profiles
    op.drop_column('user_profiles', 'following_count')
    op.drop_column('user_profiles', 'followers_count')

    # Drop indexes
    op.drop_index('ix_follows_created_at', 'follows')
    op.drop_index('ix_follows_following_id', 'follows')
    op.drop_index('ix_follows_follower_id', 'follows')

    # Drop follows table
    op.drop_table('follows')
