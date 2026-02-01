# Scripts de Análisis GPS - Documentación Completa

Este documento describe en detalle los scripts de análisis para archivos GPX y estadísticas de rutas (RouteStatistics) en ContraVento.

## 📁 Estructura de Directorios

```
backend/scripts/
├── analysis/                           # Scripts Python de análisis
│   ├── analyze_gpx_segments.py         # Analiza segmentos (slow, long, STOP)
│   ├── analyze_slow_segments.py        # Histograma de duración de segmentos lentos
│   ├── analyze_gpx_timing.py           # Analiza espaciado entre puntos GPS
│   ├── gpx_stats.py                    # Estadísticas GPX usando gpxpy (referencia)
│   ├── app_gpx_stats.py                # Estadísticas GPX usando lógica de la app
│   ├── check_route_stats.py            # Verifica existencia de RouteStatistics
│   ├── recalculate_route_stats.py      # Recalcula RouteStatistics
│   └── delete_corrupt_stats.py         # Elimina RouteStatistics corruptas
│
└── wrappers/                           # Bash wrappers para ejecutar scripts
    ├── analyze-segments.sh             # Wrapper para analyze_gpx_segments.py
    ├── analyze-slow-segments.sh        # Wrapper para analyze_slow_segments.py
    ├── analyze-timing.sh               # Wrapper para analyze_gpx_timing.py
    ├── compare-gpx-stats.sh            # Compara gpxpy vs lógica de la app
    ├── check-stats.sh                  # Wrapper para check_route_stats.py
    ├── recalculate-stats.sh            # Wrapper para recalculate_route_stats.py
    └── delete-stats.sh                 # Wrapper para delete_corrupt_stats.py
```

---

## 📋 Scripts Migrados (6 de 6)

| # | Script Python | Bash Wrapper | Dual Mode | Funcionalidad |
|---|--------------|--------------|-----------|---------------|
| 1 | `analyze_gpx_segments.py` | `analyze-segments.sh` | ✅ Sí | Analiza segmentos (slow, long, STOP) para detectar patrones de paradas |
| 2 | `analyze_slow_segments.py` | `analyze-slow-segments.sh` | ✅ Sí | Genera histograma de duración de segmentos lentos (<3 km/h) |
| 3 | `analyze_gpx_timing.py` | `analyze-timing.sh` | ✅ Sí | Analiza espaciado entre puntos GPS (distance gaps) |
| 4 | `check_route_stats.py` | `check-stats.sh` | ❌ DB-only | Verifica existencia de RouteStatistics en la base de datos |
| 5 | `recalculate_route_stats.py` | `recalculate-stats.sh` | ❌ DB-only | Recalcula RouteStatistics para un GPX existente |
| 6 | `delete_corrupt_stats.py` | `delete-stats.sh` | ❌ DB-only | Elimina RouteStatistics corruptas o no deseadas |

### Leyenda de Modos

- **✅ Dual Mode**: Soporta dos modos de operación:
  - **Modo Database**: Lee GPX desde base de datos y storage
  - **Modo File Path**: Lee GPX directamente desde ruta especificada (no requiere DB)

- **❌ DB-only**: Solo opera con base de datos (requiere GPX en DB)

---

## 🚀 Ejemplos de Uso Completo

### 1. Análisis de Segmentos GPS

Analiza segmentos de un archivo GPX para entender patrones de paradas. Clasifica segmentos en tres categorías:

- **Slow segments**: velocidad < 3 km/h (cualquier duración)
- **Long segments**: duración > 2 minutos (cualquier velocidad)
- **STOP segments**: velocidad < 3 km/h Y duración > 2 minutos

#### Modo Database (desde GPX en DB):

```bash
cd backend
./scripts/wrappers/analyze-segments.sh 13e24f2f-f792-4873-b636-ad3568861514
```

#### Modo File Path (desde archivo local):

```bash
cd backend
./scripts/wrappers/analyze-segments.sh --file-path /tmp/my-route.gpx
```

#### Salida Esperada:

