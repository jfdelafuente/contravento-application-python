"""Check latest uploaded GPX file and its statistics."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import GPXFile
from src.models.route_statistics import RouteStatistics


async def check_latest_gpx():
    """Check latest GPX file and its statistics."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Get latest GPX file
            result = await db.execute(
                select(GPXFile).order_by(GPXFile.uploaded_at.desc()).limit(1)
            )
            gpx = result.scalar_one_or_none()

            if not gpx:
                print("No GPX files found")
                return

            print("=" * 70)
            print("LATEST GPX FILE")
            print("=" * 70)
            print(f"GPX File ID:         {gpx.gpx_file_id}")
            print(f"Original Filename:   {gpx.file_name}")
            print(f"Distance:            {gpx.distance_km} km")
            print(f"Has Timestamps:      {gpx.has_timestamps}")
            print(f"Has Elevation:       {gpx.has_elevation}")
            print(f"Uploaded At:         {gpx.uploaded_at}")
            print()

            # Get statistics
            stats_result = await db.execute(
                select(RouteStatistics).where(RouteStatistics.gpx_file_id == gpx.gpx_file_id)
            )
            stats = stats_result.scalar_one_or_none()

            if stats:
                print("ROUTE STATISTICS")
                print("=" * 70)
                print()
                print("[TIME METRICS]")
                if stats.total_time_minutes:
                    total_hours = int(stats.total_time_minutes // 60)
                    total_mins = int(stats.total_time_minutes % 60)
                    moving_hours = int(stats.moving_time_minutes // 60)
                    moving_mins = int(stats.moving_time_minutes % 60)
                    stopped_time = stats.total_time_minutes - stats.moving_time_minutes

                    print(f"  Total Time:        {stats.total_time_minutes:.2f} min ({total_hours}h {total_mins}min)")
                    print(f"  Moving Time:       {stats.moving_time_minutes:.2f} min ({moving_hours}h {moving_mins}min)")
                    print(f"  Stopped Time:      {stopped_time:.2f} min ({stopped_time/60:.2f} hours)")
                    print(f"  Moving/Total:      {(stats.moving_time_minutes/stats.total_time_minutes*100):.1f}%")
                    print()
                    print(f"  ⚠️  Validation: moving_time ({stats.moving_time_minutes:.10f}) <= total_time ({stats.total_time_minutes:.10f})? {stats.moving_time_minutes <= stats.total_time_minutes}")
                else:
                    print("  No time data")
                print()

                print("[SPEED METRICS]")
                print(f"  Avg Speed:         {stats.avg_speed_kmh} km/h")
                print(f"  Max Speed:         {stats.max_speed_kmh} km/h")
                print()

                print("[GRADIENT METRICS]")
                print(f"  Avg Gradient:      {stats.avg_gradient}%")
                print(f"  Max Gradient:      {stats.max_gradient}%")
                print()

                print("[TOP CLIMBS]")
                if stats.top_climbs:
                    for i, climb in enumerate(stats.top_climbs, 1):
                        print(f"  Climb #{i}:")
                        print(f"    Start-End:       {climb['start_km']:.2f} - {climb['end_km']:.2f} km")
                        print(f"    Elevation Gain:  {climb['elevation_gain_m']:.0f} m")
                        print(f"    Avg Gradient:    {climb['avg_gradient']:.1f}%")
                else:
                    print("  No climbs detected")
                print()
                print("=" * 70)
            else:
                print("NO STATISTICS FOUND")
                print("=" * 70)

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_latest_gpx())
