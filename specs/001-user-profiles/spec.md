# Feature Specification: Sistema de Perfiles de Usuario y Autenticación

**Feature Branch**: `001-user-profiles`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Sistema de perfiles de usuario y autenticación para la plataforma de cicloturismo ContraVento"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro y Autenticación de Usuario (Priority: P1)

Un nuevo ciclista descubre ContraVento y quiere crear una cuenta para comenzar a documentar sus viajes. Necesita registrarse con sus datos básicos y luego poder iniciar sesión de forma segura para acceder a la plataforma.

**Why this priority**: Es la funcionalidad más crítica y fundacional. Sin autenticación, ninguna otra característica de la plataforma puede funcionar. Los usuarios deben poder identificarse de forma segura antes de crear contenido o interactuar con la comunidad.

**Independent Test**: Puede ser probado completamente mediante el proceso de registro de un nuevo usuario, cierre de sesión, y posterior inicio de sesión. Entrega valor inmediato al permitir que los usuarios tengan cuentas personales seguras.

**Acceptance Scenarios**:

1. **Given** un visitante sin cuenta, **When** accede al formulario de registro y proporciona email, contraseña y nombre de usuario válidos, **Then** el sistema crea la cuenta, envía confirmación por email, y redirige al usuario a su perfil inicial
2. **Given** un usuario con cuenta confirmada, **When** introduce sus credenciales correctas en el formulario de login, **Then** el sistema autentica al usuario y le permite acceder a su área personal
3. **Given** un usuario autenticado, **When** solicita cerrar sesión, **Then** el sistema invalida la sesión y redirige a la página pública
4. **Given** un usuario que olvidó su contraseña, **When** solicita recuperación mediante su email, **Then** el sistema envía un enlace seguro para restablecer la contraseña
5. **Given** un usuario intentando registrarse con un email ya existente, **When** envía el formulario, **Then** el sistema muestra un error claro indicando que el email ya está en uso

---

### User Story 2 - Gestión de Perfil Básico (Priority: P2)

Un ciclista autenticado quiere personalizar su perfil con información sobre sí mismo: biografía, ubicación, foto de perfil, y preferencias de ciclismo. Esta información será visible para otros usuarios de la comunidad.

**Why this priority**: Una vez que los usuarios pueden autenticarse, necesitan poder expresar su identidad ciclista. El perfil es la carta de presentación en la comunidad y permite que otros ciclistas entiendan quién eres y qué tipo de rutas te interesan.

**Independent Test**: Puede ser probado completamente creando una cuenta, editando el perfil con diversos campos, guardando los cambios, y verificando que la información se muestra correctamente en la vista pública del perfil.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en su perfil, **When** hace clic en "Editar perfil", **Then** accede a un formulario con todos los campos editables (bio, ubicación, tipo de ciclismo favorito, foto de perfil)
2. **Given** un usuario editando su perfil, **When** sube una foto de perfil válida (JPG/PNG, máximo 5MB), **Then** el sistema procesa y muestra la imagen en su perfil
3. **Given** un usuario editando su biografía, **When** escribe un texto de hasta 500 caracteres, **Then** el sistema guarda y muestra la biografía en su perfil público
4. **Given** un usuario editando su ubicación, **When** introduce ciudad y país, **Then** esta información se muestra en su perfil
5. **Given** un usuario seleccionando su tipo de ciclismo favorito, **When** elige entre opciones predefinidas (carretera, gravel, MTB, bikepacking, cicloturismo urbano), **Then** esta preferencia se guarda y muestra en su perfil
6. **Given** cualquier visitante, **When** accede al perfil público de otro usuario, **Then** puede ver toda la información pública del perfil (foto, bio, ubicación, tipo de ciclismo)

---

### User Story 3 - Estadísticas y Logros del Ciclista (Priority: P3)

Un ciclista quiere ver sus estadísticas acumuladas en la plataforma: kilómetros totales recorridos, número de viajes completados, países visitados, y otros logros. Estas estadísticas se calculan automáticamente basándose en sus viajes documentados.

**Why this priority**: Las estadísticas motivan a los usuarios a seguir documentando sus viajes y proporcionan una sensación de progreso y logro. Es una capa de gamificación que aumenta el engagement, pero no es crítica para la funcionalidad básica.

**Independent Test**: Puede ser probado creando una cuenta, documentando varios viajes con diferentes distancias y ubicaciones, y verificando que las estadísticas se calculan y muestran correctamente en el perfil.

**Acceptance Scenarios**:

