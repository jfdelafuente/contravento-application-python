# Feature Specification: Rutas GPS Interactivas

**Feature Branch**: `003-gps-routes`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Rutas GPS interactivas con mapas, perfiles de elevación y estadísticas automáticas"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir y Procesar Archivo GPX (Priority: P1)

Un ciclista que acaba de completar el Camino del Cid tiene el archivo GPX de su ruta guardado en su GPS o smartphone. Quiere subirlo a su entrada de viaje en ContraVento para que el sistema calcule automáticamente la distancia recorrida, la elevación, y otros datos del trayecto.

**Why this priority**: Es la funcionalidad fundacional de este feature. Sin la capacidad de subir y procesar archivos GPX, ninguna otra característica de visualización o estadísticas puede funcionar. Esta historia entrega el valor mínimo: importar datos GPS y extraer información básica.

**Independent Test**: Puede ser probado creando un viaje, subiendo un archivo GPX válido, y verificando que el sistema lo procesa correctamente, extrayendo y mostrando estadísticas básicas (distancia, elevación, puntos del track).

**Acceptance Scenarios**:

1. **Given** un usuario editando un viaje, **When** hace clic en "Subir archivo GPX", **Then** puede seleccionar y subir un archivo .gpx de hasta 10MB
2. **Given** un usuario que sube un archivo GPX válido, **When** el archivo se procesa, **Then** el sistema extrae automáticamente: distancia total, elevación ganada, elevación perdida, altitud máxima, altitud mínima, punto de inicio, punto de fin
3. **Given** un archivo GPX procesado, **When** el viaje se publica, **Then** las estadísticas calculadas se muestran junto al viaje
4. **Given** un usuario subiendo un archivo GPX inválido o corrupto, **When** el sistema intenta procesarlo, **Then** muestra un mensaje de error claro indicando el problema
5. **Given** un usuario que sube un archivo GPX, **When** el archivo contiene múltiples tracks o segmentos, **Then** el sistema procesa todos los segmentos y calcula estadísticas agregadas

---

### User Story 2 - Visualización en Mapa Interactivo (Priority: P2)

Un ciclista quiere mostrar visualmente su ruta en un mapa interactivo para que otros usuarios puedan ver exactamente qué camino siguió, explorar detalles del terreno, y hacer zoom en secciones específicas de interés.

**Why this priority**: El mapa es la representación visual más importante de la ruta GPS. Permite a otros ciclistas entender geográficamente el recorrido, evaluar si les interesa hacer una ruta similar, y planificar sus propias aventuras. Es la segunda característica más valiosa después del procesamiento básico de GPX.

**Independent Test**: Puede ser probado subiendo un GPX, accediendo al viaje publicado, y verificando que el mapa muestra correctamente la ruta con controles de zoom, pan, y marcadores de inicio/fin.

**Acceptance Scenarios**:

1. **Given** un viaje con archivo GPX procesado, **When** se visualiza el viaje, **Then** se muestra un mapa interactivo con la ruta trazada sobre él
2. **Given** un mapa mostrando la ruta, **When** el usuario interactúa con él, **Then** puede hacer zoom in/out, mover el mapa (pan), y ver diferentes capas de mapa (terreno, satélite, ciclismo)
3. **Given** una ruta en el mapa, **When** se renderiza, **Then** muestra marcadores claros en el punto de inicio (verde) y punto de fin (rojo)
4. **Given** un mapa con ruta larga, **When** se carga inicialmente, **Then** el zoom se ajusta automáticamente para mostrar toda la ruta completa
5. **Given** un visitante viendo el mapa, **When** hace clic en cualquier punto de la ruta, **Then** ve información de ese punto: coordenadas, altitud, distancia desde el inicio
6. **Given** un mapa interactivo, **When** se visualiza en móvil, **Then** funciona correctamente con gestos touch (pinch to zoom, drag to pan)

---

### User Story 3 - Perfil de Elevación Interactivo (Priority: P3)

