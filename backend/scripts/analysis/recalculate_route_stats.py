"""Recalculate RouteStatistics for an existing GPX file without re-uploading.

This script recalculates RouteStatistics for a GPX file that is already in the
database and storage. It reads the GPX file, parses it, calculates all route
metrics, deletes the old RouteStatistics record (if exists), and creates a new one.

Usage:
    poetry run python scripts/analysis/recalculate_route_stats.py <gpx_file_id>

Args:
    gpx_file_id: UUID of the GPX file to recalculate statistics for

Examples:
    poetry run python scripts/analysis/recalculate_route_stats.py 13e24f2f-f792-4873-b636-ad3568861514

Notes:
    - Requires GPX file to be in database (gpx_files table)
    - Requires GPX file to exist in storage (storage_path + file_url)
    - Requires GPX file to have timestamps (has_timestamps=true)
    - Deletes existing RouteStatistics and creates new one
"""

import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import GPXFile
from src.models.route_statistics import RouteStatistics
from src.services.gpx_service import GPXService
from src.services.route_stats_service import RouteStatsService


async def recalculate_stats(gpx_file_id: str):
    """Recalculate RouteStatistics for an existing GPX file.

    Args:
        gpx_file_id: UUID of GPX file to recalculate statistics for
    """
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
                print(f"[ERROR] GPX file not found: {gpx_file_id}")
                return

            if not gpx_file.has_timestamps:
                print(f"[INFO] GPX file has no timestamps - cannot calculate route statistics")
                return

            print(f"[INFO] GPX File: {gpx_file_id}")
            print(f"       Distance: {gpx_file.distance_km} km")
            print(f"       File URL: {gpx_file.file_url}")
            print()

            # Read GPX file from storage
            storage_path = Path(settings.storage_path) / gpx_file.file_url
            if not storage_path.exists():
                print(f"[ERROR] GPX file not found in storage: {storage_path}")
                return

            with open(storage_path, "rb") as f:
                gpx_content = f.read()

            print(f"[INFO] Read GPX file from storage ({len(gpx_content)} bytes)")
            print()

            # Parse GPX file
            gpx_service = GPXService(db)
            parsed_data = await gpx_service.parse_gpx_file(gpx_content)

            print(f"[INFO] Parsed GPX data:")
            print(f"       Total points: {parsed_data['total_points']}")
            print(f"       Distance: {parsed_data['distance_km']} km")
            print(f"       Has timestamps: {parsed_data['has_timestamps']}")
            print(f"       Has elevation: {parsed_data['has_elevation']}")
            print()

            # Convert to stats format
            trackpoints_for_stats = gpx_service.convert_points_for_stats(
                parsed_data["original_points"]
            )

            # Calculate route statistics
            stats_service = RouteStatsService(db)
            print(f"[INFO] Calculating route statistics...")
            print()

            # Calculate speed metrics
            speed_metrics = await stats_service.calculate_speed_metrics(
                trackpoints_for_stats
            )

            # Fix floating-point precision issue
            if speed_metrics.get("moving_time_minutes") and speed_metrics.get(
                "total_time_minutes"
            ):
                if (
                    speed_metrics["moving_time_minutes"]
                    > speed_metrics["total_time_minutes"]
                ):
                    speed_metrics["moving_time_minutes"] = speed_metrics[
                        "total_time_minutes"
                    ]

            # Detect climbs
            top_climbs = await stats_service.detect_climbs(trackpoints_for_stats)

            # Calculate gradient distribution
            gradient_dist = await stats_service.classify_gradients(trackpoints_for_stats)

            # Calculate avg/max gradient
            total_distance = sum(cat["distance_km"] for cat in gradient_dist.values())
            avg_gradient = None
            if total_distance > 0:
                avg_gradient = (
                    gradient_dist["llano"]["distance_km"] * 1.5
                    + gradient_dist["moderado"]["distance_km"] * 4.5
                    + gradient_dist["empinado"]["distance_km"] * 8.0
                    + gradient_dist["muy_empinado"]["distance_km"] * 12.0
                ) / total_distance

            max_gradient = None
            if parsed_data["has_elevation"]:
                gradients = [
                    p.get("gradient")
                    for p in trackpoints_for_stats
                    if p.get("gradient") is not None
                ]
                max_gradient = max(gradients) if gradients else None

            # Convert top climbs to JSON format
            top_climbs_data = [
                {
                    "start_km": climb["start_km"],
                    "end_km": climb["end_km"],
                    "elevation_gain_m": climb["elevation_gain_m"],
                    "avg_gradient": climb["avg_gradient"],
                    "description": f"Subida {i+1}: {climb['elevation_gain_m']:.0f}m gain, {climb['avg_gradient']:.1f}% avg gradient",
                }
                for i, climb in enumerate(top_climbs[:3])
            ] if top_climbs else None

            # Delete existing RouteStatistics if present
            from sqlalchemy import delete as sql_delete

            delete_result = await db.execute(
                sql_delete(RouteStatistics).where(
                    RouteStatistics.gpx_file_id == gpx_file_id
                )
            )
            if delete_result.rowcount > 0:
                await db.commit()
                print(f"[INFO] Deleted existing RouteStatistics record")

            # Create new RouteStatistics
            route_stats = RouteStatistics(
                gpx_file_id=gpx_file.gpx_file_id,
                avg_speed_kmh=speed_metrics.get("avg_speed_kmh"),
                max_speed_kmh=speed_metrics.get("max_speed_kmh"),
                total_time_minutes=speed_metrics.get("total_time_minutes"),
                moving_time_minutes=speed_metrics.get("moving_time_minutes"),
                avg_gradient=avg_gradient,
                max_gradient=max_gradient,
                top_climbs=top_climbs_data if top_climbs_data else None,
            )
            db.add(route_stats)
            await db.commit()
            await db.refresh(route_stats)

            print()
            print("=" * 70)
            print("ROUTE STATISTICS CALCULATED")
            print("=" * 70)
            print()
            print(f"[SPEED]")
            print(f"  Avg Speed:     {route_stats.avg_speed_kmh:.2f} km/h")
            print(f"  Max Speed:     {route_stats.max_speed_kmh:.2f} km/h")
            print()
            print(f"[TIME]")
            total_hours = int(route_stats.total_time_minutes // 60)
            total_mins = int(route_stats.total_time_minutes % 60)
            moving_hours = int(route_stats.moving_time_minutes // 60)
            moving_mins = int(route_stats.moving_time_minutes % 60)
            stopped_time = route_stats.total_time_minutes - route_stats.moving_time_minutes

            print(f"  Total Time:    {total_hours}h {total_mins}min ({route_stats.total_time_minutes:.2f} min)")
            print(f"  Moving Time:   {moving_hours}h {moving_mins}min ({route_stats.moving_time_minutes:.2f} min)")
            print(f"  Stopped Time:  {stopped_time:.2f} min ({stopped_time/60:.2f} hours)")
            print(f"  Moving/Total:  {(route_stats.moving_time_minutes/route_stats.total_time_minutes*100):.1f}%")
            print()
            print(f"[GRADIENT]")
            print(f"  Avg Gradient:  {route_stats.avg_gradient:.1f}%" if route_stats.avg_gradient else "  Avg Gradient:  N/A")
            print(f"  Max Gradient:  {route_stats.max_gradient:.1f}%" if route_stats.max_gradient else "  Max Gradient:  N/A")
            print()
            print(f"[CLIMBS]")
            if route_stats.top_climbs:
                for i, climb in enumerate(route_stats.top_climbs, 1):
                    print(f"  Climb #{i}:")
                    print(f"    Start-End:       {climb['start_km']:.2f} - {climb['end_km']:.2f} km")
                    print(f"    Elevation Gain:  {climb['elevation_gain_m']:.0f} m")
                    print(f"    Avg Gradient:    {climb['avg_gradient']:.1f}%")
            else:
                print("  No climbs detected")
            print()
            print("=" * 70)
            print()
            print(f"[OK] RouteStatistics recalculated successfully!")
            print(f"     Stats ID: {route_stats.stats_id}")

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback

            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Recalculate RouteStatistics for an existing GPX file without re-uploading.",
        epilog="Example:\n"
               "  %(prog)s 13e24f2f-f792-4873-b636-ad3568861514",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "gpx_file_id",
        help="UUID of GPX file to recalculate statistics for"
    )

    args = parser.parse_args()

    asyncio.run(recalculate_stats(args.gpx_file_id))