```
========================================
GPX Segment Analysis
========================================

Mode:        Database
GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
Timestamp:   2026-01-27 10:30:45

Running analysis...

Analyzing 1234 segments
===============================================================================
Total segments analyzed: 1234

SLOW SEGMENTS (speed < 3.0 km/h):              45 segments
LONG SEGMENTS (duration > 2.0 min):            23 segments
STOP SEGMENTS (speed < 3 km/h AND > 2 min):    12 segments

STOP SEGMENTS (paradas detectadas):
-------------------------------------------------------------------------------
  Segment  520 → 521:  duration=  3.5 min, speed=0.8 km/h, distance=0.045 km
  Segment  678 → 679:  duration=  2.8 min, speed=1.2 km/h, distance=0.052 km
  ...

✓ Analysis completed successfully
```

**Útil para**:
- Diagnosticar por qué `moving_time ≈ total_time` (no se detectan paradas)
- Verificar que el algoritmo de stop detection está funcionando
- Entender distribución de paradas en la ruta

---

### 2. Histograma de Segmentos Lentos

Genera un histograma de duración de segmentos lentos (<3 km/h). Clasifica en rangos:

- **0-30 segundos** (semáforos, cruces)
- **30-60 segundos** (semáforos largos)
- **1-2 minutos** (paradas breves)
- **2-5 minutos** (paradas cortas)
- **>5 minutos** (paradas largas)

#### Modo Database:

```bash
cd backend
./scripts/wrappers/analyze-slow-segments.sh 13e24f2f-f792-4873-b636-ad3568861514
```

#### Modo File Path:

```bash
cd backend
./scripts/wrappers/analyze-slow-segments.sh --file-path /tmp/CamarasAltas.gpx
```

#### Salida Esperada:

```
========================================
Slow Segments Duration Analysis
========================================

Mode:        Database
GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
Timestamp:   2026-01-27 10:35:12

Running analysis...

Analyzing slow segments (< 3 km/h) in 1234 GPS points
================================================================================

SLOW SEGMENTS ANALYSIS (speed < 3.0 km/h)
--------------------------------------------------------------------------------
Total slow segments:    45
Total slow time:        85.50 min (1.42 hours)
Average duration:       1.90 min (114.0 sec)
Maximum duration:       8.20 min (492.0 sec)
Minimum duration:       0.15 min (9.0 sec)

DURATION HISTOGRAM:
--------------------------------------------------------------------------------
  0-30 sec    :  18 segments ( 40.0%), total time:   7.50 min
  30-60 sec   :  12 segments ( 26.7%), total time:   9.80 min
  1-2 min     :   8 segments ( 17.8%), total time:  12.30 min
  2-5 min     :   5 segments ( 11.1%), total time:  18.70 min
  >5 min      :   2 segments (  4.4%), total time:  37.20 min

================================================================================

TOP 10 LONGEST SLOW SEGMENTS:
--------------------------------------------------------------------------------
  # 1:   8.20 min ( 492.0 sec), speed:  0.50 km/h, distance:   68.0 m
  # 2:   6.80 min ( 408.0 sec), speed:  1.20 km/h, distance:  136.0 m
  # 3:   4.50 min ( 270.0 sec), speed:  2.10 km/h, distance:  157.5 m
  ...

================================================================================

✓ Analysis completed successfully
```

**Útil para**:
- Entender distribución de paradas (semáforos vs paradas largas)
- Detectar paradas anómalas (>5 minutos puede indicar problemas)
- Validar thresholds de stop detection

---

### 3. Análisis de Espaciado GPS

Analiza el espaciado de distancia entre puntos GPS consecutivos. Útil para detectar:

- **Gaps grandes** (>0.5km) que pueden indicar datos perdidos
- **Densidad de puntos GPS** (avg distance/point)
- **Calidad del tracking GPS**

#### Modo Database:

```bash
cd backend
./scripts/wrappers/analyze-timing.sh 13e24f2f-f792-4873-b636-ad3568861514
```

#### Modo File Path:

```bash
cd backend
./scripts/wrappers/analyze-timing.sh --file-path /home/user/Downloads/route.gpx
```

#### Salida Esperada:

```
========================================
GPS Point Spacing Analysis
========================================

Mode:        Database
GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
Timestamp:   2026-01-27 10:40:28

Running analysis...

Analyzing 1234 GPS points from database
======================================================================

SAMPLE GPS POINT SPACING
----------------------------------------------------------------------
  Point    0 →    1: distance_gap=0.0125km, gradient=2.3%
  Point    1 →    2: distance_gap=0.0098km, gradient=1.8%
  Point    2 →    3: distance_gap=0.0112km, gradient=-0.5%
  ...
  Point 1230 → 1231: distance_gap=0.0105km, gradient=0.8%
  Point 1231 → 1232: distance_gap=0.0089km, gradient=-1.2%
  Point 1232 → 1233: distance_gap=0.0095km, gradient=0.3%

SUMMARY STATISTICS
----------------------------------------------------------------------
  Total points:        1234
  Total distance:      45.80 km

  Avg distance/point:  0.0371 km
  Min distance gap:    0.0012 km
  Max distance gap:    0.8500 km

  ⚠️  Large gaps (>0.5km): 2 found
     Largest gap:       0.8500 km

======================================================================

✓ Analysis completed successfully
```

