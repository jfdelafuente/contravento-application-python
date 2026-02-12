# Feature Specification: GPS Trip Creation Wizard

**Feature Branch**: `017-gps-trip-wizard`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "Implementar flujo completo de creación de viajes con GPS: modal de selección pre-creación (con/sin GPS), wizard paso a paso para carga GPX con procesamiento de telemetría, formulario de detalles con dificultad automática calculada por IA, mapa interactivo con visualización de track, funcionalidad POI para marcar hasta 6 puntos con descripciones y fotos, y publicación final del viaje"

## User Scenarios & Testing

### User Story 1 - Select Trip Creation Mode (Priority: P1)

Como ciclista que quiere crear un nuevo viaje, quiero poder elegir si crear el viaje con o sin datos GPS desde el principio, para poder seguir el flujo más apropiado a mi situación (tengo archivo GPX vs solo quiero escribir una crónica).

**Why this priority**: Este es el punto de entrada para todo el flujo de creación con GPS. Sin esta selección inicial, los usuarios no pueden acceder a la funcionalidad GPS. Es la decisión fundamental que determina la experiencia completa.

**Independent Test**: Se puede probar de forma independiente mostrando el modal de selección, verificando que ambas opciones son clickeables, y que cada opción redirige al flujo correcto (GPS wizard vs formulario actual).

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en la página principal, **When** hace clic en el botón "Crear Viaje", **Then** se muestra un modal con dos opciones claramente diferenciadas: "Crear Viaje con GPS" y "Crear Viaje sin GPS"
2. **Given** el modal de selección está abierto, **When** el usuario hace clic en "Crear Viaje con GPS", **Then** el modal se cierra y se inicia el wizard paso A (carga de GPX)
3. **Given** el modal de selección está abierto, **When** el usuario hace clic en "Crear Viaje sin GPS", **Then** el modal se cierra y se muestra el formulario actual de creación manual de viaje (flujo existente de 4 pasos)
4. **Given** el modal de selección está abierto, **When** el usuario presiona ESC o hace clic fuera del modal, **Then** el modal se cierra sin iniciar ningún flujo

---

### User Story 2 - Upload and Process GPX File (Priority: P2)

Como ciclista con un archivo GPX de mi ruta, quiero poder cargar el archivo y ver que el sistema extrae automáticamente la telemetría básica, para no tener que ingresar manualmente datos como distancia y desnivel.

**Why this priority**: Esta es la primera acción técnica del flujo GPS. Sin la capacidad de cargar y procesar el archivo GPX, el resto del wizard no puede funcionar. Es el corazón de la funcionalidad diferenciadora.

**Independent Test**: Se puede probar subiendo un archivo .gpx válido y verificando que el sistema extrae correctamente: distancia total, desnivel positivo/negativo, altitud máxima/mínima, y coordenadas del track. Los datos extraídos deben mostrarse en pantalla como confirmación.

**Acceptance Scenarios**:

1. **Given** el usuario está en el Paso A del wizard GPS, **When** arrastra un archivo .gpx válido al área de carga, **Then** el sistema muestra un indicador de carga, procesa el archivo, y muestra los datos extraídos: distancia total, desnivel (+/-), altitud máx/mín
2. **Given** el usuario está en el Paso A, **When** intenta cargar un archivo que no es .gpx, **Then** el sistema muestra un mensaje de error: "Formato no válido. Solo se aceptan archivos .gpx"
3. **Given** el usuario está en el Paso A, **When** intenta cargar un archivo .gpx corrupto o sin datos de track válidos, **Then** el sistema muestra un mensaje de error: "No se pudo procesar el archivo. Verifica que contenga datos de ruta válidos"
4. **Given** el archivo GPX se ha cargado exitosamente, **When** el usuario hace clic en "Siguiente", **Then** avanza al Paso B (formulario de detalles) con los datos de telemetría disponibles

---

### User Story 3 - Fill Trip Details with AI-Calculated Difficulty (Priority: P3)

Como ciclista que ha cargado un archivo GPX, quiero completar los detalles de mi viaje (nombre, descripción, privacidad) y ver la dificultad calculada automáticamente, para tener una clasificación objetiva basada en los datos de la ruta sin tener que estimarla yo mismo.

**Why this priority**: Esta historia añade contexto narrativo a los datos técnicos. Es importante para la experiencia de usuario, pero puede implementarse después del procesamiento GPX básico. La dificultad automática es un valor añadido pero no bloquea la funcionalidad core.

