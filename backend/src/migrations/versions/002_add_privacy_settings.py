"""002_add_privacy_settings

Add privacy settings to user profiles.

Adds show_email and show_location columns to user_profiles table.

Revision ID: 002
Revises: 001
Create Date: 2025-12-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add privacy settings columns to user_profiles."""
    # Add show_email column (default False)
    op.add_column(
        'user_profiles',
        sa.Column('show_email', sa.Boolean(), nullable=False, server_default='0')
    )

    # Add show_location column (default True)
    op.add_column(
        'user_profiles',
        sa.Column('show_location', sa.Boolean(), nullable=False, server_default='1')
    )


def downgrade() -> None:
    """Remove privacy settings columns from user_profiles."""
    op.drop_column('user_profiles', 'show_location')
    op.drop_column('user_profiles', 'show_email')
