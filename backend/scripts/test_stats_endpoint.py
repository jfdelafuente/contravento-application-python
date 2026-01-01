"""Test stats endpoint directly."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import AsyncSessionLocal
from src.services.stats_service import StatsService


async def main():
    """Test get_user_stats directly."""
    async with AsyncSessionLocal() as db:
        try:
            stats_service = StatsService(db)
            stats = await stats_service.get_user_stats("testuser")

            print("\n" + "=" * 60)
            print("STATS RETRIEVAL SUCCESS")
            print("=" * 60)
            print(f"Total trips: {stats.total_trips}")
            print(f"Total kilometers: {stats.total_kilometers}")
            print(f"Countries visited: {stats.countries_visited}")
            print(f"Total photos: {stats.total_photos}")
            print(f"Achievements count: {stats.achievements_count}")
            print(f"Last trip date: {stats.last_trip_date}")
            print(f"Updated at: {stats.updated_at}")
            print("=" * 60)

        except ValueError as e:
            print(f"\n[ERROR] ValueError: {e}")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