**Útil para**:
- Detectar pérdida de señal GPS (gaps grandes)
- Validar calidad del tracking (avg distance/point bajo = buen tracking)
- Diagnosticar problemas con interpolación de datos

---

### 4. Verificar RouteStatistics

Consulta la base de datos para verificar si un GPX tiene estadísticas calculadas.

#### Uso (solo modo database):

```bash
cd backend
./scripts/wrappers/check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

#### Salida si EXISTE RouteStatistics:

```
========================================
RouteStatistics Existence Check
========================================

Mode:        Database
GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
Timestamp:   2026-01-27 10:45:15

Checking RouteStatistics...

[OK] RouteStatistics FOUND!
============================================================
Stats ID:        abc123-def456-ghi789
GPX File ID:     13e24f2f-f792-4873-b636-ad3568861514

[SPEED]
  Avg Speed:     18.5 km/h
  Max Speed:     42.3 km/h

[TIME]
  Total Time:    120.5 min
  Moving Time:   95.2 min

[GRADIENT]
  Avg Gradient:  2.3%
  Max Gradient:  12.5%

[CLIMBS]
  Top Climbs:    3 climbs found
    #1: 5.20-8.50 km, 180m gain, 5.5% gradient
    #2: 12.30-14.80 km, 120m gain, 4.8% gradient
    #3: 20.10-22.00 km, 95m gain, 5.0% gradient
============================================================

✓ Check completed successfully
```

#### Salida si NO EXISTE RouteStatistics:

```
[ERROR] RouteStatistics NOT FOUND
============================================================
GPX File ID:     13e24f2f-f792-4873-b636-ad3568861514

Reason:
  The GPX file was uploaded BEFORE RouteStatistics integration

Solution:
  1. Re-upload the GPX file (recommended)
  2. Or run backfill script to calculate statistics for existing files
============================================================

✓ Check completed successfully
```

**Útil para**:
- Verificar si un GPX antiguo tiene estadísticas
- Diagnosticar problemas con cálculo de estadísticas
- Validar que estadísticas se calcularon correctamente

---

### 5. Recalcular RouteStatistics

Recalcula las estadísticas de ruta para un GPX que ya está en la base de datos. Útil para:

- Actualizar estadísticas después de cambios en el algoritmo
- Corregir estadísticas incorrectas o corruptas
- Recalcular después de ajustes en los thresholds de stop detection
- Backfill de estadísticas para GPX subidos antes de la integración

#### Uso (solo modo database):

```bash
cd backend
./scripts/wrappers/recalculate-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

#### ⚠️ ADVERTENCIA

Este script **ELIMINA** el RouteStatistics existente y crea uno nuevo. NO es una actualización in-place.

#### Salida Esperada:

```
========================================
RouteStatistics Recalculation
========================================

Mode:        Database
GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
Timestamp:   2026-01-27 10:50:32

⚠️  WARNING: This will DELETE existing RouteStatistics and create a new one

Recalculating RouteStatistics...

[INFO] GPX File: 13e24f2f-f792-4873-b636-ad3568861514
       Distance: 45.8 km
       File URL: uploads/2024/01/route-abc123.gpx

[INFO] Read GPX file from storage (125487 bytes)

[INFO] Parsed GPX data:
       Total points: 1234
       Distance: 45.8 km
       Has timestamps: True
       Has elevation: True

[INFO] Calculating route statistics...

[INFO] Deleted existing RouteStatistics record

======================================================================
ROUTE STATISTICS CALCULATED
======================================================================

[SPEED]
  Avg Speed:     18.50 km/h
  Max Speed:     42.30 km/h

[TIME]
  Total Time:    2h 0min (120.50 min)
  Moving Time:   1h 35min (95.20 min)
  Stopped Time:  25.30 min (0.42 hours)
  Moving/Total:  79.0%

[GRADIENT]
  Avg Gradient:  2.3%
  Max Gradient:  12.5%

[CLIMBS]
  Climb #1:
    Start-End:       5.20 - 8.50 km
    Elevation Gain:  180 m
    Avg Gradient:    5.5%

  Climb #2:
    Start-End:       12.30 - 14.80 km
    Elevation Gain:  120 m
    Avg Gradient:    4.8%

  Climb #3:
    Start-End:       20.10 - 22.00 km
    Elevation Gain:  95 m
    Avg Gradient:    5.0%

======================================================================

[OK] RouteStatistics recalculated successfully!
     Stats ID: new-abc123-def456-ghi789

✓ Recalculation completed successfully
```

