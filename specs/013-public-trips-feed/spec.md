# Feature Specification: Public Trips Feed

**Feature Branch**: `013-public-trips-feed`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "Vamos a crear una pagina principal de la aplicacion de acceso público. Esta pagina se mostraran todas las trips publicados de todos los usuarios que tengan el check publico activado en su perfil. Esta pagina tendra una cabecera donde se mostrará un botón de iniciar sesion si no estás logeado o el nombre del usuario, foto y botón de logout si está logeado."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse Public Trips Without Authentication (Priority: P1)

Como visitante anónimo (no autenticado), quiero ver todos los viajes públicos disponibles para poder descubrir contenido interesante de ciclismo sin necesidad de crear una cuenta.

**Why this priority**: Este es el core value proposition de la página pública - permitir que cualquier persona descubra contenido de ciclismo y se anime a unirse a la comunidad. Es el primer punto de contacto con la aplicación.

**Independent Test**: Se puede probar completamente accediendo a la URL raíz de la aplicación sin estar autenticado y verificando que se muestran viajes públicos con datos completos (título, foto, distancia, fecha, autor).

**Acceptance Scenarios**:

1. **Given** soy un visitante no autenticado, **When** accedo a la página principal, **Then** veo una lista de viajes publicados de usuarios con perfil público
2. **Given** estoy viendo la lista de viajes, **When** observo cada tarjeta de viaje, **Then** veo información básica (título, foto principal, ubicación si existe, distancia, fecha, nombre de usuario del autor)
3. **Given** hay más de 20 viajes disponibles, **When** llego al final de la lista visible, **Then** puedo cargar más viajes mediante paginación o scroll infinito
4. **Given** no hay viajes públicos disponibles, **When** accedo a la página, **Then** veo un mensaje amigable indicando que aún no hay viajes publicados

---

### User Story 2 - Authentication Header Navigation (Priority: P1)

Como visitante o usuario autenticado, quiero ver una cabecera que refleje mi estado de autenticación para poder acceder fácilmente a las acciones correspondientes (login/logout, perfil).

**Why this priority**: La cabecera es crítica para la navegación y experiencia de usuario. Debe estar presente desde el primer momento para guiar al usuario hacia el registro/login si no está autenticado, o mostrarle su identidad si ya lo está.

**Independent Test**: Se puede probar navegando a la página principal en dos estados: sin autenticación (verificar botón "Iniciar sesión") y con autenticación (verificar nombre de usuario, foto y botón "Cerrar sesión").

**Acceptance Scenarios**:

1. **Given** soy un visitante no autenticado, **When** visualizo la cabecera, **Then** veo el logo de la aplicación y un botón "Iniciar sesión"
2. **Given** soy un usuario autenticado, **When** visualizo la cabecera, **Then** veo el logo, mi foto de perfil, mi nombre de usuario y un botón "Cerrar sesión"
3. **Given** soy un visitante no autenticado, **When** hago clic en "Iniciar sesión", **Then** soy redirigido a la página de login
4. **Given** soy un usuario autenticado, **When** hago clic en "Cerrar sesión", **Then** mi sesión se cierra y se recarga la página mostrando el estado no autenticado
5. **Given** soy un usuario autenticado, **When** hago clic en mi nombre de usuario o foto, **Then** soy redirigido a mi página de perfil

---

### User Story 3 - Filter Trips by Privacy Settings (Priority: P2)

Como usuario de la aplicación, quiero que solo se muestren en la página pública los viajes de usuarios que tengan su perfil configurado como público, para respetar las preferencias de privacidad de cada ciclista.

**Why this priority**: La privacidad es importante pero es un requisito de filtrado backend, no una funcionalidad visible para el usuario final. Es esencial para el correcto funcionamiento pero no requiere interacción directa del usuario.

**Independent Test**: Se puede probar creando usuarios con diferentes configuraciones de privacidad (público/privado) y verificando que solo los viajes de usuarios con perfil público aparecen en el feed.

**Acceptance Scenarios**:

1. **Given** un usuario tiene `profile_visibility = 'public'` y viajes publicados, **When** cualquier visitante accede a la página principal, **Then** los viajes de ese usuario aparecen en el feed
2. **Given** un usuario tiene `profile_visibility = 'private'` y viajes publicados, **When** cualquier visitante accede a la página principal, **Then** los viajes de ese usuario NO aparecen en el feed
3. **Given** un usuario cambia su perfil de público a privado, **When** un visitante recarga la página principal, **Then** los viajes de ese usuario desaparecen del feed
4. **Given** un viaje está en estado DRAFT, **When** un visitante accede a la página principal, **Then** ese viaje NO aparece (solo viajes con status PUBLISHED)

