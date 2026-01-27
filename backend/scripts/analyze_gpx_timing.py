"""Analyze GPS point spacing in a GPX file to understand timestamp patterns."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import TrackPoint


async def analyze_gpx_timing(gpx_file_id: str):
    """Analyze timestamp spacing between GPS points."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Get trackpoints ordered by sequence
            result = await db.execute(
                select(TrackPoint)
                .where(TrackPoint.gpx_file_id == gpx_file_id)
                .order_by(TrackPoint.sequence)
            )
            trackpoints = result.scalars().all()

            if not trackpoints or len(trackpoints) < 2:
                print("Not enough trackpoints to analyze")
                return

            print(f"Analyzing {len(trackpoints)} GPS points")
            print("=" * 70)
            print()

            # Analyze spacing between consecutive points
            time_gaps = []
            distance_gaps = []
            speed_samples = []

            # Sample first 20 segments and last 20 segments
            sample_indices = list(range(min(20, len(trackpoints) - 1)))
            if len(trackpoints) > 40:
                sample_indices.extend(range(len(trackpoints) - 20, len(trackpoints) - 1))

            print("SAMPLE GPS POINT SPACING")
            print("-" * 70)
            for i in sample_indices[:min(30, len(sample_indices))]:
                p1 = trackpoints[i]
                p2 = trackpoints[i + 1]

                # Calculate time gap (we don't have timestamps in TrackPoint model)
                # So we'll just analyze distance gaps
                dist_gap = p2.distance_km - p1.distance_km
                distance_gaps.append(dist_gap)

                if i < 10 or i > len(trackpoints) - 10:
                    print(
                        f"  Point {i:4d} → {i+1:4d}: "
                        f"distance_gap={dist_gap:.4f}km, "
                        f"gradient={p2.gradient if p2.gradient else 'N/A'}"
                    )

            print()
            print("SUMMARY STATISTICS")
            print("-" * 70)
            print(f"  Total points:        {len(trackpoints)}")
            print(f"  Total distance:      {trackpoints[-1].distance_km:.2f} km")
            print()
            print(f"  Avg distance/point:  {sum(distance_gaps)/len(distance_gaps):.4f} km")
            print(f"  Min distance gap:    {min(distance_gaps):.4f} km")
            print(f"  Max distance gap:    {max(distance_gaps):.4f} km")
            print()

            # Count suspicious gaps (>0.5km between points, might indicate missing data)
            large_gaps = [d for d in distance_gaps if d > 0.5]
            if large_gaps:
                print(f"  ⚠️  Large gaps (>0.5km): {len(large_gaps)} found")
                print(f"     Largest gap:       {max(large_gaps):.4f} km")

            print()
            print("=" * 70)

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: poetry run python scripts/analyze_gpx_timing.py <gpx_file_id>")
        sys.exit(1)

    gpx_file_id = sys.argv[1]
    asyncio.run(analyze_gpx_timing(gpx_file_id))