Un ciclista quiere mostrar gráficamente el perfil de elevación de su ruta para que otros puedan visualizar los desniveles, identificar subidas y bajadas pronunciadas, y evaluar la dificultad del recorrido.

**Why this priority**: El perfil de elevación es crítico para ciclistas al evaluar la dificultad de una ruta. Sin embargo, depende del procesamiento GPX (P1) y es menos crítico que la visualización geográfica en mapa (P2). Añade información valiosa pero no es esencial para la funcionalidad básica.

**Independent Test**: Puede ser probado subiendo un GPX con datos de elevación, visualizando el viaje, y verificando que aparece un gráfico interactivo mostrando el perfil de elevación con información detallada al interactuar.

**Acceptance Scenarios**:

1. **Given** un viaje con archivo GPX que contiene datos de elevación, **When** se visualiza el viaje, **Then** se muestra un gráfico del perfil de elevación debajo o junto al mapa
2. **Given** un perfil de elevación mostrado, **When** el usuario pasa el cursor sobre el gráfico, **Then** ve información del punto: distancia acumulada, altitud, gradiente/pendiente
3. **Given** un usuario interactuando con el perfil de elevación, **When** hace clic en un punto del gráfico, **Then** el mapa se centra en ese punto correspondiente de la ruta
4. **Given** un perfil de elevación, **When** se visualiza, **Then** muestra claramente las subidas (relleno verde/amarillo) y bajadas (relleno azul) para facilitar lectura
5. **Given** un archivo GPX sin datos de elevación, **When** se procesa, **Then** el sistema muestra un mensaje indicando que no hay datos de elevación disponibles
6. **Given** un perfil de elevación en móvil, **When** se visualiza, **Then** se adapta responsivamente al ancho de pantalla manteniendo legibilidad

---

### User Story 4 - Puntos de Interés en la Ruta (Priority: P4)

Un ciclista quiere marcar puntos específicos de interés a lo largo de su ruta (un mirador espectacular, un pueblo pintoresco, una fuente de agua, un restaurante recomendado) para compartir recomendaciones con otros ciclistas que quieran hacer la ruta.

**Why this priority**: Los puntos de interés enriquecen la narrativa del viaje y aportan valor práctico, pero son una capa adicional sobre la funcionalidad base. No son esenciales para mostrar la ruta GPS, pero mejoran significativamente la experiencia cuando existen.

**Independent Test**: Puede ser probado subiendo un GPX, añadiendo manualmente varios puntos de interés con descripciones, y verificando que se muestran correctamente en el mapa con iconos distintivos y popups informativos.

**Acceptance Scenarios**:

1. **Given** un usuario editando un viaje con GPX, **When** hace clic en "Añadir punto de interés", **Then** puede seleccionar un punto del mapa o introducir coordenadas manualmente
2. **Given** un usuario añadiendo un punto de interés, **When** completa el formulario, **Then** puede especificar: nombre, descripción, tipo (mirador, pueblo, fuente, alojamiento, restaurante, otro), y opcionalmente foto
3. **Given** un viaje con puntos de interés, **When** se visualiza el mapa, **Then** los puntos aparecen con iconos distintivos según su tipo superpuestos a la ruta
4. **Given** un visitante viendo el mapa, **When** hace clic en un icono de punto de interés, **Then** se abre un popup mostrando nombre, descripción, foto (si hay), y distancia desde el inicio de la ruta
5. **Given** un usuario con múltiples puntos de interés, **When** visualiza el viaje, **Then** puede filtrar/mostrar u ocultar puntos por tipo
6. **Given** un usuario editando puntos de interés, **When** quiere reordenar o eliminar uno, **Then** puede hacerlo sin afectar la ruta GPX principal

---

### User Story 5 - Estadísticas Avanzadas y Análisis (Priority: P5)

Un ciclista avanzado quiere ver estadísticas detalladas de su ruta más allá de lo básico: velocidad promedio, velocidad máxima, tiempo en movimiento vs tiempo total, gradientes por sección, comparación con otras rutas similares.

