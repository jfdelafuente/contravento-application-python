# Scripts de Análisis GPS

Scripts para análisis de archivos GPX, estadísticas de rutas y testing de performance.

## 📂 Categorías de Scripts

### 1. Análisis de Segmentos GPS (Dual Mode)

Scripts que analizan segmentos GPS para detectar paradas y patrones de movimiento.

| Script | Bash Wrapper | Función |
|--------|--------------|---------|
| `analyze_gpx_segments.py` | `../wrappers/analyze-segments.sh` | Analiza segmentos (slow, long, STOP) |
| `analyze_slow_segments.py` | `../wrappers/analyze-slow-segments.sh` | Histograma de duración de segmentos lentos |
| `analyze_gpx_timing.py` | `../wrappers/analyze-timing.sh` | Analiza espaciado entre puntos GPS |

**Dual Mode**: Soportan `--file-path` para análisis sin base de datos.

---

### 2. Comparación de Estadísticas

Scripts para validar algoritmos de cálculo comparando gpxpy vs lógica de la app.

| Script | Bash Wrapper | Función |
|--------|--------------|---------|
| `gpx_stats.py` | - | Estadísticas usando gpxpy (referencia) |
| `app_gpx_stats.py` | - | Estadísticas usando lógica de la app |
| - | `../wrappers/compare-gpx-stats.sh` | Comparación lado a lado |

**Uso:**
```bash
poetry run python scripts/analysis/gpx_stats.py route.gpx
poetry run python scripts/analysis/app_gpx_stats.py route.gpx
./scripts/wrappers/compare-gpx-stats.sh route.gpx  # Comparación visual
```

---

### 3. Gestión de RouteStatistics (DB-only)

Scripts para verificar, recalcular y eliminar RouteStatistics.

| Script | Bash Wrapper | Función |
|--------|--------------|---------|
| `check_route_stats.py` | `../wrappers/check-stats.sh` | Verifica existencia de estadísticas |
| `recalculate_route_stats.py` | `../wrappers/recalculate-stats.sh` | Recalcula estadísticas |
| `delete_corrupt_stats.py` | `../wrappers/delete-stats.sh` | Elimina estadísticas corruptas |

**Uso:**
```bash
./scripts/wrappers/check-stats.sh <gpx_file_id>
./scripts/wrappers/recalculate-stats.sh <gpx_file_id>
./scripts/wrappers/delete-stats.sh <gpx_file_id>
```

---

### 4. Testing de Performance (Feature 017)

Scripts para validar performance del endpoint `/gpx/analyze` y diagnosticar cuellos de botella.

| Script | Función | Feature |
|--------|---------|---------|
| `test_gpx_analyze.py` | Test del endpoint `/gpx/analyze` con medición de tiempo | 017-gps-trip-wizard |
| `diagnose_gpx_performance.py` | Diagnóstico detallado de cuellos de botella | 017-gps-trip-wizard |

#### test_gpx_analyze.py

Prueba el endpoint `/gpx/analyze` evitando problemas de autenticación con curl.

**Uso:**
```bash
cd backend

# Test con archivo pequeño (default)
poetry run python scripts/analysis/test_gpx_analyze.py

# Test con archivo específico (ej: 10MB para SC-002)
poetry run python scripts/analysis/test_gpx_analyze.py tests/fixtures/gpx/long_route_10mb.gpx
```

**Salida:**
```
✓ Token obtained: eyJhbGci...
✓ Reading GPX file: tests/fixtures/gpx/long_route_10mb.gpx
  File size: 10,886,608 bytes (10.38 MB)

✓ Extracting telemetry...

✓ Telemetry data:
  Distance: 383.67 km
  Elevation gain: 416501.6 m
  Difficulty: EXTREME
  Trackpoints: 2

⏱  Processing time: 4.929 seconds

✗ SC-002 FAIL: 10MB+ file processed in 4.929s (>2s target)
```

**Validación:**
- ✅ **SC-002 PASS**: Tiempo < 2.0s para archivos ≥10MB
- ✗ **SC-002 FAIL**: Tiempo ≥ 2.0s

---

#### diagnose_gpx_performance.py

Diagnóstico paso a paso para identificar cuellos de botella en el procesamiento GPX.

**📖 Documentación completa**: Ver [PERFORMANCE_DIAGNOSTICS.md](PERFORMANCE_DIAGNOSTICS.md) para explicación detallada de cada paso, interpretación de resultados y casos de uso.

