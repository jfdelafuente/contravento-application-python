"""
Database models for ContraVento application.

Exports all models for Alembic autogenerate.
"""

from src.models.user import User, UserProfile
from src.models.auth import PasswordReset
from src.models.social import Follow
from src.models.stats import UserStats, Achievement, UserAchievement
from src.models.trip import Trip, TripPhoto, Tag, TripTag, TripLocation

__all__ = [
    "User",
    "UserProfile",
    "PasswordReset",
    "Follow",
    "UserStats",
    "Achievement",
    "UserAchievement",
    "Trip",
    "TripPhoto",
    "Tag",
    "TripTag",
    "TripLocation",
]
