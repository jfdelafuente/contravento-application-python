# Feature Specification: Activity Stream Feed

**Feature Branch**: `018-activity-stream-feed`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Activity Stream: Feed con likes, comments y achievements"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Activity Feed from Followed Users (Priority: P1) 🎯 MVP

Un ciclista autenticado accede a su feed de actividades y ve una línea temporal con las actividades recientes de los usuarios que sigue, incluyendo viajes publicados, fotos subidas y logros conseguidos.

**Why this priority**: Este es el core del feature. Sin el feed, no hay valor. Es el equivalente al timeline de redes sociales - muestra contenido relevante basado en la red social del usuario. Entrega valor inmediato al mostrar qué están haciendo los ciclistas que el usuario sigue.

**Independent Test**: Un usuario con al menos 3 usuarios seguidos puede acceder a `/feed` y ver una lista cronológica de actividades recientes (viajes publicados, fotos, logros). El feed funciona con datos existentes sin necesitar las features de likes/comments/achievements.

**Acceptance Scenarios**:

1. **Given** soy un usuario autenticado que sigue a 5 ciclistas, **When** accedo a la página de feed, **Then** veo una lista cronológica de las últimas 20 actividades de esos usuarios (viajes publicados, fotos subidas, logros conseguidos)

2. **Given** estoy visualizando el feed, **When** scrolleo hacia abajo, **Then** se cargan automáticamente las siguientes 20 actividades (infinite scroll o paginación)

3. **Given** un usuario que sigo publica un nuevo viaje, **When** refresco mi feed, **Then** veo la nueva actividad en la parte superior del feed

4. **Given** no sigo a ningún usuario, **When** accedo al feed, **Then** veo un mensaje sugerente para descubrir usuarios y empezar a seguirlos

5. **Given** estoy viendo el feed, **When** hago clic en una tarjeta de actividad, **Then** soy redirigido al detalle correspondiente (trip detail, user profile, achievement detail)

---

### User Story 2 - Like Activities in Feed (Priority: P2)

Un usuario puede dar "me gusta" a las actividades que aparecen en su feed (viajes, fotos), expresando apreciación por el contenido de otros ciclistas.

**Why this priority**: Los likes son la interacción social más simple y de bajo friction. Añaden engagement sin requerir esfuerzo del usuario. Es el primer paso para construir comunidad activa.

**Independent Test**: Un usuario puede hacer clic en un botón "like" en cualquier actividad del feed, ver el contador incrementarse, y el like queda persistido al recargar la página. Funciona independientemente de comments y achievements.

**Acceptance Scenarios**:

1. **Given** estoy viendo una actividad en el feed, **When** hago clic en el botón "me gusta", **Then** el contador de likes se incrementa y el botón cambia de estado (filled/highlighted)

2. **Given** he dado like a una actividad, **When** vuelvo a hacer clic en el botón "me gusta", **Then** el like se elimina (unlike), el contador decrementa y el botón vuelve a su estado inicial

3. **Given** varias personas han dado like a una actividad, **When** visualizo esa actividad, **Then** veo el número total de likes (ej: "12 personas") y los avatares de algunos usuarios que dieron like

4. **Given** he dado like a una actividad, **When** el autor de esa actividad accede a su perfil, **Then** recibe una notificación de que le han dado like

5. **Given** estoy viendo una actividad con 50+ likes, **When** hago clic en el contador de likes, **Then** veo una lista modal con todos los usuarios que dieron like

---

### User Story 3 - Comment on Activities (Priority: P2)

Un usuario puede añadir comentarios a las actividades del feed, iniciando conversaciones con otros ciclistas sobre rutas, consejos o experiencias.

**Why this priority**: Comments son la interacción social de mayor engagement. Generan conversaciones y comunidad. Aunque más complejos que likes, son esenciales para convertir el feed en una experiencia social rica.

**Independent Test**: Un usuario puede escribir un comentario en una actividad, verlo publicado inmediatamente, y otros usuarios pueden leer ese comentario. Funciona independientemente de likes y achievements.

**Acceptance Scenarios**:

1. **Given** estoy viendo una actividad en el feed, **When** escribo un comentario en el campo de texto y presiono "Enviar", **Then** el comentario aparece inmediatamente debajo de la actividad con mi nombre y timestamp

