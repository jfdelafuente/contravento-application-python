"""
GPX Statistics Calculator using Application Logic.

This script calculates GPX statistics using the same algorithms as the application
(GPXService + RouteStatsService) for comparison with gpxpy's native methods.

Usage:
    poetry run python scripts/analysis/app_gpx_stats.py <path-to-gpx-file>

Example:
    poetry run python scripts/analysis/app_gpx_stats.py scripts/datos/QH_2013.gpx
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.gpx_service import GPXService
from src.services.route_stats_service import RouteStatsService
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def formatear_segundos(segundos):
    """Convierte segundos en un formato legible HH:MM:SS"""
    if segundos is None:
        return "00:00:00"
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


async def calcular_estadisticas_app(archivo_gpx: str):
    """
    Calcula estadísticas GPX usando la lógica de la aplicación.

    Args:
        archivo_gpx: Ruta al archivo GPX
    """
    if not os.path.exists(archivo_gpx):
        print(f"Error: El archivo '{archivo_gpx}' no existe.")
        return

    # Create temporary in-memory database session (not used but required for service init)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Initialize services
        gpx_service = GPXService(session)
        stats_service = RouteStatsService(session)

        # Parse GPX file
        print(f"Parseando archivo GPX: {archivo_gpx}")
        with open(archivo_gpx, "rb") as f:
            gpx_content = f.read()

        # Parse GPX (get simplified trackpoints)
        try:
            analysis_result = await gpx_service.parse_gpx_file(gpx_content)
        except ValueError as e:
            print(f"Error: GPX inválido - {str(e)}")
            return
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return

        trackpoints = analysis_result["trackpoints"]
        original_points = analysis_result["original_points"]
        print(f"Procesados {len(trackpoints)} trackpoints (simplificados de {len(original_points)} originales)")

        # Extract basic metrics from analysis
        total_distance_km = analysis_result["distance_km"]
        elevation_gain_m = analysis_result["elevation_gain"]
        elevation_loss_m = analysis_result["elevation_loss"]
        alt_min = analysis_result["min_elevation"]
        alt_max = analysis_result["max_elevation"]

        # Convert original points to stats format (includes timestamps)
        stats_trackpoints = gpx_service.convert_points_for_stats(original_points)
        print(f"Convertidos {len(stats_trackpoints)} trackpoints para cálculo de estadísticas")

        # Calculate speed and time metrics using RouteStatsService
        speed_metrics = await stats_service.calculate_speed_metrics(stats_trackpoints)

        avg_speed_kmh = speed_metrics["avg_speed_kmh"]
        max_speed_kmh = speed_metrics["max_speed_kmh"]
        total_time_minutes = speed_metrics["total_time_minutes"]
        moving_time_minutes = speed_metrics["moving_time_minutes"]

        # Calculate stopped time
        stopped_time_minutes = None
        if total_time_minutes is not None and moving_time_minutes is not None:
            stopped_time_minutes = total_time_minutes - moving_time_minutes

        # Calculate pace (min/km)
        ritmo_str = "N/A"
        if avg_speed_kmh and avg_speed_kmh > 0:
            ritmo_decimal = 60 / avg_speed_kmh
            ritmo_str = f"{int(ritmo_decimal)}:{int((ritmo_decimal % 1) * 60):02d} min/km"

        # --- OUTPUT ---
        print(f"\n" + "═" * 45)
        print(f" 🚴 ESTADÍSTICAS (Lógica App): {os.path.basename(archivo_gpx)}")
        print(f"═" * 45)
        print(f" DISTANCIA Y ALTITUD")
        print(f"  Distancia Total:      {total_distance_km:.2f} km")
        if alt_max is not None and alt_min is not None:
            print(f"  Altitud Máxima:       {alt_max:.1f} m")
            print(f"  Altitud Mínima:       {alt_min:.1f} m")
        else:
            print(f"  Altitud Máxima:       N/A (sin datos de elevación)")
            print(f"  Altitud Mínima:       N/A")
        if elevation_gain_m is not None:
            print(f"  Desnivel Positivo:    {elevation_gain_m:.1f} m")
            print(f"  Desnivel Negativo:    {elevation_loss_m:.1f} m")
        else:
            print(f"  Desnivel Positivo:    N/A")
            print(f"  Desnivel Negativo:    N/A")
        print(f"─" * 45)
        print(f" TIEMPOS")
        if total_time_minutes is not None:
            print(f"  Tiempo Total:         {formatear_segundos(total_time_minutes * 60)}")
            print(f"  Tiempo en Movimiento: {formatear_segundos(moving_time_minutes * 60)}")
            print(f"  Tiempo Detenido:      {formatear_segundos(stopped_time_minutes * 60)}")
        else:
            print(f"  Tiempo Total:         N/A (sin timestamps)")
            print(f"  Tiempo en Movimiento: N/A")
            print(f"  Tiempo Detenido:      N/A")
        print(f"─" * 45)
        print(f" RENDIMIENTO")
        if avg_speed_kmh is not None:
            print(f"  Velocidad Media Mov.: {avg_speed_kmh:.2f} km/h")
            print(f"  Velocidad Máxima:     {max_speed_kmh:.2f} km/h" if max_speed_kmh else "  Velocidad Máxima:     N/A")
            print(f"  Ritmo Medio Mov.:     {ritmo_str}")
        else:
            print(f"  Velocidad Media Mov.: N/A (sin timestamps)")
            print(f"  Velocidad Máxima:     N/A")
            print(f"  Ritmo Medio Mov.:     N/A")
        print(f"═" * 45 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: poetry run python scripts/analysis/app_gpx_stats.py ruta/al/archivo.gpx")
        print("\nEjemplo:")
        print("  poetry run python scripts/analysis/app_gpx_stats.py scripts/datos/QH_2013.gpx")
        sys.exit(1)

    archivo_gpx = sys.argv[1]
    asyncio.run(calcular_estadisticas_app(archivo_gpx))