**Why this priority**: Las estadísticas avanzadas son valiosas para ciclistas entusiastas que quieren analizar su rendimiento en detalle, pero la mayoría de usuarios se conforman con métricas básicas (distancia, elevación). Es una mejora incremental que aporta valor a un segmento específico de usuarios.

**Independent Test**: Puede ser probado subiendo un GPX con timestamps, y verificando que el sistema calcula y muestra estadísticas avanzadas como velocidades, tiempos, y análisis de gradientes correctamente.

**Acceptance Scenarios**:

1. **Given** un archivo GPX con timestamps (tiempo en cada punto), **When** se procesa, **Then** el sistema calcula velocidad promedio, velocidad máxima, tiempo total, tiempo en movimiento
2. **Given** estadísticas de velocidad calculadas, **When** se muestran en el viaje, **Then** aparecen claramente junto a las estadísticas básicas
3. **Given** una ruta procesada, **When** el sistema analiza gradientes, **Then** identifica y muestra las secciones de mayor pendiente (top 3 subidas más duras)
4. **Given** un perfil de elevación, **When** se visualiza con estadísticas avanzadas, **Then** muestra zonas coloreadas según gradiente: llano (0-3%), moderado (3-6%), empinado (6-10%), muy empinado (>10%)
5. **Given** un archivo GPX sin timestamps, **When** se procesa, **Then** el sistema indica que estadísticas de velocidad no están disponibles pero muestra el resto de datos
6. **Given** múltiples viajes del mismo usuario con GPX, **When** visualiza uno, **Then** puede ver comparativas básicas: "Este es tu viaje más largo", "Mayor elevación ganada hasta ahora"

---

### Edge Cases

- ¿Qué ocurre si un usuario sube un archivo de más de 10MB o en formato incorrecto (.kml, .fit, .tcx)?
- ¿Cómo maneja el sistema archivos GPX con miles de puntos (tracks muy detallados de varios días)?
- ¿Qué sucede si un archivo GPX tiene datos de elevación incorrectos o anómalos (picos de 9999m)?
- ¿Cómo se comporta el sistema si un GPX contiene múltiples rutas independientes en un solo archivo?
- ¿Qué ocurre si el mapa no puede cargar (problemas de servicio de mapas externo)?
- ¿Cómo se manejan coordenadas inválidas o fuera de rango (-200°, 400°)?
- ¿Qué sucede si un usuario añade 50 puntos de interés a una sola ruta?
- ¿Cómo se calculan estadísticas cuando hay pausas largas en el track GPS (paradas para comer)?
- ¿Qué ocurre si dos viajes diferentes tienen el mismo archivo GPX?
- ¿Cómo se comporta el sistema con rutas circulares (inicio y fin en el mismo punto)?

## Requirements *(mandatory)*

### Functional Requirements

**Procesamiento de Archivos GPX:**

- **FR-001**: Los usuarios DEBEN poder subir archivos GPX a sus viajes (máximo 10MB por archivo)
- **FR-002**: El sistema DEBE aceptar formato GPX estándar (XML) versión 1.0 y 1.1
- **FR-003**: El sistema DEBE validar la estructura del archivo GPX antes de procesarlo
- **FR-004**: El sistema DEBE extraer automáticamente del GPX: lista de puntos (trackpoints) con coordenadas (lat/lon), elevación de cada punto (si disponible), timestamps (si disponible)
- **FR-005**: El sistema DEBE calcular automáticamente: distancia total en kilómetros, elevación ganada total (metros), elevación perdida total (metros), altitud máxima, altitud mínima, coordenadas de inicio, coordenadas de fin
- **FR-006**: El sistema DEBE procesar archivos GPX con múltiples tracks/segmentos agregándolos en una sola ruta
- **FR-007**: El sistema DEBE mostrar mensajes de error claros si el archivo es inválido, corrupto, o excede el tamaño máximo
- **FR-008**: El procesamiento de archivos GPX grandes (>1MB) DEBE ser asíncrono para no bloquear la interfaz

**Visualización en Mapa:**

