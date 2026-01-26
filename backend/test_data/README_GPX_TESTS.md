# Archivos GPX de Prueba - User Story 5 (Advanced Statistics)

Este directorio contiene archivos GPX de prueba para validar la funcionalidad de **estadísticas avanzadas** (Feature 003 - User Story 5).

---

## 📋 Índice

- [Archivos Disponibles](#archivos-disponibles)
  - [1. test_with_timestamps.gpx ✅](#1-test_with_timestampsgpx-)
  - [2. test_without_timestamps.gpx ❌](#2-test_without_timestampsgpx-)
  - [3. test_realistic_gradients.gpx 🏔️](#3-test_realistic_gradientsgpx-️)
- [Cómo Usar los Archivos de Prueba](#cómo-usar-los-archivos-de-prueba)
  - [1. Vía API (Postman/cURL)](#1-vía-api-postmancurl)
  - [2. Vía Frontend (Manual Testing)](#2-vía-frontend-manual-testing)
  - [3. Vía Script de Bash (Automatizado)](#3-vía-script-de-bash-automatizado)
- [Validaciones Esperadas](#validaciones-esperadas)
- [Cálculos Esperados](#cálculos-esperados)
- [Troubleshooting](#troubleshooting)
- [Plan de Pruebas Funcionales (Feature 003 - User Story 5)](#plan-de-pruebas-funcionales-feature-003---user-story-5)
  - [TC-US5-001: Carga de GPX con Timestamps](#tc-us5-001-carga-de-gpx-con-timestamps)
  - [TC-US5-002: Carga de GPX sin Timestamps](#tc-us5-002-carga-de-gpx-sin-timestamps)
  - [TC-US5-003: Validación de Datos Calculados](#tc-us5-003-validación-de-datos-calculados)
  - [TC-US5-004: Validación de Gradientes Realistas](#tc-us5-004-validación-de-gradientes-realistas)
  - [TC-US5-005: Visualización en Frontend](#tc-us5-005-visualización-en-frontend)
  - [TC-US5-006: Validación de Casos Extremos](#tc-us5-006-validación-de-casos-extremos)
  - [TC-US5-007: Testing de Rendimiento](#tc-us5-007-testing-de-rendimiento)
  - [TC-US5-008: Integración con DELETE GPX](#tc-us5-008-integración-con-delete-gpx)
- [Matriz de Trazabilidad](#matriz-de-trazabilidad)
- [Comandos de Testing Rápido](#comandos-de-testing-rápido)
- [Referencias](#referencias)
- [Notas Adicionales](#notas-adicionales)

---

## Archivos Disponibles

### 1. `test_with_timestamps.gpx` ✅
**Descripción**: Ruta completa de ~25km con timestamps y elevación.

**Características**:
- ✅ Timestamps en todos los puntos
- ✅ Datos de elevación completos
- ✅ 3 subidas significativas (para validar top climbs)
- ✅ Parada de 10 minutos (para validar moving_time vs total_time)
- ✅ Variedad de velocidades (6 km/h en subidas, 45 km/h en bajadas)

**Estadísticas Esperadas**:
```json
{
  "avg_speed_kmh": ~18.5,
  "max_speed_kmh": ~45.0,
  "total_time_minutes": ~157.67 (2h 37min),
  "moving_time_minutes": ~147.67 (2h 27min, excluye parada de 10min),
  "avg_gradient": ~5.5%,
  "max_gradient": ~12.0%,
  "top_climbs": [
    {
      "description": "Subida 1: 156m de desnivel con 7.8% de pendiente media",
      "elevation_gain_m": 156,
      "avg_gradient": 7.8,
      "start_km": 16.0,
      "end_km": 18.0
    },
    {
      "description": "Subida 2: 150m de desnivel con 7.5% de pendiente media",
      "elevation_gain_m": 150,
      "avg_gradient": 7.5,
      "start_km": 10.0,
      "end_km": 12.0
    },
    {
      "description": "Subida 3: 80m de desnivel con 5.3% de pendiente media",
      "elevation_gain_m": 80,
      "avg_gradient": 5.3,
      "start_km": 3.0,
      "end_km": 4.5
    }
  ]
}
```

**Casos de Prueba**:
- ✅ TC-US5-001: Carga de GPX con timestamps → debe calcular todas las estadísticas
- ✅ TC-US5-003: Validación de datos calculados → verificar precisión

---

### 2. `test_without_timestamps.gpx` ❌
**Descripción**: Ruta de ~15km SIN timestamps (solo coordenadas y elevación).

**Características**:
- ❌ NO tiene timestamps en ningún punto
- ✅ Datos de elevación completos
- ✅ 2 subidas

**Estadísticas Esperadas**:
```json
{
  "route_statistics": null
}
```

**Motivo**: Sin timestamps, NO se puede calcular velocidad ni tiempo → `route_statistics` debe ser `null`.

**Casos de Prueba**:
- ✅ TC-US5-002: Carga de GPX sin timestamps → NO debe generar estadísticas avanzadas

---

### 3. `test_realistic_gradients.gpx` 🏔️
**Descripción**: Puerto de Navacerrada (subida clásica española) con gradientes realistas.

**Características**:
- ✅ Timestamps en todos los puntos
- ✅ Datos de elevación realistas
- ✅ Gradientes entre 4% y 12% (rango realista para ciclismo)
- ✅ Desnivel total: ~850m en 10.5km
- ✅ Gradiente medio: ~8.1%

**Estadísticas Esperadas**:
```json
{
  "avg_speed_kmh": ~10-12 (subida dura),
  "max_speed_kmh": ~15-20,
  "total_time_minutes": ~59.5 (~1h),
  "moving_time_minutes": ~59.5,
  "avg_gradient": ~8.1%,
  "max_gradient": ~12.0% (NO debe ser +100%),
  "top_climbs": [
    {
      "description": "Subida 1: ~850m de desnivel con 8.1% de pendiente media",
      "elevation_gain_m": ~850,
      "avg_gradient": ~8.1,
      "start_km": 0.0,
      "end_km": 10.5
    }
  ]
}
```

**Validación Crítica**: El `max_gradient` debe estar entre -35% y +35% (NO +100% como en el bug reportado).

**Casos de Prueba**:
- ✅ TC-US5-004: Validación de gradientes realistas → verificar que max_gradient < 35%
- ✅ TC-US5-001: Verificar cálculo correcto de distance_2d() vs distance_3d()

---

## Cómo Usar los Archivos de Prueba

### 1. Vía API (Postman/cURL)

```bash
# Obtener token de autenticación
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'

# Crear un viaje de prueba
TRIP_ID=$(curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prueba Estadísticas GPX",
    "description": "Viaje de prueba para validar estadísticas avanzadas (User Story 5)",
    "start_date": "2024-06-15",
    "distance_km": 25.0
  }' | jq -r '.data.trip_id')

# Subir archivo GPX
curl -X POST http://localhost:8000/trips/$TRIP_ID/gpx \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_data/test_with_timestamps.gpx"

# Obtener estadísticas calculadas
curl -X GET http://localhost:8000/gpx/{gpx_file_id}/track \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.data.route_statistics'
```

### 2. Vía Frontend (Manual Testing)

1. Navega a http://localhost:5173
2. Inicia sesión con usuario de prueba
3. Ve a "Mis Viajes" → "Crear Viaje"
4. Completa el formulario de viaje
5. Publica el viaje
6. Sube uno de los archivos GPX de prueba:
   - `test_with_timestamps.gpx` → Debe mostrar estadísticas completas
   - `test_without_timestamps.gpx` → NO debe mostrar estadísticas avanzadas
   - `test_realistic_gradients.gpx` → Verificar gradientes realistas

### 3. Vía Script de Bash (Automatizado)

```bash
cd backend

# Ejecutar script de pruebas de estadísticas GPX
bash scripts/test_gpx_statistics.sh
```

---

## Validaciones Esperadas

### ✅ **Validaciones de Éxito**

| Archivo | has_timestamps | route_statistics | Validación |
|---------|----------------|------------------|------------|
| `test_with_timestamps.gpx` | `true` | ✅ Presente | Todas las métricas calculadas |
| `test_without_timestamps.gpx` | `false` | ❌ `null` | Sin estadísticas avanzadas |
| `test_realistic_gradients.gpx` | `true` | ✅ Presente | Gradientes < 35% |

### ❌ **Validaciones de Error (Casos a Rechazar)**

- Gradientes > 35% (errores de GPS)
- Gradientes < -35% (errores de GPS)
- Velocidades > 100 km/h (errores de GPS)
- moving_time > total_time (inválido)

---

## Cálculos Esperados

### **Fórmulas**

```python
# Gradiente (%) = (elevación / distancia_horizontal) * 100
gradient = (elevation_diff_m / distance_2d_m) * 100

# Velocidad (km/h) = (distancia_km / tiempo_h)
speed_kmh = (distance_km / time_seconds) * 3600

# Moving Time = suma de intervalos donde speed >= 3 km/h
moving_time = sum(intervals where speed >= MIN_SPEED_KMPH)

# Dificultad de Subida = desnivel_m * pendiente_media
difficulty_score = elevation_gain_m * avg_gradient
```

### **Constantes**

```python
MIN_SPEED_KMPH = 3.0  # Mínimo para considerar "en movimiento"
MAX_REALISTIC_SPEED_KMPH = 100.0  # Máximo realista para ciclismo
MIN_GRADIENT = -35.0  # Gradiente mínimo realista (bajada)
MAX_GRADIENT = 35.0   # Gradiente máximo realista (subida)
MIN_CLIMB_GAIN = 30.0  # Desnivel mínimo para considerar "subida"
MIN_CLIMB_DISTANCE = 0.5  # Distancia mínima para considerar "subida"
```

---

## Troubleshooting

### **Problema**: `max_gradient` muestra +100% o valores irreales

**Causa**: Uso de `distance_3d()` en lugar de `distance_2d()` (BUG CORREGIDO en commit c152238)

**Solución**: Verificar que `route_statistics_service.py` use `distance_2d()` en líneas 198 y 275:

```python
# CORRECTO ✅
distance_m = prev_point.distance_2d(curr_point)  # Solo distancia horizontal

# INCORRECTO ❌
distance_m = prev_point.distance_3d(curr_point)  # Incluye componente vertical
```

### **Problema**: `route_statistics` es `null` en archivo con timestamps

**Causa**: Procesamiento asíncrono aún no completado

**Solución**: Esperar a que `processing_status = 'completed'` antes de solicitar estadísticas.

### **Problema**: `top_climbs` está vacío

**Causa**: Archivo no cumple requisitos mínimos (>30m desnivel, >0.5km distancia)

**Solución**: Usar `test_with_timestamps.gpx` que tiene 3 subidas válidas.

---

## Plan de Pruebas Funcionales (Feature 003 - User Story 5)

### Objetivo
Validar el cálculo correcto de estadísticas avanzadas de rutas GPS incluyendo velocidad, tiempo, gradientes y detección de subidas.

### Alcance
- ✅ Cálculo de velocidad (promedio, máxima)
- ✅ Análisis de tiempo (total, en movimiento)
- ✅ Métricas de gradiente (promedio, máximo)
- ✅ Detección de top 3 subidas más difíciles
- ✅ Visualización en frontend (componente AdvancedStats)

---

### TC-US5-001: Carga de GPX con Timestamps

**Descripción**: Validar que un archivo GPX con timestamps genera estadísticas avanzadas correctamente.

**Precondiciones**:
- Usuario autenticado
- Viaje creado y publicado
- Archivo `test_with_timestamps.gpx` disponible

**Pasos**:
1. Navegar a la página del viaje
2. Subir archivo `test_with_timestamps.gpx`
3. Esperar a que el procesamiento termine (`processing_status = 'completed'`)
4. Verificar que aparece la sección "Estadísticas Avanzadas"

**Resultados Esperados**:
```json
{
  "route_statistics": {
    "stats_id": "<UUID>",
    "gpx_file_id": "<UUID>",
    "avg_speed_kmh": ~18.5,
    "max_speed_kmh": ~45.0,
    "total_time_minutes": ~157.67,
    "moving_time_minutes": ~147.67,
    "avg_gradient": ~5.5,
    "max_gradient": ~12.0,
    "top_climbs": [
      {
        "start_km": 16.0,
        "end_km": 18.0,
        "elevation_gain_m": 156.0,
        "avg_gradient": 7.8,
        "description": "Subida 1: 156m de desnivel con 7.8% de pendiente media"
      },
      {
        "start_km": 10.0,
        "end_km": 12.0,
        "elevation_gain_m": 150.0,
        "avg_gradient": 7.5,
        "description": "Subida 2: 150m de desnivel con 7.5% de pendiente media"
      },
      {
        "start_km": 3.0,
        "end_km": 4.5,
        "elevation_gain_m": 80.0,
        "avg_gradient": 5.3,
        "description": "Subida 3: 80m de desnivel con 5.3% de pendiente media"
      }
    ],
    "created_at": "<timestamp>"
  }
}
```

**Criterios de Aceptación**:
- ✅ `route_statistics` NO es `null`
- ✅ `avg_speed_kmh` está entre 0 y 100 km/h
- ✅ `max_speed_kmh` >= `avg_speed_kmh`
- ✅ `total_time_minutes` >= `moving_time_minutes` (incluye paradas)
- ✅ `max_gradient` está entre -35% y +35% (realista)
- ✅ `top_climbs` tiene exactamente 3 elementos (ordenados por dificultad)
- ✅ Frontend muestra todas las métricas correctamente formateadas

---

### TC-US5-002: Carga de GPX sin Timestamps

**Descripción**: Validar que un archivo GPX SIN timestamps NO genera estadísticas avanzadas.

**Precondiciones**:
- Usuario autenticado
- Viaje creado y publicado
- Archivo `test_without_timestamps.gpx` disponible

**Pasos**:
1. Navegar a la página del viaje
2. Subir archivo `test_without_timestamps.gpx`
3. Esperar a que el procesamiento termine
4. Verificar respuesta de API

**Resultados Esperados**:
```json
{
  "route_statistics": null
}
```

**Criterios de Aceptación**:
- ✅ `route_statistics` es `null`
- ✅ `has_timestamps` es `false` en metadatos del GPX
- ✅ Frontend NO muestra la sección "Estadísticas Avanzadas"
- ✅ Otras métricas básicas (distancia, elevación) SÍ se muestran

**Motivo**: Sin timestamps, es imposible calcular velocidad o tiempo.

---

### TC-US5-003: Validación de Datos Calculados

**Descripción**: Validar precisión de las métricas calculadas mediante verificación manual.

**Precondiciones**:
- GPX con timestamps cargado
- Estadísticas calculadas y visibles

**Pasos de Verificación**:

#### 3.1 Velocidad
1. Tomar dos puntos consecutivos del GPX
2. Calcular distancia entre ellos (en km)
3. Calcular diferencia de tiempo (en horas)
4. Verificar: `speed_kmh = distance_km / time_hours`

**Ejemplo**:
- Punto A: `40.4168, -3.7038` a `08:00:00`
- Punto B: `40.4258, -3.7045` a `08:03:00`
- Distancia: ~1.0 km
- Tiempo: 3 min = 0.05 horas
- Velocidad esperada: 1.0 / 0.05 = 20 km/h

#### 3.2 Tiempo Total vs Tiempo en Movimiento
1. Identificar segmentos con velocidad < 3 km/h (paradas)
2. Sumar tiempos de todos los segmentos → `total_time`
3. Sumar tiempos solo de segmentos con velocidad >= 3 km/h → `moving_time`
4. Verificar: `moving_time <= total_time`

**Ejemplo** (archivo test_with_timestamps.gpx):
- Parada de 10 minutos en km 8.1
- `total_time` = ~157.67 min
- `moving_time` = ~147.67 min (excluye parada)
- Diferencia: 10 min ✓

#### 3.3 Gradiente
1. Tomar dos puntos consecutivos
2. Calcular elevación vertical: `rise = elevation_diff_m`
3. Calcular distancia horizontal: `run = distance_2d_m` (NO usar distance_3d)
4. Verificar: `gradient = (rise / run) * 100`

**Ejemplo**:
- Punto A: elevación 656m
- Punto B: elevación 696m (0.5 km después)
- Rise: 40m
- Run: 500m (horizontal)
- Gradiente esperado: (40 / 500) * 100 = 8% ✓

**IMPORTANTE**: Si se usa `distance_3d()` (incluye componente vertical), el gradiente será incorrecto:
- Run (3D): ~502m (hipotenusa)
- Gradiente INCORRECTO: (40 / 502) * 100 = 7.97% (cercano pero impreciso)
- En pendientes extremas (>20%), el error es significativo

#### 3.4 Top Climbs
1. Identificar segmentos de subida continua (elevación aumenta)
2. Filtrar subidas con:
   - Desnivel >= 30m
   - Distancia >= 0.5 km
3. Calcular `difficulty_score = elevation_gain_m * avg_gradient`
4. Ordenar por `difficulty_score` (mayor = más difícil)
5. Tomar top 3

**Ejemplo** (archivo test_with_timestamps.gpx):
| Rank | Inicio | Fin | Desnivel | Gradiente | Dificultad |
|------|--------|-----|----------|-----------|------------|
| 1 | 16.0 km | 18.0 km | 156m | 7.8% | 1216.8 |
| 2 | 10.0 km | 12.0 km | 150m | 7.5% | 1125.0 |
| 3 | 3.0 km | 4.5 km | 80m | 5.3% | 424.0 |

**Criterios de Aceptación**:
- ✅ Velocidades calculadas coinciden con fórmula manual (±5%)
- ✅ Tiempos totales vs en movimiento son lógicos
- ✅ Gradientes están en rango realista (-35% a +35%)
- ✅ Top climbs están ordenados por dificultad (no solo por desnivel)

---

### TC-US5-004: Validación de Gradientes Realistas

**Descripción**: Validar que el sistema filtra gradientes irrealistas causados por errores de GPS.

**Precondiciones**:
- Archivo `test_realistic_gradients.gpx` disponible (Puerto de Navacerrada)

**Pasos**:
1. Subir archivo `test_realistic_gradients.gpx`
2. Esperar procesamiento
3. Verificar estadísticas calculadas

**Resultados Esperados**:
```json
{
  "avg_gradient": ~8.1,
  "max_gradient": ~12.0,  // NO debe ser > 35%
  "top_climbs": [
    {
      "elevation_gain_m": ~850,
      "avg_gradient": ~8.1
    }
  ]
}
```

**Criterios de Aceptación**:
- ✅ `max_gradient` < 35% (filtro de gradientes irrealistas activo)
- ✅ `max_gradient` > 0% (debe detectar subidas)
- ✅ `avg_gradient` es razonable (~8.1% para puerto de montaña)
- ✅ NO aparecen valores como +100% o -80% (errores de GPS filtrados)

**Casos de Error a Detectar**:
- ❌ `max_gradient = 100%` → BUG: usando `distance_3d()` en lugar de `distance_2d()`
- ❌ `max_gradient = -80%` → BUG: datos GPS corruptos no filtrados
- ❌ `max_gradient = 0%` → BUG: archivo sin elevación o cálculo incorrecto

---

### TC-US5-005: Visualización en Frontend

**Descripción**: Validar que el componente `AdvancedStats` muestra correctamente las estadísticas.

**Precondiciones**:
- GPX con timestamps cargado
- Estadísticas calculadas
- Usuario navegando a página de viaje

**Pasos**:
1. Navegar a `/trips/{trip_id}`
2. Scroll hasta la sección "Estadísticas Avanzadas"
3. Verificar visualización de cada métrica

**Layout Esperado**:

```
┌─────────────────────────────────────────────────────────┐
│ Estadísticas Avanzadas                                  │
│ Basado en timestamps del archivo GPX                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌──────────────┐ ┌──────────────┐      │
│ │ ⚡ Velocidad │ │ 🕐 Tiempo    │ │ 📈 Pendiente │      │
│ │ Promedio    │ │ Total        │ │ Promedio     │      │
│ │ 18.5 km/h   │ │ 2h 37min     │ │ +5.5%        │      │
│ │ Máxima      │ │ En movimiento│ │ Máxima       │      │
│ │ 45.0 km/h   │ │ 2h 27min     │ │ +12.0% (rojo)│      │
│ └─────────────┘ └──────────────┘ └──────────────┘      │
├─────────────────────────────────────────────────────────┤
│ 🏔️ Top Subidas                                          │
│ ┌───┬───────┬──────┬──────────┬──────────┐             │
│ │ # │ Inicio│ Fin  │ Desnivel │ Pendiente│             │
│ ├───┼───────┼──────┼──────────┼──────────┤             │
│ │ 1 │ 16.0km│18.0km│ 156m     │ +7.8%    │             │
│ │ 2 │ 10.0km│12.0km│ 150m     │ +7.5%    │             │
│ │ 3 │ 3.0km │ 4.5km│ 80m      │ +5.3%    │             │
│ └───┴───────┴──────┴──────────┴──────────┘             │
├─────────────────────────────────────────────────────────┤
│ ℹ️ Las estadísticas se calculan automáticamente cuando  │
│    el archivo GPX incluye timestamps. Las paradas se    │
│    detectan cuando la velocidad es inferior a 3 km/h.   │
└─────────────────────────────────────────────────────────┘
```

**Criterios de Aceptación**:
- ✅ Grid de 3 columnas responsive (stacks en mobile)
- ✅ Iconos SVG para cada sección (⚡ 🕐 📈 🏔️)
- ✅ Velocidad máxima destacada en azul
- ✅ Gradiente máximo > 10% mostrado en rojo
- ✅ Tiempo formateado como "Xh Ymin" (no minutos decimales)
- ✅ Tabla de top climbs con ranking numerado (1, 2, 3)
- ✅ Footer informativo sobre detección de paradas
- ✅ Responsive: mobile muestra 1 columna, desktop 3 columnas

---

### TC-US5-006: Validación de Casos Extremos

**Descripción**: Validar comportamiento con datos edge case.

#### 6.1 Archivo con 1 Solo Punto
**Entrada**: GPX con 1 trackpoint
**Resultado Esperado**: `route_statistics = null` (insuficientes datos)

#### 6.2 Archivo con Velocidades Irrealistas
**Entrada**: GPX con segmento de 200 km/h
**Resultado Esperado**:
- Velocidad filtrada (ignorada)
- `max_speed_kmh` no incluye valor irreal
- Log warning: "Unrealistic speed detected: 200.0 km/h at point X, skipping"

#### 6.3 Archivo sin Subidas Válidas
**Entrada**: Ruta plana (sin desnivel > 30m)
**Resultado Esperado**:
- `top_climbs = []` (array vacío)
- Frontend NO muestra tabla de subidas
- Otras métricas (velocidad, tiempo) SÍ se calculan

#### 6.4 Archivo con Gaps de Timestamp
**Entrada**: GPX con salto de 2 horas entre puntos
**Resultado Esperado**:
- Segmento incluido en `total_time`
- Segmento EXCLUIDO de `moving_time` (velocidad = 0)
- `avg_speed_kmh` calculado solo con segmentos válidos

---

### TC-US5-007: Testing de Rendimiento

**Descripción**: Validar que el cálculo de estadísticas no degrada el rendimiento.

**Pasos**:
1. Subir archivo GPX grande (5000+ puntos)
2. Medir tiempo de procesamiento
3. Verificar que estadísticas se calculan en tiempo razonable

**Criterios de Aceptación**:
- ✅ Procesamiento < 30 segundos para archivos < 1MB
- ✅ Procesamiento < 60 segundos para archivos 1-10MB
- ✅ No hay memory leaks (uso de memoria estable)
- ✅ API response time < 500ms para GET /gpx/{id}/track

---

### TC-US5-008: Integración con DELETE GPX

**Descripción**: Validar que eliminar un GPX también elimina sus estadísticas.

**Precondiciones**:
- GPX con estadísticas cargado
- Usuario es propietario del viaje

**Pasos**:
1. Navegar a página del viaje
2. Hacer clic en "Eliminar GPX"
3. Confirmar eliminación en modal
4. Verificar respuesta de API

**Resultados Esperados**:
- ✅ GPX eliminado (código 204)
- ✅ Estadísticas eliminadas por CASCADE (no quedan huérfanas en BD)
- ✅ Frontend oculta sección "Estadísticas Avanzadas"
- ✅ Frontend muestra uploader de GPX nuevamente
- ✅ Toast de confirmación: "Archivo GPX eliminado correctamente"

**Validación en Base de Datos**:
```sql
-- Verificar que no quedan estadísticas huérfanas
SELECT COUNT(*) FROM route_statistics WHERE gpx_file_id NOT IN (SELECT gpx_file_id FROM gpx_files);
-- Resultado esperado: 0
```

---

## Matriz de Trazabilidad

| Test Case | Requirement | Success Criteria | Priority | Status |
|-----------|-------------|------------------|----------|--------|
| TC-US5-001 | FR-003 | SC-015, SC-016 | Alta | ✅ |
| TC-US5-002 | FR-003 | SC-017 | Alta | ✅ |
| TC-US5-003 | FR-003 | SC-015, SC-016 | Alta | ✅ |
| TC-US5-004 | FR-003 | SC-015 | Alta | ✅ |
| TC-US5-005 | FR-003 | SC-018 | Media | ✅ |
| TC-US5-006 | FR-003 | SC-017 | Media | Pendiente |
| TC-US5-007 | NFR-001 | SC-019 | Media | Pendiente |
| TC-US5-008 | FR-039 | SC-020 | Baja | ✅ |

**Leyenda**:
- FR-003: Display Route Statistics
- FR-039: Delete GPX File
- SC-015: Accuracy of calculations
- SC-016: Realistic gradient filtering
- SC-017: Null handling for missing data
- SC-018: Frontend display correctness
- SC-019: Performance requirements
- SC-020: Data integrity on deletion

---

## Comandos de Testing Rápido

### Backend (pytest)
```bash
cd backend

# Test de cálculo de estadísticas
poetry run pytest tests/unit/test_route_statistics_service.py -v

# Test de endpoint de track data
poetry run pytest tests/integration/test_gpx_endpoints.py::test_get_track_with_statistics -v

# Test de validación de gradientes
poetry run pytest tests/unit/test_route_statistics_service.py::test_gradient_filtering -v
```

### Frontend (Manual)
```bash
cd frontend

# Iniciar dev server
npm run dev

# Navegar a:
# 1. http://localhost:5173/trips/{trip_id}
# 2. Subir test_with_timestamps.gpx
# 3. Verificar sección "Estadísticas Avanzadas"
```

### API (cURL)
```bash
# Subir GPX con timestamps
curl -X POST http://localhost:8000/trips/$TRIP_ID/gpx \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_data/test_with_timestamps.gpx"

# Obtener estadísticas
curl http://localhost:8000/gpx/$GPX_FILE_ID/track \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data.route_statistics'
```

---

## Referencias

- **Backend Service**: `backend/src/services/route_statistics_service.py`
- **Frontend Component**: `frontend/src/components/trips/AdvancedStats.tsx`
- **API Schemas**: `backend/src/schemas/gpx.py` (RouteStatisticsResponse, TopClimbResponse)
- **Database Model**: `backend/src/models/route_statistics.py`
- **Migration**: `backend/src/migrations/versions/20260125_2353_4144c09f7bc0_create_route_statistics_table.py`

---

## Notas Adicionales

- Los archivos GPX están en formato GPX 1.1 estándar
- Todas las coordenadas son válidas (Madrid y Barcelona)
- Los timestamps siguen formato ISO 8601 con timezone UTC
- Las elevaciones son realistas para las ubicaciones geográficas
- Los gradientes están calculados para simular rutas ciclistas reales
