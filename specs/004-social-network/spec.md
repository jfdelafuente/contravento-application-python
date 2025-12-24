# Feature Specification: Red Social y Feed de Ciclistas

**Feature Branch**: `004-social-network`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Red social de ciclistas con feed personalizado, interacciones y comentarios"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Feed Personalizado de Viajes (Priority: P1)

Un ciclista registrado quiere descubrir nuevos viajes y rutas publicados por otros usuarios de la comunidad. Accede al feed principal de ContraVento donde ve viajes recientes de usuarios que sigue y de la comunidad general, organizados cronológicamente.

**Why this priority**: El feed es la funcionalidad core de la red social. Sin él, los usuarios solo ven sus propios viajes y los de perfiles que buscan manualmente. El feed crea la sensación de comunidad, permite el descubrimiento de contenido, y es esencial para retención y engagement.

**Independent Test**: Puede ser probado creando múltiples cuentas con viajes publicados, siguiendo a algunos usuarios, accediendo al feed, y verificando que muestra viajes de usuarios seguidos y de la comunidad en orden cronológico con capacidad de paginación.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** accede a la página de feed/inicio, **Then** ve una lista de viajes recientes publicados por usuarios que sigue y de la comunidad
2. **Given** un feed mostrándose, **When** se carga, **Then** muestra los viajes más recientes primero (orden cronológico inverso) con paginación de 10 viajes por página
3. **Given** un viaje en el feed, **When** se visualiza, **Then** muestra: foto de portada, título, autor con avatar, fecha de publicación, distancia, ubicación, extracto de descripción (primeras 150 caracteres)
4. **Given** un usuario viendo el feed, **When** hace clic en un viaje, **Then** accede a la vista completa del viaje con toda su información
5. **Given** un usuario viendo el feed, **When** hace scroll hasta el final de la página, **Then** carga automáticamente los siguientes 10 viajes (infinite scroll)
6. **Given** un usuario que no sigue a nadie, **When** accede al feed, **Then** ve viajes populares/recientes de toda la comunidad como recomendaciones

---

### User Story 2 - Likes/Me Gusta en Viajes (Priority: P2)

Un ciclista encuentra un viaje en el feed o perfil de otro usuario que le inspira o le parece interesante. Quiere expresar su aprecio dando "me gusta" al viaje. Esto sirve tanto como feedback positivo para el autor como para marcar viajes de interés personal.

**Why this priority**: Los likes son la forma más simple y universal de interacción social. Requieren mínimo esfuerzo del usuario pero proporcionan feedback valioso al creador de contenido. Es la segunda interacción más importante después del feed.

**Independent Test**: Puede ser probado visualizando un viaje, dando like, verificando que el contador aumenta, quitando el like, y confirmando que los cambios se reflejan inmediatamente tanto en el viaje como en el perfil del usuario.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado viendo un viaje, **When** hace clic en el icono de corazón/like, **Then** el like se registra, el icono cambia a estado activo, y el contador de likes incrementa en 1
2. **Given** un usuario que ya dio like a un viaje, **When** hace clic nuevamente en el icono, **Then** el like se quita, el icono vuelve a inactivo, y el contador decrementa en 1
3. **Given** cualquier usuario viendo un viaje, **When** ve el contador de likes, **Then** muestra el número total de likes que ha recibido el viaje
4. **Given** un usuario que dio like a varios viajes, **When** accede a su perfil en sección "Viajes que me gustan", **Then** ve una lista de todos los viajes a los que dio like
5. **Given** un autor de viaje, **When** su viaje recibe likes, **Then** puede ver quiénes dieron like (lista de usuarios con avatares)
6. **Given** un usuario no autenticado, **When** intenta dar like, **Then** es redirigido al login

---

### User Story 3 - Comentarios en Viajes (Priority: P3)

Un ciclista experimentado ve el viaje de otro usuario sobre la Transpirenaica. Tiene preguntas sobre el equipo usado o quiere compartir consejos útiles. Escribe un comentario en el viaje para intercambiar información y crear conversación con el autor y otros interesados.

**Why this priority**: Los comentarios generan conversación y comunidad más profunda que los likes, pero requieren más esfuerzo. Son valiosos para intercambiar consejos prácticos y crear engagement duradero, pero no son esenciales para la funcionalidad básica del feed.

