"""Delete corrupt RouteStatistics record with invalid moving_time > total_time."""

import asyncio
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.route_statistics import RouteStatistics


async def delete_corrupt_stats(gpx_file_id: str):
    """Delete RouteStatistics record for given GPX file ID."""
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
    gpx_file_id = "13e24f2f-f792-4873-b636-ad3568861514"
    asyncio.run(delete_corrupt_stats(gpx_file_id))
