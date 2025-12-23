# Feature Specification: Diario de Viajes Digital

**Feature Branch**: `002-travel-diary`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Diario de viajes digital para documentar aventuras de cicloturismo"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear y Publicar Entrada de Viaje (Priority: P1)

Un ciclista que acaba de completar una ruta (por ejemplo, la Vía Verde del Aceite) quiere documentar su experiencia. Necesita crear una entrada de viaje con título, descripción narrativa, fechas, distancia, dificultad, y ubicaciones visitadas.

**Why this priority**: Es la funcionalidad core del diario. Sin la capacidad de crear y publicar entradas de viaje, la plataforma no cumple su propósito fundamental. Esta historia entrega el valor mínimo viable: permitir a los ciclistas documentar sus aventuras.

**Independent Test**: Puede ser probado completamente creando una cuenta, accediendo al formulario de nuevo viaje, completando todos los campos obligatorios, publicando la entrada, y verificando que aparece en el perfil del usuario como viaje publicado.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en su perfil, **When** hace clic en "Crear nuevo viaje", **Then** accede a un formulario con campos: título, descripción, fecha inicio, fecha fin, distancia, dificultad, ubicaciones
2. **Given** un usuario completando el formulario de nuevo viaje con todos los campos obligatorios (título, descripción, fecha inicio), **When** hace clic en "Publicar", **Then** el viaje se guarda como publicado y aparece en su perfil
3. **Given** un usuario con un viaje publicado, **When** cualquier visitante accede a su perfil, **Then** puede ver el viaje con toda su información
4. **Given** un usuario creando un viaje, **When** introduce una distancia en kilómetros, **Then** el sistema acepta valores numéricos positivos hasta 10,000 km
5. **Given** un usuario seleccionando dificultad, **When** ve las opciones disponibles, **Then** puede elegir entre: Fácil, Moderada, Difícil, Muy Difícil
6. **Given** un usuario añadiendo ubicaciones a su viaje, **When** introduce nombres de ciudades/lugares, **Then** puede agregar múltiples ubicaciones separadas que representan la ruta

---

### User Story 2 - Galería de Fotos del Viaje (Priority: P2)

Un ciclista quiere enriquecer su entrada de viaje subiendo múltiples fotos que documentan visualmente su experiencia: paisajes, pueblos atravesados, la bicicleta en puntos icónicos, etc.

**Why this priority**: Las fotos son fundamentales para un diario de viajes visual y atractivo. Transforman una simple descripción textual en una experiencia inmersiva que inspira a otros ciclistas. Es la segunda característica más importante después de la creación básica de entradas.

**Independent Test**: Puede ser probado creando un viaje, subiendo múltiples fotos (JPG/PNG), verificando que se muestran en galería ordenada, y confirmando que se pueden ver en tamaño completo.

**Acceptance Scenarios**:

1. **Given** un usuario editando/creando un viaje, **When** accede a la sección de fotos, **Then** puede subir múltiples imágenes (hasta 20 por viaje)
2. **Given** un usuario subiendo fotos, **When** selecciona archivos JPG, PNG o WebP de hasta 10MB cada uno, **Then** el sistema procesa y añade las fotos a la galería del viaje
3. **Given** un usuario con fotos en su viaje, **When** publica el viaje, **Then** las fotos se muestran en una galería organizada en el orden de subida
4. **Given** cualquier visitante viendo un viaje, **When** hace clic en una foto de la galería, **Then** puede verla en tamaño completo con opción de navegar entre fotos
5. **Given** un usuario con fotos ya subidas, **When** quiere eliminar una foto, **Then** puede removerla de la galería antes de publicar
6. **Given** un usuario organizando fotos, **When** reordena las imágenes mediante arrastrar y soltar, **Then** el orden se guarda y respeta al mostrar el viaje

---

### User Story 3 - Edición y Gestión de Viajes (Priority: P3)

Un ciclista que publicó un viaje se da cuenta de un error en la descripción o quiere añadir información adicional. Necesita poder editar viajes ya publicados, actualizar información, y si es necesario, eliminar viajes.

**Why this priority**: La capacidad de editar es importante para mantener la calidad del contenido, pero no es crítica para el MVP inicial. Los usuarios pueden crear viajes correctamente desde el principio, y la edición añade flexibilidad y control sobre el contenido a largo plazo.

