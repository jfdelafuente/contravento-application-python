#!/usr/bin/env python3
"""
Script to manage follow relationships between users for testing.

Usage:
    # Make testuser follow another user
    poetry run python scripts/manage_follows.py --follower testuser --following maria_garcia

    # Make testuser unfollow
    poetry run python scripts/manage_follows.py --follower testuser --following maria_garcia --unfollow

    # List who testuser follows
    poetry run python scripts/manage_follows.py --follower testuser --list

    # List testuser's followers
    poetry run python scripts/manage_follows.py --following testuser --list
"""

import asyncio
import sys
from pathlib import Path
import argparse

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.social import Follow


async def follow_user(follower_username: str, following_username: str):
    """Make follower_username follow following_username."""
    async with AsyncSessionLocal() as db:
        # Get follower user
        result = await db.execute(
            select(User).where(User.username == follower_username)
        )
        follower = result.scalar_one_or_none()

        if not follower:
            print(f"[ERROR] Usuario '{follower_username}' no encontrado")
            return

        # Get following user
        result = await db.execute(
            select(User).where(User.username == following_username)
        )
        following = result.scalar_one_or_none()

        if not following:
            print(f"[ERROR] Usuario '{following_username}' no encontrado")
            return

        # Check if already following
        result = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower.id,
                Follow.following_id == following.id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"[INFO] {follower_username} ya sigue a {following_username}")
            return

        # Create follow relationship
        follow = Follow(
            follower_id=follower.id,
            following_id=following.id
        )
        db.add(follow)
        await db.commit()

        print(f"[SUCCESS] {follower_username} ahora sigue a {following_username}")


async def unfollow_user(follower_username: str, following_username: str):
    """Make follower_username unfollow following_username."""
    async with AsyncSessionLocal() as db:
        # Get follower user
        result = await db.execute(
            select(User).where(User.username == follower_username)
        )
        follower = result.scalar_one_or_none()

        if not follower:
            print(f"[ERROR] Usuario '{follower_username}' no encontrado")
            return

        # Get following user
        result = await db.execute(
            select(User).where(User.username == following_username)
        )
        following = result.scalar_one_or_none()

        if not following:
            print(f"[ERROR] Usuario '{following_username}' no encontrado")
            return

        # Find follow relationship
        result = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower.id,
                Follow.following_id == following.id
            )
        )
        follow = result.scalar_one_or_none()

        if not follow:
            print(f"[INFO] {follower_username} no sigue a {following_username}")
            return

        # Delete follow relationship
        await db.delete(follow)
        await db.commit()

        print(f"[SUCCESS] {follower_username} dejó de seguir a {following_username}")


async def list_following(follower_username: str):
    """List users that follower_username follows."""
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User).where(User.username == follower_username)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"[ERROR] Usuario '{follower_username}' no encontrado")
            return

        # Get following
        result = await db.execute(
            select(User).join(
                Follow, Follow.following_id == User.id
            ).where(
                Follow.follower_id == user.id
            )
        )
        following = result.scalars().all()

        if not following:
            print(f"[INFO] {follower_username} no sigue a nadie")
            return

        print(f"\n{follower_username} sigue a {len(following)} usuarios:")
        for followed_user in following:
            print(f"  - {followed_user.username} ({followed_user.email})")


async def list_followers(following_username: str):
    """List followers of following_username."""
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User).where(User.username == following_username)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"[ERROR] Usuario '{following_username}' no encontrado")
            return

        # Get followers
        result = await db.execute(
            select(User).join(
                Follow, Follow.follower_id == User.id
            ).where(
                Follow.following_id == user.id
            )
        )
        followers = result.scalars().all()

        if not followers:
            print(f"[INFO] {following_username} no tiene seguidores")
            return

        print(f"\n{following_username} tiene {len(followers)} seguidores:")
        for follower in followers:
            print(f"  - {follower.username} ({follower.email})")


def main():
    parser = argparse.ArgumentParser(description="Manage follow relationships between users")
    parser.add_argument(
        "--follower",
        help="Username of the follower"
    )
    parser.add_argument(
        "--following",
        help="Username to follow/unfollow"
    )
    parser.add_argument(
        "--unfollow",
        action="store_true",
        help="Unfollow instead of follow"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List following/followers (use with --follower or --following)"
    )

    args = parser.parse_args()

    if args.list:
        if args.follower:
            asyncio.run(list_following(args.follower))
        elif args.following:
            asyncio.run(list_followers(args.following))
        else:
            print("[ERROR] Use --follower or --following with --list")
            parser.print_help()
    elif args.follower and args.following:
        if args.unfollow:
            asyncio.run(unfollow_user(args.follower, args.following))
        else:
            asyncio.run(follow_user(args.follower, args.following))
    else:
        print("[ERROR] Missing required arguments")
        parser.print_help()


if __name__ == "__main__":
    main()
