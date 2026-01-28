"""Analyze GPS point spacing in a GPX file to understand timestamp patterns."""

import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import GPXFile, TrackPoint
from src.services.gpx_service import GPXService


async def analyze_gpx_timing(gpx_file_id: str = None, file_path: str = None):
    """Analyze timestamp spacing between GPS points.

    Args:
        gpx_file_id: UUID of GPX file (required if file_path not provided)
        file_path: Path to GPX file (required if gpx_file_id not provided)
    """
    if not gpx_file_id and not file_path:
        raise ValueError("Either gpx_file_id or file_path must be provided")

    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Get trackpoints from file or database
            if file_path:
                print(f"[INFO] Using custom file path: {file_path}")
                custom_path = Path(file_path)
                if not custom_path.exists():
                    print(f"[ERROR] File not found: {file_path}")
                    return

                # Parse GPX file
                with open(custom_path, "rb") as f:
                    gpx_content = f.read()

                gpx_service = GPXService(db)
                parsed_data = await gpx_service.parse_gpx_file(gpx_content)
                trackpoints_data = gpx_service.convert_points_for_stats(
                    parsed_data["original_points"]
                )

                if not trackpoints_data or len(trackpoints_data) < 2:
                    print("[ERROR] Not enough trackpoints to analyze")
                    return

                print(f"Analyzing {len(trackpoints_data)} GPS points from file")
                print("=" * 70)
                print()

                # Analyze spacing
                distance_gaps = []
                sample_indices = list(range(min(20, len(trackpoints_data) - 1)))
                if len(trackpoints_data) > 40:
                    sample_indices.extend(range(len(trackpoints_data) - 20, len(trackpoints_data) - 1))

                print("SAMPLE GPS POINT SPACING")
                print("-" * 70)
                for i in sample_indices[:min(30, len(sample_indices))]:
                    p1 = trackpoints_data[i]
                    p2 = trackpoints_data[i + 1]

                    dist_gap = p2["distance_km"] - p1["distance_km"]
                    distance_gaps.append(dist_gap)

                    if i < 10 or i > len(trackpoints_data) - 10:
                        gradient_str = f"{p2.get('gradient'):.1f}%" if p2.get('gradient') is not None else 'N/A'
                        print(
                            f"  Point {i:4d} → {i+1:4d}: "
                            f"distance_gap={dist_gap:.4f}km, "
                            f"gradient={gradient_str}"
                        )

                print()
                print("SUMMARY STATISTICS")
                print("-" * 70)
                print(f"  Total points:        {len(trackpoints_data)}")
                print(f"  Total distance:      {trackpoints_data[-1]['distance_km']:.2f} km")
                print()
                print(f"  Avg distance/point:  {sum(distance_gaps)/len(distance_gaps):.4f} km")
                print(f"  Min distance gap:    {min(distance_gaps):.4f} km")
                print(f"  Max distance gap:    {max(distance_gaps):.4f} km")
                print()

                # Count suspicious gaps
                large_gaps = [d for d in distance_gaps if d > 0.5]
                if large_gaps:
                    print(f"  ⚠️  Large gaps (>0.5km): {len(large_gaps)} found")
                    print(f"     Largest gap:       {max(large_gaps):.4f} km")

                print()
                print("=" * 70)

            else:
                # Get trackpoints from database
                result = await db.execute(
                    select(TrackPoint)
                    .where(TrackPoint.gpx_file_id == gpx_file_id)
                    .order_by(TrackPoint.sequence)
                )
                trackpoints = result.scalars().all()

                if not trackpoints or len(trackpoints) < 2:
                    print("[ERROR] Not enough trackpoints to analyze")
                    return

                print(f"Analyzing {len(trackpoints)} GPS points from database")
                print("=" * 70)
                print()

                # Analyze spacing
                distance_gaps = []
                sample_indices = list(range(min(20, len(trackpoints) - 1)))
                if len(trackpoints) > 40:
                    sample_indices.extend(range(len(trackpoints) - 20, len(trackpoints) - 1))

                print("SAMPLE GPS POINT SPACING")
                print("-" * 70)
                for i in sample_indices[:min(30, len(sample_indices))]:
                    p1 = trackpoints[i]
                    p2 = trackpoints[i + 1]

                    dist_gap = p2.distance_km - p1.distance_km
                    distance_gaps.append(dist_gap)

                    if i < 10 or i > len(trackpoints) - 10:
                        gradient_str = f"{p2.gradient:.1f}%" if p2.gradient is not None else 'N/A'
                        print(
                            f"  Point {i:4d} → {i+1:4d}: "
                            f"distance_gap={dist_gap:.4f}km, "
                            f"gradient={gradient_str}"
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

                # Count suspicious gaps
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
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Analyze GPS point spacing and distance gaps in GPX files.",
        epilog="Examples:\n"
               "  %(prog)s 13e24f2f-f792-4873-b636-ad3568861514\n"
               "  %(prog)s --file-path /tmp/my-route.gpx",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "gpx_file_id",
        nargs='?',
        help="UUID of GPX file (required if --file-path not provided)"
    )
    parser.add_argument(
        "--file-path",
        help="Path to GPX file (required if gpx_file_id not provided)",
        default=None
    )

    args = parser.parse_args()

    # Validate that at least one argument is provided
    if not args.gpx_file_id and not args.file_path:
        parser.error("Either gpx_file_id or --file-path must be provided")

    asyncio.run(analyze_gpx_timing(args.gpx_file_id, args.file_path))
