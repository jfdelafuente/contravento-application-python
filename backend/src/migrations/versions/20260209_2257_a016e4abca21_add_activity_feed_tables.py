"""add_activity_feed_tables

Revision ID: a016e4abca21
Revises: 1f920057696f
Create Date: 2026-02-09 22:57:58.361928+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a016e4abca21"
down_revision: Union[str, None] = "1f920057696f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create activity feed tables for social stream (likes, comments, reports)."""
    # Get database dialect (postgresql or sqlite)
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        # ============================================================================
        # PostgreSQL: Create enums first
        # ============================================================================
        op.execute(
            """
            CREATE TYPE activity_type AS ENUM (
                'TRIP_PUBLISHED',
                'PHOTO_UPLOADED',
                'ACHIEVEMENT_UNLOCKED'
            );
            """
        )

        op.execute(
            """
            CREATE TYPE comment_report_reason AS ENUM (
                'spam',
                'offensive',
                'harassment',
                'other'
            );
            """
        )

        # ============================================================================
        # 1. ActivityFeedItem Table (PostgreSQL)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE activity_feed_items (
                activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                activity_type activity_type NOT NULL,
                related_id UUID NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
            """
        )

        # ============================================================================
        # 2. Activity Likes Table (PostgreSQL)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE activity_likes (
                like_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                activity_id UUID NOT NULL REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE (user_id, activity_id)
            );
            """
        )

        # ============================================================================
        # 3. Activity Comments Table (PostgreSQL)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE activity_comments (
                comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                activity_id UUID NOT NULL REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE,
                text TEXT NOT NULL CHECK (LENGTH(text) > 0 AND LENGTH(text) <= 500),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
            """
        )

        # ============================================================================
        # 4. CommentReports Table (PostgreSQL)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE comment_reports (
                report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                comment_id UUID NOT NULL REFERENCES activity_comments(comment_id) ON DELETE CASCADE,
                reporter_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                reason comment_report_reason NOT NULL,
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE (comment_id, reporter_user_id)
            );
            """
        )

    else:
        # ============================================================================
        # SQLite: Enable foreign keys
        # ============================================================================
        op.execute("PRAGMA foreign_keys = ON;")

        # ============================================================================
        # 1. ActivityFeedItem Table (SQLite)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE activity_feed_items (
                activity_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL CHECK (
                    activity_type IN ('TRIP_PUBLISHED', 'PHOTO_UPLOADED', 'ACHIEVEMENT_UNLOCKED')
                ),
                related_id TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """
        )

        # ============================================================================
        # 2. Activity Likes Table (SQLite)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE activity_likes (
                like_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                activity_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (activity_id) REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE,
                UNIQUE (user_id, activity_id)
            );
            """
        )

        # ============================================================================
        # 3. Activity Comments Table (SQLite)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE activity_comments (
                comment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                activity_id TEXT NOT NULL,
                text TEXT NOT NULL CHECK (LENGTH(text) > 0 AND LENGTH(text) <= 500),
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (activity_id) REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE
            );
            """
        )

        # ============================================================================
        # 4. CommentReports Table (SQLite)
        # ============================================================================
        op.execute(
            """
            CREATE TABLE comment_reports (
                report_id TEXT PRIMARY KEY,
                comment_id TEXT NOT NULL,
                reporter_user_id TEXT NOT NULL,
                reason TEXT NOT NULL CHECK (reason IN ('spam', 'offensive', 'harassment', 'other')),
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
                FOREIGN KEY (comment_id) REFERENCES activity_comments(comment_id) ON DELETE CASCADE,
                FOREIGN KEY (reporter_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE (comment_id, reporter_user_id)
            );
            """
        )

    # ============================================================================
    # Create Indexes (same for PostgreSQL and SQLite)
    # ============================================================================

    # ActivityFeedItem indexes
    op.create_index(
        "idx_activities_user_created",
        "activity_feed_items",
        ["user_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_activities_type_created",
        "activity_feed_items",
        ["activity_type", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_activities_created",
        "activity_feed_items",
        [sa.text("created_at DESC")],
    )

    # Activity Likes indexes
    op.create_index("idx_activity_likes_activity", "activity_likes", ["activity_id"])
    op.create_index("idx_activity_likes_user", "activity_likes", ["user_id"])
    op.create_index("idx_activity_likes_created", "activity_likes", [sa.text("created_at DESC")])

    # Activity Comments indexes
    op.create_index(
        "idx_activity_comments_activity",
        "activity_comments",
        ["activity_id", sa.text("created_at ASC")],
    )
    op.create_index("idx_activity_comments_user", "activity_comments", ["user_id"])
    op.create_index("idx_activity_comments_created", "activity_comments", [sa.text("created_at DESC")])

    # CommentReports indexes
    op.create_index("idx_comment_reports_comment", "comment_reports", ["comment_id"])
    op.create_index(
        "idx_comment_reports_created",
        "comment_reports",
        [sa.text("created_at DESC")],
    )


def downgrade() -> None:
    """Drop activity feed tables."""
    # Get database dialect
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # Drop indexes first
    op.drop_index("idx_comment_reports_created", "comment_reports")
    op.drop_index("idx_comment_reports_comment", "comment_reports")

    op.drop_index("idx_activity_comments_created", "activity_comments")
    op.drop_index("idx_activity_comments_user", "activity_comments")
    op.drop_index("idx_activity_comments_activity", "activity_comments")

    op.drop_index("idx_activity_likes_created", "activity_likes")
    op.drop_index("idx_activity_likes_user", "activity_likes")
    op.drop_index("idx_activity_likes_activity", "activity_likes")

    op.drop_index("idx_activities_created", "activity_feed_items")
    op.drop_index("idx_activities_type_created", "activity_feed_items")
    op.drop_index("idx_activities_user_created", "activity_feed_items")

    # Drop tables in reverse order (respect foreign key constraints)
    op.drop_table("comment_reports")
    op.drop_table("activity_comments")
    op.drop_table("activity_likes")
    op.drop_table("activity_feed_items")

    # Drop enums (PostgreSQL only)
    if dialect_name == "postgresql":
        op.execute("DROP TYPE IF EXISTS comment_report_reason;")
        op.execute("DROP TYPE IF EXISTS activity_type;")