2. **Given** una actividad tiene 3 comentarios, **When** visualizo esa actividad en el feed, **Then** veo los comentarios ordenados cronológicamente (más antiguo primero) con nombre de autor, foto de perfil y timestamp

3. **Given** estoy viendo una actividad con más de 5 comentarios, **When** inicialmente la actividad se muestra, **Then** veo los primeros 3 comentarios y un link "Ver más comentarios (X)" para expandir la lista completa

4. **Given** he escrito un comentario, **When** el autor de la actividad accede a su perfil, **Then** recibe una notificación de que han comentado su actividad

5. **Given** soy el autor de un comentario, **When** hago clic en "Eliminar" en mi comentario, **Then** el comentario se elimina inmediatamente y desaparece del feed

6. **Given** estoy escribiendo un comentario, **When** escribo más de 500 caracteres, **Then** veo un contador de caracteres y un mensaje indicando el límite

---

### User Story 4 - View Achievement Notifications in Feed (Priority: P3)

El feed muestra automáticamente cuando los usuarios seguidos consiguen logros (achievements), como "Primera ruta de 100km", "10 viajes publicados", etc., gamificando la experiencia y celebrando hitos.

**Why this priority**: Los achievements añaden gamificación y motivación, pero no son esenciales para el core del feed. Pueden implementarse después de tener el feed básico funcionando.

**Independent Test**: Cuando un usuario seguido desbloquea un achievement, aparece automáticamente en el feed como un tipo especial de actividad. Funciona independientemente de likes/comments.

**Acceptance Scenarios**:

1. **Given** un usuario que sigo completa su 10º viaje y desbloquea el achievement "Explorador Activo", **When** refresco mi feed, **Then** veo una tarjeta especial mostrando el achievement con icono, nombre y descripción

2. **Given** estoy viendo un achievement en el feed, **When** hago clic en la tarjeta del achievement, **Then** veo el detalle del achievement con criterios para desbloquearlo y lista de usuarios que lo han conseguido

3. **Given** varios usuarios que sigo han desbloqueado el mismo achievement, **When** visualizo el feed, **Then** cada achievement aparece como una actividad separada para cada usuario

4. **Given** un usuario desbloquea múltiples achievements en el mismo día, **When** visualizo el feed, **Then** veo una tarjeta agrupada mostrando "Juan consiguió 3 logros" con la lista de achievements

---

### User Story 5 - Filter and Sort Feed (Priority: P3)

Los usuarios pueden filtrar el feed por tipo de actividad (solo viajes, solo fotos, solo achievements) y ordenar por diferentes criterios (más reciente, más popular).

**Why this priority**: Los filtros mejoran la experiencia cuando hay mucho contenido, pero no son esenciales para el MVP. Es una progressive enhancement.

**Independent Test**: Un usuario puede seleccionar filtros (ej: "Solo viajes") y el feed se actualiza mostrando solo ese tipo de actividad. Funciona independientemente de otras features.

**Acceptance Scenarios**:

1. **Given** estoy viendo el feed completo, **When** selecciono el filtro "Solo viajes", **Then** el feed muestra únicamente actividades de tipo "viaje publicado"

2. **Given** estoy viendo el feed, **When** selecciono ordenar por "Más popular", **Then** las actividades se reordenan por número de likes + comments (descendente)

3. **Given** he aplicado filtros "Solo fotos" y "Más popular", **When** refresco la página, **Then** los filtros persisten y el feed mantiene la misma vista

4. **Given** estoy viendo el feed filtrado, **When** hago clic en "Limpiar filtros", **Then** el feed vuelve a mostrar todas las actividades ordenadas por más reciente

---

### Edge Cases

- **Feed vacío**: ¿Qué se muestra cuando un usuario no sigue a nadie o los usuarios seguidos no tienen actividad reciente?
  - Mostrar mensaje motivacional con sugerencias de usuarios populares para seguir

- **Actividad eliminada**: ¿Qué pasa si un usuario elimina un viaje/foto que aparece en el feed de otros?
  - La actividad desaparece del feed inmediatamente (o muestra placeholder "Contenido no disponible")

