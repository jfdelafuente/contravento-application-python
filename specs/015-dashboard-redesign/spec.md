# Feature Specification: Dashboard Principal Mejorado

**Feature Branch**: `015-dashboard-redesign`
**Created**: 2026-01-20
**Status**: Draft
**Input**: Panel de control principal mejorado para usuarios con header sticky, layout de 3 columnas con stats sociales, estadísticas personales, desafíos activos, feed de actividad y rutas sugeridas

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Vista Rápida de Estadísticas y Progreso Personal (Priority: P1)

Como usuario ciclista de ContraVento, quiero ver mis estadísticas personales de ciclismo (kilómetros recorridos, pueblos visitados, impacto económico local) de forma inmediata al acceder al dashboard, para mantenerme motivado y consciente de mi contribución a las comunidades locales.

**Why this priority**: Esta es la funcionalidad central del dashboard - proporciona valor inmediato al usuario mostrando su progreso y logros. Es el MVP mínimo viable.

**Independent Test**: Puede probarse de forma independiente autenticándose como usuario y verificando que se muestran las estadísticas personales actualizadas del perfil.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con viajes registrados, **When** accede al dashboard, **Then** ve sus estadísticas personales (km recorridos, pueblos visitados, impacto económico estimado) actualizadas en tiempo real
2. **Given** un usuario nuevo sin viajes, **When** accede al dashboard por primera vez, **Then** ve sus estadísticas en cero con mensajes motivacionales para comenzar su primer viaje
3. **Given** un usuario con logros desbloqueados, **When** visualiza el área de logros, **Then** ve las insignias obtenidas con descripción de cómo las ganó

---

### User Story 2 - Navegación y Búsqueda Rápida (Priority: P1)

Como usuario, quiero acceder rápidamente a búsquedas de usuarios, rutas o pueblos desde cualquier parte del dashboard mediante un buscador siempre visible, para encontrar contenido relevante sin perder contexto de dónde estoy.

**Why this priority**: La navegación eficiente es crítica para la experiencia de usuario. Un header sticky con búsqueda permite descubrimiento rápido de contenido.

**Independent Test**: Puede probarse independientemente verificando que el header permanece visible al hacer scroll y que la búsqueda funciona desde cualquier sección.

**Acceptance Scenarios**:

1. **Given** el usuario está en el dashboard, **When** hace scroll hacia abajo, **Then** el header con buscador permanece visible (sticky)
2. **Given** el usuario escribe en el buscador, **When** ingresa texto parcial de un usuario/ruta/pueblo, **Then** ve sugerencias en tiempo real mientras escribe
3. **Given** el usuario selecciona una sugerencia, **When** hace clic en un resultado, **Then** es redirigido a la página del usuario/ruta/pueblo seleccionado
4. **Given** el usuario está viendo su perfil, **When** hace clic en el logo del header, **Then** regresa al dashboard principal

---

### User Story 3 - Feed de Actividad de la Comunidad (Priority: P2)

Como usuario, quiero ver un feed de actividades recientes de las personas que sigo (nuevos viajes publicados, logros desbloqueados, desafíos completados) en la sección central del dashboard, para mantenerme conectado con la comunidad y descubrir nuevas rutas.

**Why this priority**: La conexión social es un valor diferenciador de ContraVento. El feed crea engagement y fomenta la interacción entre usuarios.

**Independent Test**: Puede probarse con un usuario que sigue a otros, verificando que se muestran actividades recientes ordenadas cronológicamente.

**Acceptance Scenarios**:

1. **Given** el usuario sigue a otros ciclistas activos, **When** accede al dashboard, **Then** ve las últimas actividades (viajes, logros, comentarios) de las personas que sigue en orden cronológico
2. **Given** una actividad reciente es un nuevo viaje, **When** hace clic en la actividad, **Then** es redirigido a los detalles del viaje
3. **Given** el usuario no sigue a nadie, **When** accede al feed, **Then** ve sugerencias de usuarios populares para seguir

---

### User Story 4 - Rutas Sugeridas y Descubrimiento (Priority: P2)

Como usuario, quiero recibir sugerencias de rutas basadas en mi ubicación, preferencias de ciclismo y pueblos que aún no he visitado, para planificar mi próximo viaje con facilidad.

**Why this priority**: El descubrimiento de nuevas rutas impulsa el uso continuo de la plataforma y ayuda a usuarios a explorar territorios nuevos.

**Independent Test**: Puede probarse verificando que se muestran rutas relevantes basadas en el perfil del usuario (ubicación, tipo de ciclismo, historial).

**Acceptance Scenarios**:

