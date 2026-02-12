"""add_mountain_pass_poi_type

Feature 003 - User Story 4: Add mountain pass type to POI enum

Adds 'mountain_pass' (Puerto de montaña) to the poi_type_enum
for PostgreSQL. SQLite uses String column, so no change needed.

Revision ID: cc4806b151bd
Revises: eee2b0a9b8cc
Create Date: 2026-01-26 14:46:32.229907+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cc4806b151bd"
down_revision: Union[str, None] = "eee2b0a9b8cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 'mountain_pass' to poi_type_enum (PostgreSQL only)."""
    conn = op.get_bind()
    is_postgresql = conn.dialect.name == "postgresql"

    if is_postgresql:
        # Add 'mountain_pass' value to existing ENUM type
        # PostgreSQL doesn't support ALTER TYPE ADD VALUE in transaction,
        # so we need to use raw SQL outside transaction
        conn.execute(
            sa.text(
                "ALTER TYPE poi_type_enum ADD VALUE IF NOT EXISTS 'mountain_pass'"
            )
        )
    # SQLite uses String column, so no database change needed


def downgrade() -> None:
    """Remove 'mountain_pass' from poi_type_enum.

    Note: PostgreSQL doesn't support removing enum values directly.
    This would require recreating the enum type and migrating data,
    which is complex and risky. In practice, keeping extra enum values
    is harmless if they're not used.
    """
    # No downgrade needed - removing enum values is not supported in PostgreSQL
    # and would be complex/risky to implement
    pass
