"""Delete corrupt or unwanted RouteStatistics records from the database.

This script deletes RouteStatistics records for a given GPX file ID. It was originally
created to delete corrupt records with invalid moving_time > total_time, but can be used
to delete any RouteStatistics record that needs to be removed.

Usage:
    poetry run python scripts/analysis/delete_corrupt_stats.py <gpx_file_id>

Args:
    gpx_file_id: UUID of the GPX file whose RouteStatistics should be deleted

Examples:
    poetry run python scripts/analysis/delete_corrupt_stats.py 13e24f2f-f792-4873-b636-ad3568861514

Notes:
    - Only deletes from route_statistics table (does NOT delete GPX file or trackpoints)
    - Shows record information before deletion
    - Commits deletion immediately (no confirmation prompt)
    - Use recalculate_route_stats.py to recreate statistics after deletion
    - CAUTION: This is a destructive operation with no undo
"""

import asyncio
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.route_statistics import RouteStatistics


async def delete_corrupt_stats(gpx_file_id: str):
    """Delete RouteStatistics record for given GPX file ID.

    Args:
        gpx_file_id: UUID of GPX file whose RouteStatistics should be deleted
    """
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as db:
        try:
            # Check if record exists
            result = await db.execute(
                select(RouteStatistics).where(
                    RouteStatistics.gpx_file_id == gpx_file_id
                )
            )
            stats = result.scalar_one_or_none()

            if stats:
                print(f"Found RouteStatistics:")
                print(f"  Stats ID: {stats.stats_id}")
                print(f"  GPX File ID: {stats.gpx_file_id}")
                print(f"  Total Time: {stats.total_time_minutes} min")
                print(f"  Moving Time: {stats.moving_time_minutes} min")
                print(f"  [ERROR] Moving time > Total time (corrupt data)")
                print()

                # Delete the record
                await db.execute(
                    delete(RouteStatistics).where(
                        RouteStatistics.gpx_file_id == gpx_file_id
                    )
                )
                await db.commit()
                print(f"[OK] Corrupt RouteStatistics record deleted successfully")
            else:
                print(f"[INFO] No RouteStatistics record found for GPX file {gpx_file_id}")

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Delete corrupt or unwanted RouteStatistics records from the database.",
        epilog="Example:\n"
               "  %(prog)s 13e24f2f-f792-4873-b636-ad3568861514",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "gpx_file_id",
        help="UUID of GPX file whose RouteStatistics should be deleted"
    )

    args = parser.parse_args()

    asyncio.run(delete_corrupt_stats(args.gpx_file_id))