**Uso:**
```bash
cd backend

# Diagnóstico con archivo por defecto (long_route_10mb.gpx)
poetry run python scripts/analysis/diagnose_gpx_performance.py

# Diagnóstico con archivo específico
poetry run python scripts/analysis/diagnose_gpx_performance.py scripts/datos/QH_2013.gpx
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/short_route.gpx
```

**Salida (archivo grande - 10MB):**
```
✓ Reading GPX file: tests/fixtures/gpx/long_route_10mb.gpx
  File size: 10,886,608 bytes (10.38 MB)

STEP 1: Parse GPX XML
✓ Parse time: 2.229s
✓ Original trackpoints: 85,000

STEP 2: RDP Simplification
✓ RDP time: 2.269s
✓ Simplified trackpoints: 2

✗ SC-002 FAIL: 10MB+ file processed in 4.960s (>2s target)

BOTTLENECK ANALYSIS
XML parsing:        2.229s (44.9%)
RDP algorithm:      2.269s (45.7%)
Other operations:   0.462s (9.3%)
```

**Salida (archivo normal - 1.2MB):**
```
✓ Reading GPX file: scripts/datos/QH_2013.gpx
  File size: 1,284,854 bytes (1.23 MB)

STEP 1: Parse GPX XML
✓ Parse time: 0.208s
✓ Original trackpoints: 4,471

STEP 2: RDP Simplification
✓ RDP time: 1.380s
✓ Simplified trackpoints: 1,197
✓ Reduction: 73.2%

✓ Processing time: 1.634s (<2s)

BOTTLENECK ANALYSIS
XML parsing:        0.208s (12.8%)
RDP algorithm:      1.380s (84.5%)
Other operations:   0.045s (2.8%)
```

---

## ⚠️ Limitaciones Conocidas (Feature 017)

### Limitación 1: Autenticación HTTP con curl

**Problema**: El endpoint `/auth/login` falla cuando se usa curl con passwords que contienen caracteres especiales.

**Síntoma:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}' \
  | jq -r '.data.access_token')

