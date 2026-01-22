#!/usr/bin/env python3
"""Generate medium-sized GPX file (~500KB) for testing."""

from pathlib import Path


def generate_medium_gpx(output_path: Path, num_points: int = 2000):
    """Generate a medium GPX file (~500KB)."""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(
            '<gpx version="1.1" creator="ContraVento Test Suite" xmlns="http://www.topografix.com/GPX/1/1">\n'
        )
        f.write("  <metadata>\n")
        f.write("    <name>Camino del Cid</name>\n")
        f.write(f"    <desc>Medium test file with {num_points} trackpoints (~500KB)</desc>\n")
        f.write("  </metadata>\n")
        f.write("  <trk>\n")
        f.write("    <name>Camino del Cid - Burgos to Valencia</name>\n")
        f.write("    <trkseg>\n")

        # Camino del Cid route: Burgos to Valencia
        start_lat = 42.3439
        start_lon = -3.6969
        end_lat = 39.4699
        end_lon = -0.3763

        lat_step = (end_lat - start_lat) / num_points
        lon_step = (end_lon - start_lon) / num_points

        base_elevation = 850

        for i in range(num_points):
            lat = start_lat + (lat_step * i)
            lon = start_lon + (lon_step * i)

            # Elevation profile with realistic variation
            elevation_variation = 350 * ((i % 50) / 50)
            if (i // 50) % 2 == 0:
                elevation = base_elevation + elevation_variation
            else:
                elevation = base_elevation + 350 - elevation_variation

            hours = (i * 3) // 60
            minutes = (i * 3) % 60
            timestamp = f"2024-06-01T{hours:02d}:{minutes:02d}:00Z"

            f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}">\n')
            f.write(f"        <ele>{elevation:.1f}</ele>\n")
            f.write(f"        <time>{timestamp}</time>\n")
            f.write("      </trkpt>\n")

        f.write("    </trkseg>\n")
        f.write("  </trk>\n")
        f.write("</gpx>\n")

    file_size = output_path.stat().st_size
    print(f"Generated {output_path.name}: {file_size:,} bytes ({file_size / 1024:.1f} KB)")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    output_file = script_dir / "camino_del_cid.gpx"

    print("Generating medium GPX file...")
    generate_medium_gpx(output_file, num_points=2000)
    print(f"Successfully created {output_file}")
