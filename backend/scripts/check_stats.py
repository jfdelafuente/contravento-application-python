"""Check stats for testuser."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.user import User, UserProfile
from src.models.stats import UserStats, Achievement, UserAchievement
from src.models.social import Follow


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == 'testuser'))
        user = result.scalar_one_or_none()

        if not user:
            print('User not found')
            return

        print(f'User ID: {user.id}')
        print(f'Username: {user.username}')

        result = await db.execute(select(UserStats).where(UserStats.user_id == user.id))
        stats = result.scalar_one_or_none()

        if not stats:
            print('\nNo stats record found for user')
        else:
            print(f'\nStats found:')
            print(f'  Total trips: {stats.total_trips}')
            print(f'  Total kilometers: {stats.total_kilometers}')
            print(f'  Countries visited: {stats.countries_visited}')
            print(f'  Type of countries_visited: {type(stats.countries_visited)}')
            print(f'  Is None: {stats.countries_visited is None}')


if __name__ == '__main__':
    asyncio.run(main())