- **FR-009**: El sistema DEBE mostrar la ruta GPX en un mapa interactivo usando un servicio de mapas (OpenStreetMap, Mapbox, Google Maps)
- **FR-010**: El mapa DEBE permitir zoom in/out, pan (arrastrar), y mostrar diferentes capas (mapa base, terreno, satélite, especializado ciclismo)
- **FR-011**: El mapa DEBE mostrar marcadores distintivos en el punto de inicio (verde) y punto de fin (rojo) de la ruta
- **FR-012**: El mapa DEBE ajustarse automáticamente al zoom apropiado para mostrar la ruta completa al cargar
- **FR-013**: Al hacer clic en cualquier punto de la ruta en el mapa, DEBE mostrar información: coordenadas, altitud (si disponible), distancia desde inicio
- **FR-014**: El mapa DEBE funcionar correctamente en dispositivos móviles con gestos touch (pinch zoom, pan)
- **FR-015**: El mapa DEBE mostrar la ruta como una línea continua con color distintivo (por defecto azul/rojo según preferencias ciclismo)

**Perfil de Elevación:**

- **FR-016**: Si el GPX contiene datos de elevación, el sistema DEBE generar un gráfico del perfil de elevación
- **FR-017**: El perfil de elevación DEBE mostrar la altitud en el eje Y y la distancia acumulada en el eje X
- **FR-018**: Al pasar el cursor sobre el perfil, DEBE mostrar tooltip con: distancia acumulada, altitud en ese punto, gradiente/pendiente
- **FR-019**: Al hacer clic en un punto del perfil, el mapa DEBE centrarse en ese punto correspondiente de la ruta
- **FR-020**: El perfil DEBE visualizar claramente subidas y bajadas mediante relleno de color diferenciado
- **FR-021**: Si el GPX no contiene elevación, el sistema DEBE mostrar un mensaje indicando que no hay datos disponibles
- **FR-022**: El perfil de elevación DEBE ser responsive y adaptarse a diferentes tamaños de pantalla

**Puntos de Interés (POI):**

- **FR-023**: Los usuarios DEBEN poder añadir puntos de interés manualmente en el mapa de la ruta
- **FR-024**: Cada punto de interés DEBE tener: nombre (obligatorio, máximo 100 caracteres), descripción (opcional, máximo 500 caracteres), tipo (mirador, pueblo, fuente, alojamiento, restaurante, otro), coordenadas, foto opcional
- **FR-025**: Los puntos de interés DEBEN aparecer en el mapa con iconos distintivos según su tipo
- **FR-026**: Al hacer clic en un POI en el mapa, DEBE mostrar popup con toda su información
- **FR-027**: El sistema DEBE permitir filtrar/mostrar u ocultar POIs por tipo en el mapa
- **FR-028**: Los usuarios DEBEN poder editar y eliminar sus propios POIs
- **FR-029**: El sistema DEBE limitar a máximo 20 POIs por viaje

**Estadísticas Avanzadas:**

- **FR-030**: Si el GPX contiene timestamps, el sistema DEBE calcular: velocidad promedio, velocidad máxima, tiempo total de ruta, tiempo en movimiento (excluyendo paradas >5 minutos)
- **FR-031**: El sistema DEBE identificar y destacar las 3 subidas más difíciles (por longitud × pendiente promedio)
- **FR-032**: El sistema DEBE clasificar gradientes de la ruta en categorías: llano (0-3%), moderado (3-6%), empinado (6-10%), muy empinado (>10%)
- **FR-033**: Si no hay timestamps, el sistema DEBE indicar claramente que estadísticas de velocidad/tiempo no están disponibles
- **FR-034**: El sistema DEBE sanitizar datos anómalos de elevación (valores >8850m o <-420m se marcan como sospechosos)

**Gestión de Datos GPS:**