**Independent Test**: Puede ser probado publicando un viaje, accediendo a la opción de editar, modificando campos, guardando cambios, y verificando que las actualizaciones se reflejan correctamente en el viaje publicado.

**Acceptance Scenarios**:

1. **Given** un usuario viendo su propio viaje publicado, **When** hace clic en "Editar viaje", **Then** accede al formulario de edición con todos los campos pre-llenados
2. **Given** un usuario editando un viaje publicado, **When** modifica campos y guarda, **Then** los cambios se reflejan inmediatamente en el viaje publicado
3. **Given** un usuario editando un viaje, **When** añade o elimina fotos, **Then** la galería se actualiza manteniendo el resto del contenido intacto
4. **Given** un usuario viendo su propio viaje, **When** selecciona "Eliminar viaje" y confirma la acción, **Then** el viaje se elimina permanentemente de su perfil y de la plataforma
5. **Given** un usuario que eliminó un viaje, **When** se recalculan sus estadísticas, **Then** los kilómetros y contadores se actualizan restando los datos del viaje eliminado
6. **Given** otro usuario (no propietario), **When** ve un viaje de otro ciclista, **Then** NO tiene opciones de editar o eliminar

---

### User Story 4 - Etiquetas y Categorización (Priority: P4)

Un ciclista con múltiples viajes quiere organizarlos mediante etiquetas personalizadas (ej: "Camino de Santiago", "Costa Mediterránea", "Viajes en familia", "Bikepacking") para facilitar la navegación y permitir que otros encuentren viajes similares.

**Why this priority**: Las etiquetas son útiles para organización y descubrimiento, pero solo tienen valor cuando ya existe contenido suficiente. Es una capa de organización que mejora la experiencia pero no es esencial para documentar viajes individuales.

**Independent Test**: Puede ser probado creando varios viajes, añadiendo diferentes etiquetas a cada uno, filtrando viajes por etiqueta en el perfil, y verificando que la categorización funciona correctamente.

**Acceptance Scenarios**:

1. **Given** un usuario creando/editando un viaje, **When** accede al campo de etiquetas, **Then** puede añadir múltiples etiquetas personalizadas separadas por comas
2. **Given** un usuario escribiendo una etiqueta, **When** introduce texto, **Then** el sistema acepta etiquetas de hasta 30 caracteres alfanuméricos (y espacios)
3. **Given** un usuario añadiendo etiquetas, **When** agrega más de 10 etiquetas, **Then** el sistema muestra un mensaje indicando el límite máximo de 10 etiquetas por viaje
4. **Given** un usuario en su perfil con múltiples viajes etiquetados, **When** hace clic en una etiqueta, **Then** ve todos sus viajes que comparten esa etiqueta
5. **Given** cualquier visitante viendo un viaje, **When** ve las etiquetas del viaje, **Then** puede hacer clic en ellas para descubrir otros viajes del mismo autor con esa etiqueta
6. **Given** un usuario editando etiquetas, **When** elimina una etiqueta de un viaje, **Then** la etiqueta se remueve sin afectar otros viajes que la usen

---

### User Story 5 - Borradores de Viaje (Priority: P5)

Un ciclista está documentando un viaje largo pero no ha terminado de escribir toda la narrativa o subir todas las fotos. Quiere guardar su progreso como borrador y continuar editando antes de publicar.

**Why this priority**: Los borradores mejoran la experiencia de creación al permitir trabajo en progreso sin presión de completar todo de una vez. Sin embargo, es posible crear viajes directamente sin esta funcionalidad intermedia.

**Independent Test**: Puede ser probado creando un viaje, guardándolo como borrador sin publicar, cerrando sesión, volviendo a entrar, y verificando que el borrador se conserva y puede editarse o publicarse posteriormente.

**Acceptance Scenarios**:

