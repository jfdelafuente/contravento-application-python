# Integración de Estadísticas de Usuario

**Última actualización**: 2025-12-30
**Estado**: ✅ Implementado y funcionando
**Commits**: `92e3173` - feat: integrate user statistics updates with trip operations

## Resumen

Las estadísticas de usuario se actualizan **automáticamente** cuando se realizan operaciones sobre viajes (trips) publicados. La integración conecta `TripService` con `StatsService` para mantener las métricas sincronizadas en tiempo real.

## Flujo de Actualización de Estadísticas

### 1. Publicar Viaje (`publish_trip`)

**Trigger**: Cuando un viaje en estado `DRAFT` se publica (cambia a `PUBLISHED`)

**Código**: [trip_service.py:141-219](../../backend/src/services/trip_service.py#L141-L219)

**Operación**: `StatsService.update_stats_on_trip_publish()`

**Actualizaciones**:
```python
stats.total_trips += 1
stats.total_kilometers += trip.distance_km
stats.total_photos += len(trip.photos)
stats.countries_visited.append(country_code)  # Si es nuevo
stats.last_trip_date = max(stats.last_trip_date, trip.start_date)
```

**Acciones adicionales**:
- ✅ Verifica automáticamente si se cumplen criterios de logros
- ✅ Otorga logros nuevos si aplican

**Ejemplo**:
```python
# Usuario publica su primer viaje de 50km con 3 fotos
await trip_service.publish_trip(trip_id="abc123", user_id="user123")

# Stats después:
# total_trips: 0 → 1
# total_kilometers: 0 → 50
# total_photos: 0 → 3
# countries_visited: [] → ["ES"]
# Logros otorgados: "first_trip" ✅
```

---

### 2. Agregar Foto a Viaje Publicado (`upload_photo`)

**Trigger**: Subir foto a un viaje en estado `PUBLISHED`

**Código**: [trip_service.py:283-403](../../backend/src/services/trip_service.py#L283-L403)

**Operación**: `TripService._update_photo_count_in_stats(user_id, increment=1)`

**Actualizaciones**:
```python
stats.total_photos += 1
```

**Nota**: Solo se actualiza si `trip.status == TripStatus.PUBLISHED`

---

### 3. Eliminar Foto de Viaje Publicado (`delete_photo`)

**Trigger**: Eliminar foto de un viaje en estado `PUBLISHED`

**Código**: [trip_service.py:405-483](../../backend/src/services/trip_service.py#L405-L483)

**Operación**: `TripService._update_photo_count_in_stats(user_id, increment=-1)`

**Actualizaciones**:
```python
stats.total_photos -= 1  # Con protección: max(0, stats.total_photos - 1)
```

---

### 4. Editar Viaje Publicado (`update_trip`)

**Trigger**: Editar campos de un viaje en estado `PUBLISHED`

**Código**: [trip_service.py:543-657](../../backend/src/services/trip_service.py#L543-L657)

**Operación**: `StatsService.update_stats_on_trip_edit()`

**Actualizaciones** (recalcula delta):
```python
# Distancia
stats.total_kilometers = stats.total_kilometers - old_distance + new_distance

# Fotos (si se modificaron tags/locations que afecten fotos)
stats.total_photos = stats.total_photos - old_photos_count + new_photos_count

# País (si cambió)
if new_country not in stats.countries_visited:
    stats.countries_visited.append(new_country)
```

**Nota**: No se eliminan países previos aunque se cambien ubicaciones

---

### 5. Eliminar Viaje Publicado (`delete_trip`)

**Trigger**: Eliminar un viaje en estado `PUBLISHED`

**Código**: [trip_service.py:659-728](../../backend/src/services/trip_service.py#L659-L728)

**Operación**: `StatsService.update_stats_on_trip_delete()`

**Actualizaciones**:
```python
stats.total_trips = max(0, stats.total_trips - 1)
stats.total_kilometers = max(0, stats.total_kilometers - trip.distance_km)
stats.total_photos = max(0, stats.total_photos - len(trip.photos))
# countries_visited NO se modifica (conserva histórico)
```

**Protecciones**:
- Valores nunca negativos (usa `max(0, ...)`)
- Países visitados se mantienen (no se eliminan del histórico)

---

## Sistema de Logros (Achievements)

Cuando se publican o editan viajes, el sistema **automáticamente**:

1. Verifica si el usuario cumple criterios para nuevos logros
2. Otorga los logros que correspondan
3. Incrementa `achievements_count`

### Tipos de Logros Disponibles

#### Logros de Distancia (T175)
- `first_100km`: Acumular 100km
- `cyclist_1000km`: Acumular 1,000km
- `explorer_5000km`: Acumular 5,000km

#### Logros de Viajes (T176)
- `first_trip`: Primer viaje publicado
- `traveler_10`: 10 viajes publicados
- `veteran_25`: 25 viajes publicados

#### Logros de Países (T177)
- `globetrotter_5`: Visitar 5 países
- `wanderer_10`: Visitar 10 países

#### Logros de Fotos (T178)
- `photographer_50`: Subir 50 fotos

### Código de Verificación

**Archivo**: [stats_service.py:365-466](../../backend/src/services/stats_service.py#L365-L466)

**Método**: `StatsService.check_and_award_achievements(user_id)`

**Flujo**:
1. Obtiene estadísticas actuales del usuario
2. Obtiene todos los logros disponibles
3. Filtra logros ya otorgados
4. Verifica criterios uno por uno
5. Otorga logros nuevos automáticamente

---

## Implementación Técnica

### Clase: `TripService`

**Archivo**: `backend/src/services/trip_service.py`

**Métodos con integración de stats**:

```python
async def publish_trip(trip_id: str, user_id: str) -> Trip:
    """Publica viaje y actualiza estadísticas."""
    # ... validación ...

    if was_draft:
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_publish(
            user_id=user_id,
            distance_km=trip.distance_km or 0.0,
            country_code="ES",  # TODO: geocoding
            photos_count=len(trip.photos),
            trip_date=trip.start_date,
        )

    return trip


async def upload_photo(...) -> TripPhoto:
    """Sube foto y actualiza stats si trip publicado."""
    # ... upload logic ...

    if trip.status == TripStatus.PUBLISHED:
        await self._update_photo_count_in_stats(user_id, increment=1)

    return photo


async def delete_photo(...) -> dict:
    """Elimina foto y actualiza stats si trip publicado."""
    # ... delete logic ...

    if trip.status == TripStatus.PUBLISHED:
        await self._update_photo_count_in_stats(user_id, increment=-1)

    return {"message": "Foto eliminada correctamente"}


async def update_trip(...) -> Trip:
    """Edita viaje y recalcula stats si publicado."""
    # ... update logic ...

    if was_published:
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_edit(
            user_id=user_id,
            old_distance_km=old_distance,
            new_distance_km=new_distance,
            # ... otros campos
        )

    return trip


async def delete_trip(...) -> dict:
    """Elimina viaje y revierte stats si publicado."""
    # ... delete logic ...

    if was_published:
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_delete(
            user_id=user_id,
            distance_km=trip.distance_km,
            country_code="ES",
            photos_count=len(trip.photos),
        )

    return {"message": "Viaje eliminado correctamente"}
```

### Helper Method: `_update_photo_count_in_stats`

**Código**: [trip_service.py:730-756](../../backend/src/services/trip_service.py#L730-L756)

```python
async def _update_photo_count_in_stats(self, user_id: str, increment: int) -> None:
    """
    Actualiza contador de fotos en stats.

    Usado por upload_photo() y delete_photo() para viajes publicados.
    Más eficiente que recalcular todas las stats.
    """
    from src.models.stats import UserStats

    result = await self.db.execute(
        select(UserStats).where(UserStats.user_id == user_id)
    )
    stats = result.scalar_one_or_none()

    if stats:
        stats.total_photos = max(0, stats.total_photos + increment)
        stats.updated_at = datetime.now(UTC)
        await self.db.commit()
```

---

## Clase: `StatsService`

**Archivo**: `backend/src/services/stats_service.py`

**Métodos principales**:

### `update_stats_on_trip_publish`

**Código**: [stats_service.py:216-268](../../backend/src/services/stats_service.py#L216-L268)

Actualiza estadísticas cuando se publica un viaje por primera vez.

### `update_stats_on_trip_edit`

**Código**: [stats_service.py:270-322](../../backend/src/services/stats_service.py#L270-L322)

Recalcula delta de estadísticas cuando se edita un viaje publicado.

### `update_stats_on_trip_delete`

**Código**: [stats_service.py:324-363](../../backend/src/services/stats_service.py#L324-L363)

Revierte estadísticas cuando se elimina un viaje publicado.

### `check_and_award_achievements`

**Código**: [stats_service.py:512-532](../../backend/src/services/stats_service.py#L512-L532)

Verifica y otorga logros automáticamente.

---

## Notas de Implementación

### ✅ Buenas Prácticas Aplicadas

1. **Idempotencia**:
   - `publish_trip()` no duplica stats si el viaje ya estaba publicado
   - `award_achievement()` verifica si ya fue otorgado antes de crear registro

2. **Transacciones**:
   - Todas las operaciones usan commits explícitos
   - Stats se actualizan DESPUÉS de modificar el trip

3. **Protección de datos**:
   - Valores nunca negativos: `max(0, value)`
   - Países visitados se conservan (no se eliminan del histórico)

4. **Eficiencia**:
   - `_update_photo_count_in_stats()` evita recalcular todas las stats
   - `selectinload()` previene N+1 queries al cargar relaciones

5. **Captura temprana de datos**:
   - Stats captura valores ANTES de commit (mientras relationships están cargadas)
   - Evita lazy loading errors

### ⚠️ Limitaciones Conocidas

1. **País por defecto**:
   - Actualmente hardcodeado a `"ES"` (España)
   - TODO: Implementar extracción automática cuando se complete geocodificación

2. **Países no se eliminan**:
   - Editar/eliminar trips no modifica `countries_visited`
   - Decisión de diseño: mantener histórico completo
   - Para limpieza exacta se requeriría query de todos los trips del usuario

3. **Solo viajes publicados**:
   - Stats solo se actualizan para trips con `status=PUBLISHED`
   - Drafts no afectan estadísticas

---

## Testing

### Tests Implementados

**Archivo**: `backend/tests/unit/test_trip_service.py`

```python
# Tests de publicación con stats
✅ test_publish_trip_success
✅ test_publish_trip_with_minimal_valid_data
✅ test_publish_trip_idempotent

# Tests de validación
✅ test_publish_trip_validation_error_short_description
✅ test_publish_trip_validation_requires_title
✅ test_publish_trip_not_found
✅ test_publish_trip_unauthorized_different_user
```

**Resultado**: 7/7 tests passing ✅

### Cómo Verificar Stats

**Endpoint**: `GET /users/{username}/stats`

```bash
# Ver estadísticas de un usuario
curl http://localhost:8000/users/maria_garcia/stats

# Respuesta esperada:
{
  "success": true,
  "data": {
    "total_trips": 5,
    "total_kilometers": 327.5,
    "total_photos": 12,
    "countries_visited": [
      {"code": "ES", "name": "España"}
    ],
    "achievements_count": 2,
    "last_trip_date": "2024-05-20"
  }
}
```

---

## Próximos Pasos

### Mejoras Planificadas

1. **Geocodificación Completa**:
   - Extraer código de país real de ubicaciones
   - Usar Google Places API para coordenadas → país
   - Eliminar hardcoded `country_code = "ES"`

2. **Logros de Seguidores**:
   - Implementar verificación de `followers_count`
   - Logro: "Popular" (100 seguidores)

3. **Tests de Integración**:
   - Test end-to-end: crear → publicar → verificar stats
   - Test de edición masiva y verificación de delta
   - Test de concurrencia (múltiples publishes simultáneos)

4. **Performance**:
   - Cachear achievement definitions (no cambian frecuentemente)
   - Batch processing para verificación de logros
   - Optimizar queries con índices en campos de stats

---

## Referencias

**Tareas relacionadas**:
- T036: Implement publish_trip with stats update (Phase 3)
- T071: Unit test for stats deletion helper (Phase 5)
- T073: Implement update_trip with stats sync (Phase 5)
- T074-T075: Implement delete_trip with stats rollback (Phase 5)
- T161-T165: Stats service methods (Phase 3)
- T175-T178: Achievement criteria validation (Phase 3)

**Commits**:
- `92e3173`: feat: integrate user statistics updates with trip operations

**Archivos modificados**:
- `backend/src/services/trip_service.py` (+270 líneas)
- `backend/src/services/stats_service.py` (+8 líneas)

---

## Soporte

Para preguntas o issues sobre la integración de estadísticas, consultar:
- Especificación completa: `specs/002-travel-diary/spec.md`
- Plan de implementación: `specs/002-travel-diary/plan.md`
- Tareas detalladas: `specs/002-travel-diary/tasks.md`
