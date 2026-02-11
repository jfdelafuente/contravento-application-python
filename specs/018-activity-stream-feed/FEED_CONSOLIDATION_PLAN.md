# Plan de Consolidación de Feeds

**Fecha**: 2026-02-10
**Objetivo**: Consolidar los 3 feeds existentes en un único Activity Feed modernizado
**Duración estimada**: 2-3 semanas

---

## Situación Actual: 3 Feeds Duplicados

### Feed 1: Feed de Viajes (`/feed`) - Feature 004
- **Endpoint**: `GET /feed/following`
- **Frontend**: `FeedPage.tsx` → `FeedList` → `FeedItem`
- **Datos**: Solo trips completos
- **Estado**: Funcional pero legacy

### Feed 2: Activity Feed (`/activities`) - Feature 018 ✅ NUEVO
- **Endpoint**: `GET /activity-feed`
- **Frontend**: `ActivityFeedPage.tsx` → `ActivityCard` → `LikeButton`
- **Datos**: ActivityFeedItems (trips, photos, achievements)
- **Estado**: Implementado con likes (US2 completo)

### Feed 3: Dashboard Social Feed
- **Endpoint**: `GET /feed/following` (reutiliza Feed 1)
- **Frontend**: `SocialFeedSection` → `SocialFeedItem`
- **Datos**: Trips convertidos a FeedActivity en frontend
- **Estado**: Funcional, embedded en dashboard

### Problemas Actuales

1. **Duplicación de código**: 3 conjuntos de componentes haciendo lo mismo
2. **Duplicación de endpoints**: 2 endpoints backend (`/feed/following` vs `/activity-feed`)
3. **Inconsistencia de features**: Activity Feed tiene likes, Feed de Viajes no
4. **Confusión de usuarios**: ¿Cuál feed usar?
5. **Mantenimiento complejo**: Cambios deben aplicarse en 3 lugares

---

## Estado Objetivo: Activity Feed Único

### Arquitectura Final

```
┌─────────────────────────────────────────────────┐
│  ACTIVITY FEED (Feature 018) - ÚNICO            │
│                                                 │
│  Endpoint: GET /activity-feed                   │
│  Tipos: TRIP_PUBLISHED, PHOTO_UPLOADED,        │
│         ACHIEVEMENT_UNLOCKED                    │
│                                                 │
│  Features:                                      │
│  ✅ Likes (US2 - Implementado)                 │
│  🔜 Comments (US3 - Próximo)                   │
│  🔜 Filters (US5 - Futuro)                     │
└─────────────────────────────────────────────────┘
           ▲                    ▲
           │                    │
    ┌──────┴────────┐    ┌─────┴──────────┐
    │ /activities   │    │ /dashboard     │
    │ (página full) │    │ (widget feed)  │
    └───────────────┘    └────────────────┘
```

### Componentes Consolidados

**Antes** (3 sets):
- `FeedPage` + `FeedList` + `FeedItem`
- `ActivityFeedPage` + `ActivityCard` + `LikeButton`
- `SocialFeedSection` + `SocialFeedItem`

**Después** (1 set reutilizable):
- `ActivityFeedPage` (página completa)
- `ActivityFeedWidget` (widget para dashboard)
- `ActivityCard` (componente común)
- `LikeButton`, `CommentButton` (componentes de interacción)

---

## Plan de Migración (4 Fases)

### FASE 1: Preparación (Semana 1) - Sin Breaking Changes

**Objetivo**: Preparar infraestructura sin romper nada existente

**Tareas**:
1. **Backend**: Crear endpoint `/feed/following` → `/activity-feed` redirect (temporal)
   ```python
   # backend/src/api/feed.py
   @router.get("/feed/following", deprecated=True)
   async def get_following_feed_legacy(db: AsyncSession, current_user: User):
       """Legacy endpoint - redirects to /activity-feed"""
       # Convert to activity feed format
       activities = await FeedService.get_user_feed(...)
       return ActivityFeedResponse(activities=activities)
   ```

2. **Frontend**: Crear `ActivityFeedWidget` componente reutilizable
   ```typescript
   // frontend/src/components/activityFeed/ActivityFeedWidget.tsx
   interface ActivityFeedWidgetProps {
     limit?: number;          // Cuántas actividades mostrar
     showHeader?: boolean;    // Mostrar título
     compact?: boolean;       // Modo compacto para dashboard
   }
   ```

3. **Testing**: Validar que ambos endpoints retornan datos equivalentes
   ```bash
   # Script de comparación
   python backend/scripts/testing/compare_feed_endpoints.py
   ```

**Entregable**: Infraestructura dual (legacy + nuevo) funcionando en paralelo

---

### FASE 2: Migración del Dashboard (Semana 1-2)

**Objetivo**: Migrar SocialFeedSection a usar Activity Feed

