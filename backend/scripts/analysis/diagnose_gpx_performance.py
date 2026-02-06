#!/usr/bin/env python3
"""
Diagnostic script for GPX performance bottleneck analysis (Feature 017 - GPS Trip Wizard).

Performs step-by-step performance profiling of GPX file processing to identify bottlenecks.
Measures XML parsing, RDP simplification, and telemetry extraction separately.

Usage:
    # Diagnose with default file (long_route_10mb.gpx)
    poetry run python scripts/analysis/diagnose_gpx_performance.py

    # Diagnose specific file (relative path)
    poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/short_route.gpx

    # Diagnose with absolute path
    poetry run python scripts/analysis/diagnose_gpx_performance.py /home/user/Downloads/my-route.gpx

    # Show help
    poetry run python scripts/analysis/diagnose_gpx_performance.py --help

Success Criteria:
    - SC-002: GPX processing <2s for files ≥10MB

Examples:
    # Identify bottlenecks in 10MB file
    $ poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/long_route_10mb.gpx

    STEP 1: Parse GPX XML
    ✓ Parse time: 2.229s
    ✓ Original trackpoints: 85,000

    STEP 2: RDP Simplification
    ✓ RDP time: 2.269s
    ✓ Simplified trackpoints: 2

    BOTTLENECK ANALYSIS
    XML parsing:        2.229s (44.9%)
    RDP algorithm:      2.269s (45.7%)
    Other operations:   0.462s (9.3%)

    # Analyze small file
    $ poetry run python scripts/analysis/diagnose_gpx_performance.py scripts/datos/QH_2013.gpx
    ✓ Total time: 0.523s
    ✓ SC-002 PASS: 0.523s / 2.0s target

Notes:
    - Measures parsing, RDP simplification, and service layer separately
    - Identifies which operation is the bottleneck
    - Validates SC-002 for files ≥10MB
    - Supports any GPX file (relative or absolute path)

Feature: 017-gps-trip-wizard
Phase: 9 (Polish)
Task: T101 - Performance testing
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, 'src')

from src.database import AsyncSessionLocal
from src.services.gpx_service import GPXService
import gpxpy


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
        # Default to long_route_10mb.gpx for SC-002 validation
        gpx_path = Path(__file__).parent.parent.parent / 'tests' / 'fixtures' / 'gpx' / 'long_route_10mb.gpx'

    return gpx_path


async def diagnose():
    """Diagnose GPX performance bottlenecks."""
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
        print(f"\nUsage: poetry run python scripts/analysis/diagnose_gpx_performance.py <path-to-gpx>")
        sys.exit(1)

    # Validate file is readable
    if not gpx_file.is_file():
        print(f"✗ Not a file: {gpx_file}")
        sys.exit(1)

    # Read GPX file
    print(f"\n✓ Reading GPX file: {gpx_file}")
    try:
        file_content = gpx_file.read_bytes()
    except Exception as e:
        print(f"✗ Failed to read file: {e}")
        sys.exit(1)

    file_size_mb = len(file_content) / (1024 * 1024)
    print(f"  File size: {len(file_content):,} bytes ({file_size_mb:.2f} MB)\n")

    # Step 1: Parse GPX and count original points
    print("=" * 60)
    print("STEP 1: Parse GPX XML")
    print("=" * 60)
    start = time.perf_counter()
    try:
        gpx = gpxpy.parse(file_content)
        parse_time = time.perf_counter() - start
        print(f"✓ Parse time: {parse_time:.3f}s")
    except Exception as e:
        print(f"\n✗ GPX parsing failed: {e}")
        print("\nPossible causes:")
        print("  - Invalid GPX format (not well-formed XML)")
        print("  - Corrupted file")
        print("  - Not a GPX file")
        sys.exit(1)

    # Count points
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            points.extend(segment.points)

    if len(points) == 0:
        print("✗ No trackpoints found in GPX file")
        sys.exit(1)

    print(f"✓ Original trackpoints: {len(points):,}")

    # Step 2: Test RDP simplification directly
    print("\n" + "=" * 60)
    print("STEP 2: RDP Simplification (epsilon=0.0001)")
    print("=" * 60)

    from rdp import rdp

    coords = [(p.latitude, p.longitude) for p in points]
    print(f"Coordinate array size: {len(coords):,}")

    start = time.perf_counter()
    simplified_coords = rdp(coords, epsilon=0.0001)
    rdp_time = time.perf_counter() - start

    print(f"✓ RDP time: {rdp_time:.3f}s")
    print(f"✓ Simplified trackpoints: {len(simplified_coords):,}")
    print(f"✓ Reduction: {(1 - len(simplified_coords)/len(coords))*100:.1f}%")

    # Step 3: Test GPXService method
    print("\n" + "=" * 60)
    print("STEP 3: GPXService._simplify_track_optimized")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        gpx_service = GPXService(db)

        start = time.perf_counter()
        simplified = gpx_service._simplify_track_optimized(points, epsilon=0.0001)
        service_time = time.perf_counter() - start

        print(f"✓ Service simplification time: {service_time:.3f}s")
        print(f"✓ Simplified trackpoints: {len(simplified):,}")

        # Sample first few points
        print(f"\nFirst 3 simplified points:")
        for i, tp in enumerate(simplified[:3]):
            print(f"  {i}: lat={tp['latitude']:.6f}, lon={tp['longitude']:.6f}, "
                  f"dist={tp['distance_km']:.2f}km, elev={tp.get('elevation')}")

    # Step 4: Test extract_telemetry_quick
    print("\n" + "=" * 60)
    print("STEP 4: extract_telemetry_quick (full workflow)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        gpx_service = GPXService(db)

        start = time.perf_counter()
        result = await gpx_service.extract_telemetry_quick(
            file_content, include_trackpoints=True
        )
        total_time = time.perf_counter() - start

        print(f"✓ Total time: {total_time:.3f}s")
        print(f"✓ Distance: {result['distance_km']:.2f} km")
        print(f"✓ Elevation gain: {result['elevation_gain']} m")
        print(f"✓ Trackpoints in result: {len(result['trackpoints']):,}")

    # Summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Parse XML:               {parse_time:.3f}s")
    print(f"RDP simplification:      {rdp_time:.3f}s")
    print(f"Service simplification:  {service_time:.3f}s")
    print(f"extract_telemetry_quick: {total_time:.3f}s")

    # Validate SC-002 (GPX processing <2s for 10MB files)
    print()
    if file_size_mb >= 10.0:
        if total_time < 2.0:
            print(f"✓ SC-002 PASS: 10MB+ file processed in {total_time:.3f}s (<2s target)")
        else:
            print(f"✗ SC-002 FAIL: 10MB+ file processed in {total_time:.3f}s (>2s target)")
    else:
        print(f"ℹ  File size {file_size_mb:.2f}MB - SC-002 not applicable (requires ≥10MB)")
        if total_time < 2.0:
            print(f"✓ Processing time: {total_time:.3f}s (<2s)")
        else:
            print(f"⚠  Processing time: {total_time:.3f}s (>2s)")

    # Bottleneck analysis
    print("\n" + "=" * 60)
    print("BOTTLENECK ANALYSIS")
    print("=" * 60)
    other_time = total_time - parse_time - rdp_time
    print(f"XML parsing:        {parse_time:.3f}s ({parse_time/total_time*100:.1f}%)")
    print(f"RDP algorithm:      {rdp_time:.3f}s ({rdp_time/total_time*100:.1f}%)")
    print(f"Other operations:   {other_time:.3f}s ({other_time/total_time*100:.1f}%)")


if __name__ == "__main__":
    asyncio.run(diagnose())