---

### User Story 4 - View Trip Details (Priority: P3)

Como visitante o usuario autenticado, quiero poder hacer clic en un viaje de la lista para ver sus detalles completos, incluyendo descripción, fotos, ubicaciones y etiquetas.

**Why this priority**: Aunque importante para la experiencia completa, esta funcionalidad depende de que primero exista la lista de viajes (US1). Es una mejora progresiva que puede implementarse después del MVP.

**Independent Test**: Se puede probar haciendo clic en cualquier tarjeta de viaje del feed y verificando que se navega a la página de detalle del viaje con toda la información completa.

**Acceptance Scenarios**:

1. **Given** estoy viendo la lista de viajes, **When** hago clic en una tarjeta de viaje, **Then** soy redirigido a la página de detalle de ese viaje
2. **Given** estoy en la página de detalle de un viaje, **When** reviso la información, **Then** veo todos los detalles (descripción completa, todas las fotos, mapa con ubicaciones, etiquetas, estadísticas)
3. **Given** soy un visitante no autenticado viendo un detalle de viaje, **When** intento realizar acciones de edición, **Then** esas opciones no están disponibles (solo lectura)

---

### Edge Cases

- ¿Qué ocurre cuando un usuario tiene perfil público pero todos sus viajes están en DRAFT? → No aparece ningún viaje de ese usuario en el feed
- ¿Qué ocurre si un usuario cambia su perfil de público a privado mientras un visitante está viendo el feed? → Al recargar, sus viajes desaparecen
- ¿Cómo se manejan usuarios con perfil público pero sin viajes publicados? → No aparecen en el feed, solo se muestran usuarios con al menos 1 viaje PUBLISHED
- ¿Qué ocurre si un viaje no tiene foto principal? → Se muestra un placeholder o la primera foto del viaje, o un icono por defecto
- ¿Qué ocurre si un viaje no tiene ninguna ubicación (location)? → No se muestra el campo de ubicación en la tarjeta
- ¿Cómo se comporta la paginación cuando se eliminan viajes mientras el usuario navega? → El sistema debe manejar IDs faltantes sin errores
- ¿Qué ocurre si un usuario elimina su cuenta mientras un visitante ve sus viajes? → Al recargar, esos viajes desaparecen del feed

## Requirements *(mandatory)*

### Functional Requirements

#### Visualización de Trips Públicos

- **FR-001**: El sistema DEBE mostrar una lista paginada de viajes (trips) publicados de usuarios con perfil público
- **FR-002**: Cada tarjeta de viaje DEBE mostrar: título, foto principal, ubicación (primera location del viaje si existe), distancia en kilómetros, fecha de inicio, y nombre de usuario del autor
- **FR-003**: El sistema DEBE aplicar filtros automáticos: solo viajes con `status = PUBLISHED` y de usuarios con `profile_visibility = 'public'`
- **FR-004**: El sistema DEBE ordenar los viajes por fecha de publicación (más recientes primero)
- **FR-005**: El sistema DEBE implementar paginación con un máximo de 20 viajes por página

#### Cabecera de Navegación

- **FR-006**: La cabecera DEBE mostrar diferentes elementos según el estado de autenticación del usuario
- **FR-007**: Para usuarios NO autenticados, la cabecera DEBE mostrar: logo de la aplicación y botón "Iniciar sesión"
- **FR-008**: Para usuarios autenticados, la cabecera DEBE mostrar: logo, foto de perfil del usuario, nombre de usuario, y botón "Cerrar sesión"
- **FR-009**: El botón "Iniciar sesión" DEBE redirigir a la página de login (`/login`)
- **FR-010**: El botón "Cerrar sesión" DEBE cerrar la sesión del usuario y recargar la página mostrando el estado no autenticado
- **FR-011**: Al hacer clic en el nombre de usuario o foto de perfil, el sistema DEBE redirigir al perfil del usuario autenticado

#### Navegación y Detalles

- **FR-012**: Cada tarjeta de viaje DEBE ser clicable y redirigir a la página de detalle del viaje
- **FR-013**: La página DEBE ser accesible sin autenticación (pública)
- **FR-014**: El sistema DEBE mostrar un mensaje amigable cuando no hay viajes públicos disponibles

#### Privacidad y Seguridad

- **FR-015**: El sistema DEBE respetar la configuración de privacidad del perfil de usuario (`profile_visibility`)
- **FR-016**: Solo los viajes de usuarios con `profile_visibility = 'public'` DEBEN aparecer en el feed público
- **FR-017**: Los viajes en estado DRAFT NUNCA deben aparecer en el feed público, independientemente de la configuración de privacidad del usuario