**Cambios en `frontend/src/components/dashboard/SocialFeedSection.tsx`**:

**Antes**:
```typescript
import { useInfiniteFeed } from '../../hooks/useFeed'; // Legacy

const SocialFeedSection: React.FC = () => {
  const { trips, isLoading } = useInfiniteFeed(10);

  const activities = trips.map(convertTripToActivity); // Conversión manual

  return activities.map(activity => <SocialFeedItem {...activity} />);
};
```

**Después**:
```typescript
import { useActivityFeed } from '../../hooks/useActivityFeed'; // Nuevo

const SocialFeedSection: React.FC = () => {
  const { activities, isLoading } = useActivityFeed({ limit: 10 });

  // No conversión necesaria - datos ya en formato correcto

  return <ActivityFeedWidget
    activities={activities}
    compact={true}  // Modo dashboard
    limit={10}
  />;
};
```

**Beneficios inmediatos**:
- ✅ Dashboard tiene likes automáticamente
- ✅ Dashboard tendrá comments cuando se implemente US3
- ✅ Menos código (eliminar `convertTripToActivity`)

**Testing**:
- Visual regression tests del dashboard
- Validar que likes funcionan en dashboard
- Performance: dashboard carga en <1s (mismo que antes)

---

### FASE 3: Deprecación de `/feed` (Semana 2)

**Objetivo**: Marcar FeedPage como deprecated y redirigir a ActivityFeedPage

**Cambios en `frontend/src/App.tsx`**:

**Antes**:
```typescript
<Route path="/feed" element={<FeedPage />} />
<Route path="/activities" element={<ActivityFeedPage />} />
```

**Después** (Opción A - Redirect):
```typescript
<Route
  path="/feed"
  element={<Navigate to="/activities" replace />}  // Redirect automático
/>
<Route path="/activities" element={<ActivityFeedPage />} />
```

**Después** (Opción B - Banner de deprecación):
```typescript
<Route path="/feed" element={
  <DeprecatedPage
    message="Esta página ha sido reemplazada por el Activity Feed"
    redirectTo="/activities"
    redirectIn={5} // 5 segundos
  />
} />
<Route path="/activities" element={<ActivityFeedPage />} />
```

**Comunicación a usuarios**:
- Toast notification: "El feed se ha movido a /activities"
- Banner en `/feed` durante 1 mes
- Actualizar navegación principal: "Feed" → "Actividades"

---

### FASE 4: Limpieza y Eliminación (Semana 3)

**Objetivo**: Eliminar código legacy completamente

**Backend - Archivos a eliminar**:
```bash
backend/src/api/feed.py                    # Endpoint legacy
backend/src/services/feed_service.py       # Si solo se usa en feed legacy
backend/tests/integration/test_feed_api.py # Tests del endpoint antiguo
```

**Frontend - Archivos a eliminar**:
```bash
frontend/src/pages/FeedPage.tsx
frontend/src/pages/FeedPage.css
frontend/src/components/feed/FeedList.tsx
frontend/src/components/feed/FeedItem.tsx
frontend/src/components/feed/FeedSkeleton.tsx
frontend/src/hooks/useFeed.ts
frontend/src/services/feedService.ts
frontend/src/components/dashboard/SocialFeedItem.tsx  # Reemplazado por ActivityCard
```

**Database - Migraciones**:
```python
# backend/migrations/versions/XXXXXX_remove_legacy_feed_tables.py
# Si hay tablas específicas del feed antiguo (unlikely)
```

**Estimación de eliminación**: ~1,500 líneas de código

---

## Beneficios de la Consolidación

### 1. Menos Código = Menos Bugs
- **Antes**: 3 implementaciones × potencial de bugs = 3× riesgo
- **Después**: 1 implementación = 1× riesgo

### 2. Features Automáticas
- Dashboard hereda likes sin trabajo adicional
- Dashboard heredará comments cuando se implemente US3
- Dashboard heredará filters cuando se implemente US5

### 3. Mantenimiento Simplificado
- **Antes**: Bug fix → cambiar en 3 lugares
- **Después**: Bug fix → cambiar en 1 lugar

### 4. Consistencia de UX
- Mismo diseño en `/activities` y dashboard
- Mismas interacciones (like, comment)
- Misma performance

### 5. Performance
- **Antes**: 2 endpoints backend duplicados
- **Después**: 1 endpoint optimizado (cursor pagination)

---

## Riesgos y Mitigación

### Riesgo 1: Breaking Changes para Usuarios
**Impacto**: Alto
**Probabilidad**: Media

**Mitigación**:
- ✅ Redirect automático `/feed` → `/activities`
- ✅ Banner de aviso 1 mes antes
- ✅ Mantener endpoint legacy 1 mes con deprecation warning

