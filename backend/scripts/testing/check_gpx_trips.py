"""
Script for verifying GPX trip data in the database.

This testing utility checks for the presence of trips with associated GPX files
and displays sample data for manual verification during development and testing.

Usage:
    cd backend
    poetry run python scripts/testing/check_gpx_trips.py

Requirements:
    - Database must be initialized and running
    - At least one trip with GPX file should exist for meaningful output

Output:
    - Total count of trips with GPX files
    - Sample trip details (ID, title, status, privacy)
    - Test URL for frontend verification
"""

import asyncio
from sqlalchemy import select, func
from src.database import AsyncSessionLocal
from src.models.trip import Trip
from src.models.gpx import GPXFile


async def check_gpx_trips() -> None:
    """
    Query database for trips with GPX files and display summary.

    This function performs two queries:
    1. Count total trips with associated GPX files
    2. Retrieve one example trip with GPX for inspection

    The output includes a test URL for verifying the trip in the frontend
    (assumes frontend running at http://localhost:5173).

    Returns:
        None. Prints results to stdout.
    """
    async with AsyncSessionLocal() as db:
        # Count trips with GPX files (inner join ensures GPX exists)
        result = await db.execute(
            select(func.count(Trip.trip_id))
            .join(GPXFile, Trip.trip_id == GPXFile.trip_id, isouter=False)
        )
        gpx_trips = result.scalar()

        print(f'Trips with GPX: {gpx_trips}')

        # Get one GPX trip example for manual verification
        if gpx_trips > 0:
            result = await db.execute(
                select(Trip.trip_id, Trip.title, Trip.status, Trip.is_private)
                .join(GPXFile)
                .limit(1)
            )
            trip = result.first()
            if trip:
                print(f'\nExample GPX trip:')
                print(f'  ID: {trip.trip_id}')
                print(f'  Title: {trip.title}')
                print(f'  Status: {trip.status}')
                print(f'  Privacy: {"Private" if trip.is_private else "Public"}')
                print(f'\nTest URL: http://localhost:5173/trips/{trip.trip_id}')


if __name__ == '__main__':
    asyncio.run(check_gpx_trips())