**Independent Test**: Puede ser probado visualizando un viaje, escribiendo un comentario, publicándolo, verificando que aparece en la sección de comentarios, editándolo, eliminándolo, y confirmando que otros usuarios también pueden comentar y ver todos los comentarios.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado viendo un viaje, **When** escribe un comentario (hasta 500 caracteres) y hace clic en "Publicar", **Then** el comentario aparece en la sección de comentarios del viaje con su avatar, nombre, y timestamp
2. **Given** un viaje con comentarios, **When** se visualiza, **Then** muestra todos los comentarios en orden cronológico (más antiguos primero) debajo del contenido del viaje
3. **Given** un usuario que escribió un comentario, **When** quiere modificarlo, **Then** puede editarlo (muestra "editado" junto al timestamp) o eliminarlo completamente
4. **Given** el autor del viaje, **When** ve comentarios en su viaje, **Then** puede eliminar comentarios inapropiados (como moderador de su propio contenido)
5. **Given** un viaje con múltiples comentarios, **When** se visualiza, **Then** muestra el contador de comentarios junto al viaje en el feed y en la vista completa
6. **Given** un usuario no autenticado, **When** ve un viaje con comentarios, **Then** puede leer los comentarios pero no puede escribir (botón de comentar redirige a login)

---

### User Story 4 - Compartir Viajes (Priority: P4)

Un ciclista encuentra un viaje increíble sobre el Camino de Santiago que quiere recomendar a otros ciclistas de su red. Comparte el viaje, creando una referencia en su propio feed para que sus seguidores lo descubran.

**Why this priority**: Compartir amplifica el alcance del contenido y ayuda en el descubrimiento, pero es una capa adicional de funcionalidad social. Los usuarios pueden lograr objetivos similares comentando o enviando enlaces directamente. Mejora el engagement pero no es esencial.

**Independent Test**: Puede ser probado visualizando un viaje, compartiéndolo, verificando que aparece en el feed del usuario como contenido compartido con atribución al autor original, y confirmando que los seguidores pueden verlo.

**Acceptance Scenarios**:

1. **Given** un usuario viendo un viaje de otro ciclista, **When** hace clic en "Compartir", **Then** puede añadir un comentario opcional (hasta 200 caracteres) y publicar el share
2. **Given** un viaje compartido, **When** aparece en el feed del usuario que compartió, **Then** muestra claramente: el viaje original con toda su info, atribución al autor original, el comentario del usuario que compartió, y timestamp del share
3. **Given** los seguidores del usuario que compartió, **When** ven su feed, **Then** aparece el viaje compartido mezclado cronológicamente con otros viajes
4. **Given** un viaje, **When** ha sido compartido múltiples veces, **Then** muestra el contador de veces compartido
5. **Given** un usuario que compartió un viaje, **When** quiere eliminar el share, **Then** puede hacerlo sin afectar el viaje original
6. **Given** un usuario viendo un viaje compartido, **When** hace clic en él, **Then** accede a la vista completa del viaje original del autor

---

### User Story 5 - Notificaciones de Interacciones (Priority: P5)

Un ciclista que publicó un viaje quiere saber cuándo otros usuarios interactúan con su contenido (likes, comentarios, shares). Recibe notificaciones para mantenerse informado y responder a comentarios o agradecer el engagement.

**Why this priority**: Las notificaciones mejoran el engagement al cerrar el loop de feedback, pero la funcionalidad social básica puede trabajar sin ellas. Los usuarios pueden revisar manualmente sus viajes para ver interacciones. Es una mejora de UX valiosa pero no crítica.

**Independent Test**: Puede ser probado creando un viaje con una cuenta, interactuando con ese viaje desde otra cuenta (like, comentario, share), y verificando que el autor recibe notificaciones en un centro de notificaciones con capacidad de marcar como leídas.

**Acceptance Scenarios**:

1. **Given** un usuario cuyo viaje recibe un like, **When** la interacción ocurre, **Then** recibe una notificación: "[Usuario] le gustó tu viaje [Título]"
2. **Given** un usuario cuyo viaje recibe un comentario, **When** se publica el comentario, **Then** recibe una notificación con extracto: "[Usuario] comentó en tu viaje: [primeras 50 caracteres]"
3. **Given** un usuario cuyo viaje es compartido, **When** ocurre el share, **Then** recibe una notificación: "[Usuario] compartió tu viaje [Título]"
4. **Given** un usuario con notificaciones pendientes, **When** accede a la plataforma, **Then** ve un indicador visual (badge con número) en el icono de notificaciones
5. **Given** un usuario accediendo al centro de notificaciones, **When** lo abre, **Then** ve una lista de todas sus notificaciones ordenadas por fecha (más recientes primero) con estado leído/no leído
6. **Given** una notificación, **When** el usuario hace clic en ella, **Then** lo lleva directamente al viaje relacionado y marca la notificación como leída

---

### Edge Cases