- **FR-035**: Los usuarios DEBEN poder reemplazar el archivo GPX de un viaje con uno nuevo
- **FR-036**: Al eliminar un viaje, el sistema DEBE eliminar también todos los datos GPS asociados
- **FR-037**: El sistema DEBE almacenar eficientemente los datos GPX (simplificación de puntos redundantes manteniendo precisión)
- **FR-038**: Un viaje PUEDE tener como máximo 1 archivo GPX asociado
- **FR-039**: El sistema DEBE permitir descargar el archivo GPX original desde el viaje publicado

### Key Entities

- **GPXFile**: Archivo GPS subido por el usuario. Atributos: ID único, viaje asociado (Trip), archivo original (URL almacenamiento), tamaño en bytes, fecha de subida, estado de procesamiento (pendiente/procesado/error), mensaje de error (si aplica)

- **GPXTrack**: Datos procesados del archivo GPX. Atributos: archivo GPX (GPXFile), distancia total (km), elevación ganada (m), elevación perdida (m), altitud máxima (m), altitud mínima (m), punto inicio (lat/lon), punto fin (lat/lon), número total de puntos, tiene elevación (booleano), tiene timestamps (booleano)

- **TrackPoint**: Punto individual del track GPS. Atributos: track (GPXTrack), latitud, longitud, elevación (opcional), timestamp (opcional), distancia acumulada desde inicio, orden/índice en secuencia

- **PointOfInterest**: Punto de interés marcado por el usuario en la ruta. Atributos: ID único, viaje (Trip), nombre, descripción, tipo (enum), latitud, longitud, foto (URL opcional), orden en la ruta, distancia desde inicio

- **RouteStatistics**: Estadísticas calculadas del GPX (avanzadas). Atributos: track (GPXTrack), velocidad promedio (km/h), velocidad máxima (km/h), tiempo total (minutos), tiempo en movimiento (minutos), gradiente promedio (%), gradiente máximo (%), top subidas (lista de 3 segmentos)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Procesamiento GPX:**

- **SC-001**: El sistema procesa correctamente el 99% de los archivos GPX válidos estándar
- **SC-002**: Archivos GPX pequeños (<1MB) se procesan en menos de 3 segundos
- **SC-003**: Archivos GPX grandes (5-10MB) se procesan en menos de 15 segundos
- **SC-004**: Los cálculos de distancia tienen precisión >95% comparados con mediciones de referencia
- **SC-005**: Los cálculos de elevación tienen precisión >90% comparados con mediciones de referencia
- **SC-006**: El 80% de los viajes publicados incluyen un archivo GPX

**Visualización en Mapa:**

- **SC-007**: El mapa con ruta carga completamente en menos de 3 segundos para rutas con hasta 1000 puntos
- **SC-008**: El mapa funciona sin errores en navegadores modernos (Chrome, Firefox, Safari, Edge) desktop y móvil
- **SC-009**: El 95% de los usuarios pueden interactuar con el mapa (zoom, pan) sin confusión
- **SC-010**: El mapa se renderiza correctamente en el 100% de las rutas válidas procesadas
- **SC-011**: La interacción con el mapa (zoom, pan, click) responde en menos de 200ms

**Perfil de Elevación:**

- **SC-012**: El perfil de elevación se genera correctamente para el 100% de los GPX con datos de altitud
- **SC-013**: El gráfico de perfil carga en menos de 2 segundos para rutas con hasta 1000 puntos
- **SC-014**: La interacción con el perfil (hover, click) responde en menos de 100ms
- **SC-015**: El 90% de los usuarios entienden el perfil de elevación sin necesidad de ayuda
- **SC-016**: El sincronizado entre perfil y mapa (click en perfil → mapa se centra) funciona en <300ms

**Puntos de Interés:**

- **SC-017**: Los usuarios pueden añadir un POI en menos de 1 minuto
- **SC-018**: El 60% de los viajes con GPX incluyen al menos 1 punto de interés
- **SC-019**: Los iconos de POI son claramente distinguibles en el mapa (90% tasa de reconocimiento)
- **SC-020**: El sistema maneja correctamente hasta 20 POIs por ruta sin degradación de rendimiento

**Estadísticas Avanzadas:**

