#!/usr/bin/env python3
"""
Generate a large GPX file (5MB) for performance testing.
Target: ~15,000 trackpoints to reach 5MB file size.
"""

from pathlib import Path


def generate_large_gpx(output_path: Path, num_points: int = 40000):
    """Generate a large GPX file with specified number of points."""

    with open(output_path, 'w', encoding='utf-8') as f:
        # Write GPX header
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="ContraVento Test Generator" xmlns="http://www.topografix.com/GPX/1/1">\n')
        f.write('  <metadata>\n')
        f.write('    <name>Large Test Route - 5MB</name>\n')
        f.write(f'    <desc>Performance test file with {num_points} trackpoints</desc>\n')
        f.write('  </metadata>\n')
        f.write('  <trk>\n')
        f.write('    <name>Camino del Cid Complete - Large File Test</name>\n')
        f.write('    <trkseg>\n')

        # Generate trackpoints
        # Simulate Camino del Cid route: Burgos (42.3439°N, 3.6969°W) to Valencia (39.4699°N, 0.3763°W)
        start_lat = 42.3439
        start_lon = -3.6969
        end_lat = 39.4699
        end_lon = -0.3763

        lat_step = (end_lat - start_lat) / num_points
        lon_step = (end_lon - start_lon) / num_points

        base_elevation = 800  # Starting elevation in meters

        for i in range(num_points):
            lat = start_lat + (lat_step * i)
            lon = start_lon + (lon_step * i)

            # Simulate elevation changes (up and down hills)
            elevation_variation = 200 * ((i % 100) / 100)  # +200m every 100 points
            if (i // 100) % 2 == 0:  # Alternate climbing and descending
                elevation = base_elevation + elevation_variation
            else:
                elevation = base_elevation + 200 - elevation_variation

            # Timestamp (5 minutes apart)
            hours = (i * 5) // 60
            minutes = (i * 5) % 60
            timestamp = f'2024-06-01T{hours:02d}:{minutes:02d}:00Z'

            f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}">\n')
            f.write(f'        <ele>{elevation:.1f}</ele>\n')
            f.write(f'        <time>{timestamp}</time>\n')
            f.write('      </trkpt>\n')

        # Write GPX footer
        f.write('    </trkseg>\n')
        f.write('  </trk>\n')
        f.write('</gpx>\n')

    # Report file size
    file_size = output_path.stat().st_size
    print(f"Generated {output_path.name}: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")


if __name__ == '__main__':
    script_dir = Path(__file__).parent
    output_file = script_dir / 'long_route_5mb.gpx'

    print("Generating large GPX file for performance testing...")
    generate_large_gpx(output_file, num_points=40000)
    print(f"Successfully created {output_file}")