1. **Given** un usuario con viajes documentados, **When** accede a su perfil, **Then** ve estadísticas agregadas: kilómetros totales, número de viajes, países visitados
2. **Given** un usuario que completa un nuevo viaje, **When** el viaje se publica, **Then** las estadísticas del perfil se actualizan automáticamente reflejando los nuevos datos
3. **Given** un usuario sin viajes documentados, **When** accede a su perfil, **Then** ve las estadísticas en cero con un mensaje motivacional para empezar a documentar
4. **Given** un usuario con logros desbloqueados (ej: primer viaje, 1000km, 10 países), **When** accede a su perfil, **Then** ve insignias o badges que representan estos logros
5. **Given** cualquier visitante, **When** ve el perfil público de otro usuario, **Then** puede ver sus estadísticas y logros principales

---

### User Story 4 - Conexiones Sociales (Seguir/Seguidores) (Priority: P4)

Un ciclista quiere seguir a otros usuarios cuyos viajes le interesan y ver quién le sigue a él. Esto crea la red social que permite descubrir contenido relevante en el feed.

**Why this priority**: Las conexiones sociales son importantes para el aspecto comunitario, pero dependen de que exista contenido (viajes) para que tenga sentido seguir a alguien. Es una capa social que se construye sobre el contenido existente.

**Independent Test**: Puede ser probado creando múltiples cuentas de usuario, haciendo que una siga a otra, verificando que las listas de seguidores/siguiendo se actualizan correctamente, y comprobando que se puede dejar de seguir.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado viendo el perfil de otro usuario, **When** hace clic en "Seguir", **Then** el sistema registra la conexión y muestra "Siguiendo" en lugar de "Seguir"
2. **Given** un usuario siguiendo a otro, **When** hace clic en "Dejar de seguir", **Then** el sistema elimina la conexión y actualiza el botón a "Seguir"
3. **Given** un usuario en su perfil, **When** accede a la sección "Seguidores", **Then** ve una lista de todos los usuarios que le siguen con foto y nombre
4. **Given** un usuario en su perfil, **When** accede a la sección "Siguiendo", **Then** ve una lista de todos los usuarios que sigue con foto y nombre
5. **Given** cualquier visitante viendo un perfil público, **When** mira las estadísticas del usuario, **Then** ve el número total de seguidores y de usuarios que sigue
6. **Given** un usuario no autenticado, **When** intenta seguir a alguien, **Then** el sistema le redirige al login

---

### Edge Cases

- ¿Qué ocurre cuando un usuario intenta registrarse con un email inválido o contraseña débil?
- ¿Cómo maneja el sistema múltiples intentos fallidos de login (protección contra ataques de fuerza bruta)?
- ¿Qué sucede si un usuario sube una foto de perfil con formato incorrecto o tamaño excesivo?
- ¿Cómo se comporta el sistema si un usuario intenta seguirse a sí mismo?
- ¿Qué ocurre cuando un usuario solicita recuperación de contraseña para un email que no existe en el sistema?
- ¿Cómo se manejan caracteres especiales o contenido inapropiado en biografías y nombres de usuario?
- ¿Qué sucede si dos usuarios intentan registrarse simultáneamente con el mismo nombre de usuario?
- ¿Cómo se calculan las estadísticas si un viaje se elimina después de publicado?

## Requirements *(mandatory)*

### Functional Requirements

**Autenticación y Seguridad:**

- **FR-001**: El sistema DEBE permitir el registro de nuevos usuarios mediante email, nombre de usuario y contraseña
- **FR-002**: El sistema DEBE validar que los emails tengan formato válido y sean únicos en la plataforma
- **FR-003**: El sistema DEBE validar que los nombres de usuario sean únicos, contengan solo caracteres alfanuméricos y guiones, y tengan entre 3-30 caracteres
- **FR-004**: El sistema DEBE validar que las contraseñas tengan mínimo 8 caracteres, incluyendo al menos una letra mayúscula, una minúscula y un número
- **FR-005**: El sistema DEBE enviar un email de confirmación al registrarse y requerir verificación antes de permitir acceso completo
- **FR-006**: El sistema DEBE permitir inicio de sesión mediante email/nombre de usuario y contraseña
- **FR-007**: El sistema DEBE permitir cierre de sesión invalidando la sesión activa
- **FR-008**: El sistema DEBE ofrecer recuperación de contraseña mediante enlace temporal enviado por email
- **FR-009**: El sistema DEBE bloquear temporalmente cuentas después de 5 intentos fallidos de login consecutivos (15 minutos de bloqueo)
- **FR-010**: El sistema DEBE mantener sesiones seguras con expiración automática después de 30 días de inactividad

**Gestión de Perfil:**