**Útil para**:
- Actualizar estadísticas después de fix en algoritmo de stop detection
- Corregir estadísticas con `moving_time > total_time`
- Backfill masivo de estadísticas para GPX antiguos

---

### 6. Eliminar RouteStatistics

Elimina el registro RouteStatistics de un GPX específico. Útil para:

- Eliminar estadísticas corruptas (`moving_time > total_time`)
- Limpiar estadísticas incorrectas antes de recalcular
- Eliminar estadísticas de GPX que serán re-procesados
- Preparar para backfill de estadísticas

#### Uso (solo modo database):

```bash
cd backend
./scripts/wrappers/delete-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

#### ⚠️ ADVERTENCIA

Esta es una operación **DESTRUCTIVA** sin opción de deshacer. El registro se elimina permanentemente de la base de datos.

#### Salida Esperada:

```
========================================
RouteStatistics Deletion
========================================

Mode:        Database
GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
Timestamp:   2026-01-27 10:55:48

⚠️  WARNING: This will PERMANENTLY DELETE RouteStatistics (no undo!)

Deleting RouteStatistics...

Found RouteStatistics:
  Stats ID: abc123-def456-ghi789
  GPX File ID: 13e24f2f-f792-4873-b636-ad3568861514
  Total Time: 120.5 min
  Moving Time: 95.2 min
  [ERROR] Moving time > Total time (corrupt data)

[OK] Corrupt RouteStatistics record deleted successfully

✓ Deletion completed successfully

Next steps:
  - To recreate statistics: ./scripts/wrappers/recalculate-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

**Útil para**:
- Preparar para recalcular estadísticas (workflow de corrección)
- Limpiar estadísticas de prueba
- Eliminar datos corruptos

---

## 📈 Comparación de Estadísticas GPX

### 7. Estadísticas GPX con gpxpy (Referencia)

Calcula estadísticas GPX usando directamente la librería `gpxpy` (implementación de referencia).

**Uso:**

```bash
cd backend
poetry run python scripts/analysis/gpx_stats.py <ruta-al-archivo.gpx>
```

**Ejemplo:**

```bash
poetry run python scripts/analysis/gpx_stats.py scripts/datos/QH_2013.gpx
```

**Salida Esperada:**

```
═════════════════════════════════════════════
 🛰️  ESTADÍSTICAS GPX: QH_2013.gpx
═════════════════════════════════════════════
 DISTANCIA Y ALTITUD
  Distancia Total:      196.78 km
  Altitud Máxima:       1764.3 m
  Altitud Mínima:       328.0 m
  Desnivel Positivo:    3641.1 m
  Desnivel Negativo:    3640.2 m
─────────────────────────────────────────────
 TIEMPOS
  Tiempo Total:         08:17:09
  Tiempo en Movimiento: 08:02:27
  Tiempo Detenido:      00:13:54
─────────────────────────────────────────────
 RENDIMIENTO
  Velocidad Media Mov.: 24.46 km/h
  Ritmo Medio Mov.:     2:27 min/km
═════════════════════════════════════════════
```

**Útil para:**
- Validar resultados de la aplicación contra implementación de referencia
- Verificar que gpxpy y nuestra lógica dan resultados similares
- Debugging de discrepancias en cálculos

---

### 8. Estadísticas GPX con Lógica de la App

Calcula estadísticas GPX usando la misma lógica que la aplicación (`GPXService` + `RouteStatsService`).

**Uso:**

```bash
cd backend
poetry run python scripts/analysis/app_gpx_stats.py <ruta-al-archivo.gpx>
```

**Ejemplo:**

```bash
poetry run python scripts/analysis/app_gpx_stats.py scripts/datos/QH_2013.gpx
```

