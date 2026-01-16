# Feature Specification: Enlaces Sociales con Control de Privacidad Granular

**Feature Branch**: `015-social-links-privacy`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Sistema de integración de redes sociales con control de privacidad granular para enlaces externos (Instagram, Strava, Blog, Portfolio) con 4 niveles de visibilidad: Público, Solo Comunidad, Círculo de Confianza, y Oculto

## User Scenarios & Testing

### User Story 1 - Añadir Enlaces Sociales con Visibilidad Pública (Priority: P1)

Un ciclista profesional, guía local o creador de contenido quiere aumentar su visibilidad y compartir sus redes sociales (Instagram, Strava, Blog, Portfolio) de forma pública para que cualquier visitante pueda encontrarlo y seguirlo fuera de ContraVento.

**Why this priority**: Es la funcionalidad base (MVP) que permite a usuarios añadir enlaces sociales y configurar la privacidad más básica. Sin esto, no hay feature. Los usuarios que buscan visibilidad (guías, creadores) son casos de uso prioritarios para adopción temprana.

**Independent Test**: Puede ser completamente probado visitando un perfil como usuario anónimo y verificando que los iconos de redes sociales sean visibles y clicables. Entrega valor inmediato al permitir descubrimiento de usuarios fuera de la plataforma.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en la página de edición de perfil, **When** hace clic en "Añadir enlace social" y selecciona Instagram con visibilidad "Público", **Then** el sistema guarda el enlace y lo muestra con el icono de Instagram en su perfil público
2. **Given** un visitante anónimo (no autenticado), **When** visita el perfil de un usuario con enlaces públicos, **Then** ve todos los iconos de redes sociales configurados como públicos y puede hacer clic para abrirlos en nueva pestaña
3. **Given** un usuario con enlaces públicos, **When** otro usuario (autenticado o no) hace clic en el icono de Strava, **Then** se abre el perfil de Strava del usuario en una nueva ventana con atributo `rel="me nofollow"`

---

### User Story 2 - Configurar Enlaces Solo para Comunidad (Priority: P2)

Un ciclista que valora su privacidad quiere compartir sus redes sociales solo con la comunidad de ContraVento (usuarios registrados que aceptaron el manifiesto), evitando que Google u otros buscadores indexen sus enlaces personales.

**Why this priority**: Diferencia a ContraVento de otras plataformas al ofrecer control de privacidad intermedio. Es la segunda prioridad porque depende de tener la infraestructura básica de enlaces (P1) pero añade valor significativo al permitir exclusividad comunitaria.

**Independent Test**: Puede probarse visitando un perfil en dos contextos: como usuario anónimo (no debe ver enlaces) y como usuario autenticado (debe verlos). Entrega valor al proteger la privacidad fuera de la plataforma.

**Acceptance Scenarios**:

1. **Given** un usuario con un enlace de Blog configurado como "Solo Comunidad", **When** un visitante anónimo visita su perfil, **Then** no ve ningún icono de Blog
2. **Given** el mismo perfil, **When** un usuario autenticado (miembro de la comunidad) lo visita, **Then** ve el icono de Blog y puede hacer clic para acceder
3. **Given** un usuario editando su perfil, **When** cambia la visibilidad de Instagram de "Público" a "Solo Comunidad", **Then** el sistema actualiza la configuración y usuarios anónimos dejan de ver el icono inmediatamente

---

### User Story 3 - Enlaces Exclusivos para Círculo de Confianza (Priority: P3)

Un usuario quiere compartir sus redes personales (WhatsApp, Telegram, Portfolio privado) solo con ciclistas con los que ha construido una relación mutua (seguidores mutuos), evitando contacto de desconocidos.

**Why this priority**: Es la funcionalidad más avanzada de privacidad pero depende del sistema de seguidores (Feature 011 - Follows). Menor prioridad porque afecta a un subconjunto de usuarios que ya tienen relaciones establecidas.