### Key Entities

- **Trip (Viaje)**: Representa un viaje de ciclismo publicado
  - Atributos clave: título, descripción, fecha de inicio, fecha de fin, distancia en km, dificultad, estado (DRAFT/PUBLISHED), foto principal, ubicaciones (locations)
  - Relaciones: pertenece a un Usuario (owner), puede tener múltiples ubicaciones (TripLocation)

- **User (Usuario)**: Representa un usuario de la aplicación
  - Atributos clave: nombre de usuario, email, foto de perfil, configuración de privacidad del perfil (`profile_visibility`: public/private)
  - Relaciones: puede tener múltiples Viajes

- **TripLocation (Ubicación de Viaje)**: Representa una ubicación asociada a un viaje
  - Atributos clave: nombre del lugar, coordenadas (latitud, longitud), dirección
  - Relaciones: pertenece a un Viaje

- **Header Component (Componente de Cabecera)**: Elemento de UI que muestra información del usuario o botones de autenticación
  - Variantes: modo no autenticado (logo + botón login), modo autenticado (logo + foto + nombre + botón logout)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los visitantes pueden visualizar la lista completa de viajes públicos sin necesidad de autenticación
- **SC-002**: La página principal carga en menos de 2 segundos con hasta 50 viajes mostrados
- **SC-003**: El 100% de los viajes mostrados corresponden a usuarios con perfil público y viajes en estado PUBLISHED
- **SC-004**: Los usuarios no autenticados pueden navegar a la página de login con un solo clic desde la cabecera
- **SC-005**: Los usuarios autenticados pueden cerrar sesión con un solo clic y ver el cambio reflejado inmediatamente
- **SC-006**: El sistema mantiene la consistencia de privacidad: 0% de viajes privados aparecen en el feed público
- **SC-007**: La paginación permite navegar a través de más de 100 viajes sin degradación de rendimiento

## Assumptions

- Se asume que la configuración de privacidad del perfil ya existe en el modelo de usuario (`profile_visibility` field)
- Se asume que los viajes ya tienen un campo de estado (`status`) con valores DRAFT y PUBLISHED
- Se asume que existe autenticación mediante cookies HTTP-only (basado en Feature 008)
- Se asume que ya existe una página de detalle de viaje que puede ser referenciada
- Se asume ordenamiento por fecha de publicación como el más relevante para un feed público (puede ser ajustado según feedback)
- Se asume paginación del lado del servidor para manejar grandes volúmenes de viajes
- Se asume que la foto principal del viaje es la primera foto de la colección de fotos del viaje, o un placeholder si no hay fotos

## Dependencies

- **Feature 001**: User Profiles Backend - Necesario para obtener configuración de privacidad del usuario
- **Feature 002**: Travel Diary - Necesario para obtener viajes publicados
- **Feature 005**: Frontend User Profile - Necesario para obtener foto de perfil del usuario
- **Feature 008**: Travel Diary Frontend - Puede reutilizar componentes de tarjetas de viaje

## Out of Scope

- Filtros de búsqueda (por ubicación, dificultad, distancia, tags) - puede ser una feature futura
- Sistema de "likes" o "favoritos" - feature futura
- Comentarios en viajes - feature futura
- Feed personalizado basado en preferencias del usuario autenticado - feature futura
- Sistema de notificaciones de nuevos viajes - feature futura
- Compartir viajes en redes sociales - feature futura
- Estadísticas agregadas del feed (total de kilómetros, países visitados, etc.) - feature futura

## Risks & Mitigations

- **Riesgo**: Rendimiento degradado con miles de viajes públicos
  - **Mitigación**: Implementar paginación eficiente con índices en base de datos, caché de queries frecuentes

- **Riesgo**: Usuarios cambiando configuración de privacidad y esperando cambios instantáneos en el feed
  - **Mitigación**: Documentar que los cambios pueden tardar hasta X segundos en reflejarse (tiempo de caché), o invalidar caché al cambiar privacidad

- **Riesgo**: Exposición accidental de viajes privados por error de filtrado
  - **Mitigación**: Tests exhaustivos de privacidad, validación en múltiples capas (query DB + filtro adicional en backend)

## Notes

- Esta es la primera página pública de la aplicación, por lo que es importante que la experiencia sea excelente para atraer nuevos usuarios
- Considerar añadir meta tags OpenGraph para que los viajes se compartan bien en redes sociales (feature futura)
- La cabecera diseñada aquí puede ser reutilizada en otras páginas públicas futuras