1. **Given** un usuario con preferencia de "Bikepacking" y ubicado en Madrid, **When** accede a rutas sugeridas, **Then** ve rutas de bikepacking cercanas que aún no ha realizado
2. **Given** un usuario ha visitado 5 pueblos, **When** visualiza sugerencias, **Then** se priorizan rutas que incluyen pueblos no visitados
3. **Given** una ruta sugerida tiene alta valoración, **When** el usuario la visualiza, **Then** ve el rating y número de ciclistas que la completaron

---

### User Story 5 - Desafíos Activos y Progreso (Priority: P3)

Como usuario, quiero ver mis desafíos activos (ej. "Visita 5 comercios rurales", "Ruta de los Molinos") con barra de progreso visual, para motivarme a completarlos y ganar recompensas.

**Why this priority**: Los desafíos gamifican la experiencia y crean objetivos a medio plazo. Es un complemento motivacional pero no crítico para el MVP.

**Independent Test**: Puede probarse con un usuario inscrito en desafíos, verificando que se muestra el progreso actualizado.

**Acceptance Scenarios**:

1. **Given** un usuario inscrito en un desafío activo, **When** accede al dashboard, **Then** ve el desafío con barra de progreso actualizada (ej. "3/5 comercios visitados")
2. **Given** un usuario completa un desafío, **When** realiza la acción final, **Then** recibe una notificación de logro desbloqueado y ve el desafío marcado como completado
3. **Given** un usuario sin desafíos activos, **When** visualiza la sección de desafíos, **Then** ve desafíos disponibles para unirse

---

### User Story 6 - Notificaciones y Alertas (Priority: P3)

Como usuario, quiero recibir notificaciones sobre interacciones sociales (likes, comentarios, nuevos seguidores) y alertas de seguridad o actualizaciones de retos, para estar informado sin necesidad de revisar manualmente.

**Why this priority**: Las notificaciones mejoran el engagement pero no son esenciales para la funcionalidad central del dashboard.

**Independent Test**: Puede probarse generando eventos que disparen notificaciones y verificando que aparecen en el contador del header.

**Acceptance Scenarios**:

1. **Given** otro usuario le da like a mi viaje, **When** accedo al dashboard, **Then** veo el contador de notificaciones incrementado en 1
2. **Given** tengo notificaciones sin leer, **When** hago clic en el icono de notificaciones, **Then** se despliega un panel con el listado de notificaciones recientes
3. **Given** una notificación de seguridad (ej. cambio de contraseña), **When** la recibo, **Then** aparece destacada en color diferente para llamar la atención

---

### User Story 7 - Acciones Rápidas (Priority: P3)

Como usuario, quiero acceder rápidamente a acciones frecuentes (crear viaje, ver perfil, explorar rutas) desde el dashboard sin tener que navegar por múltiples menús.

**Why this priority**: Las acciones rápidas mejoran la eficiencia pero son un complemento de conveniencia, no una funcionalidad crítica.

**Independent Test**: Puede probarse verificando que los botones de acciones rápidas redirigen correctamente a las páginas correspondientes.

**Acceptance Scenarios**:

1. **Given** el usuario está en el dashboard, **When** hace clic en "Crear Viaje", **Then** es redirigido al formulario de creación de viaje
2. **Given** el usuario hace clic en "Ver Perfil", **When** la acción se ejecuta, **Then** accede a su perfil personal
3. **Given** el usuario hace clic en "Explorar Rutas", **When** la acción se ejecuta, **Then** accede al buscador de rutas globales

---

### User Story 8 - Métricas Sociales (Priority: P2)

Como usuario, quiero ver cuántos seguidores tengo y a cuántas personas sigo directamente en el dashboard, para monitorear el crecimiento de mi red social sin salir de la vista principal.

**Why this priority**: Las métricas sociales refuerzan el aspecto comunitario de la plataforma y son un indicador clave de engagement.

**Independent Test**: Puede probarse verificando que los contadores de seguidores/siguiendo se actualizan en tiempo real al seguir/dejar de seguir usuarios.

**Acceptance Scenarios**:

1. **Given** un usuario con 50 seguidores y 30 seguidos, **When** accede al dashboard, **Then** ve estos números actualizados en la sección de métricas sociales
2. **Given** un usuario hace clic en "Seguidores", **When** la acción se ejecuta, **Then** ve el listado completo de usuarios que lo siguen
3. **Given** un usuario hace clic en "Siguiendo", **When** la acción se ejecuta, **Then** ve el listado completo de usuarios que sigue

### Edge Cases