- **FR-011**: Los usuarios DEBEN poder editar su información de perfil: biografía, ubicación (ciudad y país), tipo de ciclismo favorito
- **FR-012**: Los usuarios DEBEN poder subir y cambiar su foto de perfil en formatos JPG, PNG o WebP con tamaño máximo de 5MB
- **FR-013**: El sistema DEBE redimensionar automáticamente las fotos de perfil a dimensiones apropiadas para optimizar rendimiento
- **FR-014**: Las biografías DEBEN tener un límite de 500 caracteres
- **FR-015**: Los tipos de ciclismo favorito DEBEN incluir: Carretera, Gravel, MTB, Bikepacking, Cicloturismo Urbano, Touring
- **FR-016**: Los perfiles DEBEN ser públicamente visibles (cualquier visitante puede verlos)
- **FR-017**: El sistema DEBE mostrar la fecha de registro del usuario en su perfil
- **FR-018**: Los usuarios DEBEN poder configurar privacidad de ciertos campos (email privado por defecto, ubicación opcional)

**Estadísticas del Ciclista:**

- **FR-019**: El sistema DEBE calcular y mostrar kilómetros totales recorridos basándose en todos los viajes publicados del usuario
- **FR-020**: El sistema DEBE calcular y mostrar el número total de viajes completados
- **FR-021**: El sistema DEBE calcular y mostrar el número de países únicos visitados basándose en las ubicaciones de los viajes
- **FR-022**: El sistema DEBE actualizar automáticamente las estadísticas cuando se publica, edita o elimina un viaje
- **FR-023**: El sistema DEBE mostrar estadísticas en cero para usuarios sin viajes, con mensaje motivacional
- **FR-024**: El sistema DEBE otorgar logros/badges automáticamente basados en hitos: primer viaje, 100km, 500km, 1000km, 5000km, 5 viajes, 10 viajes, 3 países, 10 países

**Conexiones Sociales:**

- **FR-025**: Los usuarios autenticados DEBEN poder seguir a otros usuarios
- **FR-026**: Los usuarios autenticados DEBEN poder dejar de seguir a usuarios que siguen actualmente
- **FR-027**: El sistema DEBE prevenir que un usuario se siga a sí mismo
- **FR-028**: El sistema DEBE mantener listas de "Seguidores" (usuarios que me siguen) y "Siguiendo" (usuarios que sigo)
- **FR-029**: El sistema DEBE mostrar el conteo de seguidores y siguiendo en cada perfil
- **FR-030**: Los usuarios DEBEN poder ver la lista completa de seguidores y siguiendo de cualquier perfil público
- **FR-031**: El sistema DEBE actualizar instantáneamente los contadores cuando se establece o rompe una conexión
- **FR-032**: Los usuarios no autenticados DEBEN ser redirigidos al login si intentan seguir a alguien

### Key Entities

- **User**: Representa a un ciclista registrado en la plataforma. Atributos: email (único), nombre de usuario (único), contraseña (hasheada), fecha de registro, email verificado, foto de perfil, biografía, ubicación (ciudad, país), tipo de ciclismo favorito, estado de cuenta (activa/bloqueada)

- **UserProfile**: Extensión del usuario con información pública adicional. Atributos: biografía, ubicación, tipo de ciclismo favorito, foto de perfil, configuración de privacidad

- **UserStats**: Estadísticas agregadas del ciclista calculadas automáticamente. Atributos: kilómetros totales, número de viajes, países visitados (lista), fecha última actualización. Relación: uno-a-uno con User

- **Achievement**: Logros desbloqueables para gamificación. Atributos: tipo de logro, nombre, descripción, criterio de desbloqueo, icono/badge

- **UserAchievement**: Relación entre usuarios y logros desbloqueados. Atributos: usuario, logro, fecha de desbloqueo

- **Follow**: Conexión social entre dos usuarios. Atributos: usuario seguidor (follower), usuario seguido (following), fecha de conexión. Relación: muchos-a-muchos auto-referencial con User

- **PasswordReset**: Token temporal para recuperación de contraseña. Atributos: usuario, token (único), fecha de expiración, usado (booleano)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Eficiencia de Registro y Autenticación:**

- **SC-001**: Los nuevos usuarios pueden completar el proceso de registro en menos de 2 minutos
- **SC-002**: El 95% de los usuarios pueden iniciar sesión exitosamente en el primer intento con credenciales correctas
- **SC-003**: El tiempo de respuesta para autenticación de usuarios es menor a 500ms en el percentil 95
- **SC-004**: El sistema maneja al menos 100 registros concurrentes sin degradación de rendimiento

**Gestión de Perfil:**

- **SC-005**: Los usuarios pueden actualizar su perfil completo (todos los campos) en menos de 3 minutos
- **SC-006**: Las fotos de perfil se procesan y muestran en menos de 5 segundos después de la carga
- **SC-007**: El 90% de los usuarios completan al menos 3 campos de su perfil dentro de las primeras 24 horas de registro
- **SC-008**: Los perfiles públicos cargan completamente en menos de 1 segundo

