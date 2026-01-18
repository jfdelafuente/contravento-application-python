"""
Database models for ContraVento application.

Exports all models for Alembic autogenerate.
"""

from src.models.auth import PasswordReset
from src.models.comment import Comment
from src.models.cycling_type import CyclingType
from src.models.like import Like
from src.models.notification import Notification
from src.models.share import Share
from src.models.social import Follow
from src.models.stats import Achievement, UserAchievement, UserStats
from src.models.trip import Tag, Trip, TripLocation, TripPhoto, TripTag
from src.models.user import User, UserProfile, UserRole

__all__ = [
    "User",
    "UserProfile",
    "UserRole",
    "PasswordReset",
    "CyclingType",
    "Follow",
    "Like",
    "Comment",
    "Share",
    "Notification",
    "UserStats",
    "Achievement",
    "UserAchievement",
    "Trip",
    "TripPhoto",
    "Tag",
    "TripTag",
    "TripLocation",
]