1. **Given** un usuario creando un nuevo viaje, **When** hace clic en "Guardar borrador" en lugar de "Publicar", **Then** el viaje se guarda como borrador privado no visible públicamente
2. **Given** un usuario con borradores guardados, **When** accede a su área de "Mis viajes", **Then** ve una sección separada de "Borradores" con todos sus viajes no publicados
3. **Given** un usuario con un borrador, **When** hace clic en él, **Then** puede continuar editándolo desde donde lo dejó
4. **Given** un usuario editando un borrador, **When** lo completa y hace clic en "Publicar", **Then** el viaje pasa de borrador a publicado y aparece en su perfil público
5. **Given** un usuario con un borrador, **When** decide descartarlo y hace clic en "Eliminar borrador", **Then** el borrador se elimina sin afectar viajes publicados
6. **Given** un visitante viendo el perfil de un usuario, **When** el usuario tiene borradores guardados, **Then** los borradores NO son visibles para otros (solo para el propietario)

---

### Edge Cases

- ¿Qué ocurre si un usuario intenta publicar un viaje sin título o descripción (campos obligatorios)?
- ¿Cómo maneja el sistema la subida simultánea de 20 fotos de 10MB cada una?
- ¿Qué sucede si un usuario introduce una distancia negativa o texto en el campo de kilómetros?
- ¿Cómo se comporta el sistema si se suben fotos en formatos no soportados (GIF, TIFF, RAW)?
- ¿Qué ocurre si un usuario intenta añadir más de 20 fotos a un viaje?
- ¿Cómo se manejan fechas inválidas (fecha fin anterior a fecha inicio)?
- ¿Qué sucede con las fotos de un viaje cuando este se elimina? ¿Se liberan del almacenamiento?
- ¿Cómo se comporta el editor de texto con contenido muy largo (>10,000 caracteres)?
- ¿Qué ocurre si un usuario tiene 50 borradores sin publicar?
- ¿Cómo se previene la duplicación accidental de viajes (mismo título, fechas, distancia)?

## Requirements *(mandatory)*

### Functional Requirements

**Creación y Publicación de Viajes:**

- **FR-001**: Los usuarios autenticados DEBEN poder crear nuevas entradas de viaje
- **FR-002**: El sistema DEBE requerir campos obligatorios: título (máximo 100 caracteres), descripción (mínimo 50 caracteres), fecha de inicio
- **FR-003**: El sistema DEBE permitir campos opcionales: fecha de fin, distancia (km), dificultad, ubicaciones visitadas
- **FR-004**: El sistema DEBE ofrecer niveles de dificultad predefinidos: Fácil, Moderada, Difícil, Muy Difícil
- **FR-005**: El sistema DEBE validar que las distancias sean valores numéricos positivos entre 0.1 y 10,000 km
- **FR-006**: El sistema DEBE validar que la fecha de inicio no sea futura y que la fecha de fin no sea anterior a la fecha de inicio
- **FR-007**: Los usuarios DEBEN poder publicar viajes, haciendo que sean visibles públicamente en su perfil
- **FR-008**: El sistema DEBE mostrar viajes publicados en orden cronológico inverso (más recientes primero) en el perfil

**Galería de Fotos:**

- **FR-009**: Los usuarios DEBEN poder subir múltiples fotos a cada viaje (máximo 20 fotos por viaje)
- **FR-010**: El sistema DEBE aceptar formatos de imagen: JPG, PNG, WebP con tamaño máximo de 10MB por foto
- **FR-011**: El sistema DEBE redimensionar y optimizar automáticamente las fotos para web (versión optimizada + thumbnail)
- **FR-012**: El sistema DEBE mantener el orden de las fotos según fueron subidas, permitiendo reordenamiento manual
- **FR-013**: Los usuarios DEBEN poder eliminar fotos individuales de la galería durante la edición
- **FR-014**: El sistema DEBE mostrar las fotos en galería con opción de vista ampliada (lightbox)
- **FR-015**: Las fotos DEBEN tener texto alternativo automático para accesibilidad

**Edición y Gestión:**

- **FR-016**: Los usuarios DEBEN poder editar sus propios viajes publicados
- **FR-017**: Los usuarios DEBEN poder eliminar sus propios viajes con confirmación obligatoria
- **FR-018**: El sistema DEBE actualizar automáticamente las estadísticas del usuario cuando se edita o elimina un viaje
- **FR-019**: Solo el propietario del viaje DEBE tener permisos de edición y eliminación
- **FR-020**: El sistema DEBE prevenir edición concurrente mostrando advertencia si el viaje está siendo editado