**Salida Esperada:**

```
Parseando archivo GPX: scripts/datos/QH_2013.gpx
Procesados 1197 trackpoints (simplificados de 4471 originales)
Convertidos 4471 trackpoints para cálculo de estadísticas

═════════════════════════════════════════════
 🚴 ESTADÍSTICAS (Lógica App): QH_2013.gpx
═════════════════════════════════════════════
 DISTANCIA Y ALTITUD
  Distancia Total:      196.78 km
  Altitud Máxima:       1764.3 m
  Altitud Mínima:       328.0 m
  Desnivel Positivo:    3641.1 m
  Desnivel Negativo:    3640.2 m
─────────────────────────────────────────────
 TIEMPOS
  Tiempo Total:         08:17:09
  Tiempo en Movimiento: 08:03:15
  Tiempo Detenido:      00:13:54
─────────────────────────────────────────────
 RENDIMIENTO
  Velocidad Media Mov.: 24.43 km/h
  Velocidad Máxima:     68.50 km/h
  Ritmo Medio Mov.:     2:27 min/km
═════════════════════════════════════════════
```

**Diferencias esperadas con gpxpy:**
- ✅ Distancia total debe coincidir exactamente
- ✅ Tiempos deben ser similares (±2% diferencia aceptable)
- ✅ Velocidad media debe ser similar (±5% diferencia aceptable)
- ⚠️ Velocidad máxima puede diferir (nuestra app filtra outliers > 100 km/h)

**Útil para:**
- Validar que la lógica de la aplicación funciona correctamente
- Verificar impacto de cambios en algoritmos
- Debugging de problemas específicos de la aplicación

---

### 9. Comparación Lado a Lado (RECOMENDADO)

Ejecuta ambos scripts en paralelo para comparación visual directa.

**Uso:**

```bash
cd backend
./scripts/wrappers/compare-gpx-stats.sh <ruta-al-archivo.gpx>
```

**Ejemplo:**

```bash
./scripts/wrappers/compare-gpx-stats.sh scripts/datos/QH_2013.gpx
```

**Salida Esperada:**

```
========================================
GPX Statistics Comparison
========================================

File: scripts/datos/QH_2013.gpx
Timestamp: 2026-01-31 15:30:45

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. gpxpy Library (Reference)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... salida de gpx_stats.py ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. Application Logic (Our Implementation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... salida de app_gpx_stats.py ...]

========================================
✓ Comparison completed
========================================

Note: Small differences are expected due to:
  - Trackpoint simplification (Douglas-Peucker algorithm)
  - Different rounding/precision in calculations
  - GPS error filtering (our app filters outliers)

Key metrics to compare:
  - Moving time should be similar (±5%)
  - Average speed should be similar (±5%)
  - Total distance should match exactly
```

**Útil para:**
- Validación rápida de algoritmos tras cambios
- Verificar corrección de bugs en cálculos
- Documentar diferencias entre implementaciones
- Testing de regresión

---

## 🔄 Workflows Típicos

### Workflow 1: Diagnosticar Por Qué Moving Time ≈ Total Time

Cuando `moving_time_minutes` es casi igual a `total_time_minutes`, el algoritmo de stop detection puede no estar funcionando correctamente.

```bash
# 1. Analizar segmentos para ver qué está pasando
./scripts/wrappers/analyze-segments.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output esperado: Debería mostrar STOP SEGMENTS detectados.
# Si STOP SEGMENTS = 0, hay un problema con stop detection.

# 2. Ver histograma de duración de paradas
./scripts/wrappers/analyze-slow-segments.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output esperado: Histograma mostrando distribución de segmentos lentos.
# Si mayoría son 0-30 sec, puede que threshold de 2 min sea muy alto.

# 3. Verificar espaciado de puntos GPS (puede haber gaps grandes)
./scripts/wrappers/analyze-timing.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output esperado: Avg distance/point debería ser ~0.01-0.05 km.
# Si hay muchos gaps >0.5km, puede afectar detección de paradas.
```

**Posibles causas y soluciones**:

| Síntoma | Causa Probable | Solución |
|---------|---------------|----------|
| STOP segments = 0 | Threshold muy estricto | Revisar algoritmo (velocidad < 3 km/h Y duración > 2 min) |
| Muchos gaps >0.5km | Pérdida de señal GPS | Datos de mala calidad, considerar filtrar ruta |
| Avg distance/point muy alto | Pocos puntos GPS | Tracking GPS de baja frecuencia, datos válidos pero limitados |
| Moving time > Total time | Bug en algoritmo (ya corregido) | Usar workflow 2 para corregir |

