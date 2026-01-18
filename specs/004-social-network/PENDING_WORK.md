# Feature 004 - Trabajo Pendiente

**Branch**: `004-social-network`
**Última actualización**: 2026-01-18
**Estado actual**: US1 + US2 implementadas, testing al 50%

---

## Resumen Ejecutivo

### ✅ Completado (US1 + US2)

**Backend** (100%):
- Modelos: `Follow`, `Like` con relaciones y constraints
- Servicios: `SocialService`, `LikeService` completos
- Endpoints: `/feed`, `/trips/{trip_id}/like` (POST/DELETE)
- Validaciones: prevent self-like, duplicate like, authentication

**Frontend** (100%):
- Páginas: `PublicFeedPage` con infinite scroll
- Componentes: `LikeButton`, `PublicTripCard`
- Hooks: `useLike` con optimistic UI
- Servicios: `likeService` para API calls

**Testing Manual** (50% - 14/28 tests):
- US1: 5/8 tests pasados (62%)
- US2: 8/10 tests pasados (80%)
- Integration: 3/3 tests pasados (100%)

---

## 🔴 Trabajo Pendiente - Feature 004

### Fase 1: Completar Testing Manual US1/US2 (Actual)

**Objetivo**: Alcanzar 90%+ coverage en testing manual antes de merge

**Tests Funcionales Pendientes** (3 tests):

1. **TC-US1-004: Infinite Scroll Pagination**
   - Verificar que al scrollear al final, se cargan 10 trips más
   - Validar que no hay duplicados
   - Confirmar que el loading spinner aparece durante carga

2. **TC-US1-005: Skeleton Loading State**
   - Verificar skeleton placeholders durante carga inicial
   - Confirmar transición suave skeleton → contenido real

3. **TC-US2-006: Prevent Duplicate Like (Backend)**
   - Intentar dar like dos veces al mismo viaje vía API
   - Verificar que backend retorna error 409 Conflict
   - Confirmar que frontend no permite double-click

**Tests de Performance** (4 tests):

1. **PV-001: Feed Load <1s (SC-001)**
   - Medir tiempo de carga inicial del feed
   - Target: <1 segundo (p95)
   - Herramienta: Chrome DevTools Network tab

2. **PV-002: Pagination <500ms (SC-002)**
   - Medir tiempo de carga de página siguiente
   - Target: <500ms (p95)
   - Validar smooth scrolling sin jank

3. **PV-003: Like <200ms (SC-006)**
   - Medir tiempo de respuesta de POST /like
   - Target: <200ms (p95)
   - Ejecutar 10 likes y verificar percentil 95

4. **PV-004: Unlike <100ms (SC-007)**
   - Medir tiempo de respuesta de DELETE /like
   - Target: <100ms (p95)
   - Más rápido que like (no crea registro)

**Tests de Accessibility** (3 tests):

1. **A11Y-001: Keyboard Navigation**
   - Tab para navegar entre elementos
   - Enter/Space para activar like button
   - Verificar focus indicator visible

2. **A11Y-002: Screen Reader Support**
   - NVDA/VoiceOver anuncia "Trip card: {title}"
   - Like button anuncia estado: "pressed/not pressed"
   - ARIA live regions para updates

3. **A11Y-003: Color Contrast**
   - Lighthouse accessibility audit
   - Verificar contraste ≥4.5:1 (WCAG AA)
   - Sin violaciones de accesibilidad

**Estimación Fase 1**: 2-3 horas

---

### Fase 2: Implementar Follow/Unfollow UI (Bloqueador)

**Objetivo**: Desbloquear TC-US1-002 (Feed Content - Followed Users)

**Componentes a Crear**:

1. **FollowButton Component** (`frontend/src/components/social/FollowButton.tsx`):
   ```typescript
   interface FollowButtonProps {
     userId: string;
     initialFollowing: boolean;
     size?: 'small' | 'medium' | 'large';
   }
   ```
   - Optimistic UI (like LikeButton)
   - Loading state con spinner
   - Error rollback
   - ARIA accessibility

2. **useFollow Hook** (`frontend/src/hooks/useFollow.ts`):
   ```typescript
   const { isFollowing, isLoading, toggleFollow } = useFollow(userId, initialFollowing);
   ```
   - Lógica similar a useLike
   - Optimistic updates
   - Spanish error messages

3. **followService** (`frontend/src/services/followService.ts`):
   ```typescript
   export const followUser = async (userId: string): Promise<void>
   export const unfollowUser = async (userId: string): Promise<void>
   ```

**Integración**:
- Añadir FollowButton a `UserProfilePage` (header section)
- Añadir FollowButton a `PublicTripCard` (junto al autor)
- Mostrar contador followers/following en perfil

**Tests**:
- TC-US1-002: Feed Content (Followed Users) - ahora desbloqueado
- Nuevos tests de Follow/Unfollow (optimistic UI, error handling)

**Estimación Fase 2**: 3-4 horas

---

### Fase 3: Implementar Likes List UI (Opcional)

**Objetivo**: Desbloquear TC-US2-008 (Get Likes List)

**Componentes a Crear**:

1. **LikesListModal** (`frontend/src/components/likes/LikesListModal.tsx`):
   - Modal overlay con lista de usuarios que dieron like
   - Avatar + nombre + botón Follow (si aplica)
   - Scroll infinito si >50 likes
   - Close button (X)