- **SC-021**: Las estadísticas de velocidad son precisas dentro del ±5% para GPX con timestamps correctos
- **SC-022**: El sistema identifica correctamente las subidas más duras en el 95% de los casos
- **SC-023**: El cálculo de gradientes es preciso dentro del ±2% comparado con cálculos manuales
- **SC-024**: El 70% de los ciclistas avanzados utilizan las estadísticas avanzadas cuando están disponibles

**Rendimiento y Escala:**

- **SC-025**: El sistema maneja rutas con hasta 10,000 puntos sin errores
- **SC-026**: El almacenamiento optimizado reduce el tamaño de datos GPX en al menos 30% sin pérdida de precisión visual
- **SC-027**: El sistema procesa 20 uploads de GPX concurrentes sin degradación
- **SC-028**: La descarga del archivo GPX original toma menos de 2 segundos para archivos de hasta 10MB

**Experiencia de Usuario:**

- **SC-029**: El 90% de los usuarios suben exitosamente su primer archivo GPX sin ayuda
- **SC-030**: Los mensajes de error de validación GPX son claros y accionables (85% comprensión)
- **SC-031**: El 85% de los usuarios encuentran el mapa y perfil de elevación útiles para evaluar rutas
- **SC-032**: La tasa de abandono durante la subida de GPX es menor al 10%

## Assumptions

1. **Formato GPX estándar**: Solo se soporta formato GPX (no KML, FIT, TCX) en la versión inicial
2. **Servicio de mapas externo**: Se utiliza un proveedor de mapas externo (OpenStreetMap/Mapbox); no mapas propios
3. **Procesamiento server-side**: El parsing y cálculos de GPX se realizan en el servidor, no en el cliente
4. **Un GPX por viaje**: Cada viaje puede tener máximo 1 archivo GPX; no se soportan múltiples rutas por viaje
5. **Elevación de GPX**: Se usa la elevación del archivo GPX; no se consultan servicios externos de elevación (SRTM) en v1
6. **Coordenadas WGS84**: Se asume sistema de coordenadas WGS84 (estándar GPS)
7. **Timestamps opcionales**: Muchos GPX no tienen timestamps; funcionalidad básica debe trabajar sin ellos
8. **Puntos de interés manuales**: Los POI se añaden manualmente; no hay importación automática desde el GPX (waypoints)
9. **Mapas online**: Los mapas requieren conexión a internet; no hay soporte offline
10. **Simplificación de tracks**: Para optimizar rendimiento, tracks muy densos se pueden simplificar usando algoritmos (Douglas-Peucker) sin afectar visualización
11. **Descarga pública**: Cualquier visitante puede descargar el archivo GPX de viajes públicos
12. **Sin edición de GPX**: No hay editor de rutas GPS; solo visualización de datos existentes

## Out of Scope

Las siguientes funcionalidades NO están incluidas en esta especificación:

- Planificador de rutas (crear rutas desde cero en el mapa)
- Editor de rutas GPS (modificar tracks existentes)
- Importación de otros formatos (KML, FIT, TCX, GeoJSON)
- Consulta de elevación desde servicios externos (SRTM, Google Elevation API)
- Análisis de cadencia, potencia, frecuencia cardíaca (datos avanzados de ciclocomputadores)
- Comparación de rutas entre múltiples usuarios
- Segmentos Strava-style (KOMs, clasificaciones)
- Navegación en tiempo real o instrucciones giro a giro
- Sincronización automática con dispositivos GPS o apps (Garmin, Wahoo, Strava)
- Exportación a otros formatos (KML, FIT, TCX)
- Mapas offline o descarga de tiles
- Modo 3D o vista street-view integrada
- Análisis de temperatura, clima, condiciones meteorológicas
- Alertas de peligros en la ruta (tráfico, terreno difícil)
- Importación automática de waypoints como POIs
- Rutas multi-día con separación por etapas (en v1 todo es una ruta continua)
- Animación de la ruta (playback temporal del viaje)
- Integración con sensores IoT o dispositivos wearables