---

### Workflow 2: Corregir RouteStatistics Corruptas

Cuando encuentras RouteStatistics con `moving_time > total_time` (datos corruptos):

```bash
# 1. Verificar estadísticas actuales
./scripts/wrappers/check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output: Confirma que RouteStatistics existe y muestra métricas.

# 2. Eliminar estadísticas corruptas
./scripts/wrappers/delete-stats.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output: Muestra registro antes de eliminar, confirma eliminación.

# 3. Recalcular estadísticas correctas
./scripts/wrappers/recalculate-stats.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output: Parsea GPX, calcula métricas, crea nuevo RouteStatistics.

# 4. Verificar que estadísticas nuevas son correctas
./scripts/wrappers/check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514

# Output: Confirma que moving_time <= total_time y métricas son razonables.
```

**Criterios de validación**:

- ✅ `moving_time_minutes <= total_time_minutes`
- ✅ `avg_speed_kmh` razonable (5-50 km/h para ciclismo)
- ✅ `max_speed_kmh` razonable (<100 km/h para ciclismo)
- ✅ `moving_time / total_time` ratio razonable (50-95%)

---

### Workflow 3: Analizar GPX Externo (Sin Subir a DB)

Para analizar un archivo GPX sin necesidad de subirlo a la base de datos:

```bash
# Descargar o copiar GPX a ubicación temporal
cp ~/Downloads/route.gpx /tmp/route.gpx

# Analizar segmentos
./scripts/wrappers/analyze-segments.sh --file-path /tmp/route.gpx

# Analizar segmentos lentos
./scripts/wrappers/analyze-slow-segments.sh --file-path /tmp/route.gpx

# Analizar espaciado GPS
./scripts/wrappers/analyze-timing.sh --file-path /tmp/route.gpx
```

**Ventajas**:

- ✅ No requiere subir GPX a base de datos
- ✅ Análisis rápido de archivos GPX externos
- ✅ Útil para validar calidad antes de importar
- ✅ Funciona con cualquier GPX bien formado

**Limitaciones**:

- ❌ No accede a RouteStatistics (no están calculadas)
- ❌ Scripts 4-6 (check/recalculate/delete) no funcionan

---

### Workflow 4: Backfill de RouteStatistics (Múltiples GPX)

Para procesar múltiples GPX files que no tienen estadísticas:

```bash
# Paso 1: Identificar GPX files sin estadísticas (SQL query manual)
# SELECT gpx_file_id FROM gpx_files
# WHERE gpx_file_id NOT IN (SELECT gpx_file_id FROM route_statistics)
# AND has_timestamps = true;

# Ejemplo de IDs: id1, id2, id3, ...

# Paso 2: Recalcular para cada uno
./scripts/wrappers/recalculate-stats.sh id1
./scripts/wrappers/recalculate-stats.sh id2
./scripts/wrappers/recalculate-stats.sh id3

# Paso 3: O usar un loop (más eficiente)
for id in id1 id2 id3; do
  echo "========================================="
  echo "Processing GPX: $id"
  echo "========================================="
  ./scripts/wrappers/recalculate-stats.sh "$id"
  echo ""
  echo "Waiting 2 seconds before next..."
  sleep 2
done

# Paso 4: Verificar resultados
for id in id1 id2 id3; do
  echo "Checking GPX: $id"
  ./scripts/wrappers/check-stats.sh "$id" | grep -E "(FOUND|NOT FOUND)"
done
```

**Recomendaciones**:

- 🔴 **CUIDADO**: Ejecutar en entorno de testing primero
- ⚠️ Añadir sleep entre GPX para no saturar I/O
- ✅ Hacer backup de base de datos antes de backfill masivo
- ✅ Ejecutar en horario de bajo tráfico (noche)
- ✅ Monitorear logs para detectar errores

---

## 🔧 Requisitos y Dependencias

### Scripts con Dual Mode (1-3):

#### Modo Database:

- ✅ GPX file debe estar en tabla `gpx_files`
- ✅ Archivo GPX debe existir en `storage_path + file_url`
- ✅ Para análisis de tiempo: GPX debe tener timestamps (`has_timestamps=true`)