- ¿Qué ocurre cuando un usuario tiene más de 100 actividades en el feed? → Se implementa scroll infinito o paginación
- ¿Cómo se maneja la búsqueda cuando no hay resultados? → Se muestra mensaje "No se encontraron resultados" con sugerencias de búsquedas populares
- ¿Qué pasa si un usuario no tiene estadísticas (nuevo usuario)? → Se muestran valores en cero con mensajes motivacionales
- ¿Cómo se comporta el dashboard en tablets (768px-1024px)? → Layout responsive adapta el grid de 3 columnas a 2 o 1 columna según viewport
- ¿Qué sucede si las rutas sugeridas no están disponibles por falta de datos de ubicación? → Se muestran rutas populares globales como fallback
- ¿Cómo se manejan notificaciones cuando hay más de 99? → Contador muestra "99+" y el panel muestra las más recientes
- ¿Qué pasa si un usuario intenta acceder al dashboard sin estar autenticado? → Redirigido automáticamente a la página de login
- ¿Cómo se comporta el feed cuando un usuario deja de seguir a alguien? → Las actividades de ese usuario desaparecen inmediatamente del feed
- ¿Qué ocurre si falla la carga de estadísticas del servidor? → Se muestra mensaje de error con opción de reintentar carga

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar estadísticas personales del usuario (kilómetros recorridos, pueblos visitados, impacto económico local estimado) actualizadas en tiempo real
- **FR-002**: El sistema DEBE proporcionar un header fijo (sticky) que permanezca visible durante el scroll en toda la sesión del dashboard
- **FR-003**: El sistema DEBE incluir un buscador global en el header que permita búsquedas de usuarios, rutas y pueblos con autocompletado
- **FR-004**: El sistema DEBE mostrar un feed de actividades recientes de usuarios seguidos ordenado cronológicamente (viajes, logros, comentarios)
- **FR-005**: El sistema DEBE sugerir rutas personalizadas basándose en ubicación del usuario, tipo de ciclismo preferido y pueblos no visitados
- **FR-006**: El sistema DEBE mostrar desafíos activos del usuario con indicadores visuales de progreso (ej. barras, porcentajes)
- **FR-007**: El sistema DEBE proporcionar un contador de notificaciones en el header que muestre alertas sin leer
- **FR-008**: El sistema DEBE mostrar métricas sociales (seguidores, siguiendo) actualizadas en tiempo real
- **FR-009**: El sistema DEBE mostrar logros y badges obtenidos por el usuario con descripciones de cómo se desbloquearon
- **FR-010**: El sistema DEBE proporcionar acceso rápido a acciones frecuentes (crear viaje, ver perfil, explorar rutas)
- **FR-011**: El sistema DEBE adaptar el layout a diferentes tamaños de pantalla (responsive: desktop, tablet, mobile)
- **FR-012**: El sistema DEBE redirigir al dashboard principal cuando el usuario hace clic en el logo del header
- **FR-013**: El sistema DEBE cargar el dashboard completo en menos de 2 segundos en conexiones estándar (>5 Mbps)
- **FR-014**: El sistema DEBE mantener el estado de scroll cuando el usuario navega y regresa al dashboard desde otra página
- **FR-015**: El sistema DEBE mostrar mensajes motivacionales cuando el usuario no tiene datos (nuevo usuario, sin desafíos, sin seguidores)
- **FR-016**: El sistema DEBE actualizar el contador de notificaciones en tiempo real cuando ocurren nuevos eventos
- **FR-017**: El sistema DEBE mostrar sugerencias de búsqueda mientras el usuario escribe en el buscador global
- **FR-018**: El sistema DEBE permitir al usuario navegar a perfiles, rutas o pueblos directamente desde los resultados de búsqueda
- **FR-019**: El sistema DEBE mostrar actividades del feed con información contextual (quién, qué, cuándo)
- **FR-020**: El sistema DEBE actualizar métricas sociales inmediatamente cuando el usuario sigue o deja de seguir a alguien

### Key Entities

