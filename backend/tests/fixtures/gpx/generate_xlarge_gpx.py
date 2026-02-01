#!/usr/bin/env python3
"""
Generate an extra-large GPX file (10MB+) for performance testing.

Target: ~80,000 trackpoints to reach 10MB+ file size.

Feature: 017-gps-trip-wizard
Phase: 9 (Polish)
Task: T101 - Performance testing

Usage:
    python3 generate_xlarge_gpx.py

Output:
    long_route_10mb.gpx (~10-11 MB)
"""

from pathlib import Path


def generate_xlarge_gpx(output_path: Path, num_points: int = 80000):
    """
    Generate an extra-large GPX file with specified number of points.

    Args:
        output_path: Path where GPX file will be saved
        num_points: Number of trackpoints to generate (default: 80,000 for ~10MB)
    """

    with open(output_path, "w", encoding="utf-8") as f:
        # Write GPX header
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(
            '<gpx version="1.1" creator="ContraVento Test Generator" '
            'xmlns="http://www.topografix.com/GPX/1/1" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 '
            'http://www.topografix.com/GPX/1/1/gpx.xsd">\n'
        )
        f.write("  <metadata>\n")
        f.write("    <name>Extra Large Test Route - 10MB+</name>\n")
        f.write(f"    <desc>Performance test file with {num_points:,} trackpoints for SC-002 validation</desc>\n")
        f.write("    <author>\n")
        f.write("      <name>ContraVento Test Suite</name>\n")
        f.write("    </author>\n")
        f.write("    <time>2024-06-01T08:00:00Z</time>\n")
        f.write("  </metadata>\n")
        f.write("  <trk>\n")
        f.write("    <name>Trans Pyrenees Complete - Extra Large File Test</name>\n")
        f.write("    <type>Bikepacking</type>\n")
        f.write("    <trkseg>\n")

        # Generate trackpoints
        # Simulate Trans Pyrenees route: Atlantic (43.3333°N, 1.4667°W) to Mediterranean (42.5063°N, 3.1075°E)
        start_lat = 43.3333
        start_lon = -1.4667
        end_lat = 42.5063
        end_lon = 3.1075

        lat_step = (end_lat - start_lat) / num_points
        lon_step = (end_lon - start_lon) / num_points

        base_elevation = 500  # Starting elevation in meters
        max_elevation = 2500  # Maximum elevation (mountain passes)

        print(f"Generating {num_points:,} trackpoints...")
        print("Progress: ", end="", flush=True)

        for i in range(num_points):
            # Show progress every 10,000 points
            if i % 10000 == 0 and i > 0:
                print(f"{i:,}...", end="", flush=True)

            lat = start_lat + (lat_step * i)
            lon = start_lon + (lon_step * i)

            # Simulate realistic elevation profile with multiple mountain passes
            # Create 8 major climbs throughout the route
            climb_frequency = num_points // 8
            climb_position = i % climb_frequency
            climb_progress = climb_position / climb_frequency

            # Simulate climbing (0-0.5) and descending (0.5-1.0)
            if climb_progress < 0.5:
                # Climbing: gradual increase
                elevation_factor = climb_progress * 2  # 0 to 1
            else:
                # Descending: gradual decrease
                elevation_factor = 2 - (climb_progress * 2)  # 1 to 0

            # Add some noise for realism
            noise = (i % 50) * 5 - 125  # ±125m variation

            elevation = base_elevation + (max_elevation - base_elevation) * elevation_factor + noise
            elevation = max(200, min(2800, elevation))  # Clamp between 200m and 2800m

            # Timestamp (3 minutes apart for realistic cycling pace)
            # ~4 months of riding data if continuous
            total_minutes = i * 3
            days = total_minutes // (24 * 60)
            hours = (total_minutes % (24 * 60)) // 60
            minutes = total_minutes % 60

            # Wrap days to valid date (June 1-30, 2024)
            day = (days % 30) + 1
            timestamp = f"2024-06-{day:02d}T{hours:02d}:{minutes:02d}:00Z"

            # Write trackpoint with minimal whitespace to save space
            f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}">\n')
            f.write(f"        <ele>{elevation:.1f}</ele>\n")
            f.write(f"        <time>{timestamp}</time>\n")
            f.write("      </trkpt>\n")

        print(f"{num_points:,} ✓")

        # Write GPX footer
        f.write("    </trkseg>\n")
        f.write("  </trk>\n")
        f.write("</gpx>\n")

    # Report file size
    file_size = output_path.stat().st_size
    size_mb = file_size / 1024 / 1024

    print(f"\n✓ Generated {output_path.name}")
    print(f"  Size: {file_size:,} bytes ({size_mb:.2f} MB)")
    print(f"  Trackpoints: {num_points:,}")

    if size_mb >= 10.0:
        print(f"  ✓ SUCCESS: File size ≥10 MB (required for T101)")
    else:
        print(f"  ⚠ WARNING: File size <10 MB (may need more trackpoints)")

    return file_size


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    output_file = script_dir / "long_route_10mb.gpx"

    print("=" * 60)
    print("GPX Extra-Large File Generator")
    print("Feature: 017-gps-trip-wizard (Phase 9)")
    print("Purpose: Performance testing (SC-002: <2s for 10MB files)")
    print("=" * 60)
    print()

    # Check if file already exists
    if output_file.exists():
        existing_size = output_file.stat().st_size / 1024 / 1024
        print(f"⚠ File already exists: {output_file.name} ({existing_size:.2f} MB)")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("Aborted.")
            exit(0)
        print()

    # Generate file (85,000 points to ensure >10MB)
    generate_xlarge_gpx(output_file, num_points=85000)

    print()
    print("=" * 60)
    print("Next Steps:")
    print("  1. Test GPX processing time:")
    print(f"     time curl -X POST http://localhost:8000/gpx/analyze \\")
    print(f"       -H 'Authorization: Bearer $TOKEN' \\")
    print(f"       -F 'file=@{output_file}' \\")
    print(f"       -o /dev/null -s -w '%{{time_total}}s\\n'")
    print()
    print("  2. Expected result: <2.000s (SC-002)")
    print("=" * 60)