- ¿Qué ocurre si un viaje compartido es eliminado por su autor original?
- ¿Cómo se manejan comentarios ofensivos o spam antes de implementar moderación automática?
- ¿Qué sucede si un usuario intenta dar like a un viaje que ya no existe?
- ¿Cómo se comporta el feed si un usuario no sigue a nadie y no hay viajes recientes en la comunidad?
- ¿Qué ocurre si un viaje recibe 1000+ comentarios? ¿Se paginan?
- ¿Cómo se previene el spam de likes (dar y quitar like repetidamente)?
- ¿Qué sucede con las notificaciones cuando un usuario elimina su comentario o like?
- ¿Cómo se maneja el feed cuando hay 10,000 viajes en la plataforma? ¿Rendimiento de consultas?
- ¿Qué ocurre si un usuario comparte el mismo viaje múltiples veces?
- ¿Cómo se ordena el feed cuando hay viajes con igual timestamp?

## Requirements *(mandatory)*

### Functional Requirements

**Feed de Viajes:**

- **FR-001**: El sistema DEBE mostrar un feed personalizado de viajes para usuarios autenticados
- **FR-002**: El feed DEBE incluir viajes de usuarios que el usuario autenticado sigue, ordenados cronológicamente (más recientes primero)
- **FR-003**: Si el usuario no sigue a nadie o hay pocos viajes, el feed DEBE incluir viajes populares/recientes de la comunidad
- **FR-004**: Cada item del feed DEBE mostrar: foto de portada (si existe), título del viaje, autor (nombre + avatar), fecha de publicación, distancia, ubicación, extracto de descripción (150 caracteres)
- **FR-005**: El feed DEBE implementar paginación mostrando 10 viajes por página
- **FR-006**: El feed DEBE soportar infinite scroll cargando automáticamente la siguiente página al llegar al final
- **FR-007**: Al hacer clic en un viaje del feed, el usuario DEBE acceder a la vista completa del viaje
- **FR-008**: El feed DEBE mostrar contadores de interacciones en cada viaje: número de likes, número de comentarios, número de shares

**Likes/Me Gusta:**

- **FR-009**: Los usuarios autenticados DEBEN poder dar like a cualquier viaje público
- **FR-010**: El sistema DEBE prevenir que un usuario dé like múltiples veces al mismo viaje (toggle on/off)
- **FR-011**: El sistema DEBE actualizar el contador de likes instantáneamente al dar o quitar like
- **FR-012**: Los viajes DEBEN mostrar el número total de likes que han recibido
- **FR-013**: El sistema DEBE permitir ver la lista de usuarios que dieron like a un viaje (avatares + nombres)
- **FR-014**: Los usuarios DEBEN tener una sección en su perfil "Viajes que me gustan" con todos los viajes a los que dieron like
- **FR-015**: Los usuarios no autenticados DEBEN poder ver el contador de likes pero no pueden dar like (redirige a login)

**Comentarios:**

- **FR-016**: Los usuarios autenticados DEBEN poder comentar en cualquier viaje público
- **FR-017**: Los comentarios DEBEN tener un límite de 500 caracteres
- **FR-018**: Los comentarios DEBEN mostrarse en orden cronológico (más antiguos primero) debajo del viaje
- **FR-019**: Cada comentario DEBE mostrar: autor (avatar + nombre), texto del comentario, timestamp, indicador "editado" si fue modificado
- **FR-020**: Los usuarios DEBEN poder editar sus propios comentarios (se marca como "editado")
- **FR-021**: Los usuarios DEBEN poder eliminar sus propios comentarios
- **FR-022**: El autor del viaje DEBE poder eliminar cualquier comentario en su propio viaje (moderación básica)
- **FR-023**: El sistema DEBE mostrar el contador de comentarios junto a cada viaje
- **FR-024**: Los comentarios con más de 50 en un viaje DEBEN paginarse (mostrar 50 iniciales + botón "Cargar más")
- **FR-025**: Los usuarios no autenticados DEBEN poder leer comentarios pero no escribir (redirige a login)

**Compartir Viajes:**

- **FR-026**: Los usuarios autenticados DEBEN poder compartir viajes de otros usuarios en su propio feed
- **FR-027**: Al compartir, el usuario DEBE poder añadir un comentario opcional de hasta 200 caracteres
- **FR-028**: Un viaje compartido DEBE mostrar claramente: contenido del viaje original, atribución al autor original, comentario del usuario que compartió, timestamp del share
- **FR-029**: Los viajes compartidos DEBEN aparecer en el feed de los seguidores del usuario que compartió
- **FR-030**: El sistema DEBE mostrar el contador de veces que un viaje ha sido compartido
- **FR-031**: Los usuarios DEBEN poder eliminar un viaje que compartieron (no afecta el original)
- **FR-032**: El sistema DEBE prevenir compartir el mismo viaje múltiples veces en un periodo corto (cooldown de 1 hora)
- **FR-033**: Si el viaje original es eliminado, el share DEBE mostrar mensaje "[Viaje no disponible]" o eliminarse