2. **useTripLikes Hook** (`frontend/src/hooks/useTripLikes.ts`):
   ```typescript
   const { likes, isLoading, error, loadMore } = useTripLikes(tripId);
   ```

**Integración**:
- Click en contador de likes → abre LikesListModal
- Mostrar en TripDetailPage y PublicTripCard

**Estimación Fase 3**: 2-3 horas (opcional - no bloqueante)

---

### Fase 4: Merge a Develop

**Criterios de Merge**:
- ✅ Testing manual ≥90% (actualmente 50%)
- ✅ Follow/Unfollow UI implementado
- ✅ Performance targets alcanzados (SC-001, SC-002, SC-006, SC-007)
- ✅ Accessibility tests pasados (A11Y-001, A11Y-002, A11Y-003)
- ✅ 2 tests bloqueados documentados como "deferred to Phase 2"

**Pasos**:
1. Revisar TESTING_MANUAL_US1_US2.md con resultados finales
2. Actualizar spec.md con implementación completa
3. Crear PR: `004-social-network` → `develop`
4. Code review (si aplica)
5. Merge squash (mantener commits limpios)

**Estimación Fase 4**: 1 hora

---

## 🟡 Trabajo Futuro - US3, US4, US5 (Diferido)

### US3: Comentarios en Viajes (Priority: P3)

**Scope**:
- Backend: modelo `Comment`, endpoints `/trips/{trip_id}/comments` (GET/POST/PUT/DELETE)
- Frontend: `CommentList`, `CommentForm`, `CommentItem` components
- Features: editar, eliminar, moderación del autor
- Validación: max 500 caracteres, paginación >50 comentarios

**Estimación**: 6-8 horas

---

### US4: Compartir Viajes (Priority: P4)

**Scope**:
- Backend: modelo `Share`, endpoints `/trips/{trip_id}/share` (POST/DELETE)
- Frontend: `ShareButton`, `ShareModal` components
- Features: comentario opcional (200 chars), contador de shares
- Validación: cooldown 1 hora para mismo viaje

**Estimación**: 4-5 horas

---

### US5: Notificaciones de Interacciones (Priority: P5)

**Scope**:
- Backend: modelo `Notification`, endpoints `/notifications` (GET/PUT)
- Frontend: `NotificationCenter`, `NotificationBadge` components
- Features: likes, comentarios, shares, follows
- Real-time: WebSockets o polling

**Estimación**: 8-10 horas (complejo - requiere real-time)

---

## 📊 Resumen de Esfuerzo Restante

### Para Merge US1/US2 a Develop:
- **Mínimo**: 2-3 horas (completar tests funcionales + performance)
- **Recomendado**: 5-7 horas (+ Follow/Unfollow UI para desbloquear TC-US1-002)
- **Completo**: 7-10 horas (+ Likes List UI)

### Para Completar Feature 004 (US1-US5):
- **Total**: +18-23 horas adicionales (US3 + US4 + US5)

---

## 🎯 Próxima Sesión Recomendada

**Opción A - Continuar Testing Manual** (2-3 horas):
1. Ejecutar TC-US1-004, TC-US1-005, TC-US2-006 (funcionales)
2. Ejecutar PV-001, PV-002, PV-003, PV-004 (performance)
3. Ejecutar A11Y-001, A11Y-002, A11Y-003 (accessibility)
4. Actualizar TESTING_MANUAL_US1_US2.md con resultados
5. Si performance targets OK → preparar merge

**Opción B - Implementar Follow/Unfollow** (3-4 horas):
1. Crear FollowButton component
2. Crear useFollow hook
3. Crear followService
4. Integrar en UserProfilePage y PublicTripCard
5. Probar TC-US1-002 (ahora desbloqueado)

**Opción C - Pausar Feature 004, Trabajar en Otra Cosa**:
- US1/US2 ya están funcionales y probados al 50%
- Se puede mergear con tests diferidos documentados
- Continuar con otra feature prioritaria
- Retomar 004 después para completar US3/US4/US5

**Recomendación**: Opción A (completar testing) → luego decidir merge vs Opción B

---

## 📁 Archivos Clave

### Testing:
- `specs/004-social-network/TESTING_MANUAL_US1_US2.md` - Guía de testing con checklist

### Backend:
- `backend/src/models/like.py` - Modelo Like
- `backend/src/models/social.py` - Modelo Follow
- `backend/src/services/like_service.py` - Lógica de likes
- `backend/src/services/social_service.py` - Lógica de follows
- `backend/src/api/feed.py` - Feed endpoint
- `backend/src/api/likes.py` - Likes endpoints

### Frontend:
- `frontend/src/pages/PublicFeedPage.tsx` - Página de feed
- `frontend/src/components/likes/LikeButton.tsx` - Botón de like
- `frontend/src/components/PublicTripCard.tsx` - Card de viaje
- `frontend/src/hooks/useLike.ts` - Hook de likes
- `frontend/src/services/likeService.ts` - API calls

### Especificación:
- `specs/004-social-network/spec.md` - Especificación completa (US1-US5)
- `specs/004-social-network/plan.md` - Plan de implementación
- `specs/004-social-network/tasks.md` - Tareas técnicas

---

**Última actualización**: 2026-01-18
**Mantenido por**: Claude Code
