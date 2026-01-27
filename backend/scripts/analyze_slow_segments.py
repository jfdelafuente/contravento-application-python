"""Analyze duration of slow segments to understand stop patterns."""

import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import GPXFile
from src.services.gpx_service import GPXService


async def analyze_slow_segments(gpx_file_id: str):
    """Analyze slow segments to understand their duration."""
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

            print(f"Analyzing slow segments (< 3 km/h) in {len(trackpoints)} GPS points")
            print("=" * 80)
            print()

            # Analyze slow segments
            STOP_SPEED_THRESHOLD = 3.0  # km/h
            slow_segments = []

            for i in range(len(trackpoints) - 1):
                p1 = trackpoints[i]
                p2 = trackpoints[i + 1]

                time_delta = p2["timestamp"] - p1["timestamp"]
                segment_time_minutes = time_delta.total_seconds() / 60.0
                segment_distance_km = p2["distance_km"] - p1["distance_km"]

                segment_speed_kmh = 0.0
                if segment_time_minutes > 0:
                    segment_speed_kmh = (segment_distance_km / segment_time_minutes) * 60.0

                if segment_speed_kmh < STOP_SPEED_THRESHOLD:
                    slow_segments.append({
                        "index": i,
                        "duration_min": segment_time_minutes,
                        "duration_sec": segment_time_minutes * 60,
                        "speed_kmh": segment_speed_kmh,
                        "distance_km": segment_distance_km,
                    })

            # Statistics
            total_slow_segments = len(slow_segments)
            total_slow_time = sum(s["duration_min"] for s in slow_segments)

            if slow_segments:
                avg_duration = total_slow_time / total_slow_segments
                max_duration = max(s["duration_min"] for s in slow_segments)
                min_duration = min(s["duration_min"] for s in slow_segments)

                print(f"SLOW SEGMENTS ANALYSIS (speed < {STOP_SPEED_THRESHOLD} km/h)")
                print("-" * 80)
                print(f"Total slow segments:    {total_slow_segments}")
                print(f"Total slow time:        {total_slow_time:.2f} min ({total_slow_time/60:.2f} hours)")
                print(f"Average duration:       {avg_duration:.2f} min ({avg_duration * 60:.1f} sec)")
                print(f"Maximum duration:       {max_duration:.2f} min ({max_duration * 60:.1f} sec)")
                print(f"Minimum duration:       {min_duration:.2f} min ({min_duration * 60:.1f} sec)")
                print()

                # Duration histogram
                ranges = [
                    (0, 0.5, "0-30 sec"),
                    (0.5, 1.0, "30-60 sec"),
                    (1.0, 2.0, "1-2 min"),
                    (2.0, 5.0, "2-5 min"),
                    (5.0, float('inf'), ">5 min"),
                ]

                print("DURATION HISTOGRAM:")
                print("-" * 80)
                for min_dur, max_dur, label in ranges:
                    count = sum(1 for s in slow_segments if min_dur <= s["duration_min"] < max_dur)
                    if count > 0:
                        percentage = (count / total_slow_segments) * 100
                        total_time_range = sum(s["duration_min"] for s in slow_segments if min_dur <= s["duration_min"] < max_dur)
                        print(f"  {label:12s}: {count:3d} segments ({percentage:5.1f}%), total time: {total_time_range:6.2f} min")

                print()
                print("=" * 80)
                print()

                # Show longest slow segments
                sorted_segments = sorted(slow_segments, key=lambda s: s["duration_min"], reverse=True)
                print(f"TOP 10 LONGEST SLOW SEGMENTS:")
                print("-" * 80)
                for i, seg in enumerate(sorted_segments[:10], 1):
                    print(f"  #{i:2d}: {seg['duration_min']:6.2f} min ({seg['duration_sec']:6.1f} sec), "
                          f"speed: {seg['speed_kmh']:5.2f} km/h, distance: {seg['distance_km']*1000:6.1f} m")
                print()

            else:
                print(f"NO SLOW SEGMENTS FOUND (all segments have speed >= {STOP_SPEED_THRESHOLD} km/h)")

            print("=" * 80)

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: poetry run python scripts/analyze_slow_segments.py <gpx_file_id>")
        sys.exit(1)

    gpx_file_id = sys.argv[1]
    asyncio.run(analyze_slow_segments(gpx_file_id))