#### Modo File Path:

- ✅ Ruta del archivo GPX válida y accesible
- ✅ Archivo GPX bien formado (XML válido)
- ✅ Para análisis de tiempo: GPX debe tener timestamps en trackpoints

### Scripts DB-only (4-6):

- ✅ GPX file debe estar en tabla `gpx_files` (para scripts 5-6)
- ✅ Archivo GPX debe existir en storage (para script 5)
- ✅ RouteStatistics debe existir en DB (para scripts 4 y 6)

### Software Requerido:

- Python 3.12+ con Poetry
- PostgreSQL (para scripts DB-only)
- Bash shell (Linux/Mac/WSL)
- Dependencias Python: SQLAlchemy, GPXService, RouteStatsService

---

## 📚 Referencia Rápida de Comandos

### Scripts de Análisis (Dual Mode):

```bash
# analyze_gpx_segments.py - Analizar segmentos (slow, long, STOP)
./scripts/wrappers/analyze-segments.sh <gpx_file_id>
./scripts/wrappers/analyze-segments.sh --file-path <ruta>

# analyze_slow_segments.py - Histograma de duración
./scripts/wrappers/analyze-slow-segments.sh <gpx_file_id>
./scripts/wrappers/analyze-slow-segments.sh --file-path <ruta>

# analyze_gpx_timing.py - Espaciado GPS
./scripts/wrappers/analyze-timing.sh <gpx_file_id>
./scripts/wrappers/analyze-timing.sh --file-path <ruta>
```

### Scripts de RouteStatistics (DB-only):

```bash
# check_route_stats.py - Verificar existencia
./scripts/wrappers/check-stats.sh <gpx_file_id>

# recalculate_route_stats.py - Recalcular estadísticas
./scripts/wrappers/recalculate-stats.sh <gpx_file_id>

# delete_corrupt_stats.py - Eliminar estadísticas
./scripts/wrappers/delete-stats.sh <gpx_file_id>
```

### Ejecutar Scripts Python Directamente:

```bash
cd backend

# Con argparse (modo estándar)
poetry run python scripts/analysis/analyze_gpx_segments.py <gpx_file_id>
poetry run python scripts/analysis/analyze_gpx_segments.py --file-path /tmp/file.gpx

# Ver ayuda
poetry run python scripts/analysis/analyze_gpx_segments.py --help
```

---

## 🐛 Troubleshooting

### Error: "GPX file not found in database"

**Causa**: El `gpx_file_id` no existe en la tabla `gpx_files`

**Solución**:

```bash
# Verificar que UUID es correcto
psql -d contravento -c "SELECT gpx_file_id, distance_km FROM gpx_files WHERE gpx_file_id = '<uuid>';"

# O usar modo --file-path si tienes el archivo
./scripts/wrappers/analyze-segments.sh --file-path /path/to/file.gpx
```

---

### Error: "File not found: /path/to/file.gpx"

**Causa**: La ruta del archivo no existe o no es accesible

**Solución**:

```bash
# Verificar que archivo existe
ls -lh /path/to/file.gpx

# Verificar permisos de lectura
chmod +r /path/to/file.gpx

# Usar ruta absoluta (no relativa)
./scripts/wrappers/analyze-segments.sh --file-path /home/user/Downloads/route.gpx
```

---

### Error: "GPX file has no timestamps"

**Causa**: El GPX no tiene timestamps en sus trackpoints

**Solución**:

- ❌ No puedes analizar métricas de tiempo (moving_time, stopped_time, avg_speed)
- ✅ Puedes analizar distancia y elevación solamente
- ℹ️ Considera re-exportar GPX desde Strava/Garmin con timestamps

---

### Warning: "Moving time > Total time (corrupt data)"

**Causa**: Bug en algoritmo de stop detection (ya corregido en versión actual)

**Solución**: Usa workflow 2 para corregir:

```bash
./scripts/wrappers/delete-stats.sh <gpx_file_id>
./scripts/wrappers/recalculate-stats.sh <gpx_file_id>
```

---

### No se detectan paradas (STOP segments = 0)

**ACTUALIZADO (2026-01-31)**: El algoritmo de detección de paradas ha sido mejorado para coincidir con gpxpy:

