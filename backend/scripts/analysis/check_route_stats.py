"""Check if RouteStatistics record exists for a GPX file.

This script queries the RouteStatistics table in the database to verify if
statistics have been calculated for a given GPX file.

Usage:
    poetry run python scripts/analysis/check_route_stats.py <gpx_file_id>

Args:
    gpx_file_id: UUID of the GPX file to check

Examples:
    poetry run python scripts/analysis/check_route_stats.py 13e24f2f-f792-4873-b636-ad3568861514
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.route_statistics import RouteStatistics


async def check_stats(gpx_file_id: str):
    """Check if RouteStatistics exists for given GPX file ID.

    Args:
        gpx_file_id: UUID of GPX file to check
    """
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as db:
        try:
            # Query for RouteStatistics
            result = await db.execute(
                select(RouteStatistics).where(
                    RouteStatistics.gpx_file_id == gpx_file_id
                )
            )
            stats = result.scalar_one_or_none()

            if stats:
                print("[OK] RouteStatistics FOUND!")
                print("=" * 60)
                print(f"Stats ID:        {stats.stats_id}")
                print(f"GPX File ID:     {stats.gpx_file_id}")
                print()
                print("[SPEED]")
                print(f"  Avg Speed:     {stats.avg_speed_kmh} km/h" if stats.avg_speed_kmh else "  Avg Speed:     N/A")
                print(f"  Max Speed:     {stats.max_speed_kmh} km/h" if stats.max_speed_kmh else "  Max Speed:     N/A")
                print()
                print("[TIME]")
                print(f"  Total Time:    {stats.total_time_minutes} min" if stats.total_time_minutes else "  Total Time:    N/A")
                print(f"  Moving Time:   {stats.moving_time_minutes} min" if stats.moving_time_minutes else "  Moving Time:   N/A")
                print()
                print("[GRADIENT]")
                print(f"  Avg Gradient:  {stats.avg_gradient}%" if stats.avg_gradient else "  Avg Gradient:  N/A")
                print(f"  Max Gradient:  {stats.max_gradient}%" if stats.max_gradient else "  Max Gradient:  N/A")
                print()
                print("[CLIMBS]")
                if stats.top_climbs:
                    print(f"  Top Climbs:    {len(stats.top_climbs)} climbs found")
                    for i, climb in enumerate(stats.top_climbs, 1):
                        print(f"    #{i}: {climb['start_km']:.2f}-{climb['end_km']:.2f} km, "
                              f"{climb['elevation_gain_m']:.0f}m gain, "
                              f"{climb['avg_gradient']:.1f}% gradient")
                else:
                    print("  Top Climbs:    None")
                print("=" * 60)
            else:
                print("[ERROR] RouteStatistics NOT FOUND")
                print("=" * 60)
                print(f"GPX File ID:     {gpx_file_id}")
                print()
                print("Reason:")
                print("  The GPX file was uploaded BEFORE RouteStatistics integration")
                print()
                print("Solution:")
                print("  1. Re-upload the GPX file (recommended)")
                print("  2. Or run backfill script to calculate statistics for existing files")
                print("=" * 60)

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Check if RouteStatistics record exists for a GPX file in the database.",
        epilog="Example:\n"
               "  %(prog)s 13e24f2f-f792-4873-b636-ad3568861514",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "gpx_file_id",
        help="UUID of GPX file to check"
    )

    args = parser.parse_args()

    asyncio.run(check_stats(args.gpx_file_id))