**Notificaciones:**

- **FR-034**: El sistema DEBE generar notificaciones cuando: alguien da like a un viaje del usuario, alguien comenta en un viaje del usuario, alguien comparte un viaje del usuario
- **FR-035**: Las notificaciones DEBEN incluir: tipo de interacción, usuario que realizó la acción, viaje relacionado, timestamp
- **FR-036**: El sistema DEBE mostrar un indicador visual (badge con número) de notificaciones no leídas
- **FR-037**: Las notificaciones DEBEN ordenarse cronológicamente (más recientes primero)
- **FR-038**: El usuario DEBE poder marcar notificaciones individuales como leídas
- **FR-039**: El usuario DEBE poder marcar todas las notificaciones como leídas con un botón
- **FR-040**: Al hacer clic en una notificación, el sistema DEBE redirigir al viaje relacionado y marcar la notificación como leída
- **FR-041**: Las notificaciones leídas DEBEN conservarse por 30 días, luego archivarse/eliminarse

**Controles de Privacidad y Moderación:**

- **FR-042**: Solo viajes con estado "publicado" DEBEN aparecer en el feed (no borradores)
- **FR-043**: El sistema DEBE sanitizar comentarios para prevenir XSS y HTML malicioso
- **FR-044**: El sistema DEBE limitar la tasa de comentarios (máximo 10 comentarios por usuario por hora)
- **FR-045**: El sistema DEBE limitar la tasa de likes/unlikes (máximo 100 acciones por hora)

### Key Entities

- **Like**: Interacción de me gusta. Atributos: ID único, usuario que dio like, viaje al que se dio like, fecha de like

- **Comment**: Comentario en un viaje. Atributos: ID único, autor (User), viaje (Trip), texto (máximo 500 caracteres), fecha de creación, fecha de edición (opcional), editado (booleano), eliminado (booleano soft delete)

- **Share**: Viaje compartido por un usuario. Atributos: ID único, usuario que compartió, viaje original (Trip), comentario del share (opcional, máximo 200 caracteres), fecha de share

- **Notification**: Notificación de interacción. Atributos: ID único, usuario destinatario, tipo (like/comment/share), usuario que realizó la acción, viaje relacionado, extracto de contenido (para comentarios), leída (booleano), fecha de creación

- **FeedItem**: Elemento del feed (abstracción). Atributos: tipo (viaje directo/viaje compartido), viaje referenciado, autor del item (usuario original o usuario que compartió), fecha de creación del item, metadatos de interacciones (likes count, comments count, shares count)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Feed de Viajes:**

- **SC-001**: El feed carga la primera página (10 viajes) en menos de 1 segundo en el percentil 95
- **SC-002**: El infinite scroll carga la siguiente página en menos de 500ms
- **SC-003**: El 80% de los usuarios activos acceden al feed al menos 3 veces por semana
- **SC-004**: El feed muestra correctamente viajes de usuarios seguidos el 100% del tiempo
- **SC-005**: El algoritmo de recomendaciones (viajes populares) mantiene relevancia del 70% (medido por engagement)

**Likes/Me Gusta:**

- **SC-006**: La acción de dar/quitar like responde en menos de 200ms
- **SC-007**: El contador de likes se actualiza instantáneamente sin necesidad de refrescar la página
- **SC-008**: El 90% de los viajes publicados reciben al menos 1 like dentro de la primera semana
- **SC-009**: Los usuarios activos dan like a un promedio de 5-10 viajes por semana
- **SC-010**: La lista de usuarios que dieron like carga en menos de 1 segundo para listas de hasta 100 usuarios

**Comentarios:**

- **SC-011**: Los usuarios pueden publicar un comentario en menos de 30 segundos (escribir + publicar)
- **SC-012**: El 60% de los viajes publicados reciben al menos 1 comentario dentro del primer mes
- **SC-013**: Los comentarios aparecen instantáneamente después de publicar (menos de 300ms)
- **SC-014**: El 95% de las ediciones/eliminaciones de comentarios se procesan correctamente sin errores
- **SC-015**: La paginación de comentarios (cuando hay >50) carga en menos de 500ms

**Compartir Viajes:**