**Etiquetas y Categorización:**

- **FR-021**: Los usuarios DEBEN poder añadir etiquetas personalizadas a sus viajes (máximo 10 etiquetas por viaje)
- **FR-022**: Las etiquetas DEBEN tener máximo 30 caracteres alfanuméricos (incluyendo espacios y guiones)
- **FR-023**: El sistema DEBE permitir filtrar viajes por etiqueta en el perfil del usuario
- **FR-024**: El sistema DEBE mostrar etiquetas como enlaces clicables en la vista de viaje
- **FR-025**: Las etiquetas DEBEN ser case-insensitive ("Bikepacking" = "bikepacking")

**Borradores:**

- **FR-026**: Los usuarios DEBEN poder guardar viajes como borradores privados sin publicarlos
- **FR-027**: Los borradores DEBEN ser visibles solo para su propietario en una sección separada "Mis Borradores"
- **FR-028**: Los usuarios DEBEN poder convertir un borrador en viaje publicado en cualquier momento
- **FR-029**: Los usuarios DEBEN poder eliminar borradores sin afectar viajes publicados
- **FR-030**: El sistema DEBE permitir editar borradores ilimitadamente antes de publicar

**Editor de Contenido:**

- **FR-031**: El sistema DEBE proporcionar un editor de texto enriquecido con formato básico: negritas, cursivas, listas, enlaces
- **FR-032**: El editor DEBE soportar descripciones de hasta 50,000 caracteres
- **FR-033**: El sistema DEBE auto-guardar borradores cada 30 segundos durante la edición para prevenir pérdida de datos
- **FR-034**: El sistema DEBE sanitizar el contenido HTML para prevenir XSS

### Key Entities

- **Trip**: Entrada de viaje documentada por un ciclista. Atributos: ID único, propietario (User), título, descripción (texto enriquecido), fecha de inicio, fecha de fin (opcional), distancia en km (opcional), dificultad, ubicaciones (lista de strings), estado (publicado/borrador), fecha de creación, fecha de última edición, etiquetas (lista)

- **TripPhoto**: Fotografía asociada a un viaje. Atributos: ID único, viaje (Trip), archivo de imagen (URL almacenamiento), thumbnail (URL), orden en galería, fecha de subida, tamaño en bytes, dimensiones (ancho x alto)

- **Tag**: Etiqueta para categorizar viajes. Atributos: nombre normalizado (lowercase), fecha de primer uso. Relación: muchos-a-muchos con Trip

- **TripLocation**: Ubicación visitada durante un viaje. Atributos: viaje (Trip), nombre del lugar, país (opcional), orden en la ruta

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Creación y Publicación:**

- **SC-001**: Los usuarios pueden crear y publicar un viaje completo (con texto y fotos) en menos de 10 minutos
- **SC-002**: El 85% de los usuarios que inician la creación de un viaje lo completan y publican
- **SC-003**: El sistema procesa la publicación de un viaje en menos de 2 segundos (sin fotos) o menos de 5 segundos (con fotos)
- **SC-004**: El 90% de los viajes publicados contienen al menos 100 caracteres de descripción

**Galería de Fotos:**

- **SC-005**: Las fotos se suben y procesan en menos de 3 segundos por foto (promedio con conexión estándar)
- **SC-006**: El sistema procesa correctamente el 100% de las fotos en formatos soportados (JPG, PNG, WebP)
- **SC-007**: Las fotos optimizadas ocupan máximo el 30% del tamaño original manteniendo calidad visual aceptable
- **SC-008**: El 70% de los viajes publicados incluyen al menos 3 fotos
- **SC-009**: La galería de fotos carga completamente en menos de 2 segundos para viajes con 10 fotos

**Edición y Gestión:**

- **SC-010**: Los usuarios pueden editar un viaje publicado y guardar cambios en menos de 1 minuto
- **SC-011**: El 95% de las ediciones de viajes se completan sin errores
- **SC-012**: Las estadísticas del usuario se actualizan en menos de 3 segundos después de eliminar un viaje
- **SC-013**: Menos del 2% de los viajes publicados son eliminados por sus autores (indica contenido de calidad)

**Etiquetas y Organización:**

