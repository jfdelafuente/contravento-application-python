# Guía de Pruebas - Feature 008: Travel Diary Frontend

## Fase de Implementación Actual

✅ **Fase 2 Completa (Foundational)**: Infraestructura base (16 tareas: T005-T020)
  - Tipos TypeScript, validadores, utilidades
  - Servicios API (tripService, tripPhotoService)
  - Hooks personalizados

✅ **Fase 3 Completa (User Story 1)**: Lista de viajes con filtros (10 tareas: T021-T030)
  - TripsListPage con grid responsivo
  - TripCard component
  - TripFilters component con búsqueda, tags y estados
  - Paginación

✅ **Fase 4 Completa (User Story 2)**: Detalles de viaje (9 tareas: T031-T039)
  - TripDetailPage con hero image
  - TripGallery con lightbox interactivo
  - TripMap con OpenStreetMap
  - Botones de acción (publicar/eliminar para dueños)

⏸️ **Fase 5 Pendiente (User Story 3)**: Crear viajes - multi-step form (18 tareas: T040-T057)
  - TripFormWizard (4 pasos)
  - PhotoUploader con drag & drop
  - Validación por pasos

**Total**: 35 de 53 tareas completadas (66%)

---

## Pre-requisitos para Pruebas

### 1. Backend en Funcionamiento
```bash
# Opción A: LOCAL-DEV (SQLite - Recomendado)
cd backend
./run-local-dev.sh  # Linux/Mac
# O
.\run-local-dev.ps1  # Windows PowerShell

# El backend debe estar en: http://localhost:8000
```

### 2. Frontend en Funcionamiento
```bash
cd frontend
npm run dev

# El frontend debe estar en: http://localhost:3001
```

### 3. Usuario Autenticado
**Credenciales de prueba** (auto-creadas durante setup):
- Username: `testuser`
- Password: `TestPass123!`

**O usa el usuario admin**:
- Username: `admin`
- Password: `AdminPass123!`

---

## Checklist de Pruebas

### ✅ FASE 2: Infraestructura Base

#### T026-T028: Servicios API
- [ ] Abrir DevTools → Network
- [ ] Verificar que las llamadas a `/trips` usan el cliente Axios configurado
- [ ] Confirmar que las cookies de autenticación se envían automáticamente

#### T029-T030: Tipos TypeScript
- [ ] El código no muestra errores de TypeScript en el editor
- [ ] Las interfaces `Trip`, `TripPhoto`, `TripLocation`, `Tag` están definidas

#### T031-T033: Utilidades
- [ ] Verificar que las fechas se muestran en formato español (ej: "1-5 jun 2024")
- [ ] Verificar que las distancias se muestran correctamente (ej: "320.5 km")
- [ ] Verificar que las dificultades se traducen (Fácil, Moderado, Difícil, Extremo)

---

### ✅ FASE 3: Lista de Viajes

#### T034: Página de Lista de Viajes

**Paso 1**: Navegar a la lista
1. Ir a: `http://localhost:3001/trips`
2. **Esperar**: Debería mostrar "Mis Viajes" como título
3. **Verificar**: Debe aparecer el subtítulo "Explora, organiza y comparte tus aventuras en bicicleta"

**Paso 2**: Ver viajes en grid
- [ ] Los viajes se muestran en una cuadrícula responsiva
- [ ] Cada tarjeta muestra: imagen, título, fechas, distancia, etiquetas
- [ ] El estado de carga muestra skeletons animados

**Paso 3**: Paginación
- [ ] Si hay más de 12 viajes, aparecen controles de paginación
- [ ] Botones "Anterior" y "Siguiente" funcionan
- [ ] Los números de página son clickeables
- [ ] Se muestra "Página X de Y"

#### T035: TripCard Component

**Verificar cada tarjeta de viaje**:
- [ ] **Thumbnail**: Muestra la primera foto del viaje (o placeholder si no hay foto)
- [ ] **Título**: Se muestra correctamente
- [ ] **Rango de fechas**: Formato español (ej: "1-5 jun 2024")
- [ ] **Distancia**: Con unidad "km" (ej: "320.5 km")
- [ ] **Etiquetas**: Máximo 3 etiquetas visibles, resto muestra "+N más"
- [ ] **Badge de dificultad**: Color correcto según nivel
- [ ] **Badge de estado**: Solo visible para dueño, solo en borradores
- [ ] **Hover**: La tarjeta tiene efecto de elevación al pasar el mouse
- [ ] **Click**: Navega a `/trips/{trip_id}`

#### T036-T037: TripFilters Component

**Paso 1**: Búsqueda por texto
1. Escribir en el campo de búsqueda: "pirineos"
2. **Esperar**: La lista se filtra en tiempo real (debounce de 300ms)
3. **Verificar**: Solo aparecen viajes que contienen "pirineos" en título o descripción
4. **Limpiar**: Borrar texto → todos los viajes vuelven a aparecer