**Independent Test**: Puede probarse con dos usuarios: uno que sigue al otro (relación unilateral) y otro par que se siguen mutuamente. Solo el par con seguimiento mutuo debe ver los enlaces de "Círculo de Confianza". Entrega valor al proteger información de contacto personal.

**Acceptance Scenarios**:

1. **Given** el usuario A tiene un enlace de Telegram configurado como "Círculo de Confianza", **When** el usuario B (que sigue a A pero A no sigue a B) visita el perfil de A, **Then** B ve un botón que dice "Sigue a este ciclista para ver sus redes de contacto" pero no ve el enlace directo
2. **Given** el usuario A y el usuario C se siguen mutuamente, **When** C visita el perfil de A, **Then** C ve el icono de Telegram y puede hacer clic para abrir el enlace
3. **Given** un usuario con varios enlaces en diferentes niveles de privacidad, **When** un seguidor mutuo visita su perfil, **Then** ve los enlaces públicos, comunitarios Y de círculo de confianza, mientras que un desconocido solo ve los públicos

---

### User Story 4 - Indicadores de Privacidad en Edición de Perfil (Priority: P2)

Un usuario editando su perfil necesita entender visualmente qué nivel de privacidad tiene cada enlace social para tomar decisiones informadas sobre su visibilidad.

**Why this priority**: Experiencia de usuario crítica para evitar confusión. Sin indicadores visuales claros, usuarios podrían exponer información personal accidentalmente. Prioridad P2 porque mejora significativamente la usabilidad pero no es bloqueante para funcionalidad básica.

**Independent Test**: Puede probarse simplemente navegando a la página de edición de perfil y verificando que cada enlace muestra su nivel de privacidad con iconografía coherente (candado, ojo, grupo). Entrega valor al prevenir errores de configuración.

**Acceptance Scenarios**:

1. **Given** un usuario en la página de edición de perfil con 3 enlaces configurados, **When** visualiza la lista de enlaces, **Then** cada uno muestra un icono distintivo: candado abierto (Público), candado cerrado (Solo Comunidad), grupo de personas (Círculo de Confianza)
2. **Given** un usuario añadiendo un nuevo enlace, **When** selecciona el nivel de privacidad en un dropdown, **Then** el icono correspondiente se actualiza en tiempo real para reflejar la selección
3. **Given** un usuario con enlaces en nivel "Oculto", **When** visualiza su lista de enlaces, **Then** ve el enlace guardado con un icono de "ojo tachado" indicando que está oculto pero persiste en la base de datos

---

### User Story 5 - Validación y Sanitización de Enlaces (Priority: P1)

El sistema debe validar todos los enlaces externos ingresados por usuarios para prevenir ataques de phishing, XSS y asegurar que apuntan a dominios legítimos de las redes sociales soportadas.

**Why this priority**: Seguridad crítica. Sin validación, la plataforma expone a usuarios a ataques. Debe implementarse desde el MVP (junto con P1) para evitar vulnerabilidades desde el inicio.

**Independent Test**: Puede probarse intentando ingresar URLs maliciosas, scripts, o dominios incorrectos y verificando que el sistema rechaza o sanitiza correctamente. Entrega valor al proteger la comunidad de ataques.

**Acceptance Scenarios**:

1. **Given** un usuario intentando añadir un enlace de Instagram, **When** ingresa una URL con formato incorrecto (e.g., `javascript:alert('XSS')`), **Then** el sistema rechaza el enlace y muestra un mensaje de error en español: "URL no válida. Ingresa un enlace de Instagram válido (https://instagram.com/usuario)"
2. **Given** un usuario ingresando un enlace de Strava, **When** la URL contiene parámetros sospechosos o scripts, **Then** el sistema sanitiza la URL eliminando todo excepto el dominio y path válido
3. **Given** un usuario guardando un enlace válido de Portfolio, **When** el sistema lo persiste en la base de datos, **Then** añade automáticamente el atributo `rel="me nofollow"` al HTML generado para proteger SEO y cumplir con estándares de identidad descentralizada

