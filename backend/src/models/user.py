"""
User and UserProfile models.

User: Core authentication and account data
UserProfile: Extended profile information (1-to-1 with User)
"""

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class UserRole(str, enum.Enum):
    """
    User role enumeration.

    Roles:
        USER: Regular user (default) - can manage own content
        ADMIN: Administrator - can manage platform configuration and data
    """

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User model for authentication and core account data.

    Represents a registered user account with authentication credentials.

    Attributes:
        id: Unique user identifier (UUID)
        username: Unique username (3-30 alphanumeric + underscores)
        email: Unique email address (normalized to lowercase)
        hashed_password: Bcrypt hashed password
        role: User role (user/admin) - default: user
        profile_visibility: Profile visibility (public/private) - default: public
        trip_visibility: Trip visibility (public/followers/private) - default: public
        is_active: Account active flag (for soft delete/ban)
        is_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last successful login timestamp
        failed_login_attempts: Counter for rate limiting (resets on success)
        locked_until: Timestamp until which account is locked (failed attempts)
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique user identifier (UUID)",
    )

    # Authentication fields
    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique username (3-30 characters)",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique email address (normalized to lowercase)",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password",
    )

    # Role
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
        index=True,
        doc="User role (user/admin) - default: user",
    )

    # Privacy settings (Feature 013 - Public Trips Feed)
    profile_visibility: Mapped[str] = mapped_column(
        String(20),
        default="public",
        nullable=False,
        index=True,
        doc="Profile visibility: 'public' or 'private' - default: public",
    )

    trip_visibility: Mapped[str] = mapped_column(
        String(20),
        default="public",
        nullable=False,
        index=True,
        doc="Trip visibility: 'public', 'followers', or 'private' - default: public",
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Account active flag (False = banned/deactivated)",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Email verification status",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        doc="Account creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        doc="Last update timestamp (UTC)",
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last successful login timestamp (UTC)",
    )

    # Rate limiting
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        doc="Failed login attempts counter (resets on success)",
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp until which account is locked due to failed attempts",
    )

    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        doc="1-to-1 relationship with UserProfile",
    )

    stats: Mapped["UserStats"] = relationship(
        "UserStats",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        doc="1-to-1 relationship with UserStats",
    )

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Achievements earned by this user",
    )

    password_resets: Mapped[list["PasswordReset"]] = relationship(
        "PasswordReset",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Password reset and verification tokens",
    )

    # Social network relationships (Feature 004)
    likes: Mapped[list["Like"]] = relationship(
        "Like",
        foreign_keys="Like.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Likes given by this user",
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        foreign_keys="Comment.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Comments posted by this user",
    )

    shares: Mapped[list["Share"]] = relationship(
        "Share",
        foreign_keys="Share.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Shares created by this user",
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        foreign_keys="Notification.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Notifications received by this user",
    )

    # Social relationships (T199)
    followers: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
        doc="Users who follow this user",
    )

    following: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
        doc="Users this user follows",
    )

    # Travel Diary relationships (002-travel-diary)
    trips: Mapped[list["Trip"]] = relationship(
        "Trip",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Travel diary trips created by this user",
    )

    # Activity Stream relationships (018-activity-stream-feed)
    activity_feed_items: Mapped[list["ActivityFeedItem"]] = relationship(
        "ActivityFeedItem",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Activity feed items created by this user",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role.value})>"


class UserProfile(Base):
    """
    UserProfile model for extended user information.

    1-to-1 relationship with User. Initialized empty on registration,
    populated when user edits their profile.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User (1-to-1)
        full_name: User's full name (optional)
        bio: Profile biography (max 500 characters)
        location: User's location (city, country)
        cycling_type: Type of cycling (bikepacking, commuting, gravel, mountain, road, touring)
        profile_photo_url: URL/path to profile photo
        created_at: Profile creation timestamp
        updated_at: Last profile update timestamp
    """

    __tablename__ = "user_profiles"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique profile identifier (UUID)",
    )

    # Foreign key (1-to-1 with User)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Foreign key to User (1-to-1)",
    )

    # Profile fields
    full_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="User's full name",
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Profile biography (max 500 characters)",
    )

    location: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="User's location (e.g., 'Madrid, España')",
    )

    cycling_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Type of cycling: bikepacking, commuting, gravel, mountain, road, touring",
    )

    profile_photo_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="URL or path to profile photo",
    )

    # Privacy settings
    show_email: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Show email in public profile",
    )

    show_location: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Show location in public profile",
    )

    # Social counters (T199)
    followers_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        doc="Number of followers (denormalized counter)",
    )

    following_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        doc="Number of users being followed (denormalized counter)",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        doc="Profile creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        doc="Last profile update timestamp (UTC)",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        doc="1-to-1 relationship with User",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, full_name={self.full_name})>"