**Paso 2**: Filtro por etiqueta
1. Click en el select "Todas las etiquetas"
2. **Verificar**: Se muestran todas las etiquetas disponibles
3. Seleccionar una etiqueta (ej: "bikepacking")
4. **Esperar**: Solo aparecen viajes con esa etiqueta
5. **Verificar**: El contador de resultados se actualiza

**Paso 3**: Filtro por estado (solo para dueño)
1. Click en el select "Todos los estados"
2. **Verificar**: Opciones disponibles: "Todos", "Borrador", "Publicado"
3. Seleccionar "Borrador"
4. **Esperar**: Solo aparecen viajes en estado borrador
5. **Verificar**: Cada tarjeta muestra el badge "BORRADOR"

**Paso 4**: Filtros combinados
1. Activar búsqueda + etiqueta + estado simultáneamente
2. **Verificar**: Los filtros se aplican en conjunto (AND lógico)
3. **Verificar**: El contador muestra el total correcto

**Paso 5**: Estado vacío
1. Aplicar filtros que no coincidan con ningún viaje
2. **Verificar**: Aparece ilustración de mapa vacío
3. **Verificar**: Mensaje: "No se encontraron viajes"
4. **Verificar**: Sugerencia: "Intenta ajustar los filtros..."

#### T038-T039: Hooks Personalizados

**useTripList Hook** (verificar en DevTools):
- [ ] Se ejecuta petición GET a `/users/{username}/trips?limit=12&offset=0`
- [ ] Los parámetros de query incluyen: `search`, `tag`, `status` cuando están activos
- [ ] El estado de loading se maneja correctamente
- [ ] La función `refetch()` recarga los datos

**useTripFilters Hook**:
- [ ] Los filtros persisten en la URL (query params)
- [ ] Al recargar la página con filtros activos, se restauran
- [ ] La paginación se resetea a página 1 cuando cambian los filtros

---

### ✅ FASE 4: Detalles de Viaje (User Story 2)

#### T031-T039: TripDetailPage, TripGallery, TripMap

**Paso 1**: Navegar a un viaje
1. Desde la lista, click en cualquier tarjeta de viaje
2. **URL esperada**: `http://localhost:3001/trips/{trip_id}`

**Paso 2**: Sección Hero
- [ ] Se muestra la primera foto del viaje como hero image (altura: 500px)
- [ ] Si no hay foto, se muestra placeholder con ícono
- [ ] Si es borrador Y el usuario es dueño: se muestra badge "BORRADOR" en la esquina superior izquierda

**Paso 3**: Cabecera con metadatos
- [ ] **Título del viaje**: Grande y prominente
- [ ] **Fecha**: Rango con formato español (ej: "1-5 jun 2024")
- [ ] **Distancia**: Con ícono y unidad "km"
- [ ] **Dificultad**: Badge con color (verde/amarillo/naranja/rojo)

**Paso 4**: Botones de acción (solo para dueño)
- [ ] Si NO eres el dueño: los botones no aparecen
- [ ] Si eres el dueño Y es borrador: aparece botón "Publicar" (verde)
- [ ] Si eres el dueño: aparece botón "Eliminar" (rojo)
- [ ] Botón "Editar" está comentado (disponible en Fase 5)

**Paso 5**: Sección Descripción
- [ ] Título de sección: "Descripción"
- [ ] El contenido HTML se renderiza correctamente (dangerouslySetInnerHTML)
- [ ] Los párrafos, listas, y enlaces se muestran formateados

**Paso 6**: Sección Etiquetas
- [ ] Solo aparece si el viaje tiene etiquetas
- [ ] Cada etiqueta es un link clickeable
- [ ] Al hacer click: navega a `/trips?tag={tag_name}`
- [ ] Hover: cambia color a azul primario

**Paso 7**: Botón "Volver a Mis Viajes"
- [ ] Aparece al final de la página
- [ ] Tiene ícono de flecha izquierda
- [ ] Navega de vuelta a `/trips`

#### TripGallery Component (T031-T032, T037)

**Solo se muestra si el viaje tiene fotos**

**Paso 1**: Grid de thumbnails
- [ ] Las fotos se muestran en grid responsivo (3 columnas en desktop)
- [ ] Cada thumbnail es cuadrado (object-fit: cover)
- [ ] Muestra máximo 12 fotos inicialmente
- [ ] Si hay más de 12: botón "Ver todas las fotos (N)"

**Paso 2**: Lightbox (yet-another-react-lightbox)
1. Click en cualquier thumbnail
2. **Verificar**: Se abre lightbox en pantalla completa
3. **Controles disponibles**:
   - [ ] Flechas izquierda/derecha para navegar
   - [ ] Thumbnails en la parte inferior
   - [ ] Botón de cerrar (X)
   - [ ] Zoom con rueda del mouse o pinch
   - [ ] Pantalla completa (botón en esquina)
