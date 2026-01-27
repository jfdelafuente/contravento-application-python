"""Analyze segment speeds in a GPX file to understand stop detection."""

import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import GPXFile
from src.services.gpx_service import GPXService


async def analyze_segments(gpx_file_id: str):
    """Analyze segment speeds to understand stop detection."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as db:
        try:
            # Get GPX file
            result = await db.execute(
                select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id)
            )
            gpx_file = result.scalar_one_or_none()

            if not gpx_file:
                print(f"[ERROR] GPX file not found")
                return

            # Read GPX file
            storage_path = Path(settings.storage_path) / gpx_file.file_url
            with open(storage_path, "rb") as f:
                gpx_content = f.read()

            # Parse GPX
            gpx_service = GPXService(db)
            parsed_data = await gpx_service.parse_gpx_file(gpx_content)
            trackpoints = gpx_service.convert_points_for_stats(
                parsed_data["original_points"]
            )

            print(f"Analyzing {len(trackpoints)} GPS points")
            print("=" * 80)
            print()

            # Analyze segments
            STOP_SPEED_THRESHOLD = 3.0  # km/h
            STOP_DURATION_THRESHOLD = 2.0  # minutes (REVISED from 5.0)

            slow_segments = []
            long_segments = []
            stop_segments = []

            for i in range(len(trackpoints) - 1):
                p1 = trackpoints[i]
                p2 = trackpoints[i + 1]

                time_delta = p2["timestamp"] - p1["timestamp"]
                segment_time_minutes = time_delta.total_seconds() / 60.0
                segment_distance_km = p2["distance_km"] - p1["distance_km"]

                segment_speed_kmh = 0.0
                if segment_time_minutes > 0:
                    segment_speed_kmh = (segment_distance_km / segment_time_minutes) * 60.0

                # Classify segment
                is_slow = segment_speed_kmh < STOP_SPEED_THRESHOLD
                is_long = segment_time_minutes > STOP_DURATION_THRESHOLD
                is_stop = is_slow and is_long

                if is_slow:
                    slow_segments.append((i, segment_time_minutes, segment_speed_kmh))
                if is_long:
                    long_segments.append((i, segment_time_minutes, segment_speed_kmh))
                if is_stop:
                    stop_segments.append((i, segment_time_minutes, segment_speed_kmh))

            # Report findings
            print(f"SEGMENT ANALYSIS")
            print("-" * 80)
            print(f"Total segments:             {len(trackpoints) - 1}")
            print(f"Slow segments (< 3 km/h):   {len(slow_segments)}")
            print(f"Long segments (> {STOP_DURATION_THRESHOLD} min):    {len(long_segments)}")
            print(f"STOP segments (both):       {len(stop_segments)}")
            print()

            if stop_segments:
                print(f"DETECTED STOPS (speed < {STOP_SPEED_THRESHOLD} km/h, duration > {STOP_DURATION_THRESHOLD} min):")
                print("-" * 80)
                total_stop_time = 0.0
                for i, duration, speed in stop_segments:
                    print(f"  Segment {i:4d}: {duration:6.2f} min, {speed:6.2f} km/h")
                    total_stop_time += duration
                print()
                print(f"Total stop time: {total_stop_time:.2f} min ({total_stop_time/60:.2f} hours)")
            else:
                print(f"NO STOPS DETECTED (no segments with speed < {STOP_SPEED_THRESHOLD} km/h AND duration > {STOP_DURATION_THRESHOLD} min)")
                print()
                print("Possible reasons:")
                print(f"  1. The route had no stops longer than {STOP_DURATION_THRESHOLD} minutes")
                print("  2. GPS points are too far apart (stops get averaged out)")
                print("  3. GPS device kept recording movement even when stopped")

            print()
            print("=" * 80)
            print()

            # Sample slow segments
            if slow_segments and len(slow_segments) <= 20:
                print("SLOW SEGMENTS (< 3 km/h, any duration):")
                print("-" * 80)
                for i, duration, speed in slow_segments[:20]:
                    print(f"  Segment {i:4d}: {duration:6.2f} min, {speed:6.2f} km/h")
                print()

            # Sample long segments
            if long_segments and len(long_segments) <= 20:
                print(f"LONG SEGMENTS (> {STOP_DURATION_THRESHOLD} min, any speed):")
                print("-" * 80)
                for i, duration, speed in long_segments[:20]:
                    print(f"  Segment {i:4d}: {duration:6.2f} min, {speed:6.2f} km/h")
                print()

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: poetry run python scripts/analyze_gpx_segments.py <gpx_file_id>")
        sys.exit(1)

    gpx_file_id = sys.argv[1]
    asyncio.run(analyze_segments(gpx_file_id))