---

### Edge Cases

- **¿Qué pasa si un usuario intenta añadir más de 10 enlaces sociales?** El sistema debe limitar a un máximo de 6-8 enlaces para mantener la UI limpia (por determinar número exacto en diseño)
- **¿Cómo maneja el sistema un enlace que apunta a un dominio válido pero la cuenta no existe?** El sistema valida el formato pero no verifica la existencia de la cuenta (responsabilidad del usuario). Muestra el enlace tal cual.
- **¿Qué sucede si dos usuarios se dejan de seguir mutuamente?** Los enlaces de "Círculo de Confianza" dejan de ser visibles inmediatamente para ambos.
- **¿Cómo se comporta el sistema si un usuario cambia un enlace de "Público" a "Oculto" mientras otra persona está viendo su perfil?** La próxima vez que el visitante recargue la página, el enlace desaparece. No hay actualización en tiempo real.
- **¿Qué pasa si un usuario intenta añadir el mismo enlace dos veces con diferente privacidad?** El sistema debe prevenir duplicados por tipo de red social (solo un Instagram, un Strava, etc.).

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE permitir a usuarios autenticados añadir hasta 6 enlaces de redes sociales en su perfil (Instagram, Substack/Blog, Strava, Portfolio, y 2 campos personalizables)
- **FR-002**: El sistema DEBE soportar 4 niveles de visibilidad para cada enlace: Público, Solo Comunidad, Círculo de Confianza, y Oculto
- **FR-003**: El sistema DEBE validar que las URLs de enlaces correspondan a dominios válidos de las redes sociales soportadas (instagram.com, strava.com, substack.com, medium.com, etc.)
- **FR-004**: El sistema DEBE sanitizar todas las URLs ingresadas para prevenir ataques XSS, phishing e inyección de scripts
- **FR-005**: El sistema DEBE añadir automáticamente el atributo `rel="me nofollow"` a todos los enlaces sociales renderizados en HTML
- **FR-006**: El sistema DEBE mostrar iconos de redes sociales solo si el nivel de privacidad permite al usuario actual verlos según su relación con el dueño del perfil
- **FR-007**: El sistema DEBE mostrar un botón "Sigue a este ciclista para ver sus redes de contacto" cuando un usuario no autorizado intenta ver enlaces de "Círculo de Confianza"
- **FR-008**: El sistema DEBE permitir editar y eliminar enlaces sociales existentes manteniendo su historial de visibilidad
- **FR-009**: La interfaz de edición de perfil DEBE mostrar indicadores visuales (iconos de candado, ojo, grupo) para cada nivel de privacidad configurado
- **FR-010**: El sistema DEBE prevenir duplicados: solo un enlace por tipo de red social permitido
- **FR-011**: El sistema DEBE verificar relaciones de seguimiento mutuo en tiempo real al renderizar perfiles para determinar visibilidad de enlaces de "Círculo de Confianza"
- **FR-012**: El sistema DEBE soportar enlaces en formato URL completa (https://instagram.com/usuario) o formato de usuario (@usuario para Instagram/Strava)
- **FR-013**: El sistema DEBE abrir todos los enlaces sociales en una nueva pestaña/ventana (atributo `target="_blank"`)

### Key Entities

- **SocialLink**: Representa un enlace a una red social externa configurado por un usuario
  - Atributos conceptuales: tipo de red social (Instagram, Strava, Blog, Portfolio, Custom), URL o handle de usuario, nivel de visibilidad, fecha de creación, fecha de última actualización
  - Relaciones: Pertenece a un User (un usuario puede tener múltiples enlaces)

- **PrivacyLevel**: Enumeración de niveles de visibilidad para enlaces sociales
  - Valores: PUBLIC (visible para todos), COMMUNITY (solo usuarios autenticados), MUTUAL_FOLLOWERS (solo seguidores mutuos), HIDDEN (guardado pero no visible)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Los usuarios pueden añadir y configurar un enlace social con nivel de privacidad en menos de 30 segundos desde la página de edición de perfil
- **SC-002**: El 95% de los intentos de añadir URLs válidas de redes sociales se guardan correctamente en el primer intento
- **SC-003**: El 100% de las URLs maliciosas o con scripts son rechazadas o sanitizadas antes de persistir en la base de datos
- **SC-004**: Los usuarios pueden entender el nivel de privacidad de sus enlaces sin leer documentación (indicadores visuales autoexplicativos)
- **SC-005**: La visibilidad de enlaces se actualiza correctamente en menos de 1 segundo cuando un usuario cambia el nivel de privacidad
- **SC-006**: El sistema previene 100% de intentos de inyección XSS a través de URLs de enlaces sociales
- **SC-007**: Los enlaces de "Círculo de Confianza" solo son visibles para seguidores mutuos con precisión del 100%
- **SC-008**: El tiempo de carga de un perfil con 6 enlaces sociales no aumenta más de 50ms comparado con un perfil sin enlaces

## Assumptions

- Se asume que la Feature 011 (Follows/Seguidores) está implementada y funcional para soportar el nivel "Círculo de Confianza"
- Se asume que los usuarios entienden qué significa "Círculo de Confianza" a través de tooltips o ayuda contextual en la UI (no requiere tutorial extenso)
- Se asume que validar solo el formato de URL (no la existencia de la cuenta) es suficiente para evitar enlaces rotos (responsabilidad del usuario verificar)
- Se asume que 6 enlaces sociales son suficientes para la mayoría de casos de uso (expandible en futuro si hay demanda)
- Se asume que los iconos sociales se adaptan a la paleta de colores de ContraVento (tonos tierra) sin romper el branding de las redes originales
- Se asume que el atributo `rel="me nofollow"` es suficiente para proteger SEO y cumplir con estándares de identidad (no se requiere verificación adicional)
- Se asume que los enlaces abiertos en nueva pestaña (`target="_blank"`) no requieren confirmación adicional del usuario

## Out of Scope

- Verificación automática de existencia de cuentas en redes sociales (e.g., validar que @usuario existe en Instagram)
- Importación automática de contenido de redes sociales (fotos de Instagram, actividades de Strava) al perfil de ContraVento
- Autenticación OAuth con redes sociales para vincular cuentas (solo enlaces manuales)
- Analíticas de clics en enlaces sociales (cuántas personas hacen clic en Instagram del usuario)
- Sincronización bidireccional de seguidores entre ContraVento y redes externas
- Notificaciones cuando alguien hace clic en un enlace social
- Previews embebidas de contenido de redes sociales (cards de Instagram, widgets de Strava)
- Soporte para redes sociales fuera de la lista predefinida (Instagram, Strava, Blog, Portfolio + 2 custom)
- Verificación de identidad de cuentas sociales (badges de "verificado")

## Dependencies

- **Feature 011 (Follows/Seguidores)**: Requerida para implementar el nivel de visibilidad "Círculo de Confianza" que depende de relaciones de seguimiento mutuo
- **Feature 001 (User Profiles)**: Base de datos de usuarios y sistema de edición de perfil debe estar funcional para almacenar enlaces sociales
- **Sistema de Autenticación**: Necesario para distinguir entre usuarios anónimos y autenticados al aplicar reglas de visibilidad

## Notes

- Esta feature es un diferenciador clave de ContraVento frente a otras plataformas al ofrecer privacidad granular sin precedentes
- La iconografía coherente con la estética de ContraVento (tonos tierra, trazos suaves) es crítica para mantener la armonía visual de la plataforma
- Los enlaces "Ocultos" permiten a usuarios guardar información sin exponerla, útil para migrar datos o guardar enlaces temporalmente sin publicar
- El botón "Sigue a este ciclista para ver sus redes de contacto" incentiva el engagement y construcción de comunidad
- La sanitización de URLs debe ser robusta para prevenir ataques sofisticados de phishing que imiten dominios legítimos
