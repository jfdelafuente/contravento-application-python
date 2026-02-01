# GPX Test Fixtures

Archivos GPX de prueba para testing de performance y funcionalidad del GPS Trip Wizard (Feature 017).

## Archivos Disponibles

### short_route.gpx
- **Tamaño**: ~50KB
- **Trackpoints**: ~500
- **Uso**: Tests unitarios básicos, validación funcional
- **Performance**: <1s de procesamiento

### long_route_10mb.gpx
- **Tamaño**: 10.38 MB (10,886,608 bytes)
- **Trackpoints**: 85,000
- **Patrón**: ⚠️ **Línea recta** (Atlantic → Mediterranean)
- **RDP Reduction**: 99.998% (85,000 → 2 puntos)
- **Processing time**: ~5s
- **Uso**: ⚠️ **NO REPRESENTATIVO** de rutas reales
- **Generador**: `generate_xlarge_gpx.py`

**Problema**: Este archivo fue útil para identificar que el endpoint funciona, pero la línea recta permite a RDP eliminar casi todos los puntos, dando tiempos de procesamiento artificialmente rápidos que no reflejan el uso real.

### realistic_route_10mb.gpx ⭐ RECOMENDADO
- **Tamaño**: 10.41 MB (10,914,961 bytes)
- **Trackpoints**: 85,000
- **Patrón**: ✅ **Ruta realista** con curvas, zigzags y cambios de elevación
- **Elevación**: 500m - 2500m (mountain cycling)
- **RDP Reduction**: 94% (85,000 → 5,056 puntos)
- **Processing time**: ~37s
- **Uso**: ✅ **REPRESENTATIVO** de archivos GPX reales de usuarios
- **Generador**: `generate_realistic_gpx.py`

**Características**:
- Zigzag pattern con cambios de dirección cada ~1000 puntos
- Spiral pattern para simular switchbacks de montaña
- Elevación con múltiples sine waves para crear hills/valleys realistas
- Timestamps at 3s intervals (realistic GPS sampling)

## Comparación de Performance

| Archivo | Parse | RDP | Total | Puntos | Uso Recomendado |
|---------|-------|-----|-------|--------|-----------------|
| **short_route.gpx** | <0.1s | <0.1s | <0.5s | ~100 | ✅ Tests unitarios |
| **long_route_10mb.gpx** | 2.2s | 2.3s | 4.96s | 2 | ⚠️ Legacy (no usar) |
| **realistic_route_10mb.gpx** | 2.2s | **34.6s** | **36.6s** | 5,056 | ✅ **Performance testing real** |

## Generadores de Archivos

### generate_xlarge_gpx.py (Legacy)
Genera `long_route_10mb.gpx` con línea recta.

**No recomendado** para nuevos tests - usar `generate_realistic_gpx.py` en su lugar.

### generate_realistic_gpx.py ⭐
Genera `realistic_route_10mb.gpx` con patrón realista.

**Uso**:
```bash
cd backend/tests/fixtures/gpx
python3 generate_realistic_gpx.py

# Output: realistic_route_10mb.gpx (10.41 MB)
```

**Parámetros configurables** (editar el script):
- `num_points`: Número de trackpoints (default: 85,000)
- `elevation_amplitude`: Rango de elevación (default: ±400m)
- `avg_speed_kmh`: Velocidad promedio para timestamps (default: 20 km/h)
- `time_interval_s`: Intervalo entre puntos GPS (default: 3s)

## Testing de Performance

### Validar SC-002 (Success Criteria 002)

**Con archivo realista** (recomendado):
```bash
cd backend
poetry run python scripts/analysis/test_gpx_analyze.py tests/fixtures/gpx/realistic_route_10mb.gpx
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/realistic_route_10mb.gpx
```

**Con archivo de línea recta** (legacy):
```bash
cd backend
poetry run python scripts/analysis/test_gpx_analyze.py tests/fixtures/gpx/long_route_10mb.gpx
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/long_route_10mb.gpx
```

### Comparación lado a lado

```bash
cd backend

echo "=== LÍNEA RECTA (NO REPRESENTATIVO) ==="
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/long_route_10mb.gpx

echo ""
echo "=== RUTA REALISTA (REPRESENTATIVO) ==="
poetry run python scripts/analysis/diagnose_gpx_performance.py tests/fixtures/gpx/realistic_route_10mb.gpx
```

## Recommendations

1. **Para tests unitarios**: Usar `short_route.gpx`
2. **Para performance testing**: Usar `realistic_route_10mb.gpx` ⭐
3. **Para validación de SC-002**: Usar `realistic_route_10mb.gpx` ⭐
4. **Para tests de integración**: Mezclar ambos archivos (small + realistic)

## Known Issues

### Issue 1: RDP Performance con Rutas Reales
**Problema**: El algoritmo RDP es 15x más lento con rutas realistas (34s) que con líneas rectas (2.3s).

**Causa**: Rutas con curvas requieren preservar muchos más puntos (5,056 vs 2), y RDP es O(n²) en el peor caso.

**Estado**: Limitación documentada en [specs/017-gps-trip-wizard/spec.md - Known Limitations](../../../specs/017-gps-trip-wizard/spec.md#known-limitations)

**Soluciones propuestas**:
- Corto plazo: Aumentar epsilon de RDP (0.0001 → 0.0002)
- Medio plazo: Pre-filtrar puntos <5m antes de RDP
- Largo plazo: Background processing para archivos >5MB

## Referencias

- **Feature Spec**: [specs/017-gps-trip-wizard/spec.md](../../../specs/017-gps-trip-wizard/spec.md)
- **Performance Testing**: [specs/017-gps-trip-wizard/PERFORMANCE_TESTING.md](../../../specs/017-gps-trip-wizard/PERFORMANCE_TESTING.md)
- **Performance Diagnostics**: [backend/scripts/analysis/PERFORMANCE_DIAGNOSTICS.md](../../scripts/analysis/PERFORMANCE_DIAGNOSTICS.md)
- **Testing Scripts**: [backend/scripts/analysis/README.md](../../scripts/analysis/README.md)

---

**Última actualización**: 2026-02-01
**Feature**: 017-gps-trip-wizard
**Versión**: 2.0.0 (añadido realistic_route_10mb.gpx, deprecado long_route_10mb.gpx)