**Independent Test**: Se puede probar cargando un archivo GPX (con datos conocidos), completando el formulario, y verificando que: 1) todos los campos se validan correctamente, 2) la dificultad se calcula basándose en distancia y desnivel, y 3) los botones de acción funcionan como se espera.

**Acceptance Scenarios**:

1. **Given** el usuario está en el Paso B (formulario de detalles) con un GPX cargado, **When** completa los campos obligatorios (Nombre de la ruta, Descripción), **Then** puede ver un badge de dificultad que se actualiza dinámicamente (Fácil, Moderada, Difícil, Muy difícil, Extrema) basado en la distancia y desnivel del GPX
2. **Given** el usuario está en el Paso B, **When** selecciona "Privacidad: Privada" en el selector, **Then** el viaje se marcará como privado y solo será visible para el usuario después de publicar
3. **Given** el usuario está en el Paso B, **When** hace clic en "Eliminar", **Then** se muestra una confirmación, y si acepta, se descarta el GPX cargado y vuelve al modal de selección inicial
4. **Given** el usuario está en el Paso B con todos los campos válidos, **When** hace clic en "Siguiente", **Then** avanza al Paso C (mapa y telemetría)
5. **Given** el usuario está en el Paso B, **When** hace clic en "Cancelar", **Then** se muestra una confirmación de descarte, y si acepta, cierra el wizard y vuelve a la página anterior

---

### User Story 4 - Visualize Route on Map with Telemetry Panel (Priority: P4)

Como ciclista que ha cargado un archivo GPX, quiero ver mi ruta visualizada en un mapa interactivo junto con un panel de datos de telemetría, para confirmar que el track es correcto y revisar las métricas clave antes de publicar.

**Why this priority**: La visualización del mapa confirma que el GPX se procesó correctamente y permite al usuario validar visualmente su ruta. Es importante pero no crítico - el viaje podría publicarse sin esta visualización si fuera necesario reducir scope.

**Independent Test**: Se puede probar cargando un GPX, navegando al Paso C, y verificando que: 1) el mapa renderiza el track completo, 2) el panel muestra todos los datos de telemetría correctamente, 3) el mapa es interactivo (zoom, pan).

**Acceptance Scenarios**:

1. **Given** el usuario está en el Paso C (mapa y telemetría) con un GPX cargado, **When** la pantalla carga, **Then** el mapa muestra el track completo visualizado como una línea sobre el mapa base, centrado automáticamente en la ruta
2. **Given** el usuario está en el Paso C, **When** observa el panel de datos, **Then** ve claramente: Distancia total (km), Desnivel positivo (m), Desnivel negativo (m), Altitud máxima (m), Altitud mínima (m)
3. **Given** el usuario está en el Paso C, **When** interactúa con el mapa (zoom in/out, pan), **Then** el mapa responde de forma fluida y mantiene el track visible
4. **Given** el usuario está en el Paso C, **When** hace clic en "Siguiente", **Then** avanza al Paso C.1 (funcionalidad POI) si aún no ha añadido POIs, o al Paso D (publicación) si ya completó los POIs

---

### User Story 5 - Add Points of Interest (POI) to Route (Priority: P5)

Como ciclista que quiere compartir lugares destacados de mi ruta, quiero poder marcar hasta 6 puntos de interés en el mapa, añadir descripciones y fotos a cada uno, para enriquecer mi viaje con información sobre lugares específicos que otros ciclistas querrán visitar.

**Why this priority**: Los POIs son contenido enriquecido opcional. Añaden mucho valor narrativo y social, pero el viaje es válido sin ellos. Pueden implementarse como fase final o incluso como mejora post-MVP.

**Independent Test**: Se puede probar en el Paso C.1 añadiendo POIs mediante clic en el mapa, verificando que cada POI permite descripción de texto y carga de hasta 2 fotos, que se pueden editar/eliminar, y que no se pueden añadir más de 6 POIs.

**Acceptance Scenarios**:

