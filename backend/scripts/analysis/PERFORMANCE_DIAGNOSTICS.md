# Guía de Diagnóstico de Performance GPX

Documentación detallada del script `diagnose_gpx_performance.py` para entender qué se mide en cada paso y cómo interpretar los resultados.

## Índice

1. [Visión General](#visión-general)
2. [STEP 1: Parse GPX XML](#step-1-parse-gpx-xml)
3. [STEP 2: RDP Simplification](#step-2-rdp-simplification)
4. [STEP 3: GPXService Simplification](#step-3-gpxservice-simplification)
5. [STEP 4: Extract Telemetry Quick](#step-4-extract-telemetry-quick)
6. [Análisis de Bottlenecks](#análisis-de-bottlenecks)
7. [Interpretación de Resultados](#interpretación-de-resultados)
8. [Casos de Uso](#casos-de-uso)

---

## Visión General

El script `diagnose_gpx_performance.py` realiza un análisis **paso a paso** del procesamiento de archivos GPX para identificar dónde se invierte el tiempo de procesamiento.

### ¿Por qué 4 pasos separados?

Cada paso mide una operación específica de forma aislada para poder identificar exactamente dónde está el cuello de botella:

1. **STEP 1**: Parsing XML (lectura y parseo del archivo)
2. **STEP 2**: Simplificación con algoritmo RDP (reducción de puntos)
3. **STEP 3**: Simplificación del servicio (método usado en producción)
4. **STEP 4**: Flujo completo (extracción de telemetría)

---

## STEP 1: Parse GPX XML

### ¿Qué mide?

Tiempo que tarda la librería `gpxpy` en **parsear** (leer y convertir a objetos Python) el archivo XML del GPX.

### Código ejecutado

```python
start = time.perf_counter()
gpx = gpxpy.parse(file_content)
parse_time = time.perf_counter() - start
```

### Operaciones internas

1. **Lectura XML**: Convierte el string/bytes del archivo en estructura XML
2. **Validación del schema**: Verifica que sea un GPX válido
3. **Construcción de objetos**: Crea objetos `Track`, `Segment`, `TrackPoint` en memoria
4. **Extracción de metadatos**: Lee timestamps, elevaciones, coordenadas

### Salida

```
============================================================
STEP 1: Parse GPX XML
============================================================
✓ Parse time: 2.229s
✓ Original trackpoints: 85,000
```

### Interpretación

| Métrica | Significado |
|---------|-------------|
| **Parse time** | Tiempo que tarda gpxpy en leer el archivo |
| **Original trackpoints** | Número total de puntos GPS en el archivo original |

### ¿Cuándo es un problema?

- ⚠️ **Parse time > 2s**: El archivo es muy grande o gpxpy es lento para este tamaño
- ⚠️ **Parse time > 50% del tiempo total**: El parsing XML es el cuello de botella principal

### Soluciones si es bottleneck

1. **Cambiar de parser XML**:
   - Evaluar `lxml` (más rápido que gpxpy para archivos grandes)
   - Evaluar `defusedxml` (más seguro y potencialmente más rápido)

2. **Implementar streaming parsing**:
   - Procesar el GPX en chunks en lugar de cargarlo todo en memoria
   - Útil para archivos >50MB

3. **Limitar tamaño de entrada**:
   - Rechazar archivos >20MB en el endpoint
   - Advertir al usuario sobre archivos muy grandes

---

## STEP 2: RDP Simplification

### ¿Qué mide?

Tiempo que tarda el algoritmo **Ramer-Douglas-Peucker (RDP)** en simplificar los trackpoints eliminando puntos redundantes.

### Código ejecutado

```python
from rdp import rdp

coords = [(p.latitude, p.longitude) for p in points]
start = time.perf_counter()
simplified_coords = rdp(coords, epsilon=0.0001)
rdp_time = time.perf_counter() - start
```

### Operaciones internas

1. **Conversión a array**: Transforma `TrackPoint` objetos a tuplas `(lat, lon)`
2. **Algoritmo RDP**:
   - Calcula distancia perpendicular de cada punto a la línea recta entre inicio y fin
   - Si distancia < epsilon, elimina el punto
   - Recursivamente aplica a los subsegmentos
3. **Complejidad**: O(n²) en el peor caso, O(n log n) en promedio

### Parámetro epsilon

- **epsilon=0.0001**: Tolerancia en grados (≈11 metros en el ecuador)
- Valores más pequeños = más puntos preservados
- Valores más grandes = más simplificación

### Salida

```
============================================================
STEP 2: RDP Simplification (epsilon=0.0001)
============================================================
Coordinate array size: 85,000
✓ RDP time: 2.269s
✓ Simplified trackpoints: 2
✓ Reduction: 100.0%
```

### Interpretación

| Métrica | Significado | Rango Típico |
|---------|-------------|--------------|
| **Coordinate array size** | Puntos de entrada al algoritmo | 1,000 - 100,000 |
| **RDP time** | Tiempo de ejecución del algoritmo | 0.1s - 3s |
| **Simplified trackpoints** | Puntos que quedan después de simplificar | 100 - 1,000 |
| **Reduction** | % de puntos eliminados | 90% - 99.9% |

### ¿Cuándo es un problema?

- ⚠️ **RDP time > 2s**: El archivo tiene demasiados puntos originales
- ⚠️ **Reduction > 99.5%**: Simplificación excesiva (puede perder detalles de la ruta)
- ⚠️ **Reduction < 90%**: Simplificación insuficiente (mapa puede ser lento)
- ⚠️ **RDP time > 50% del tiempo total**: El algoritmo RDP es el cuello de botella

### Casos especiales

**Archivo de prueba 10MB (ruta recta):**
```
✓ Original trackpoints: 85,000
✓ Simplified trackpoints: 2
✓ Reduction: 100.0%
```
- **Causa**: El archivo genera una ruta casi recta (Atlántico → Mediterráneo)
- **Resultado**: RDP elimina todos los puntos intermedios porque están en línea recta
- **Impacto**: No es representativo de rutas reales con curvas

**Archivo real (QH_2013.gpx):**
```
✓ Original trackpoints: 4,471
✓ Simplified trackpoints: 1,197
✓ Reduction: 73.2%
```
- **Causa**: Ruta real con curvas y cambios de dirección
- **Resultado**: RDP preserva ~1,200 puntos para mantener la forma de la ruta
- **Impacto**: Representa el comportamiento real del algoritmo

### Soluciones si es bottleneck

1. **Aumentar epsilon**:
   - Cambiar de `0.0001` a `0.0002` (reduce iteraciones)
   - Trade-off: Menos precisión en el trazado

2. **Pre-filtrar puntos muy cercanos**:
   - Eliminar puntos a <5 metros antes de RDP
   - Reduce el tamaño del input al algoritmo

3. **Implementar RDP multithread**:
   - Dividir los trackpoints en chunks
   - Simplificar cada chunk en paralelo
   - Combinar resultados

4. **Limitar puntos de entrada**:
   - Advertir si GPX >50,000 puntos
   - Rechazar si GPX >100,000 puntos

---

## STEP 3: GPXService Simplification

### ¿Qué mide?

Tiempo que tarda el método **`_simplify_track_optimized()`** del `GPXService` en simplificar trackpoints. Este es el método usado en **producción**.

### Código ejecutado

```python
gpx_service = GPXService(db)
start = time.perf_counter()
simplified = gpx_service._simplify_track_optimized(points, epsilon=0.0001)
service_time = time.perf_counter() - start
```

### Operaciones internas

1. **Conversión a coordenadas**: Similar a STEP 2
2. **RDP simplification**: Llama al mismo algoritmo RDP
3. **Cálculo de distancias acumuladas**: Para cada punto simplificado
4. **Cálculo de gradientes**: Entre puntos consecutivos (slope %)
5. **Construcción de diccionarios**: Retorna lista de `dict` con todos los campos

### Diferencia con STEP 2

| Aspecto | STEP 2 | STEP 3 |
|---------|--------|--------|
| **Input** | Raw coordinates `[(lat, lon)]` | TrackPoint objects |
| **Output** | Simplified coordinates `[(lat, lon)]` | Full trackpoint dicts con metadatos |
| **Procesamiento** | Solo RDP | RDP + distancias + gradientes |
| **Uso** | Benchmarking aislado | Producción real |

### Salida

```
============================================================
STEP 3: GPXService._simplify_track_optimized
============================================================
✓ Service simplification time: 1.390s
✓ Simplified trackpoints: 1,197

First 3 simplified points:
  0: lat=42.505509, lon=-0.358096, dist=0.00km, elev=772.6
  1: lat=42.505746, lon=-0.358521, dist=0.04km, elev=770.7
  2: lat=42.510119, lon=-0.356067, dist=0.57km, elev=766.3
```

### Interpretación

| Métrica | Significado |
|---------|-------------|
| **Service simplification time** | Tiempo del método usado en producción |
| **Simplified trackpoints** | Mismo resultado que STEP 2 |
| **First 3 points** | Muestra de datos procesados con todos los campos |

### ¿Por qué service_time ≈ rdp_time?

Si `service_time` es **muy similar** a `rdp_time`, significa que:
- ✅ El overhead del servicio es mínimo
- ✅ El cálculo de distancias y gradientes es rápido
- ✅ El RDP es el 95%+ del tiempo del método

### ¿Cuándo service_time >> rdp_time?

Si `service_time` es **mucho mayor** que `rdp_time` (ej: 3s vs 1s):
- ⚠️ El cálculo de distancias/gradientes es lento
- ⚠️ Hay demasiadas operaciones adicionales
- ⚠️ Posible problema en la construcción de diccionarios

---

## STEP 4: Extract Telemetry Quick

### ¿Qué mide?

Tiempo del **flujo completo** de extracción de telemetría que se ejecuta en producción cuando un usuario sube un GPX.

### Código ejecutado

```python
gpx_service = GPXService(db)
start = time.perf_counter()
result = await gpx_service.extract_telemetry_quick(
    file_content, include_trackpoints=True
)
total_time = time.perf_counter() - start
```

### Operaciones internas

Este método realiza **todas** las operaciones de procesamiento GPX:

1. **Parse GPX** (similar a STEP 1)
2. **Validar GPX**: Verificar que tenga tracks y puntos
3. **Calcular estadísticas básicas**:
   - Distancia total (km)
   - Elevación ganada/perdida (m)
   - Elevación máxima/mínima (m)
4. **Validar elevaciones**: Rechazar si fuera de rango (-420m a 8850m)
5. **Calcular dificultad**: Basado en distancia y elevación ganada
6. **Simplificar trackpoints** (similar a STEP 3)
7. **Extraer timestamps**: start_date, end_date
8. **Detectar capacidades**: has_elevation, has_timestamps
9. **Construir respuesta**: Dict con todos los campos

### Salida

```
============================================================
STEP 4: extract_telemetry_quick (full workflow)
============================================================
✓ Total time: 1.634s
✓ Distance: 196.15 km
✓ Elevation gain: 3709.5 m
✓ Trackpoints in result: 1,197
```

### Interpretación

| Métrica | Significado |
|---------|-------------|
| **Total time** | Tiempo del flujo completo (lo que ve el usuario) |
| **Distance** | Distancia total calculada de la ruta |
| **Elevation gain** | Subida acumulada (suma de tramos ascendentes) |
| **Trackpoints in result** | Puntos simplificados retornados al frontend |

### Validación SC-002

Esta es la métrica **crítica** para validar el Success Criteria 002:

```
SC-002: GPX processing <2s for files ≥10MB
```

**Resultado para archivo 10MB:**
```
✗ SC-002 FAIL: 10MB+ file processed in 4.960s (>2s target)
```

**Resultado para archivo 1.2MB:**
```
✓ Processing time: 1.634s (<2s)
ℹ  File size 1.23MB - SC-002 not applicable (requires ≥10MB)
```

### ¿Cuándo es un problema?

- ❌ **total_time > 2s** para archivos ≥10MB: No cumple SC-002
- ⚠️ **total_time > 5s**: Usuario puede abandonar la operación
- ⚠️ **total_time >> (parse_time + rdp_time)**: Hay overhead oculto

---

## Análisis de Bottlenecks

### ¿Qué mide?

Distribución porcentual del tiempo entre las 3 operaciones principales:

```python
other_time = total_time - parse_time - rdp_time
print(f"XML parsing:        {parse_time:.3f}s ({parse_time/total_time*100:.1f}%)")
print(f"RDP algorithm:      {rdp_time:.3f}s ({rdp_time/total_time*100:.1f}%)")
print(f"Other operations:   {other_time:.3f}s ({other_time/total_time*100:.1f}%)")
```

### Salida (archivo 10MB)

```
============================================================
BOTTLENECK ANALYSIS
============================================================
XML parsing:        2.229s (44.9%)
RDP algorithm:      2.269s (45.7%)
Other operations:   0.462s (9.3%)
```

### Salida (archivo 1.2MB)

```
============================================================
BOTTLENECK ANALYSIS
============================================================
XML parsing:        0.208s (12.8%)
RDP algorithm:      1.380s (84.5%)
Other operations:   0.045s (2.8%)
```

### Interpretación

| Componente | % Tiempo | Interpretación |
|------------|----------|----------------|
| **XML parsing** | >40% | Parser XML es lento, considerar alternativa (lxml) |
| **RDP algorithm** | >40% | Algoritmo de simplificación es lento, optimizar |
| **Other operations** | >15% | Hay operaciones lentas fuera de parsing/RDP |

### Patrones comunes

**Archivo grande (10MB+):**
- XML parsing y RDP equilibrados (45% cada uno)
- Ambos son cuellos de botella
- Optimizar los dos tiene impacto significativo

**Archivo normal (1-5MB):**
- RDP domina (70-85%)
- Parsing es rápido (10-20%)
- Optimizar RDP tiene mayor impacto

**Archivo pequeño (<500KB):**
- "Other operations" puede ser >20%
- Overhead relativo es mayor
- No es prioritario optimizar

---

## Interpretación de Resultados

### Escenario 1: Archivo Grande (≥10MB) - SC-002 FAIL

```
File size: 10.38 MB
Parse time: 2.229s (44.9%)
RDP time: 2.269s (45.7%)
Total time: 4.960s
✗ SC-002 FAIL: 10MB+ file processed in 4.960s (>2s target)
```

**Diagnóstico:**
- ❌ No cumple SC-002 (objetivo: <2s)
- ⚠️ Parsing y RDP son igualmente lentos
- ⚠️ Se necesitan optimizaciones en ambos componentes

**Acciones recomendadas:**

1. **Corto plazo** (workaround):
   - Documentar limitación conocida ✅
   - Actualizar SC-002 a ~5s o marcar como "futuro enhancement"
   - Advertir usuarios sobre archivos >10MB

2. **Medio plazo** (optimizaciones):
   - Cambiar parser: Evaluar `lxml` (puede reducir parsing a ~1s)
   - Optimizar RDP: Aumentar epsilon a 0.0002 (reduce iteraciones)
   - Pre-filtrado: Eliminar puntos <5m antes de RDP

3. **Largo plazo** (arquitectura):
   - Processing en background (retornar respuesta inmediata, procesar async)
   - Cache de telemetría (almacenar hash del archivo)

### Escenario 2: Archivo Normal (1-5MB) - OK

```
File size: 1.23 MB
Parse time: 0.208s (12.8%)
RDP time: 1.380s (84.5%)
Total time: 1.634s
✓ Processing time: 1.634s (<2s)
```

**Diagnóstico:**
- ✅ Performance aceptable (<2s)
- ✅ Parsing es rápido (XML pequeño)
- ⚠️ RDP domina el tiempo (84.5%)
- ℹ️ Ruta real con curvas (73.2% reducción vs 100% del archivo de prueba)

**Interpretación:**
- Para archivos normales (<5MB), el sistema funciona bien
- RDP es el único cuello de botella, pero está dentro del objetivo
- Si se optimiza RDP, se podría reducir a <1s

### Escenario 3: Overhead Excesivo

```
Parse time: 0.500s (20%)
RDP time: 0.600s (24%)
Other operations: 1.400s (56%)
Total time: 2.500s
```

**Diagnóstico:**
- ⚠️ "Other operations" es >50% del tiempo
- ⚠️ Hay operaciones lentas no identificadas
- 🔍 Requiere profiling adicional

**Posibles causas:**
- Cálculos de distancia/elevación lentos
- Validaciones complejas
- I/O de base de datos
- Construcción de objetos ineficiente

**Cómo investigar:**
- Agregar timers adicionales en `extract_telemetry_quick()`
- Usar profiler Python (`cProfile`, `line_profiler`)
- Revisar logs de base de datos

---

## Casos de Uso

### Caso 1: Validar SC-002 con archivo de prueba

```bash
poetry run python scripts/analysis/diagnose_gpx_performance.py \
  tests/fixtures/gpx/long_route_10mb.gpx
```

**Objetivo**: Verificar si cumplimos el Success Criteria 002

**Qué buscar:**
- ✓/✗ en la línea "SC-002 PASS/FAIL"
- Tiempo total vs objetivo de 2s
- Identificar cuál componente es más lento

### Caso 2: Comparar performance entre archivos

```bash
# Archivo pequeño
poetry run python scripts/analysis/diagnose_gpx_performance.py \
  tests/fixtures/gpx/short_route.gpx

# Archivo mediano
poetry run python scripts/analysis/diagnose_gpx_performance.py \
  scripts/datos/QH_2013.gpx

# Archivo grande
poetry run python scripts/analysis/diagnose_gpx_performance.py \
  tests/fixtures/gpx/long_route_10mb.gpx
```

**Objetivo**: Entender cómo escala el performance con el tamaño

**Qué buscar:**
- Relación entre tamaño de archivo y tiempo de procesamiento
- Si el bottleneck cambia según el tamaño
- Punto de quiebre donde performance se degrada

### Caso 3: Antes/después de optimización

```bash
# ANTES de optimizar
poetry run python scripts/analysis/diagnose_gpx_performance.py archivo.gpx > before.txt

# ... hacer cambios en el código ...

# DESPUÉS de optimizar
poetry run python scripts/analysis/diagnose_gpx_performance.py archivo.gpx > after.txt

# Comparar
diff before.txt after.txt
```

**Objetivo**: Medir impacto de optimizaciones

**Qué buscar:**
- Reducción en parse_time si cambiamos parser
- Reducción en rdp_time si optimizamos algoritmo
- Reducción en total_time (objetivo final)

### Caso 4: Diagnóstico de archivo del usuario

Usuario reporta: "Mi GPX tarda mucho en subirse"

```bash
# Pedir al usuario el archivo
poetry run python scripts/analysis/diagnose_gpx_performance.py \
  /path/to/user/file.gpx
```

**Objetivo**: Identificar si es problema del archivo o del sistema

**Qué buscar:**
- Tamaño del archivo (¿>10MB?)
- Número de trackpoints originales (¿>100,000?)
- Distribución de bottlenecks
- Si es similar a archivos de prueba o es un caso especial

---

## Fórmulas y Cálculos

### Cálculo de Porcentajes

```
% XML parsing = (parse_time / total_time) × 100
% RDP algorithm = (rdp_time / total_time) × 100
% Other operations = ((total_time - parse_time - rdp_time) / total_time) × 100
```

**Validación**: Los 3 porcentajes deben sumar ≈100%

### Reducción de Trackpoints

```
Reduction % = (1 - simplified_points / original_points) × 100
```

**Ejemplos:**
- 10,000 → 1,000 puntos: `(1 - 1000/10000) × 100 = 90%`
- 85,000 → 2 puntos: `(1 - 2/85000) × 100 = 99.998%`

### Throughput (trackpoints/segundo)

```
Throughput = original_points / rdp_time
```

**Ejemplo:**
- 85,000 puntos en 2.269s: `85000 / 2.269 = 37,457 pts/s`
- Útil para comparar performance entre versiones

---

## Glosario

| Término | Definición |
|---------|------------|
| **Bottleneck** | Componente que limita el performance general del sistema |
| **Epsilon** | Tolerancia del algoritmo RDP en grados (≈11m por 0.0001°) |
| **Trackpoint** | Punto GPS con coordenadas (lat, lon, elevation, timestamp) |
| **RDP** | Ramer-Douglas-Peucker, algoritmo de simplificación de líneas |
| **Telemetry** | Metadatos extraídos del GPX (distancia, elevación, dificultad) |
| **SC-002** | Success Criteria 002: GPX processing <2s for 10MB+ files |
| **Overhead** | Tiempo consumido por operaciones auxiliares (no core) |
| **Throughput** | Cantidad de datos procesados por unidad de tiempo |

---

## Referencias

- **Script**: [diagnose_gpx_performance.py](diagnose_gpx_performance.py)
- **Service**: [backend/src/services/gpx_service.py](../../src/services/gpx_service.py)
- **Spec**: [specs/017-gps-trip-wizard/spec.md](../../../specs/017-gps-trip-wizard/spec.md)
- **RDP Algorithm**: [rdp PyPI](https://pypi.org/project/rdp/)
- **gpxpy Library**: [gpxpy GitHub](https://github.com/tkrajina/gpxpy)

---

**Última actualización**: 2026-02-01
**Feature**: 017-gps-trip-wizard
**Versión**: 1.0.0