**Estadísticas y Logros:**

- **SC-009**: Las estadísticas del usuario se actualizan en tiempo real (menos de 2 segundos) después de publicar un viaje
- **SC-010**: El cálculo de estadísticas es 100% preciso comparado con la suma manual de datos de viajes
- **SC-011**: El 80% de los usuarios con al menos un viaje desbloquean su primer logro
- **SC-012**: Los logros se otorgan automáticamente en menos de 5 segundos después de cumplir el criterio

**Conexiones Sociales:**

- **SC-013**: Los usuarios pueden seguir/dejar de seguir a otros usuarios con retroalimentación instantánea (menos de 500ms)
- **SC-014**: Los contadores de seguidores/siguiendo son 100% precisos en todo momento
- **SC-015**: Las listas de seguidores/siguiendo cargan en menos de 2 segundos incluso con 500+ conexiones
- **SC-016**: El 60% de los usuarios activos siguen al menos a 3 otros ciclistas dentro del primer mes

**Seguridad y Confiabilidad:**

- **SC-017**: El sistema previene el 100% de intentos de registro con emails duplicados o nombres de usuario duplicados
- **SC-018**: Cero vulnerabilidades de seguridad críticas relacionadas con autenticación (inyección SQL, XSS, contraseñas en texto plano)
- **SC-019**: El 100% de las contraseñas almacenadas están hasheadas con algoritmo seguro (bcrypt con mínimo 12 rondas)
- **SC-020**: Los tokens de recuperación de contraseña expiran automáticamente después de 1 hora
- **SC-021**: El sistema mantiene 99.9% de disponibilidad para operaciones de autenticación

**Experiencia de Usuario:**

- **SC-022**: Los mensajes de error son claros y accionables (90% de usuarios entienden cómo resolver el error sin ayuda)
- **SC-023**: El 85% de los nuevos usuarios confirman su email dentro de las primeras 24 horas
- **SC-024**: Menos del 5% de usuarios solicitan recuperación de contraseña en el primer mes
- **SC-025**: Los usuarios pueden navegar entre secciones de perfil (vista, editar, estadísticas, conexiones) sin confusión (medido por tasa de éxito en tests de usabilidad)

## Assumptions

1. **Idioma principal**: La plataforma usará español como idioma principal en toda la interfaz de usuario, con soporte futuro para internacionalización
2. **Alcance geográfico inicial**: Enfoque inicial en usuarios de España y Latinoamérica, expandible globalmente
3. **Dispositivos**: La plataforma debe funcionar en desktop y móvil (responsive), pero versión MVP puede priorizar desktop
4. **Almacenamiento de imágenes**: Las fotos de perfil se almacenarán en el sistema de almacenamiento de la plataforma (no terceros inicialmente)
5. **Email transaccional**: Se requiere servicio de email para confirmaciones y recuperación de contraseña
6. **Unicidad de datos**: Emails y nombres de usuario deben ser únicos globalmente en la plataforma
7. **Privacidad por defecto**: Los perfiles son públicos por defecto (necesario para red social), pero ciertos campos sensibles (email) son privados
8. **Gamificación**: Los logros son automáticos y no requieren aprobación manual
9. **Estadísticas**: Se calculan de forma agregada basándose únicamente en viajes publicados (no borradores)
10. **Conexiones bidireccionales**: Seguir es una acción unidireccional (no requiere aprobación del usuario seguido)
11. **Autenticación inicial**: Se usa autenticación basada en email/contraseña; OAuth/SSO puede añadirse en futuras iteraciones
12. **Retención de datos**: Los datos de usuario se mantienen indefinidamente a menos que el usuario solicite eliminación (cumplimiento GDPR)

## Out of Scope

Las siguientes funcionalidades NO están incluidas en esta especificación y serán consideradas en features separadas:

- Autenticación mediante redes sociales (Google, Facebook, Strava OAuth)
- Sistema de notificaciones (cuando alguien te sigue, nuevos logros)
- Configuración de privacidad avanzada del perfil
- Búsqueda y descubrimiento de usuarios
- Mensajería directa entre usuarios
- Bloqueo o reporte de usuarios
- Verificación de identidad o perfiles verificados
- Exportación de datos del usuario
- Eliminación permanente de cuenta
- Gestión de múltiples sesiones activas
- Autenticación de dos factores (2FA)
- Historial de actividad del usuario
- Preferencias de notificaciones por email
- Temas oscuros/claros o personalización de UI
- Integración con dispositivos GPS o aplicaciones de terceros (Strava, Komoot)