**Cambios aplicados:**
- ✅ Umbral de velocidad reducido: 3 km/h → **1 km/h** (matches gpxpy default)
- ✅ Eliminado requisito de duración mínima (antes: solo paradas > 2 min)
- ✅ Ahora cuenta CUALQUIER segmento < 1 km/h como tiempo detenido
- ✅ Resultados similares a gpxpy (±5% diferencia esperada)

**Causa posible (si aún hay problemas)**: GPX tiene gaps grandes (puntos espaciados > 0.5km)

**Solución**: Revisa output de `analyze-timing.sh`:

```bash
./scripts/wrappers/analyze-timing.sh <gpx_file_id>

# Si ves muchos gaps >0.5km, el GPX tiene mala calidad de datos
```

---

### Script bash no ejecuta (Linux/Mac)

**Causa**: Permisos de ejecución no configurados

**Solución**:

```bash
# Dar permisos de ejecución
chmod +x backend/scripts/wrappers/*.sh

# Verificar permisos
ls -lh backend/scripts/wrappers/
```

---

## 📝 Notas Adicionales

### 1. Documentación en Bash Wrappers

Todos los bash wrappers tienen documentación completa en sus headers. Ejecuta cualquier script sin argumentos para ver la ayuda:

```bash
./scripts/wrappers/analyze-segments.sh

# Output:
# Error: GPX file ID or --file-path is required
#
# Usage:
#   ./analyze-segments.sh <gpx_file_id>
#   ./analyze-segments.sh --file-path <ruta>
# ...
```

---

### 2. Validación de UUID

Los wrappers validan formato de UUID (regex pattern):

```bash
# UUID válido (continúa ejecución)
./scripts/wrappers/check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514

# UUID inválido (muestra warning pero continúa)
./scripts/wrappers/check-stats.sh invalid-uuid

# Output:
# Warning: 'invalid-uuid' doesn't look like a valid UUID
# Continuing anyway...
```

---

### 3. Colores en Output

Los wrappers usan colores para mejor legibilidad:

- 🟢 **Verde**: Operaciones exitosas, headers
- 🔴 **Rojo**: Errores
- 🟡 **Amarillo**: Advertencias (warnings)

---

### 4. Exit Codes

Todos los wrappers retornan exit codes estándar:

- `0`: Éxito
- `1`: Error (útil para scripts de automatización)

Ejemplo de uso en scripts:

```bash
if ./scripts/wrappers/check-stats.sh "$id"; then
  echo "✓ RouteStatistics exists"
else
  echo "✗ RouteStatistics missing, recalculating..."
  ./scripts/wrappers/recalculate-stats.sh "$id"
fi
```

---

### 5. Mejoras Aplicadas (Migración Completa)

Todos los scripts han sido actualizados con:

#### Scripts Python:

- ✅ Docstring de módulo completo (Usage, Args, Examples, Notes)
- ✅ Docstring de función con Args section
- ✅ argparse en lugar de sys.argv (parsing robusto)
- ✅ Dual mode support (database + file-path) en scripts de análisis
- ✅ Parámetro gpx_file_id opcional (nargs='?') en scripts dual-mode
- ✅ Validación mutua exclusiva de parámetros

#### Bash Wrappers:

- ✅ Header completo con DESCRIPCIÓN, USO, PARÁMETROS, EJEMPLOS, SALIDA, NOTAS, MODOS
- ✅ Validación de argumentos (obligatorio gpx_file_id o --file-path)
- ✅ Validación de UUID (regex pattern check)
- ✅ Colores (RED, GREEN, YELLOW) para mejor legibilidad
- ✅ Manejo de errores con exit codes
- ✅ Headers informativos mostrando modo de operación
- ✅ Warnings prominentes en scripts destructivos

---

## 📖 Documentación Relacionada

Para más información sobre el feature de GPS Routes y RouteStatistics, ver:

- **[specs/003-gps-routes/spec.md](../specs/003-gps-routes/spec.md)**: Especificación completa del feature
- **[specs/003-gps-routes/tasks.md](../specs/003-gps-routes/tasks.md)**: Lista de tareas de implementación
- **[backend/docs/api/ROUTE_STATISTICS.md](../docs/api/ROUTE_STATISTICS.md)**: Documentación de la API de RouteStatistics (si existe)
- **[backend/scripts/README.md](README.md)**: Índice general de todos los scripts backend

---

**Última actualización**: 2026-01-31
**Versión**: 1.1.0 (añadidos scripts de comparación gpxpy vs app logic)
**Autor**: ContraVento Team