4. **Navegación**:
   - [ ] Click en thumbnails cambia la foto principal
   - [ ] Teclas de flecha funcionan
   - [ ] ESC cierra el lightbox

**Paso 3**: Captions (si existen)
- [ ] Si la foto tiene caption, se muestra en el lightbox
- [ ] El caption aparece superpuesto en la parte inferior

#### TripMap Component (T033-T034, T038)

**Solo se muestra si el viaje tiene ubicaciones con coordenadas válidas**

**Paso 1**: Verificar renderizado condicional
- [ ] Si NO hay ubicaciones: no aparece la sección "Ruta y Ubicaciones"
- [ ] Si hay ubicaciones: se muestra el mapa (lazy-loaded)

**Paso 2**: Mapa interactivo (react-leaflet)
1. **Verificar**: El mapa se carga con tiles de OpenStreetMap
2. **Controles**:
   - [ ] Zoom in/out funcionan
   - [ ] Scroll con rueda del mouse para zoom
   - [ ] Arrastrar para mover el mapa
3. **Markers**:
   - [ ] Se muestra un marker por cada ubicación
   - [ ] Los markers están numerados en orden de secuencia
4. **Popups**:
   - [ ] Click en marker abre popup
   - [ ] Popup muestra: número + nombre de ubicación + título del viaje

**Paso 3**: Polyline (ruta)
- [ ] Si hay 2+ ubicaciones: se dibuja una línea punteada azul conectándolas
- [ ] La línea sigue el orden de secuencia

**Paso 4**: Lista de ubicaciones
- [ ] Debajo del mapa aparece la lista "Ubicaciones (N)"
- [ ] Cada ubicación tiene número circular azul + nombre
- [ ] El orden coincide con los markers del mapa

**Paso 5**: Zoom automático
- [ ] Si hay 1 ubicación: zoom nivel 12 (ciudad)
- [ ] Si hay múltiples: zoom calculado para mostrar todas

---

### 🔧 Funcionalidades Interactivas

#### Publicar Viaje (solo dueño de borradores)

**Pre-requisito**: Tener un viaje en estado borrador

**Paso 1**: Validación
1. Ir a un viaje borrador con descripción < 50 caracteres
2. Click en botón "Publicar"
3. **Esperar**: Toast error: "La descripción debe tener al menos 50 caracteres para publicar"
4. **Verificar**: El viaje NO se publica

**Paso 2**: Publicación exitosa
1. Ir a un viaje borrador con descripción ≥ 50 caracteres
2. Click en botón "Publicar"
3. **Esperar**:
   - Botón cambia a "Publicando..."
   - Toast success: "Viaje publicado correctamente"
   - El badge "BORRADOR" desaparece
   - El botón "Publicar" desaparece
4. **Verificar en la lista**: El viaje ya no tiene badge de borrador

#### Eliminar Viaje (solo dueño)

**Paso 1**: Confirmación
1. Click en botón "Eliminar" (rojo)
2. **Esperar**: Diálogo de confirmación del navegador
3. **Mensaje**: "¿Estás seguro de que quieres eliminar este viaje? Esta acción no se puede deshacer."

**Paso 2**: Cancelar
1. Click en "Cancelar"
2. **Verificar**: El viaje NO se elimina, permanece en la página

**Paso 3**: Confirmar eliminación
1. Click en "Eliminar" → "Aceptar"
2. **Esperar**:
   - Botón cambia a "Eliminando..."
   - Toast success: "Viaje eliminado correctamente"
   - Redirección a `/trips`
3. **Verificar en la lista**: El viaje eliminado ya no aparece

---

### 🐛 Manejo de Errores

#### Error 401: Sesión Expirada (NUEVO - recién corregido)

**Paso 1**: Simular sesión expirada
1. En DevTools → Application → Cookies
2. Eliminar la cookie de autenticación
3. Intentar navegar a `/trips/{trip_id}`

**Esperado**:
- [ ] Toast error: "Tu sesión ha expirado. Por favor inicia sesión nuevamente."
- [ ] Redirección automática a `/login`

#### Error 404: Viaje No Encontrado

**Paso 1**: URL inválida
1. Navegar manualmente a: `http://localhost:3001/trips/00000000-0000-0000-0000-000000000000`

**Esperado**:
- [ ] Página de error con ícono de advertencia
- [ ] Título: "Viaje no encontrado"
- [ ] Botón "Volver a Mis Viajes"

#### Error 403: Sin Permiso

**Solo si el backend implementa visibilidad privada**

**Esperado**:
- [ ] Toast error: "No tienes permiso para ver este viaje"
- [ ] Página de error con mensaje apropiado