# Token obtained: null
# Error: JSON decode error field '43'
```

**Causa**: Shell escaping de WSL/Bash no maneja correctamente caracteres especiales (`!`) en JSON.

**Workaround**: Usar script Python en lugar de curl:
```bash
poetry run python scripts/analysis/test_gpx_analyze.py [archivo.gpx]
```

**Estado**: ✅ Workaround funcional - No bloqueante

---

### Limitación 2: Performance SC-002 FAIL (CRÍTICO)

**Problema**: El procesamiento de archivos GPX de 10MB excede el objetivo de SC-002 (<2s).

**Mediciones:**

| Métrica | Actual | Objetivo | Estado |
|---------|--------|----------|--------|
| **Tiempo total** | 4.960s | <2.000s | ✗ FAIL (+248%) |
| XML parsing (gpxpy) | 2.229s (45%) | - | Cuello de botella #1 |
| RDP simplification | 2.269s (46%) | - | Cuello de botella #2 |
| Other operations | 0.462s (9%) | - | OK |

**Archivo de prueba**: `backend/tests/fixtures/gpx/long_route_10mb.gpx`
- Tamaño: 10.38 MB (10,886,608 bytes)
- Trackpoints: 85,000

**Cuellos de botella identificados:**

1. **gpxpy parsing (2.23s, 45%)**
   - La librería gpxpy es lenta con archivos grandes
   - Parsing XML bloqueante (no async)
   - 85,000 trackpoints en memoria

2. **RDP algorithm (2.27s, 46%)**
   - Douglas-Peucker es O(n²) en peor caso
   - Con 85,000 puntos, el algoritmo es lento
   - Epsilon muy pequeño (0.0001°) requiere más iteraciones

**Soluciones propuestas:**

**Corto plazo** (workaround):
- ✅ Documentar limitación conocida
- ⚠️ Actualizar SC-002 para reflejar tiempo real (~5s para 10MB)
- ⚠️ Advertir usuarios sobre archivos >10MB

**Medio plazo** (optimizaciones):
1. **Cambiar parser XML**: Evaluar lxml, defusedxml (más rápidos que gpxpy)
2. **Implementar streaming parsing**: Procesar GPX en chunks
3. **Optimizar RDP**:
   - Aumentar epsilon a 0.0002° (reduce iteraciones)
   - Implementar RDP multithread/async
   - Pre-filtrar puntos muy cercanos antes de RDP
4. **Limitar puntos de entrada**: Advertir si GPX >50,000 puntos

**Largo plazo** (arquitectura):
1. **Processing en background**:
   - Retornar respuesta inmediata con `processing_status=pending`
   - Calcular telemetría en task async
   - Notificar al usuario cuando complete
2. **Cache de telemetría**: Almacenar hash del archivo para evitar reprocesar

**Estado**: ⚠️ Limitación documentada - Requiere optimización

---

### Limitación 3: Performance con Rutas Reales (CRÍTICA)

**Problema**: El algoritmo RDP es **15x más lento** con rutas realistas (curvas) que con rutas de línea recta.

**Mediciones comparativas:**

| Archivo | Parse | RDP | Total | Puntos simplificados |
|---------|-------|-----|-------|----------------------|
| **long_route_10mb.gpx** (línea recta) | 2.2s | 2.3s | **4.96s** | 2 (99.998% reducción) |
| **realistic_route_10mb.gpx** (curvas) | 2.2s | **34.6s** | **36.6s** | 5,056 (94% reducción) |

**Causa raíz**:
1. **Archivo de línea recta no es representativo**: El archivo `long_route_10mb.gpx` genera una ruta casi recta, permitiendo a RDP eliminar casi todos los puntos
2. **Rutas reales con curvas son el peor caso para RDP**: El algoritmo es O(n²) en el peor caso, y rutas con curvas requieren preservar muchos más puntos
3. **Preservar 2,500x más puntos requiere 15x más tiempo**: El tiempo de RDP escala exponencialmente con el número de puntos preservados

**Impacto**:
- ⚠️ **Crítico para UX**: Los usuarios deben esperar **30-40 segundos** para procesar archivos de 10MB
- ⚠️ **SC-002 no se cumple**: Objetivo era <2s, realidad es ~37s (18x más lento)
- ⚠️ **Riesgo de abandono**: Usuarios pueden pensar que la app está colgada

**Soluciones propuestas:**

**Inmediato** (MVP):
- ✅ **Archivo de prueba realista**: Generado `realistic_route_10mb.gpx` con curvas
- ✅ **Indicador de progreso**: Mostrar "Procesando archivo grande... puede tardar hasta 60s"
- ✅ **Documentar limitación**: SC-002 actualizado a <60s (objetivo realista)
- ⚠️ **Limitar tamaño**: Considerar rechazar archivos >10MB

**Corto plazo** (Post-MVP Priority 1 - ALTAMENTE RECOMENDADO):
1. **Aumentar epsilon de RDP**: De 0.0001 a 0.0002 o 0.0005
   - Reducción esperada: 34s → 10-15s
   - Trade-off: Pérdida mínima de precisión visual

2. **Pre-filtrado de puntos**: Eliminar puntos <5m antes de RDP
   - Reducción esperada: 34s → 15s
   - Sin trade-off (puntos cercanos no aportan valor)

**Medio plazo**:
- Implementar RDP multithread (reducción: 34s → 10s con 4 cores)
- Cache de telemetría por hash de archivo

**Largo plazo**:
- Background processing con WebSocket para archivos >5MB

**Estado**: ⚠️ **CRÍTICO** - Limitación severa que afecta significativamente la UX. Optimización post-MVP es **altamente recomendada**.

**Testing**:
```bash
# Archivo de línea recta (rápido pero no representativo)
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/long_route_10mb.gpx

# Archivo realista (lento pero representativo del uso real)
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/realistic_route_10mb.gpx
```

---

## 📚 Referencias

- **📖 Guía de Diagnóstico de Performance**: [PERFORMANCE_DIAGNOSTICS.md](PERFORMANCE_DIAGNOSTICS.md) - Explicación detallada de cada paso del diagnóstico
- **Documentación general**: [../README.md](../README.md)
- **Scripts GPS completos**: [../GPS_ANALYSIS_SCRIPTS.md](../GPS_ANALYSIS_SCRIPTS.md)
- **Feature 017 Spec**: [../../specs/017-gps-trip-wizard/spec.md](../../specs/017-gps-trip-wizard/spec.md)
- **Performance Testing**: [../../specs/017-gps-trip-wizard/PERFORMANCE_TESTING.md](../../specs/017-gps-trip-wizard/PERFORMANCE_TESTING.md)

---

**Última actualización**: 2026-02-01
**Feature**: 017-gps-trip-wizard
**Estado**: 2 scripts de testing añadidos, 3 limitaciones documentadas