- **SC-014**: El 60% de los viajes incluyen al menos 2 etiquetas
- **SC-015**: Filtrar viajes por etiqueta muestra resultados en menos de 1 segundo
- **SC-016**: El sistema maneja correctamente búsquedas de etiquetas con acentos y mayúsculas/minúsculas

**Borradores:**

- **SC-017**: El 40% de los viajes se guardan como borrador al menos una vez antes de publicarse
- **SC-018**: El auto-guardado de borradores funciona el 100% del tiempo sin pérdida de datos
- **SC-019**: Los usuarios convierten el 80% de sus borradores en viajes publicados eventualmente
- **SC-020**: El sistema mantiene borradores sin límite de tiempo (hasta que el usuario los publique o elimine)

**Rendimiento y Escala:**

- **SC-021**: El sistema maneja 50 creaciones de viaje concurrentes sin degradación
- **SC-022**: Un usuario puede gestionar hasta 500 viajes publicados sin problemas de rendimiento
- **SC-023**: La carga de un viaje individual (texto + galería) toma menos de 2 segundos en el percentil 95
- **SC-024**: El almacenamiento de fotos se optimiza para mantener menos de 5MB promedio por viaje

**Experiencia de Usuario:**

- **SC-025**: Los mensajes de validación de formularios son claros y accionables (90% comprensión sin ayuda)
- **SC-026**: El editor de texto enriquecido funciona sin errores en navegadores modernos (Chrome, Firefox, Safari, Edge)
- **SC-027**: El 95% de los usuarios publican su primer viaje dentro de la primera semana de registro
- **SC-028**: La tasa de abandono en el formulario de creación de viaje es menor al 20%

## Assumptions

1. **Contenido generado por usuario**: Todo el contenido (textos, fotos) es creado por los usuarios, no hay contenido pre-poblado
2. **Propiedad del contenido**: Los viajes pertenecen exclusivamente a su creador; no hay viajes colaborativos en v1
3. **Visibilidad**: Los viajes publicados son públicos por defecto; privacidad granular se considerará en futuras versiones
4. **Formato de texto**: El editor soporta formato básico (negritas, cursivas, listas); no se requiere Markdown o HTML avanzado inicialmente
5. **Almacenamiento de fotos**: Las fotos se almacenan en el sistema de la plataforma; integración con servicios externos (Flickr, Instagram) es futura
6. **Geolocalización**: Las ubicaciones son campos de texto libre; integración con mapas y coordenadas GPS se maneja en feature separada (003-gps-routes)
7. **Idioma del contenido**: Los usuarios escriben en el idioma de su preferencia; no hay traducción automática
8. **Moderación**: No hay moderación de contenido automática en v1; se asume contenido apropiado
9. **Versioning**: No se mantiene historial de ediciones; solo la versión actual del viaje
10. **Multimedia**: Solo fotos estáticas; no se soportan videos, audio, o archivos GPX en esta feature (GPX va en 003-gps-routes)
11. **Interacción social**: No hay likes, comentarios, o compartidos en esta feature (va en 004-social-network)
12. **Búsqueda global**: Búsqueda de viajes entre todos los usuarios es parte de otra feature; aquí solo filtrado personal por etiquetas

## Out of Scope

Las siguientes funcionalidades NO están incluidas en esta especificación:

- Integración con archivos GPX o rutas GPS (feature 003-gps-routes)
- Comentarios, likes, o compartir viajes (feature 004-social-network)
- Estadísticas automáticas calculadas desde GPX (elevación, velocidad) (feature 003-gps-routes)
- Mapas interactivos mostrando la ruta (feature 003-gps-routes)
- Búsqueda global de viajes entre todos los usuarios
- Recomendaciones de viajes similares
- Exportación de viajes a PDF o formatos externos
- Importación masiva de viajes desde otras plataformas
- Programación de publicación (publicar en fecha futura)
- Viajes colaborativos o multi-autor
- Sistema de plantillas para viajes recurrentes
- Integración con redes sociales externas (compartir en Facebook, Twitter)
- Monetización o viajes premium/patrocinados
- Moderación automática de contenido inapropiado
- Versionado o historial de cambios en viajes
- Soporte para videos o audio en viajes
- Reconocimiento automático de lugares en fotos (geotagging)
- Watermarks o protección de copyright en fotos
