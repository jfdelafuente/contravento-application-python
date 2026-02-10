"""
CommentReport model for Activity Stream Feed (Feature 018).

Stores user reports of offensive comments (Option C: report button, no UI in MVP).
Task: T014
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.user import User


class CommentReportReason(str, enum.Enum):
    """
    Comment report reason enum (Option C: FR-020).

    Reasons:
        - spam: Spam or unsolicited advertising
        - offensive: Offensive or inappropriate language
        - harassment: Harassment or bullying
        - other: Other reason (explained in notes)
    """

    SPAM = "spam"
    OFFENSIVE = "offensive"
    HARASSMENT = "harassment"
    OTHER = "other"


class CommentReport(Base):
    """
    T014: CommentReport model for storing offensive comment reports.

    Option C Implementation (FR-020):
    - Users can report comments via report button
    - Reports are stored in database without moderation UI
    - Admins query reports via SQL for moderation
    - Future iteration will add moderation UI

    Constraints:
        - UNIQUE(comment_id, reporter_user_id): One report per user per comment

    Indexes:
        - (comment_id): Reports for a specific comment
        - (created_at DESC): Recent reports for admin queries
    """

    __tablename__ = "comment_reports"

    report_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    comment_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )  # Foreign key to activity_comments.comment_id
    reporter_user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )  # Foreign key to users.user_id
    reason: Mapped[CommentReportReason] = mapped_column(
        String(50),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Optional additional context from reporter
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    reporter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reporter_user_id],
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("comment_id", "reporter_user_id", name="uq_comment_reporter"),
        Index("idx_comment_reports_comment", "comment_id"),
        Index("idx_comment_reports_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CommentReport(report_id={self.report_id}, reason={self.reason}, comment_id={self.comment_id})>"