#### Estados de Carga

**TripDetailPage**:
- [ ] Skeleton loader mientras carga (hero + título + meta + descripción)
- [ ] Animación de pulso

**TripsListPage**:
- [ ] 12 tarjetas skeleton en grid
- [ ] Animación de carga con gradiente

**TripGallery**:
- [ ] Mensaje "Cargando mapa..." mientras lazy-load del TripMap

---

### 📱 Pruebas Responsivas

#### Desktop (> 1024px)
- [ ] Grid de viajes: 3 columnas
- [ ] Hero image: 500px altura
- [ ] Galería: 3 columnas
- [ ] Mapa: 400px altura

#### Tablet (768px - 1023px)
- [ ] Grid de viajes: 2 columnas
- [ ] Hero image: 400px altura
- [ ] Galería: 2 columnas
- [ ] Mapa: 350px altura

#### Mobile (< 768px)
- [ ] Grid de viajes: 1 columna
- [ ] Hero image: 300px altura
- [ ] Galería: 1 columna
- [ ] Mapa: 300px altura
- [ ] Botones de acción: stack vertical (100% ancho)
- [ ] Metadatos: stack vertical

**Para probar**: Usar DevTools → Toggle device toolbar → Probar iPhone, iPad, etc.

---

### 🌐 Pruebas de Integración

#### Flujo Completo: Buscar → Filtrar → Ver Detalle → Volver

1. Ir a `/trips`
2. Escribir búsqueda: "montaña"
3. Seleccionar etiqueta: "bikepacking"
4. **Verificar**: Lista filtrada correctamente
5. Click en un viaje de la lista
6. **Verificar**: Se abre la página de detalle
7. Scroll para ver galería y mapa
8. Click en "Volver a Mis Viajes"
9. **Verificar**: Vuelve a `/trips` CON los filtros preservados en la URL

#### Flujo: Ver Galería → Lightbox → Cerrar → Mapa

1. En página de detalle, scroll hasta galería
2. Click en foto #3
3. **Verificar**: Lightbox abre con foto #3
4. Navegar a foto #5 con flechas
5. Zoom in/out
6. Cerrar lightbox (ESC o botón X)
7. **Verificar**: Vuelve a la página de detalle
8. Scroll hasta mapa
9. Click en marker #2
10. **Verificar**: Popup muestra info correcta

---

## 🚧 Funcionalidades Pendientes (Fase 5)

Las siguientes funcionalidades estarán disponibles después de implementar la Fase 5:

- ❌ Botón "Crear Viaje" (comentado en TripsListPage)
- ❌ Botón "Editar" (comentado en TripDetailPage)
- ❌ Formulario multi-step para crear viajes
- ❌ Subir fotos con drag & drop
- ❌ Agregar ubicaciones al mapa
- ❌ Auto-complete de etiquetas

---

## 📊 Checklist de Calidad

### Accesibilidad
- [ ] Todos los botones tienen aria-labels apropiados
- [ ] Las imágenes tienen alt text
- [ ] La navegación con teclado funciona (Tab, Enter, Esc)
- [ ] Los estados de focus son visibles

### Performance
- [ ] La lista de viajes carga en < 2 segundos
- [ ] La página de detalle carga en < 1 segundo
- [ ] El mapa se carga lazy (solo cuando se scrollea hasta él)
- [ ] Las imágenes usan object-fit para evitar layout shift

### UX
- [ ] Todos los textos están en español
- [ ] Los mensajes de error son claros y útiles
- [ ] Los toasts desaparecen automáticamente (3-5 segundos)
- [ ] Los botones muestran estados de loading ("Publicando...", "Eliminando...")
- [ ] Los estados vacíos tienen ilustraciones y mensajes útiles

---

## 🐞 Bugs Conocidos Corregidos

### ✅ Bug #1: TripCard - tag_names undefined
**Síntoma**: `Uncaught TypeError: Cannot read properties of undefined (reading 'length')`
**Causa**: Backend devuelve `tag_names: undefined` en vez de `tag_names: []`
**Fix**: Agregado null check en TripCard.tsx:148

### ✅ Bug #2: Error 401 muestra "Viaje no encontrado"
**Síntoma**: Session expirada mostraba mensaje genérico
**Causa**: Error handling no distinguía entre 401 y 404
**Fix**: Agregado manejo específico de 401 con redirect a login (TripDetailPage.tsx:67-75)

---

## 📝 Notas Finales

- **Datos de prueba**: Usar el usuario `testuser` con viajes de ejemplo
- **Backend debe estar corriendo**: En http://localhost:8000
- **Console logs**: Algunos logs de debug aún activos (pueden removerse después)
- **Leaflet tiles**: Requiere conexión a internet para cargar mapas de OpenStreetMap

**¡Listo para probar!** 🚀
