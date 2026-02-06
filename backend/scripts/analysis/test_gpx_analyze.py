#!/usr/bin/env python3
"""
Test script for /gpx/analyze endpoint (Feature 017 - GPS Trip Wizard).

Validates GPX file processing performance and extracts telemetry data.
Workaround for curl authentication issues with special characters.

Usage:
    # Test with default file (short_route.gpx)
    poetry run python scripts/analysis/test_gpx_analyze.py

    # Test with specific file (relative path)
    poetry run python scripts/analysis/test_gpx_analyze.py tests/fixtures/gpx/long_route_10mb.gpx

    # Test with absolute path
    poetry run python scripts/analysis/test_gpx_analyze.py /home/user/Downloads/my-route.gpx

    # Show help
    poetry run python scripts/analysis/test_gpx_analyze.py --help

Success Criteria:
    - SC-002: GPX processing <2s for files ≥10MB

Examples:
    # Validate SC-002 with 10MB file
    $ poetry run python scripts/analysis/test_gpx_analyze.py tests/fixtures/gpx/long_route_10mb.gpx
    ✓ Token obtained: eyJhbGci...
    ✓ Reading GPX file: tests/fixtures/gpx/long_route_10mb.gpx
      File size: 10,886,608 bytes (10.38 MB)
    ⏱  Processing time: 4.929 seconds
    ✗ SC-002 FAIL: 10MB+ file processed in 4.929s (>2s target)

    # Analyze external GPX file
    $ poetry run python scripts/analysis/test_gpx_analyze.py ~/Downloads/strava-export.gpx
    ✓ GPX analysis SUCCESS
    Distance: 42.5 km
    Processing time: 0.523 seconds

Notes:
    - This script bypasses HTTP authentication (no curl needed)
    - Supports any GPX file (relative or absolute path)
    - Automatically validates SC-002 for files ≥10MB
    - Shows detailed telemetry and performance metrics

Feature: 017-gps-trip-wizard
Phase: 9 (Polish)
Task: T101 - Performance testing
"""

import asyncio
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.database import AsyncSessionLocal
from src.services.auth_service import AuthService
from src.schemas.auth import LoginRequest
from src.services.gpx_service import GPXService


def show_help():
    """Show help message and exit."""
    print(__doc__)
    sys.exit(0)


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Path: GPX file path to analyze

    Raises:
        SystemExit: If --help flag or invalid arguments
    """
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ('--help', '-h', 'help'):
        show_help()

    # Get GPX file path (default or from argument)
    if len(sys.argv) > 1:
        gpx_path = Path(sys.argv[1]).expanduser().resolve()
    else:
        # Default to short_route.gpx in tests/fixtures
        gpx_path = Path(__file__).parent.parent.parent / 'tests' / 'fixtures' / 'gpx' / 'short_route.gpx'

    return gpx_path


async def test_gpx_analyze():
    """
    Test GPX analyze endpoint with performance measurement.

    Authenticates, reads GPX file, extracts telemetry, and validates SC-002.
    """
    # Parse arguments
    try:
        gpx_file = parse_arguments()
    except Exception as e:
        print(f"✗ Error parsing arguments: {e}")
        sys.exit(1)

    # Validate file exists
    if not gpx_file.exists():
        print(f"✗ File not found: {gpx_file}")
        print(f"\nℹ  Current directory: {Path.cwd()}")
        print(f"ℹ  Searched path: {gpx_file.absolute()}")
        print(f"\nUsage: poetry run python scripts/analysis/test_gpx_analyze.py <path-to-gpx>")
        sys.exit(1)

    # Validate file is readable
    if not gpx_file.is_file():
        print(f"✗ Not a file: {gpx_file}")
        sys.exit(1)

    # Get authentication token
    async with AsyncSessionLocal() as db:
        # Login
        auth_service = AuthService(db)
        login_data = LoginRequest(login='testuser', password='TestPass123!')
        response = await auth_service.login(login_data)
        token = response.access_token
        print(f"✓ Token obtained: {token[:50]}...")

        # Test GPX service directly
        gpx_service = GPXService(db)

        # Read GPX file
        print(f"\n✓ Reading GPX file: {gpx_file}")
        try:
            file_content = gpx_file.read_bytes()
        except Exception as e:
            print(f"✗ Failed to read file: {e}")
            sys.exit(1)

        file_size_mb = len(file_content) / (1024 * 1024)
        print(f"  File size: {len(file_content):,} bytes ({file_size_mb:.2f} MB)")

        # Extract telemetry with timing
        print("\n✓ Extracting telemetry...")
        start_time = time.time()

        try:
            telemetry = await gpx_service.extract_telemetry_quick(
                file_content, include_trackpoints=True
            )
            elapsed_time = time.time() - start_time

            print("\n✓ Telemetry data:")
            print(f"  Distance: {telemetry['distance_km']:.2f} km")
            print(f"  Elevation gain: {telemetry['elevation_gain']} m")
            print(f"  Elevation loss: {telemetry['elevation_loss']} m")
            print(f"  Max elevation: {telemetry['max_elevation']} m")
            print(f"  Min elevation: {telemetry['min_elevation']} m")
            print(f"  Has elevation: {telemetry['has_elevation']}")
            print(f"  Has timestamps: {telemetry['has_timestamps']}")
            print(f"  Difficulty: {telemetry['difficulty']}")
            print(f"  Trackpoints: {len(telemetry['trackpoints'])}")
            print(f"  Start date: {telemetry['start_date']}")
            print(f"  End date: {telemetry['end_date']}")

            print(f"\n⏱  Processing time: {elapsed_time:.3f} seconds")

            # Validate SC-002 (GPX processing <2s for 10MB files)
            if file_size_mb >= 10.0:
                if elapsed_time < 2.0:
                    print(f"✓ SC-002 PASS: 10MB+ file processed in {elapsed_time:.3f}s (<2s target)")
                else:
                    print(f"✗ SC-002 FAIL: 10MB+ file processed in {elapsed_time:.3f}s (>2s target)")
            else:
                print(f"ℹ  File size <10MB - SC-002 not applicable")

            print("\n✓ GPX analysis SUCCESS - Service layer works correctly")
            print("\nℹ  Note: HTTP endpoint authentication via curl is failing due to shell escaping.")
            print("   Use this Python script instead for testing.")

        except ValueError as e:
            print(f"\n✗ GPX validation failed: {e}")
            print("\nPossible causes:")
            print("  - Invalid GPX format (not well-formed XML)")
            print("  - Missing trackpoints in GPX file")
            print("  - Anomalous elevation data (outside -420m to 8850m range)")
            sys.exit(1)

        except Exception as e:
            print(f"\n✗ Telemetry extraction failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_gpx_analyze())
