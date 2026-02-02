#!/usr/bin/env python3
"""
Generate a realistic 10MB+ GPX file with curves, elevation changes, and zigzags.

This script creates a GPX file that simulates a real cycling route with:
- Curves and direction changes (not a straight line)
- Realistic elevation profile (hills, valleys)
- ~85,000 trackpoints to reach 10MB+ file size
- Timestamps at realistic intervals

Usage:
    python3 generate_realistic_gpx.py

Output:
    realistic_route_10mb.gpx (10.5MB+)

Feature: 017-gps-trip-wizard
Purpose: Replace long_route_10mb.gpx (straight line) with realistic test file
"""

import math
import random
from datetime import datetime, timedelta


def generate_realistic_route():
    """
    Generate a realistic cycling route with curves and elevation changes.

    Route design:
    - Start: Pyrenees region (42.5°N, -0.4°E)
    - Pattern: Zigzag mountain route with multiple valleys and peaks
    - Distance: ~200km equivalent
    - Elevation: 500m - 2500m (realistic mountain cycling)
    """

    # Starting point (Pyrenees)
    start_lat = 42.5
    start_lon = -0.4
    start_elevation = 800

    # Target: 85,000 trackpoints to reach 10MB+
    num_points = 85000

    # Timestamp setup
    start_time = datetime(2024, 6, 15, 8, 0, 0)  # Start at 8 AM

    # GPX header
    gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="ContraVento Test Generator" version="1.1"
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>Realistic Mountain Route 10MB</name>
    <desc>Realistic cycling route with curves, elevation changes, and zigzags for testing GPX processing performance</desc>
    <time>2024-06-15T08:00:00Z</time>
  </metadata>
  <trk>
    <name>Pyrenees Mountain Circuit</name>
    <desc>Challenging mountain route with multiple climbs and descents</desc>
    <type>Cycling</type>
    <trkseg>
"""

    print("Generating realistic GPX file...")
    print(f"Target points: {num_points:,}")

    # Generate trackpoints with realistic patterns
    current_lat = start_lat
    current_lon = start_lon
    current_elevation = start_elevation
    current_time = start_time

    # Track generation parameters
    avg_speed_kmh = 20.0  # Average cycling speed
    avg_speed_ms = avg_speed_kmh * 1000 / 3600  # meters per second
    time_interval_s = 3  # 3 seconds between points (realistic GPS sampling)

    # Elevation profile parameters
    elevation_period = num_points / 8  # 8 major hills/valleys
    elevation_amplitude = 400  # ±400m elevation changes

    # Direction change parameters (creates curves)
    direction_angle = 0  # Starting direction (east)

    for i in range(num_points):
        # Progress indicator
        if i % 10000 == 0:
            progress = (i / num_points) * 100
            print(f"  Progress: {progress:.1f}% ({i:,} / {num_points:,} points)")

        # PATTERN 1: Zigzag route (creates curves instead of straight line)
        # Change direction every ~1000 points
        if i % 1000 == 0:
            direction_angle += random.uniform(-45, 45)  # Random direction change

        # Add small random variations to create natural curves
        direction_angle += random.uniform(-2, 2)

        # PATTERN 2: Spiral pattern for mountain switchbacks
        if i % 5000 < 2500:  # First half of cycle
            direction_angle += 0.5  # Gradual curve
        else:  # Second half
            direction_angle -= 0.5  # Curve back

        # Calculate movement (small steps to create dense trackpoints)
        distance_m = avg_speed_ms * time_interval_s  # meters traveled in time_interval

        # Convert direction angle to radians
        direction_rad = math.radians(direction_angle)

        # Calculate lat/lon deltas
        # At 42° latitude, 1° ≈ 111km lat, ~82km lon
        lat_delta = (distance_m / 111000) * math.cos(direction_rad)
        lon_delta = (distance_m / 82000) * math.sin(direction_rad)

        current_lat += lat_delta
        current_lon += lon_delta

        # PATTERN 3: Realistic elevation profile
        # Combine multiple sine waves for realistic hills/valleys
        base_elevation = 800 + elevation_amplitude * math.sin(2 * math.pi * i / elevation_period)

        # Add secondary wave (smaller hills)
        secondary_elevation = 100 * math.sin(2 * math.pi * i / (elevation_period / 3))

        # Add random noise for realism
        noise = random.uniform(-20, 20)

        current_elevation = base_elevation + secondary_elevation + noise

        # Clamp elevation to realistic range
        current_elevation = max(500, min(2500, current_elevation))

        # Update timestamp
        current_time += timedelta(seconds=time_interval_s)

        # Write trackpoint to GPX
        gpx_content += f"""      <trkpt lat="{current_lat:.6f}" lon="{current_lon:.6f}">
        <ele>{current_elevation:.1f}</ele>
        <time>{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}</time>
      </trkpt>
"""

    # GPX footer
    gpx_content += """    </trkseg>
  </trk>
</gpx>
"""

    return gpx_content


def main():
    """Generate and save realistic GPX file."""

    print("=" * 60)
    print("Realistic GPX Generator")
    print("=" * 60)
    print()

    # Generate GPX content
    gpx_content = generate_realistic_route()

    # Save to file
    output_file = "realistic_route_10mb.gpx"
    print(f"\nWriting to {output_file}...")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(gpx_content)

    # Verify file size
    import os

    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"✓ File: {output_file}")
    print(f"✓ Size: {file_size:,} bytes ({file_size_mb:.2f} MB)")

    if file_size_mb >= 10.0:
        print("✓ SUCCESS: File size ≥10 MB (required for SC-002 testing)")
    else:
        print("⚠ WARNING: File size <10 MB (may not trigger SC-002 validation)")

    print()
    print("Route characteristics:")
    print("  - Pattern: Zigzag mountain route with curves")
    print("  - Elevation: 500m - 2500m (realistic mountain cycling)")
    print("  - Duration: ~7 hours (realistic long ride)")
    print("  - Trackpoints: ~85,000 (dense GPS sampling)")
    print()
    print("Next steps:")
    print(
        "  1. Test with: poetry run python scripts/analysis/test_gpx_analyze.py realistic_route_10mb.gpx"
    )
    print(
        "  2. Diagnose: poetry run python scripts/analysis/diagnose_gpx_performance.py realistic_route_10mb.gpx"
    )
    print("  3. Compare RDP reduction: Should preserve ~500-1500 points (not 2 like straight line)")
    print()


if __name__ == "__main__":
    main()