- **Estadísticas Personales**: Representa métricas agregadas del usuario (km recorridos, pueblos visitados, impacto económico local). Se calcula a partir de todos los viajes publicados del usuario.
- **Feed de Actividad**: Colección de eventos recientes generados por usuarios seguidos (publicación de viaje, logro desbloqueado, comentario). Ordenado cronológicamente con timestamp.
- **Ruta Sugerida**: Propuesta de viaje generada por el sistema basada en preferencias del usuario (ubicación, tipo de ciclismo, historial). Incluye descripción, dificultad, distancia, pueblos incluidos.
- **Desafío Activo**: Objetivo a medio plazo en el que el usuario está inscrito (ej. "Visita 5 comercios rurales"). Incluye progreso actual, requisitos para completar y recompensa (badge).
- **Notificación**: Alerta para el usuario sobre interacciones sociales (likes, comentarios, nuevos seguidores) o eventos del sistema (actualizaciones de desafíos, alertas de seguridad). Incluye timestamp, tipo, estado (leída/no leída).
- **Métrica Social**: Contador de seguidores y usuarios seguidos. Se actualiza en tiempo real cuando ocurren cambios en las relaciones sociales.
- **Logro/Badge**: Insignia otorgada al usuario por cumplir criterios específicos (ej. "Primer viaje publicado", "Visitó 10 pueblos"). Incluye imagen, título, descripción, fecha de obtención.
- **Resultado de Búsqueda**: Item retornado por el buscador global que puede ser un usuario, ruta o pueblo. Incluye nombre, tipo, imagen de preview y enlace al detalle.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden visualizar sus estadísticas personales completas en menos de 1 segundo desde que cargan el dashboard
- **SC-002**: El 90% de los usuarios encuentran contenido relevante usando el buscador del header en el primer intento
- **SC-003**: El dashboard mantiene una tasa de refresco inferior a 2 segundos para cargar el feed de actividades completo (hasta 50 entradas)
- **SC-004**: El sistema sugiere al menos 3 rutas personalizadas relevantes para el 80% de los usuarios basándose en su perfil
- **SC-005**: Los usuarios activos (con viajes registrados) pasan al menos 5 minutos explorando el dashboard en el 70% de sus sesiones
- **SC-006**: Las notificaciones se entregan en tiempo real con un delay máximo de 3 segundos desde que ocurre el evento
- **SC-007**: El dashboard es completamente funcional en dispositivos tablet (768px-1024px) sin pérdida de funcionalidad crítica
- **SC-008**: El 85% de los usuarios completan al menos una acción rápida (crear viaje, explorar rutas, ver perfil) durante su primera visita al dashboard
- **SC-009**: El tiempo promedio para descubrir un nuevo usuario o ruta a través del feed de actividad es menor a 2 minutos
- **SC-010**: El dashboard mantiene un rendimiento fluido (>30 FPS) durante scroll y transiciones en dispositivos de gama media

## Assumptions

- Los usuarios ya tienen cuentas creadas y están autenticados antes de acceder al dashboard
- El sistema de estadísticas personales ya calcula y almacena métricas agregadas (feature existente)
- El sistema de seguidores/seguidos ya está implementado (feature 004 - Social Network)
- Las rutas y viajes están almacenados en la base de datos con metadatos necesarios (ubicación, dificultad, tags)
- El sistema de notificaciones push está fuera del alcance (solo se muestra contador y panel de notificaciones recientes)
- El diseño visual (colores, tipografías, iconos) seguirá la guía de estilo existente de ContraVento (terracota #D35400, verde bosque #1B2621, crema #F9F7F2)
- Las métricas de "impacto económico local" se calculan mediante algoritmo predefinido (fuera del alcance de esta feature)
- El sistema de desafíos/badges ya existe en el backend (solo se visualiza en dashboard)

## Dependencies

- **Feature 001**: Sistema de autenticación y perfiles de usuario (COMPLETED)
- **Feature 002**: Travel Diary con viajes y fotos (COMPLETED)
- **Feature 004**: Red Social con sistema de seguir/dejar de seguir usuarios (COMPLETED - US1/US2/US3)
- **Feature 006**: Dashboard básico con estadísticas (COMPLETED) - Este dashboard es una evolución/mejora
- Backend debe exponer endpoint de "feed de actividad" con paginación
- Backend debe exponer endpoint de "rutas sugeridas" basado en perfil de usuario
- Backend debe exponer endpoint de "desafíos activos" con progreso del usuario
- Backend debe exponer endpoint de "búsqueda global" con autocompletado para usuarios/rutas/pueblos

## Out of Scope

- Notificaciones push en tiempo real (WebSockets) - Se muestra solo contador y listado de notificaciones recientes
- Personalización del layout del dashboard por el usuario (drag-and-drop de widgets)
- Exportación de estadísticas en formatos PDF/CSV
- Integración con dispositivos de ciclismo (Garmin, Strava)
- Dashboard para administradores (solo dashboard de usuario final)
- Chat en tiempo real con otros usuarios
- Mapa interactivo global mostrando todos los viajes de la comunidad
- Calendario de eventos/viajes planificados
- Sistema de recompensas monetarias por completar desafíos (badges sí, premios en efectivo no)
- Análisis avanzado de estadísticas (gráficos de progreso temporal, comparaciones con otros usuarios)
- Sistema de rankings o leaderboards globales
