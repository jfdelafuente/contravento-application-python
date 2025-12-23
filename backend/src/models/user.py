"""
User and UserProfile models.

User: Core authentication and account data
UserProfile: Extended profile information (1-to-1 with User)
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class User(Base):
    """
    User model for authentication and core account data.

    Represents a registered user account with authentication credentials.

    Attributes:
        id: Unique user identifier (UUID)
        username: Unique username (3-30 alphanumeric + underscores)
        email: Unique email address (normalized to lowercase)
        hashed_password: Bcrypt hashed password
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
        default=datetime.utcnow,
        nullable=False,
        doc="Account creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp (UTC)",
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
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

    locked_until: Mapped[Optional[datetime]] = mapped_column(
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

    password_resets: Mapped[list["PasswordReset"]] = relationship(
        "PasswordReset",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Password reset and verification tokens",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


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
        cycling_type: Type of cycling (road, mountain, gravel, touring, commuting)
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
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's full name",
    )

    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Profile biography (max 500 characters)",
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's location (e.g., 'Madrid, España')",
    )

    cycling_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="Type of cycling: road, mountain, gravel, touring, commuting",
    )

    profile_photo_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="URL or path to profile photo",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Profile creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
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