### Riesgo 2: Performance Degradation
**Impacto**: Alto
**Probabilidad**: Baja

**Mitigación**:
- ✅ Performance tests antes/después
- ✅ Activity Feed ya tiene cursor pagination (más rápido)
- ✅ Load testing con 1000 actividades

### Riesgo 3: Pérdida de Features Específicas
**Impacto**: Medio
**Probabilidad**: Baja

**Mitigación**:
- ✅ Audit de features en FeedPage vs ActivityFeedPage
- ✅ Migrar features únicas antes de deprecar

### Riesgo 4: Bugs en Dashboard Feed
**Impacto**: Medio
**Probabilidad**: Media

**Mitigación**:
- ✅ Visual regression tests
- ✅ E2E tests del dashboard
- ✅ Canary deployment (1% usuarios primero)

---

## Checklist de Migración

### Fase 1: Preparación
- [ ] Crear endpoint redirect `/feed/following` → `/activity-feed`
- [ ] Crear `ActivityFeedWidget` componente
- [ ] Script de comparación de endpoints
- [ ] Tests: ambos endpoints retornan datos equivalentes

### Fase 2: Dashboard
- [ ] Migrar `SocialFeedSection` a `useActivityFeed`
- [ ] Reemplazar `SocialFeedItem` con `ActivityCard`
- [ ] Visual regression tests
- [ ] Validar likes en dashboard

### Fase 3: Deprecación
- [ ] Añadir redirect `/feed` → `/activities`
- [ ] Banner de deprecación en `/feed`
- [ ] Toast notification
- [ ] Actualizar navegación principal

### Fase 4: Limpieza
- [ ] Eliminar `FeedPage.tsx` y componentes
- [ ] Eliminar `useFeed.ts` hook
- [ ] Eliminar endpoint `/feed/following` backend
- [ ] Actualizar tests
- [ ] Code review final
- [ ] Deploy a producción

---

## Timeline Sugerido

```
Semana 1
├─ Día 1-2: FASE 1 - Preparación (infraestructura dual)
├─ Día 3-4: FASE 2 - Migración Dashboard
└─ Día 5:   Testing y validación

Semana 2
├─ Día 1-2: FASE 3 - Deprecación de /feed
├─ Día 3-4: Monitoreo de métricas (¿usuarios usando /activities?)
└─ Día 5:   Ajustes basados en feedback

Semana 3
├─ Día 1-3: FASE 4 - Limpieza de código legacy
├─ Día 4:   Code review y tests finales
└─ Día 5:   Deploy a producción
```

---

## Métricas de Éxito

### Pre-Migración (Baseline)
- Líneas de código: ~3,000 (feeds)
- Endpoints backend: 2 (`/feed/following`, `/activity-feed`)
- Componentes frontend: 3 sets (FeedPage, ActivityFeedPage, Dashboard)
- Load time `/feed`: ~800ms
- Load time dashboard: ~600ms

### Post-Migración (Target)
- Líneas de código: ~1,500 (50% reducción) ✅
- Endpoints backend: 1 (`/activity-feed`) ✅
- Componentes frontend: 1 set + widget ✅
- Load time `/activities`: <1s (mismo o mejor) ✅
- Load time dashboard: <700ms (mismo o mejor) ✅

### Monitoreo (Primeros 30 días)
- Error rate: <0.1% (mismo que baseline)
- User adoption `/activities`: >80% de usuarios migrados
- Tickets de soporte: <5 relacionados a cambio de feed

---

## Notas Técnicas

### Compatibilidad de Datos

**FeedItem (Legacy)** → **ActivityFeedItem (Nuevo)**:
```typescript
// Conversión automática en backend
{
  trip_id: "uuid",           → activity_id: "uuid",
  title: "Ruta Pirineos",    → metadata: { title: "Ruta Pirineos", ... },
  author: {...},             → user: {...},
  likes_count: 10,           → likes_count: 10,  ✅ Compatible
  // NUEVO:
                             → activity_type: "TRIP_PUBLISHED",
                             → is_liked_by_me: false,
}
```

### Query Key Migration

```typescript
// Antes (FeedPage):
queryKey: ['feed', 'following', page]

// Después (ActivityFeedPage):
queryKey: ['activityFeed', limit]

// Invalidación al migrar:
queryClient.invalidateQueries({ queryKey: ['feed'] });
queryClient.invalidateQueries({ queryKey: ['activityFeed'] });
```

---

## Próximos Pasos Inmediatos

1. **Review de este plan** con el equipo
2. **Crear feature flag** `ENABLE_FEED_CONSOLIDATION`
3. **Iniciar FASE 1** (Preparación)
4. **Daily standup** para tracking de progreso

---

**Autor**: Claude
**Última actualización**: 2026-02-10
**Estado**: Propuesto - Pendiente de aprobación