- **SC-016**: Los usuarios pueden compartir un viaje en menos de 20 segundos (añadir comentario + publicar)
- **SC-017**: El 30% de los viajes populares son compartidos al menos una vez
- **SC-018**: Los viajes compartidos aparecen correctamente en el feed de los seguidores el 100% del tiempo
- **SC-019**: El sistema maneja correctamente la eliminación del viaje original actualizando/eliminando shares en <5 segundos

**Notificaciones:**

- **SC-020**: Las notificaciones se generan en menos de 1 segundo después de la interacción
- **SC-021**: El indicador de notificaciones no leídas se actualiza en tiempo real (o al refrescar en <2 segundos)
- **SC-022**: El 85% de los usuarios marcan las notificaciones como leídas dentro de las 24 horas
- **SC-023**: El centro de notificaciones carga en menos de 1 segundo para listas de hasta 50 notificaciones
- **SC-024**: La navegación desde notificación al viaje relacionado funciona correctamente el 100% del tiempo

**Engagement y Comunidad:**

- **SC-025**: El engagement promedio (likes + comentarios + shares) por viaje aumenta 40% con features sociales vs sin ellos
- **SC-026**: El 70% de los usuarios que ven el feed interactúan con al menos 1 viaje (like, comentario, o share)
- **SC-027**: Los usuarios activos en la red social regresan a la plataforma 2x más frecuentemente que usuarios sin interacciones sociales
- **SC-028**: La tasa de retención a 30 días aumenta 25% para usuarios que interactúan socialmente vs usuarios solo con perfil

**Rendimiento y Escala:**

- **SC-029**: El sistema maneja 1000 interacciones concurrentes (likes, comentarios, shares) sin degradación
- **SC-030**: Las consultas del feed optimizadas cargan eficientemente incluso con 100,000+ viajes en la plataforma
- **SC-031**: El almacenamiento de notificaciones (con archivo/eliminación a 30 días) se mantiene eficiente
- **SC-032**: Los rate limits previenen efectivamente spam manteniendo experiencia fluida para usuarios legítimos

## Assumptions

1. **Conexiones sociales existentes**: Se asume que la feature de seguir usuarios (001-user-profiles) ya está implementada
2. **Contenido existente**: Se asume que los viajes (002-travel-diary) ya existen y están publicados
3. **Feed algorithm simple**: Versión inicial usa orden cronológico simple; algoritmos de recomendación avanzados son futuros
4. **Notificaciones in-app**: Solo notificaciones dentro de la plataforma; email/push notifications son futuras
5. **Moderación manual**: No hay filtros automáticos de contenido ofensivo; se confía en moderación del autor del viaje
6. **Sin hilos de comentarios**: Comentarios son planos, no hay respuestas anidadas (replies)
7. **Sin reacciones adicionales**: Solo "like" básico; emojis de reacción variados son futuros
8. **Feed público**: El feed es privado (requiere login); feed público de viajes destacados es futuro
9. **Sin menciones**: No se soporta mencionar usuarios en comentarios (@username)
10. **Sin hashtags**: No hay funcionalidad de hashtags en comentarios o descripciones
11. **Compartir interno**: Solo se comparte dentro de ContraVento; compartir a redes externas (Twitter, Facebook) es futuro
12. **Sin mensajería directa**: Los comentarios son públicos; mensajes privados entre usuarios es feature separada

## Out of Scope

Las siguientes funcionalidades NO están incluidas en esta especificación:

- Notificaciones por email o push notifications móvil
- Algoritmos de recomendación avanzados (machine learning, personalización profunda)
- Respuestas anidadas en comentarios (hilos de conversación)
- Menciones de usuarios en comentarios (@username)
- Hashtags y búsqueda por hashtags
- Reacciones variadas (emoji reactions más allá de like simple)
- Guardado de viajes en colecciones/favoritos (diferente de likes)
- Feed público (sin login) de viajes destacados
- Compartir a redes sociales externas (Facebook, Twitter, Instagram)
- Reportar contenido inapropiado (sistema de reportes y moderación)
- Bloquear usuarios o silenciar contenido
- Mensajería directa privada entre usuarios
- Transmisiones en vivo o stories estilo Instagram
- Grupos o comunidades temáticas (ej: "Ciclistas de Madrid")
- Eventos y quedadas de ciclistas
- Clasificaciones o leaderboards (ej: usuarios con más likes)
- Insignias o gamificación social (ej: "Comentarista activo")
- Análisis de engagement para creadores (estadísticas detalladas de interacciones)
- Opciones de privacidad granular (viajes solo para seguidores, comentarios desactivados)
- Modo oscuro o personalización de feed
- Filtros de feed (solo viajes de X país, solo ciertos tipos de ciclismo)
