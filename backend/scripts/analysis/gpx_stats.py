import gpxpy
import sys
import os

def formatear_segundos(segundos):
    """Convierte segundos en un formato legible HH:MM:SS"""
    if segundos is None: return "00:00:00"
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"

def calcular_estadisticas(archivo_gpx):
    if not os.path.exists(archivo_gpx):
        print(f"Error: El archivo '{archivo_gpx}' no existe.")
        return

    with open(archivo_gpx, 'r') as f:
        gpx = gpxpy.parse(f)

    # 1. Cálculos de Distancia y Desniveles
    distancia_total = gpx.length_3d()
    subida_acumulada, bajada_acumulada = gpx.get_uphill_downhill()
    
    # 2. Obtener Altitudes Extreman (Máx/Mín)
    # gpx.get_elevation_extremes() devuelve un objeto con (minimum, maximum)
    extremes = gpx.get_elevation_extremes()
    alt_min = extremes.minimum if extremes.minimum is not None else 0
    alt_max = extremes.maximum if extremes.maximum is not None else 0
    
    # 3. Cálculos de Tiempo y Movimiento
    tiempo_total_seg = gpx.get_duration()
    datos_movimiento = gpx.get_moving_data()
    
    tiempo_mov_seg = datos_movimiento.moving_time
    tiempo_parado_seg = datos_movimiento.stopped_time
    distancia_mov = datos_movimiento.moving_distance
    
    # 4. Velocidad y Ritmo
    vel_media_mov = (distancia_mov / tiempo_mov_seg * 3.6) if tiempo_mov_seg > 0 else 0
    
    ritmo_str = "N/A"
    if vel_media_mov > 0:
        ritmo_decimal = 60 / vel_media_mov
        ritmo_str = f"{int(ritmo_decimal)}:{int((ritmo_decimal % 1) * 60):02d} min/km"

    # --- SALIDA DE DATOS ---
    print(f"\n" + "═"*45)
    print(f" 🛰️  ESTADÍSTICAS GPX: {os.path.basename(archivo_gpx)}")
    print(f"═"*45)
    print(f" DISTANCIA Y ALTITUD")
    print(f"  Distancia Total:      {distancia_total / 1000:.2f} km")
    print(f"  Altitud Máxima:       {alt_max:.1f} m")
    print(f"  Altitud Mínima:       {alt_min:.1f} m")
    print(f"  Desnivel Positivo:    {subida_acumulada:.1f} m")
    print(f"  Desnivel Negativo:    {bajada_acumulada:.1f} m")
    print(f"─" * 45)
    print(f" TIEMPOS")
    print(f"  Tiempo Total:         {formatear_segundos(tiempo_total_seg)}")
    print(f"  Tiempo en Movimiento: {formatear_segundos(tiempo_mov_seg)}")
    print(f"  Tiempo Detenido:      {formatear_segundos(tiempo_parado_seg)}")
    print(f"─" * 45)
    print(f" RENDIMIENTO")
    print(f"  Velocidad Media Mov.: {vel_media_mov:.2f} km/h")
    print(f"  Ritmo Medio Mov.:     {ritmo_str}")
    print(f"═"*45 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python gpx_stats.py ruta/al/archivo.gpx")
    else:
        calcular_estadisticas(sys.argv[1])