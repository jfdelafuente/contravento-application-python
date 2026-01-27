"""
Manual test script for User Story 5 - Advanced Statistics.

Tests the complete flow:
1. Upload GPX file with timestamps
2. Verify RouteStatistics record created
3. Retrieve statistics via API
4. Display results in readable format

Usage:
    poetry run python scripts/test_route_statistics.py
"""

import asyncio
import json
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.gpx import GPXFile
from src.models.route_statistics import RouteStatistics
from src.models.trip import Trip
from src.models.user import User
from src.services.gpx_service import GPXService


async def test_route_statistics():
    """Test route statistics calculation and retrieval."""
    print("=" * 80)
    print("MANUAL TEST: User Story 5 - Advanced Statistics")
    print("=" * 80)
    print()

    # Create async database engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Step 1: Get or create test user
            print("[1/6] Setting up test user...")
            result = await db.execute(select(User).where(User.username == "testuser"))
            user = result.scalar_one_or_none()

            if not user:
                print("   [ERROR] Test user 'testuser' not found. Please run:")
                print("   poetry run python scripts/create_verified_user.py")
                return

            print(f"   [OK] Test user found: {user.username} (ID: {user.id})")
            print()

            # Step 2: Create test trip
            print("[2/6] Creating test trip...")
            test_trip = Trip(
                user_id=user.id,
                title="Test Trip - Route Statistics",
                description="Manual test for advanced statistics (User Story 5)",
                start_date=date(2024, 6, 15),
                status="PUBLISHED",
            )
            db.add(test_trip)
            await db.commit()
            await db.refresh(test_trip)
            print(f"   [OK] Test trip created: {test_trip.title} (ID: {test_trip.trip_id})")
            print()

            # Step 3: Upload GPX file with timestamps
            print("[3/6] Uploading GPX file with timestamps...")
            gpx_file_path = Path("tests/fixtures/gpx/via-verde.gpx")

            if not gpx_file_path.exists():
                print(f"   [ERROR] GPX file not found: {gpx_file_path}")
                return

            with open(gpx_file_path, "rb") as f:
                file_content = f.read()

            print(f"   [FILE] File: {gpx_file_path.name} ({len(file_content)} bytes)")

            # Parse GPX file
            gpx_service = GPXService(db)
            parsed_data = await gpx_service.parse_gpx_file(file_content)

            print(f"   [DATA] Parsed data:")
            print(f"      - Distance: {parsed_data['distance_km']} km")
            print(f"      - Elevation gain: {parsed_data['elevation_gain']} m")
            print(f"      - Has timestamps: {parsed_data['has_timestamps']}")
            print(f"      - Has elevation: {parsed_data['has_elevation']}")
            print(f"      - Total points: {parsed_data['total_points']}")
            print()

            # Save GPX to storage
            file_url = await gpx_service.save_gpx_to_storage(
                trip_id=test_trip.trip_id,
                file_content=file_content,
                filename=gpx_file_path.name,
            )

            # Create GPX file record
            from datetime import UTC, datetime

            gpx_file = GPXFile(
                trip_id=test_trip.trip_id,
                file_url=file_url,
                file_size=len(file_content),
                file_name=gpx_file_path.name,
                distance_km=parsed_data["distance_km"],
                elevation_gain=parsed_data["elevation_gain"],
                elevation_loss=parsed_data["elevation_loss"],
                max_elevation=parsed_data["max_elevation"],
                min_elevation=parsed_data["min_elevation"],
                start_lat=parsed_data["start_lat"],
                start_lon=parsed_data["start_lon"],
                end_lat=parsed_data["end_lat"],
                end_lon=parsed_data["end_lon"],
                total_points=parsed_data["total_points"],
                simplified_points=parsed_data["simplified_points_count"],
                has_elevation=parsed_data["has_elevation"],
                has_timestamps=parsed_data["has_timestamps"],
                processing_status="completed",
                processed_at=datetime.now(UTC),
            )
            db.add(gpx_file)
            await db.commit()
            await db.refresh(gpx_file)

            print(f"   [OK] GPX file saved: {gpx_file.gpx_file_id}")
            print()

            # Step 4: Calculate route statistics
            print("[4/6] Calculating route statistics...")

            if parsed_data["has_timestamps"]:
                from src.services.route_stats_service import RouteStatsService

                # Convert points for stats service
                trackpoints_for_stats = gpx_service.convert_points_for_stats(
                    parsed_data["original_points"]
                )

                stats_service = RouteStatsService(db)

                # Calculate speed metrics
                speed_metrics = await stats_service.calculate_speed_metrics(
                    trackpoints_for_stats
                )

                # Detect top climbs
                top_climbs_data = await stats_service.detect_climbs(trackpoints_for_stats)

                # Calculate gradient distribution
                gradient_distribution = await stats_service.classify_gradients(
                    trackpoints_for_stats
                )

                # Calculate avg/max gradient
                avg_gradient = None
                max_gradient = None
                if parsed_data["has_elevation"]:
                    total_distance = sum(
                        cat["distance_km"]
                        for cat in gradient_distribution.values()
                        if cat["distance_km"] > 0
                    )
                    if total_distance > 0:
                        weighted_sum = (
                            gradient_distribution["llano"]["distance_km"] * 1.5
                            + gradient_distribution["moderado"]["distance_km"] * 4.5
                            + gradient_distribution["empinado"]["distance_km"] * 8.0
                            + gradient_distribution["muy_empinado"]["distance_km"] * 12.0
                        )
                        avg_gradient = round(weighted_sum / total_distance, 1)

                    if gradient_distribution["muy_empinado"]["distance_km"] > 0:
                        max_gradient = 15.0

                # Create RouteStatistics record
                route_stats = RouteStatistics(
                    gpx_file_id=gpx_file.gpx_file_id,
                    avg_speed_kmh=speed_metrics["avg_speed_kmh"],
                    max_speed_kmh=speed_metrics["max_speed_kmh"],
                    total_time_minutes=speed_metrics["total_time_minutes"],
                    moving_time_minutes=speed_metrics["moving_time_minutes"],
                    avg_gradient=avg_gradient,
                    max_gradient=max_gradient,
                    top_climbs=top_climbs_data if top_climbs_data else None,
                )
                db.add(route_stats)
                await db.commit()
                await db.refresh(route_stats)

                print(f"   [OK] Route statistics created: {route_stats.stats_id}")
                print()

            else:
                print("   [WARN]  GPX file has no timestamps - statistics not calculated")
                route_stats = None
                print()

            # Step 5: Retrieve statistics from database
            print("[5/6] Retrieving statistics from database...")

            stats_result = await db.execute(
                select(RouteStatistics).where(RouteStatistics.gpx_file_id == gpx_file.gpx_file_id)
            )
            retrieved_stats = stats_result.scalar_one_or_none()

            if retrieved_stats:
                print(f"   [OK] Statistics retrieved from database")
                print()
            else:
                print(f"   [ERROR] No statistics found in database")
                return

            # Step 6: Display results
            print("[6/6] RESULTS - Route Statistics:")
            print("=" * 80)
            print()

            # Speed metrics
            print("[SPEED] SPEED METRICS")
            print("-" * 40)
            if retrieved_stats.avg_speed_kmh:
                print(f"   Average Speed:    {retrieved_stats.avg_speed_kmh:.1f} km/h")
                print(f"   Maximum Speed:    {retrieved_stats.max_speed_kmh:.1f} km/h")
            else:
                print("   [WARN]  No speed data (no timestamps)")
            print()

            # Time metrics
            print("[TIME] TIME METRICS")
            print("-" * 40)
            if retrieved_stats.total_time_minutes:
                total_hours = int(retrieved_stats.total_time_minutes // 60)
                total_mins = int(retrieved_stats.total_time_minutes % 60)
                moving_hours = int(retrieved_stats.moving_time_minutes // 60)
                moving_mins = int(retrieved_stats.moving_time_minutes % 60)

                print(f"   Total Time:       {total_hours}h {total_mins}min")
                print(f"   Moving Time:      {moving_hours}h {moving_mins}min")
                print(
                    f"   Stopped Time:     {int(retrieved_stats.total_time_minutes - retrieved_stats.moving_time_minutes)}min"
                )
            else:
                print("   [WARN]  No time data (no timestamps)")
            print()

            # Gradient metrics
            print("[GRADIENT] GRADIENT METRICS")
            print("-" * 40)
            if retrieved_stats.avg_gradient:
                print(f"   Average Gradient: {retrieved_stats.avg_gradient:.1f}%")
                if retrieved_stats.max_gradient:
                    print(f"   Maximum Gradient: {retrieved_stats.max_gradient:.1f}%")
                else:
                    print(f"   Maximum Gradient: N/A")
            else:
                print("   [WARN]  No gradient data (no elevation)")
            print()

            # Top climbs
            print("[CLIMBS] TOP 3 CLIMBS")
            print("-" * 40)
            if retrieved_stats.top_climbs and len(retrieved_stats.top_climbs) > 0:
                for i, climb in enumerate(retrieved_stats.top_climbs, 1):
                    print(f"   Climb #{i}:")
                    print(f"      Start:          {climb['start_km']:.2f} km")
                    print(f"      End:            {climb['end_km']:.2f} km")
                    print(f"      Distance:       {climb['end_km'] - climb['start_km']:.2f} km")
                    print(f"      Elevation Gain: {climb['elevation_gain_m']:.0f} m")
                    print(f"      Avg Gradient:   {climb['avg_gradient']:.1f}%")
                    print()
            else:
                print("   [WARN]  No climbs detected (minimum 50m gain required)")
                print()

            # Gradient distribution
            print("[DATA] GRADIENT DISTRIBUTION")
            print("-" * 40)

            # Re-calculate for display
            gradient_dist = await stats_service.classify_gradients(trackpoints_for_stats)

            for category, data in gradient_dist.items():
                category_names = {
                    "llano": "Flat (0-3%)",
                    "moderado": "Moderate (3-6%)",
                    "empinado": "Steep (6-10%)",
                    "muy_empinado": "Very Steep (>10%)",
                }
                print(
                    f"   {category_names[category]:20s}: {data['distance_km']:6.2f} km ({data['percentage']:5.1f}%)"
                )
            print()

            print("=" * 80)
            print()
            print("[OK] TEST COMPLETED SUCCESSFULLY!")
            print()
            print(f"Test Trip ID:     {test_trip.trip_id}")
            print(f"GPX File ID:      {gpx_file.gpx_file_id}")
            print(f"Statistics ID:    {retrieved_stats.stats_id}")
            print()
            print("You can now test the API endpoint:")
            print(f"  GET http://localhost:8000/gpx/{gpx_file.gpx_file_id}/track")
            print()

        except Exception as e:
            print(f"[ERROR] Error: {e}")
            import traceback

            traceback.print_exc()
            await db.rollback()
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(test_route_statistics())