- **Usuario bloqueado**: ¿Cómo afecta bloquear a un usuario al feed?
  - Las actividades del usuario bloqueado no aparecen en el feed (filtrado a nivel backend)

- **Comentarios ofensivos**: ¿Cómo se manejan reportes de comentarios inapropiados?
  - **RESOLVED**: MVP incluirá botón de reporte que almacena reportes en base de datos, pero sin UI de moderación. Administradores pueden consultar reportes mediante queries SQL directas. UI de moderación se implementará en iteración futura. Esta aproximación permite recopilar datos sobre frecuencia de abuso con mínimo esfuerzo de desarrollo (+1 día).

- **Concurrencia en likes**: ¿Qué pasa si dos usuarios dan like simultáneamente a la misma actividad?
  - El contador debe incrementarse correctamente usando transacciones atómicas

- **Feed muy largo**: ¿Hay límite de actividades cargadas en memoria?
  - Usar paginación o virtual scrolling para cargar máximo 100 actividades en memoria

- **Actividades duplicadas**: ¿Qué pasa si el mismo viaje se publica múltiples veces (draft → published)?
  - Solo la publicación inicial aparece en el feed, no los cambios posteriores

---

## Requirements *(mandatory)*

### Functional Requirements

**Feed & Activities**:

- **FR-001**: System MUST display a chronological activity feed showing activities from followed users only (not from users the current user doesn't follow)

- **FR-002**: System MUST support these activity types in the feed:
  - Trip published (when user publishes a new trip)
  - Photo uploaded (when user adds photos to a trip)
  - Achievement unlocked (when user earns a badge/achievement)

- **FR-003**: System MUST load feed activities in batches of 20 items with pagination or infinite scroll

- **FR-004**: System MUST show activity metadata including: author name, author photo, activity type, timestamp (relative time: "hace 2 horas", "ayer", "3 días"), and preview content

- **FR-005**: System MUST display an empty state message with follow suggestions when user has no followed users or no recent activity

**Likes**:

- **FR-006**: Users MUST be able to like activities in the feed with a single click/tap

- **FR-007**: System MUST allow users to unlike previously liked activities

- **FR-008**: System MUST display total like count for each activity

- **FR-009**: System MUST show avatars of first 3-5 users who liked an activity (visual engagement indicators)

- **FR-010**: System MUST prevent duplicate likes (one like per user per activity)

- **FR-011**: System MUST create a notification for activity author when someone likes their content

**Comments**:

- **FR-012**: Users MUST be able to write comments on activities with a maximum length of 500 characters

- **FR-013**: System MUST display comments chronologically (oldest first) below each activity

- **FR-014**: System MUST show comment metadata: author name, author photo, comment text, timestamp

- **FR-015**: System MUST allow users to delete their own comments

- **FR-016**: System MUST collapse comments beyond the first 3 (show "Ver más comentarios (X)" link)

- **FR-017**: System MUST create a notification for activity author when someone comments on their content

- **FR-018**: System MUST sanitize comment HTML to prevent XSS attacks

**Achievements in Feed**:

- **FR-019**: System MUST automatically create feed activity when a user unlocks an achievement

- **FR-020**: System MUST display achievement activities with special visual styling (icon, badge, description)

- **FR-021**: System MUST group multiple achievements unlocked on the same day into a single feed activity ("Usuario X consiguió 3 logros")

**Filtering & Sorting**:

- **FR-022**: Users MUST be able to filter feed by activity type: All, Trips only, Photos only, Achievements only

- **FR-023**: Users MUST be able to sort feed by: Most recent (default), Most popular (likes + comments count)

- **FR-024**: System MUST persist filter/sort preferences in URL query params for shareability

**Navigation**:

- **FR-025**: Users MUST be able to click on any activity to navigate to its detail page (trip detail, user profile, achievement detail)

- **FR-026**: System MUST provide a clickable link to the activity author's profile from every feed item

**Performance**:

- **FR-027**: System MUST load the initial feed page (20 activities) in under 2 seconds on standard connection

- **FR-028**: System MUST use eager loading or caching to avoid N+1 queries for likes/comments counts

### Key Entities

- **ActivityFeedItem**: Represents an activity in the feed
  - Attributes: activity_id, user_id (author), activity_type (TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED), related_id (trip_id, photo_id, achievement_id), created_at, metadata (JSON with type-specific data)
  - Relationships: belongs to User (author), has many Likes, has many Comments

- **Like**: Represents a like on an activity
  - Attributes: like_id, user_id, activity_id, created_at
  - Relationships: belongs to User, belongs to ActivityFeedItem
  - Constraint: Unique constraint on (user_id, activity_id) - one like per user per activity

- **Comment**: Represents a comment on an activity
  - Attributes: comment_id, user_id (author), activity_id, text (max 500 chars), created_at
  - Relationships: belongs to User (author), belongs to ActivityFeedItem

- **Notification**: Represents a notification for user (for likes/comments)
  - Attributes: notification_id, user_id (recipient), type (LIKE, COMMENT), related_id (like_id, comment_id), read (boolean), created_at
  - Relationships: belongs to User (recipient)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can load and view their activity feed in under 2 seconds on standard connection

- **SC-002**: 80% of users who access the feed scroll through at least 3 pages of activities (indicating engagement)

- **SC-003**: Average of 5+ likes per trip activity within 24 hours of publication (indicating social engagement)

- **SC-004**: Average of 2+ comments per trip activity within 48 hours of publication

- **SC-005**: Users can like/unlike an activity and see the change reflected immediately (<200ms perceived latency)

- **SC-006**: Feed correctly handles 100+ followed users without performance degradation

- **SC-007**: Feed handles concurrent likes/comments from multiple users without data inconsistencies

- **SC-008**: 90% of users successfully interact with the feed (like, comment, or click through) on first visit

- **SC-009**: Feed updates with new activities within 5 minutes of activity creation (real-time or near real-time)

- **SC-010**: Achievement notifications appear in feed immediately after being unlocked (within 1 minute)

---

## Assumptions

- Users are already familiar with social feed patterns (Facebook, Twitter, Instagram) - no extensive UX education needed
- The Follow/Unfollow feature already exists from Feature 004 (Social Network)
- Achievement system already exists or will be developed in parallel
- Notifications infrastructure exists or will be added as part of this feature
- Feed activities are created automatically when users publish trips/photos/achievements (event-driven)
- Default ordering is chronological (most recent first) unless user changes filter
- Comments are plain text only (no rich text, images, or reactions) for MVP
- Like notifications are non-intrusive (badge count, not push notifications)
- Feed data retention: activities older than 90 days may be archived or deprioritized
- Activity privacy follows trip privacy settings (private trips don't generate feed activities)

---

## Dependencies

- **Feature 004 (Social Network)**: Follow/Unfollow functionality must exist to determine whose activities appear in feed
- **Achievement System**: Achievement unlocking logic must exist to generate achievement activities
- **Notification System**: Basic notification infrastructure needed for like/comment notifications
- **Trip/Photo Models**: Existing trip and photo entities to reference in feed activities

---

## Out of Scope (For Future Iterations)

- Real-time feed updates (WebSocket/SSE) - MVP uses refresh or manual polling
- Rich media in comments (images, GIFs, emojis)
- Comment reactions or nested replies (threading)
- Feed algorithm (personalized ranking, ML-based recommendations)
- Feed sharing (share feed permalink with non-authenticated users)
- Activity editing/updating (if user edits a trip, feed activity doesn't update)
- Muting/hiding specific activities or users
- Trending activities or "Discover" feed beyond followed users
- Activity insights/analytics (who viewed, engagement metrics)
- Comment moderation tools beyond basic delete

---

## Notes

- **UX Pattern Reference**: Instagram Feed (activity cards), Twitter (chronological timeline), Strava (activity feed with likes/comments)
- **Privacy**: All feed activities respect source content privacy (private trips don't generate activities)
- **Scalability**: Consider pagination strategy carefully - infinite scroll vs numbered pages affects caching and UX
- **Localization**: All timestamps should use Spanish relative time ("hace 2 horas", "ayer", "hace 3 días")
- **Accessibility**: Feed should be keyboard navigable, screen reader friendly
- **Mobile First**: Majority of users likely access from mobile - optimize touch targets and scrolling