1. **Given** el usuario está en el Paso C con el mapa visible, **When** hace clic en el botón "Añadir POI", **Then** el cursor cambia a modo de marcado y puede hacer clic en cualquier punto del mapa para crear un nuevo POI (hasta un máximo de 6)
2. **Given** el usuario ha marcado un POI en el mapa, **When** hace clic en el marcador, **Then** se abre un panel donde puede: añadir una descripción de texto (max 500 caracteres), cargar hasta 2 fotos por POI
3. **Given** el usuario ha añadido 6 POIs, **When** intenta añadir un POI adicional, **Then** el botón "Añadir POI" está deshabilitado y se muestra un mensaje: "Máximo 6 POIs alcanzado"
4. **Given** el usuario está viendo un POI existente, **When** hace clic en "Eliminar POI", **Then** el POI se elimina del mapa y del listado, y el contador de POIs se actualiza
5. **Given** el usuario ha completado sus POIs (o decidido no añadir ninguno), **When** hace clic en "Siguiente", **Then** avanza al Paso D (publicación)

---

### User Story 6 - Publish GPS Trip (Priority: P2)

Como ciclista que ha completado todos los pasos del wizard GPS, quiero poder publicar mi viaje con un solo clic, consolidando todos los datos (GPX, detalles, POIs) y ser redirigido a la página de detalle de mi viaje, para compartirlo con la comunidad o guardarlo como privado.

**Why this priority**: Este es el punto final del flujo GPS. Sin la publicación, todos los pasos anteriores no tienen sentido. Es crítico para cerrar el ciclo, aunque técnicamente podría implementarse guardando como borrador primero.

**Independent Test**: Se puede probar completando todos los pasos del wizard, haciendo clic en "Publicar", y verificando que: 1) el viaje se crea en la base de datos con todos los datos asociados, 2) el usuario es redirigido a la página de detalle del viaje, 3) el viaje muestra correctamente el mapa, telemetría, POIs y fotos.

**Acceptance Scenarios**:

1. **Given** el usuario está en el Paso D (publicación) con todos los datos completos, **When** hace clic en el botón "Publicar", **Then** el sistema consolida todos los datos (GPX, nombre, descripción, privacidad, POIs con fotos), crea el viaje, y muestra un mensaje de confirmación: "Viaje publicado correctamente"
2. **Given** el viaje se ha publicado exitosamente, **When** la confirmación aparece, **Then** el usuario es redirigido automáticamente a la página de detalle del viaje recién creado
3. **Given** el usuario está en el Paso D, **When** hace clic en "Cancelar", **Then** se muestra una confirmación: "¿Descartar viaje? Todos los datos se perderán", y si acepta, cierra el wizard y vuelve a la página anterior
4. **Given** ocurre un error durante la publicación (red, servidor, validación), **When** el error se detecta, **Then** se muestra un mensaje de error específico en español y el usuario permanece en el Paso D con sus datos intactos para reintentar

---

### Edge Cases

- **¿Qué pasa si el usuario cierra el navegador a mitad del wizard?** Los datos del wizard se pierden (no se persiste estado intermedio). El usuario debe reiniciar desde el modal de selección. No se implementa guardado automático en el MVP para simplificar la implementación inicial.
- **¿Qué pasa si el archivo GPX no tiene datos de altitud?** El sistema no puede calcular desnivel ni altitud máx/mín. Se muestra un mensaje: "El archivo GPX no contiene datos de altitud. La dificultad se calculará solo basándose en distancia" y el campo de desnivel aparece como "No disponible"
- **¿Qué pasa si el archivo GPX es muy grande (ej. >10MB o >100k puntos)?** El sistema muestra un indicador de carga más largo durante el procesamiento. Si el procesamiento excede 60 segundos, se muestra un error de timeout y se permite reintentar
- **¿Qué pasa si el usuario intenta subir fotos de POI muy grandes?** Las fotos se validan antes de cargar: tamaño máximo por foto de 5MB (consistente con límite actual de fotos de viaje). Si excede, se muestra: "La foto es demasiado grande. Tamaño máximo: 5MB"
- **¿Qué pasa si el usuario añade un POI pero no completa la descripción ni sube fotos?** El POI se guarda con la descripción vacía y sin fotos. Ambos campos son opcionales, solo la ubicación del marcador es obligatoria
- **¿Cómo se maneja la privacidad si el usuario marca el viaje como "Privado"?** El viaje se crea pero solo es visible para el usuario propietario. No aparece en feeds públicos ni búsquedas de otros usuarios

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar un modal de selección cuando el usuario hace clic en "Crear Viaje", con dos opciones claras: "Crear Viaje con GPS" y "Crear Viaje sin GPS"
- **FR-002**: El sistema DEBE permitir al usuario cargar archivos con extensión .gpx mediante drag-and-drop o selección de archivo
- **FR-003**: El sistema DEBE validar que el archivo cargado sea un GPX válido con datos de track (coordenadas GPS)
- **FR-004**: El sistema DEBE extraer automáticamente del archivo GPX: distancia total (km), desnivel positivo (m), desnivel negativo (m), altitud máxima (m), altitud mínima (m), y coordenadas del track completo
- **FR-005**: El sistema DEBE calcular automáticamente la dificultad del viaje basándose en distancia y desnivel, clasificándola como: Fácil, Moderada, Difícil, Muy difícil, o Extrema
- **FR-006**: El sistema DEBE proporcionar un formulario con los siguientes campos: Nombre de la ruta (texto obligatorio, max 200 caracteres), Descripción (textarea obligatorio, min 50 caracteres), Privacidad (selector: Pública/Privada, por defecto Pública)
- **FR-007**: El sistema DEBE renderizar un mapa interactivo que visualice el track completo del GPX como una línea sobre el mapa base, centrado automáticamente en la ruta
- **FR-008**: El sistema DEBE mostrar un panel de telemetría con todos los datos extraídos del GPX (distancia, desniveles, altitudes) en formato legible para el usuario
- **FR-009**: El sistema DEBE permitir al usuario añadir hasta 6 POIs (Puntos de Interés) haciendo clic en el mapa
- **FR-010**: Cada POI DEBE permitir: añadir una descripción de texto (opcional), cargar hasta 2 fotos (opcional, max 5MB por foto)
- **FR-011**: El sistema DEBE validar que no se puedan añadir más de 6 POIs, deshabilitando el botón "Añadir POI" cuando se alcanza el límite
- **FR-012**: El sistema DEBE consolidar todos los datos (GPX, detalles del formulario, POIs con fotos) al hacer clic en "Publicar" y crear el viaje en la base de datos
- **FR-013**: El sistema DEBE redirigir al usuario a la página de detalle del viaje después de una publicación exitosa
- **FR-014**: El sistema DEBE permitir al usuario cancelar o eliminar el proceso en cualquier paso, mostrando confirmación antes de descartar datos
- **FR-015**: El sistema DEBE mostrar mensajes de error en español para todas las validaciones (formato inválido, archivo corrupto, fotos muy grandes, etc.)
- **FR-016**: El sistema DEBE mantener la coherencia visual con la estética de ContraVento: fondo crema (#F9F7F2), acentos terracota (#D35400) y verde bosque (#1B2621), tipografía serif para títulos y sans-serif para datos técnicos

### Key Entities

- **GPX File**: Archivo XML con datos de ruta GPS, contiene: coordenadas de track (latitud, longitud, altitud), timestamp de cada punto, metadatos opcionales (nombre, descripción)
- **Trip (Viaje)**: Entidad central que representa un viaje de ciclismo, contiene: nombre, descripción, fecha de creación, privacidad (pública/privada), dificultad calculada, relación con usuario propietario, relación con archivo GPX procesado
- **Route Telemetry (Telemetría de Ruta)**: Datos extraídos del GPX, contiene: distancia total en kilómetros, desnivel positivo en metros, desnivel negativo en metros, altitud máxima en metros, altitud mínima en metros, track simplificado para visualización (lista de coordenadas)
- **Point of Interest (POI)**: Punto destacado en la ruta, contiene: coordenadas (latitud, longitud), descripción de texto (opcional), relación con hasta 2 fotos, relación con el viaje padre, orden/índice (1-6)
- **POI Photo**: Foto asociada a un POI, contiene: archivo de imagen (max 5MB), URL de almacenamiento, metadata (tamaño, formato), relación con POI padre

## Success Criteria

### Measurable Outcomes

- **SC-001**: Los usuarios pueden completar el flujo completo de creación de viaje con GPS (desde selección hasta publicación) en menos de 5 minutos para rutas típicas
- **SC-002**: El sistema procesa archivos GPX de hasta 10MB o 100,000 puntos de track en menos de 60 segundos (⚠️ **Actualizado**: Objetivo original <30s no alcanzable con rutas reales. Actualmente ~30-40s para archivos 10MB con curvas - ver Known Limitations para detalles y roadmap de optimización)
- **SC-003**: El cálculo automático de dificultad coincide con la evaluación manual de usuarios expertos en al menos el 80% de los casos (validar con muestra de 50 rutas conocidas)
- **SC-004**: El mapa interactivo renderiza tracks de hasta 100km con más de 1000 puntos de forma fluida (sin lag perceptible al hacer zoom/pan)
- **SC-005**: Los usuarios completan exitosamente la carga de GPX en el primer intento en al menos el 90% de los casos (sin errores de formato o validación)
- **SC-006**: Al menos el 60% de los usuarios que inician el wizard GPS añaden al menos 1 POI a su viaje (indicador de engagement con la funcionalidad)
- **SC-007**: La tasa de abandono del wizard (usuarios que cancelan o cierran sin publicar) es menor al 25%
- **SC-008**: Los usuarios que completan el wizard reportan satisfacción alta (≥4/5) con la claridad del flujo paso a paso
- **SC-009**: El tiempo de carga de la página de detalle del viaje después de publicar es menor a 3 segundos (incluyendo renderizado del mapa con el track)

## Clarifications

1. **Cálculo de dificultad basado en telemetría**: La dificultad del viaje se calcula **exclusivamente** a partir de los datos de telemetría extraídos del archivo GPX. No es un campo editable por el usuario ni una estimación manual. El sistema utiliza dos métricas principales de telemetría:
   - **Distancia total (km)**: Extraída sumando las distancias entre puntos consecutivos del track GPS
   - **Desnivel positivo acumulado (m)**: Calculado sumando todas las ganancias de altitud a lo largo del track

   El algoritmo combina estas dos métricas para determinar la clasificación de dificultad automáticamente. El usuario solo puede visualizar esta clasificación como un badge informativo, no puede modificarla.

2. **Límite de descripción de POI**: Cada POI puede tener una descripción de texto opcional con un máximo de 500 caracteres, suficiente para descripciones concisas pero informativas.

3. **No auto-guardado en wizard**: En el MVP, el estado del wizard no se guarda automáticamente. Si el usuario cierra el navegador o abandona el flujo, los datos se pierden y debe reiniciar desde el modal de selección.

4. **Timeout de procesamiento GPX**: El procesamiento de archivos GPX tiene un límite de tiempo de 60 segundos para tolerar archivos grandes y conexiones lentas sin bloquear indefinidamente la interfaz.

## Assumptions

1. **Algoritmo de dificultad**: La dificultad se calcula usando la siguiente fórmula basada en telemetría (distancia + desnivel):
   - **Fácil**: <30km y <500m desnivel positivo
   - **Moderada**: 30-60km o 500-1000m desnivel
   - **Difícil**: 60-100km o 1000-1500m desnivel
   - **Muy difícil**: 100-150km o 1500-2500m desnivel
   - **Extrema**: >150km o >2500m desnivel

   Estos umbrales pueden ajustarse basándose en feedback de usuarios expertos, pero siempre calculados automáticamente a partir de telemetría, nunca ingresados manualmente

2. **Integración con flujo existente**: Se asume que el flujo actual de creación de viaje sin GPS (wizard de 4 pasos existente) se mantiene intacto y el nuevo flujo GPS es una alternativa paralela, no un reemplazo

3. **Backend GPX processing**: Se asume que existe o se implementará un servicio backend capaz de parsear archivos GPX, extraer telemetría, y simplificar tracks para renderizado (puede reutilizarse lógica existente de Feature 003-gps-routes)

4. **Límite de POIs**: Se establece un límite de 6 POIs por viaje para mantener la experiencia de usuario enfocada y evitar sobrecarga de información (límite negociable basándose en feedback)

5. **Persistencia de datos**: No se implementa guardado automático durante el wizard. El usuario debe completar todo el flujo hasta "Publicar" o los datos se pierden. Esto simplifica la implementación MVP pero puede mejorarse en el futuro

6. **Mapa base**: Se asume uso de Leaflet/OpenStreetMap (consistente con tecnología existente en Feature 009-gps-coordinates y Feature 010-reverse-geocoding)

7. **Formato de fotos de POI**: Se aceptan los mismos formatos que las fotos de viaje actuales (JPG, PNG, WebP), con validación de tamaño máximo 5MB por foto

8. **Experiencia móvil**: El wizard debe ser responsive y funcionar en móviles, pero la experiencia óptima es en desktop debido a la complejidad del mapa interactivo y drag-and-drop de archivos

## Known Limitations

### Performance (SC-002)

**Limitación**: El procesamiento de archivos GPX ≥10MB tarda actualmente **~30-40 segundos** para rutas realistas con curvas, muy por encima del objetivo aspiracional de <2 segundos.

**Impacto**:
- ⚠️ **Crítico para UX**: Los usuarios deben esperar 30-40s, lo cual es perceptible y puede causar frustración
- ✅ **Mitigable con UI**: Un indicador de progreso claro y mensaje "Procesando archivo grande..." hace la espera tolerable
- ⚠️ **Riesgo de timeout**: Archivos >10MB o conexiones lentas pueden exceder el timeout de 60s

**Causa raíz** (identificada mediante [diagnose_gpx_performance.py](../../backend/scripts/analysis/diagnose_gpx_performance.py)):

**Archivo con línea recta** (no representativo):
- XML Parsing: ~2.2s (45%)
- RDP Algorithm: ~2.3s (46%)
- Total: ~5s

**Archivo realista con curvas** (representativo del uso real):
- XML Parsing: ~2.2s (6%)
- **RDP Algorithm: ~34.6s (94%)** ← Bottleneck crítico
- Total: **~37s**

**Por qué RDP es tan lento con rutas reales**:
- Archivos de prueba con línea recta simplifican 85,000 → 2 puntos (99.998% reducción)
- Rutas reales con curvas simplifican 85,000 → 5,056 puntos (94% reducción)
- El algoritmo RDP es O(n²) en el peor caso, y rutas con curvas son el peor caso
- Preservar 2,500x más puntos requiere 15x más tiempo de procesamiento

**Soluciones propuestas**:

**Inmediato** (MVP shipping - REQUERIDO):
1. ✅ **Indicador de progreso robusto**: Mostrar spinner con mensaje claro "Procesando archivo GPX grande... esto puede tardar hasta 60 segundos"
2. ✅ **Timeout aumentado**: Asegurar que el timeout es ≥60s (actualmente configurado correctamente)
3. ⚠️ **Limitar tamaño de archivo**: Considerar rechazar archivos >10MB con mensaje: "Archivo muy grande. El límite actual es 10MB. Puedes simplificar el track con herramientas como gpsbabel"
4. ✅ **Documentar en UI**: Añadir tooltip en la zona de carga: "Archivos grandes (>5MB) pueden tardar hasta 1 minuto en procesarse"

**Corto plazo** (Post-MVP Priority 1 - MUY RECOMENDADO):
1. **Aumentar epsilon de RDP**: Cambiar de 0.0001 a 0.0002 o 0.0005
   - Impacto: Reduce puntos preservados (ej: 5,056 → ~2,000)
   - Beneficio: Reduce tiempo RDP significativamente (potencial 34s → 10-15s)
   - Trade-off: Pérdida mínima de precisión visual (imperceptible en el mapa)

2. **Pre-filtrado de puntos**: Eliminar puntos <5m de distancia ANTES de RDP
   - Impacto: Reduce input de 85,000 a ~40,000 puntos
   - Beneficio: Reduce tiempo RDP a la mitad (~34s → 15s)
   - Trade-off: Ninguno (puntos tan cercanos no aportan valor visual)

**Medio plazo** (Post-MVP Priority 2):
1. **Implementar RDP multithread**: Dividir track en chunks, procesar en paralelo
   - Potencial: Reducir 34s → 10-15s (con 4 cores)
2. **Cambiar parser XML**: Evaluar `lxml` (reducción mínima: 2.2s → 1s)
3. **Cache de telemetría**: Almacenar hash del archivo para evitar reprocesar

**Largo plazo** (Architectural):
1. **Background processing con WebSocket**: Retornar respuesta inmediata, procesar async, notificar vía WebSocket cuando complete
2. **Progressive rendering**: Mostrar preview del mapa con puntos parciales mientras se completa el procesamiento

**Estado**: ⚠️ **CRÍTICO** - Limitación severa que afecta significativamente la UX. MVP es viable con indicador de progreso claro, pero optimización post-MVP es **altamente recomendada**

**Referencias**:
- [PERFORMANCE_DIAGNOSTICS.md](../../backend/scripts/analysis/PERFORMANCE_DIAGNOSTICS.md) - Análisis detallado de cada paso
- [backend/scripts/analysis/README.md](../../backend/scripts/analysis/README.md) - Scripts de testing y diagnóstico
- [test_gpx_analyze.py](../../backend/scripts/analysis/test_gpx_analyze.py) - Script de validación SC-002
