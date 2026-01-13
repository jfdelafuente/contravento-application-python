# Feature 013 - Public Trips Feed: Guía de Pruebas End-to-End

**Versión**: 1.0
**Fecha**: 2026-01-13
**Feature**: Public Trips Feed (Feed Público de Viajes)

---

## 📋 Tabla de Contenidos

1. [Configuración del Entorno de Pruebas](#configuración-del-entorno-de-pruebas)
2. [Datos de Prueba](#datos-de-prueba)
3. [User Story 1: Explorar Feed Público](#user-story-1-explorar-feed-público)
4. [User Story 2: Cabecera con Autenticación](#user-story-2-cabecera-con-autenticación)
5. [User Story 3: Filtrado de Privacidad](#user-story-3-filtrado-de-privacidad)
6. [User Story 4: Navegación a Detalles](#user-story-4-navegación-a-detalles)
7. [Pruebas de Integración Cross-Feature](#pruebas-de-integración-cross-feature)
8. [Pruebas de Rendimiento](#pruebas-de-rendimiento)
9. [Pruebas de Accesibilidad](#pruebas-de-accesibilidad)
10. [Pruebas en Dispositivos Móviles](#pruebas-en-dispositivos-móviles)
11. [Checklist de Validación Final](#checklist-de-validación-final)

---

## Configuración del Entorno de Pruebas

### Requisitos Previos

**Backend**:
```bash
cd backend

# Asegurar base de datos limpia (SQLite local)
rm -f contravento_dev.db

# Ejecutar setup con datos de prueba
./run-local-dev.sh --setup

# Iniciar servidor backend
./run-local-dev.sh

# Verificar en http://localhost:8000/docs
```

**Frontend**:
```bash
cd frontend

# Instalar dependencias si es necesario
npm install

# Iniciar servidor de desarrollo
npm run dev

# Acceder a http://localhost:5173
```

### Usuarios de Prueba Disponibles

Creados automáticamente durante `--setup`:

| Usuario | Email | Password | Role | Perfil |
|---------|-------|----------|------|--------|
| `admin` | admin@contravento.com | AdminPass123! | ADMIN | público |
| `testuser` | test@example.com | TestPass123! | USER | público |
| `maria_garcia` | maria@example.com | SecurePass456! | USER | público |

### Crear Usuario con Perfil Privado (para pruebas)

```bash
cd backend
poetry run python scripts/create_verified_user.py \
  --username privateuser \
  --email private@example.com \
  --password "PrivatePass123!"

# Cambiar perfil a privado (manual via psql/sqlite3)
# UPDATE users SET profile_visibility = 'private' WHERE username = 'privateuser';
```

---

## Datos de Prueba

### Setup de Viajes para Pruebas

**Escenario Base**: Crear viajes con diferentes estados y privacidad

**Usuario Público con Viajes Publicados** (`testuser`):
1. Viaje publicado con foto, ubicación, tags
2. Viaje publicado sin foto (placeholder)
3. Viaje borrador (NO debe aparecer en feed)

**Usuario Privado con Viajes Publicados** (`privateuser`):
1. Viaje publicado (NO debe aparecer en feed - perfil privado)

**Usuario con Múltiples Viajes** (para paginación):
- Crear 25+ viajes publicados con el usuario `testuser`

### Script de Setup de Datos (Ejemplo)

```bash
# Login como testuser
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# Guardar cookie de sesión y crear viajes via API
# (Ver sección de "Creación de Viajes de Prueba" abajo)
```

---

## User Story 1: Explorar Feed Público

### TC-US1-001: Acceso Anónimo al Feed

**Objetivo**: Verificar que usuarios no autenticados pueden ver el feed público

**Precondiciones**:
- Backend corriendo en http://localhost:8000
- Frontend corriendo en http://localhost:5173
- Base de datos con al menos 3 viajes publicados (perfil público)

**Pasos**:
1. Abrir navegador en modo incógnito
2. Navegar a `http://localhost:5173/`
3. Verificar que la página carga sin redirigir a login

**Resultado Esperado**:
- ✅ Página principal muestra feed de viajes
- ✅ Cabecera muestra botón "Iniciar sesión"
- ✅ No hay botones de edición/eliminación
- ✅ Título: "Explora Viajes en Bicicleta"
- ✅ Subtítulo: "Descubre las últimas aventuras compartidas por la comunidad ciclista"

**Capturas Recomendadas**:
- Vista completa de la página principal (anónimo)

---

### TC-US1-002: Visualización de Tarjetas de Viaje

**Objetivo**: Verificar que cada tarjeta muestra la información correcta

**Precondiciones**:
- Feed con viajes publicados
- Al menos un viaje con foto, ubicación, y distancia

**Pasos**:
1. Acceder al feed público
2. Localizar una tarjeta de viaje
3. Inspeccionar cada elemento de la tarjeta

**Resultado Esperado - Cada tarjeta debe mostrar**:
- ✅ Foto del viaje (o placeholder si no hay foto)
- ✅ Título del viaje
- ✅ Avatar y nombre del autor (username)
- ✅ Ubicación (si existe) con icono de mapa
- ✅ Distancia en km (si existe) con icono de bicicleta
- ✅ Fecha de publicación en español (ej: "1 de junio de 2024")
- ✅ Imagen con aspect ratio 3:2 (sin deformación)
- ✅ Atributo `loading="lazy"` en imágenes

**Capturas Recomendadas**:
- Tarjeta con foto
- Tarjeta sin foto (placeholder)
- Tarjeta sin ubicación

---

### TC-US1-003: Ordenación por Fecha de Publicación

**Objetivo**: Verificar que los viajes se muestran ordenados por `published_at DESC` (más recientes primero)

**Precondiciones**:
- Base de datos con al menos 5 viajes con diferentes `published_at`

**Pasos**:
1. Acceder al feed público
2. Anotar los títulos de los primeros 3 viajes
3. Verificar en la base de datos:
   ```sql
   SELECT title, published_at FROM trips
   WHERE status = 'PUBLISHED'
   ORDER BY published_at DESC LIMIT 3;
   ```

**Resultado Esperado**:
- ✅ El primer viaje del feed tiene el `published_at` más reciente
- ✅ Los viajes están en orden descendente por fecha de publicación
- ✅ No hay viajes borradores (DRAFT) en el feed

---

### TC-US1-004: Paginación - Navegación Básica

**Objetivo**: Verificar funcionamiento de controles de paginación

**Precondiciones**:
- Base de datos con 25+ viajes publicados (para 2+ páginas con limit=20)

**Pasos**:
1. Acceder al feed público
2. Verificar contador: "X viajes disponibles"
3. Verificar botones de paginación en la parte inferior
4. Hacer clic en "Siguiente"
5. Verificar que la página hace scroll al inicio
6. Hacer clic en "Anterior"

**Resultado Esperado**:
- ✅ Contador muestra el número total de viajes (ej: "25 viajes disponibles")
- ✅ Página 1 muestra máximo 20 viajes
- ✅ Botón "Anterior" deshabilitado en página 1
- ✅ Botón "Siguiente" habilitado si hay más páginas
- ✅ Al hacer clic en "Siguiente":
  - Navega a página 2
  - Muestra viajes diferentes (sin duplicados)
  - Hace scroll al inicio de la página
  - Botón "Anterior" ahora habilitado
- ✅ Al hacer clic en "Anterior":
  - Vuelve a página 1
  - Muestra los viajes originales
  - Botón "Anterior" deshabilitado de nuevo

**Capturas Recomendadas**:
- Página 1 con contador y paginación
- Página 2 con botón "Anterior" habilitado

---

### TC-US1-005: Estado Vacío (Sin Viajes)

**Objetivo**: Verificar mensaje cuando no hay viajes publicados

**Precondiciones**:
- Base de datos sin viajes publicados (solo borradores o viajes privados)

**Pasos**:
1. Limpiar todos los viajes publicados (o cambiar todos a DRAFT)
2. Acceder al feed público

**Resultado Esperado**:
- ✅ Icono de mapa vacío
- ✅ Mensaje: "Aún no hay viajes publicados"
- ✅ Submensaje: "Sé el primero en compartir tu aventura con la comunidad."
- ✅ No hay tarjetas de viaje
- ✅ No hay controles de paginación

**Capturas Recomendadas**:
- Vista completa del estado vacío

---

### TC-US1-006: Manejo de Errores de API

**Objetivo**: Verificar comportamiento cuando la API falla

**Precondiciones**:
- Backend detenido o endpoint roto

**Pasos**:
1. Detener el servidor backend (`Ctrl+C`)
2. Acceder al feed público en el navegador
3. Esperar que la petición falle

**Resultado Esperado**:
- ✅ Icono de advertencia (triángulo con !)
- ✅ Mensaje: "Error al cargar viajes"
- ✅ Descripción del error (ej: "Network Error")
- ✅ Botón: "Intentar de nuevo"
- ✅ Al hacer clic en "Intentar de nuevo":
  - Recarga la página (`window.location.reload()`)

**Capturas Recomendadas**:
- Vista de error con botón de reintento

---

### TC-US1-007: Loading State (Carga)

**Objetivo**: Verificar estado de carga mientras se obtienen viajes

**Precondiciones**:
- Backend con latencia simulada (opcional: agregar delay en el endpoint)

**Pasos**:
1. Acceder al feed público
2. Observar el estado inicial (antes de recibir datos)

**Resultado Esperado**:
- ✅ Spinner animado con aria-label="Cargando viajes..."
- ✅ Mensaje: "Cargando viajes..."
- ✅ Cabecera y título visibles durante la carga
- ✅ Al completar, spinner desaparece y muestra las tarjetas

**Nota**: Si la API es muy rápida, simular latencia con DevTools (Network throttling: Slow 3G)

---

## User Story 2: Cabecera con Autenticación

### TC-US2-001: Cabecera para Usuario Anónimo

**Objetivo**: Verificar elementos de la cabecera para usuarios no autenticados

**Precondiciones**:
- Usuario no autenticado (modo incógnito)

**Pasos**:
1. Acceder al feed público
2. Inspeccionar la cabecera

**Resultado Esperado**:
- ✅ Logo "ContraVento" visible a la izquierda
- ✅ Botón "Iniciar sesión" a la derecha
- ✅ NO hay avatar de usuario
- ✅ NO hay botón "Cerrar sesión"
- ✅ Fondo con gradiente (verde oliva → verde bosque)
- ✅ Texto en color crema (#F5F1E8)
- ✅ Sombra pronunciada debajo de la cabecera

**Capturas Recomendadas**:
- Cabecera completa (anónimo)

---

### TC-US2-002: Click en Logo (Usuario Anónimo)

**Objetivo**: Verificar que el logo navega a la página principal

**Precondiciones**:
- Usuario en cualquier página del sitio

**Pasos**:
1. Navegar a una página diferente (ej: `/login`)
2. Hacer clic en el logo "ContraVento" de la cabecera

**Resultado Esperado**:
- ✅ Navega a `/` (página principal)
- ✅ Muestra el feed público

---

### TC-US2-003: Navegación a Login

**Objetivo**: Verificar que el botón "Iniciar sesión" redirige correctamente

**Precondiciones**:
- Usuario anónimo en el feed

**Pasos**:
1. Hacer clic en el botón "Iniciar sesión" de la cabecera

**Resultado Esperado**:
- ✅ Navega a `/login`
- ✅ Muestra el formulario de inicio de sesión

---

### TC-US2-004: Cabecera para Usuario Autenticado

**Objetivo**: Verificar elementos de la cabecera para usuarios autenticados

**Precondiciones**:
- Usuario autenticado (testuser / TestPass123!)

**Pasos**:
1. Iniciar sesión con credenciales válidas
2. Navegar a `/` (feed público)
3. Inspeccionar la cabecera

**Resultado Esperado**:
- ✅ Logo "ContraVento" visible a la izquierda
- ✅ Avatar del usuario (foto o inicial) a la derecha
- ✅ Username del usuario visible junto al avatar
- ✅ Botón "Cerrar sesión"
- ✅ NO hay botón "Iniciar sesión"
- ✅ Mismo diseño visual (gradiente, colores) que cabecera anónima

**Capturas Recomendadas**:
- Cabecera completa (autenticado)
- Detalle de avatar con username

---

### TC-US2-005: Avatar con Foto de Perfil

**Objetivo**: Verificar que se muestra la foto de perfil del usuario

**Precondiciones**:
- Usuario con foto de perfil configurada (ej: `testuser` con profile_photo_url)

**Pasos**:
1. Iniciar sesión con usuario que tiene foto de perfil
2. Verificar avatar en la cabecera

**Resultado Esperado**:
- ✅ Imagen circular (40px × 40px)
- ✅ Borde de 2px en color `--color-primary-dark`
- ✅ Sombra sutil
- ✅ Atributo `alt` con el username del usuario
- ✅ Imagen carga correctamente (src apunta a la URL de la foto)

---

### TC-US2-006: Avatar sin Foto de Perfil (Inicial)

**Objetivo**: Verificar que se muestra la inicial del username cuando no hay foto

**Precondiciones**:
- Usuario sin foto de perfil (profile_photo_url = null)

**Pasos**:
1. Iniciar sesión con usuario sin foto de perfil
2. Verificar avatar en la cabecera

**Resultado Esperado**:
- ✅ Avatar circular con inicial del username (ej: "T" para testuser)
- ✅ Fondo en color `--color-primary`
- ✅ Texto en color blanco
- ✅ Mismo tamaño y estilo que avatar con foto
- ✅ aria-label con texto "Avatar de [username]"

---

### TC-US2-007: Navegación a Dashboard al Click en Avatar

**Objetivo**: Verificar que hacer clic en el avatar/username navega al dashboard

**Precondiciones**:
- Usuario autenticado

**Pasos**:
1. Estando en el feed público (`/`)
2. Hacer clic en el avatar o username del usuario

**Resultado Esperado**:
- ✅ Navega a `/dashboard`
- ✅ Muestra la página de dashboard del usuario
- ✅ aria-label del botón indica "Ir al dashboard de [username]"

---

### TC-US2-008: Cerrar Sesión desde Cabecera

**Objetivo**: Verificar funcionamiento del botón "Cerrar sesión"

**Precondiciones**:
- Usuario autenticado en el feed público

**Pasos**:
1. Hacer clic en el botón "Cerrar sesión"
2. Esperar a que se complete el proceso

**Resultado Esperado**:
- ✅ Petición POST a `/auth/logout` se envía correctamente
- ✅ Cookie de sesión se elimina
- ✅ Página se recarga (`window.location.reload()`)
- ✅ Cabecera ahora muestra estado anónimo (botón "Iniciar sesión")
- ✅ No hay errores en consola

**Verificación Adicional**:
- Intentar acceder a `/dashboard` → debe redirigir a `/login`

---

### TC-US2-009: Manejo de Errores al Cerrar Sesión

**Objetivo**: Verificar comportamiento cuando logout falla

**Precondiciones**:
- Usuario autenticado
- Backend con endpoint de logout roto (simular error 500)

**Pasos**:
1. Hacer clic en "Cerrar sesión"
2. Esperar respuesta del servidor (error)

**Resultado Esperado**:
- ✅ Error se captura en consola (`console.error('Logout error:', ...)`)
- ✅ Página se recarga de todas formas (`window.location.reload()`)
- ✅ Usuario queda en estado anónimo (si el backend eliminó la sesión)

**Nota**: El componente hace reload forzoso incluso en error para asegurar limpieza del estado.

---

### TC-US2-010: Responsive - Cabecera en Mobile

**Objetivo**: Verificar diseño responsive de la cabecera en móviles

**Precondiciones**:
- Usuario autenticado

**Pasos**:
1. Abrir DevTools → Device Toolbar
2. Seleccionar dispositivo móvil (ej: iPhone 12)
3. Inspeccionar la cabecera

**Resultado Esperado (< 768px)**:
- ✅ Logo más pequeño (28px × 28px)
- ✅ Texto "ContraVento" con font-size reducido
- ✅ Username del usuario **oculto** (solo avatar visible)
- ✅ Avatar más pequeño (32px × 32px)
- ✅ Botones con padding reducido
- ✅ Todo cabe en una sola línea horizontal
- ✅ Mínimo 44px de altura táctil en botones

**Capturas Recomendadas**:
- Cabecera mobile (anónimo)
- Cabecera mobile (autenticado)

---

## User Story 3: Filtrado de Privacidad

### TC-US3-001: Exclusión de Viajes DRAFT

**Objetivo**: Verificar que los viajes en estado DRAFT no aparecen en el feed

**Precondiciones**:
- Usuario con viajes publicados y borradores:
  - 2 viajes con `status=PUBLISHED`
  - 2 viajes con `status=DRAFT`

**Pasos**:
1. Acceder al feed público (anónimo o autenticado)
2. Contar el número de viajes visibles

**Resultado Esperado**:
- ✅ Solo se muestran los 2 viajes publicados
- ✅ Los viajes DRAFT NO aparecen en el feed
- ✅ Contador muestra "2 viajes disponibles"

**Verificación Backend**:
```bash
curl http://localhost:8000/trips/public?page=1&limit=20 | jq '.data[] | .status'
# Todos deben ser "PUBLISHED"
```

---

### TC-US3-002: Exclusión de Perfiles Privados

**Objetivo**: Verificar que viajes de usuarios con perfil privado NO aparecen

**Precondiciones**:
- Usuario público (`testuser`) con 2 viajes publicados
- Usuario privado (`privateuser`) con 2 viajes publicados

**Pasos**:
1. Verificar que `privateuser` tiene `profile_visibility='private'`
2. Acceder al feed público
3. Buscar viajes del usuario privado

**Resultado Esperado**:
- ✅ Solo se muestran los viajes de `testuser`
- ✅ Viajes de `privateuser` NO aparecen en el feed
- ✅ Contador refleja solo viajes de perfiles públicos

**Verificación Backend**:
```bash
curl http://localhost:8000/trips/public?page=1&limit=20 | jq '.data[] | .author.username'
# NO debe aparecer "privateuser"
```

---

### TC-US3-003: Transición de Privacidad (Público → Privado)

**Objetivo**: Verificar que los viajes desaparecen del feed cuando el usuario cambia a privado

**Precondiciones**:
- Usuario público (`testuser`) con viajes publicados
- Usuario autenticado como `testuser` (para usar la API)

**Pasos**:
1. Acceder al feed público → ver viajes de `testuser`
2. Cambiar el perfil del usuario a privado via API:
   ```bash
   # Iniciar sesión como testuser
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"TestPass123!"}' \
     -c cookies.txt

   # Cambiar visibilidad a privado
   curl -X PUT http://localhost:8000/users/testuser/profile \
     -H "Content-Type: application/json" \
     -b cookies.txt \
     -d '{"profile_visibility":"private"}'
   ```
3. Recargar el feed público (navegar a `/` en el navegador)

**Resultado Esperado**:
- ✅ Los viajes de `testuser` YA NO aparecen en el feed
- ✅ Contador de viajes se reduce
- ✅ Si no hay otros viajes públicos → muestra estado vacío
- ✅ API responde con `"success": true` y muestra `"profile_visibility": "private"` en el perfil

**Revertir** (volver a público):
```bash
curl -X PUT http://localhost:8000/users/testuser/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"profile_visibility":"public"}'
```

**Alternativa**: Cambio directo en base de datos (solo para debugging):
```sql
-- Cambiar a privado
UPDATE users SET profile_visibility = 'private' WHERE username = 'testuser';

-- Revertir a público
UPDATE users SET profile_visibility = 'public' WHERE username = 'testuser';
```

---

### TC-US3-004: Verificación de Eager Loading (N+1 Prevention)

**Objetivo**: Verificar que la consulta usa eager loading para relaciones (user, photos, locations)

**Precondiciones**:
- Backend con logging de SQL activado

**Pasos**:
1. Activar logging de SQLAlchemy (en `src/database.py`):
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       echo=True  # Muestra todas las queries SQL
   )
   ```
2. Acceder al feed público
3. Revisar logs del backend

**Resultado Esperado**:
- ✅ Una sola query principal con JOINs a `users`, `trip_photos`, `trip_locations`
- ✅ NO hay múltiples queries individuales (problema N+1)
- ✅ Ejemplo de query esperada:
   ```sql
   SELECT trips.*, users.*, trip_photos.*, trip_locations.*
   FROM trips
   JOIN users ON trips.user_id = users.user_id
   LEFT JOIN trip_photos ON trips.trip_id = trip_photos.trip_id
   LEFT JOIN trip_locations ON trips.trip_id = trip_locations.trip_id
   WHERE trips.status = 'PUBLISHED' AND users.profile_visibility = 'public'
   ORDER BY trips.published_at DESC
   LIMIT 20;
   ```

---

## User Story 4: Navegación a Detalles

### TC-US4-001: Click en Tarjeta de Viaje

**Objetivo**: Verificar navegación a la página de detalles al hacer clic en la tarjeta

**Precondiciones**:
- Feed con viajes visibles

**Pasos**:
1. Acceder al feed público
2. Hacer clic en cualquier parte de una tarjeta de viaje

**Resultado Esperado**:
- ✅ Navega a `/trips/{trip_id}` (página de detalles del viaje)
- ✅ Muestra toda la información del viaje:
  - Título, descripción completa
  - Todas las fotos (galería)
  - Todas las ubicaciones
  - Tags
  - Autor, fecha de publicación
- ✅ Cursor cambia a `pointer` al pasar sobre la tarjeta

---

### TC-US4-002: Click en Foto del Viaje

**Objetivo**: Verificar que hacer clic en la foto también navega a detalles

**Preconditions**:
- Feed con viajes visibles

**Pasos**:
1. Acceder al feed público
2. Hacer clic específicamente en la **foto** de una tarjeta

**Resultado Esperado**:
- ✅ Navega a `/trips/{trip_id}`
- ✅ Mismo comportamiento que TC-US4-001

---

### TC-US4-003: Click en Título del Viaje

**Objetivo**: Verificar que hacer clic en el título también navega a detalles

**Precondiciones**:
- Feed con viajes visibles

**Pasos**:
1. Acceder al feed público
2. Hacer clic específicamente en el **título** de una tarjeta

**Resultado Esperado**:
- ✅ Navega a `/trips/{trip_id}`
- ✅ Mismo comportamiento que TC-US4-001

---

### TC-US4-004: Vista de Detalles para Usuario Anónimo

**Objetivo**: Verificar que usuarios anónimos ven vista de solo lectura

**Precondiciones**:
- Usuario NO autenticado

**Pasos**:
1. Acceder al feed público (anónimo)
2. Hacer clic en una tarjeta de viaje
3. Inspeccionar la página de detalles

**Resultado Esperado**:
- ✅ Toda la información del viaje es visible
- ✅ NO hay botón "Editar"
- ✅ NO hay botón "Eliminar"
- ✅ NO hay botón "Publicar" (si fuera borrador, pero no debería ser accesible)
- ✅ Cabecera muestra estado anónimo (botón "Iniciar sesión")

---

### TC-US4-005: Vista de Detalles para Usuario Autenticado (No Propietario)

**Objetivo**: Verificar que usuarios autenticados ven solo lectura si no son dueños del viaje

**Precondiciones**:
- Usuario autenticado (`testuser`)
- Viaje publicado por otro usuario (`maria_garcia`)

**Pasos**:
1. Iniciar sesión con `testuser`
2. Acceder al feed público
3. Hacer clic en un viaje de `maria_garcia`

**Resultado Esperado**:
- ✅ Toda la información del viaje es visible
- ✅ NO hay botón "Editar"
- ✅ NO hay botón "Eliminar"
- ✅ Cabecera muestra estado autenticado (avatar de `testuser`)

---

### TC-US4-006: Vista de Detalles para Propietario del Viaje

**Objetivo**: Verificar que el propietario ve botones de edición

**Precondiciones**:
- Usuario autenticado (`testuser`)
- Viaje publicado por `testuser`

**Pasos**:
1. Iniciar sesión con `testuser`
2. Acceder al feed público
3. Hacer clic en un viaje propio

**Resultado Esperado**:
- ✅ Toda la información del viaje es visible
- ✅ SÍ hay botón "Editar" (navega a `/trips/{trip_id}/edit`)
- ✅ SÍ hay botón "Eliminar" (abre modal de confirmación)
- ✅ Si el viaje es borrador, SÍ hay botón "Publicar"

**Nota**: Esta funcionalidad es de Feature 008, no de Feature 013, pero es importante verificar la integración.

---

## Pruebas de Integración Cross-Feature

### TC-INT-001: Navegación Completa (Feed → Dashboard → Feed)

**Objetivo**: Verificar flujo completo de navegación entre feed y dashboard

**Precondiciones**:
- Usuario autenticado

**Pasos**:
1. Acceder al feed público (`/`)
2. Hacer clic en avatar/username → navegar a dashboard (`/dashboard`)
3. En dashboard, hacer clic en link "Inicio" → volver a feed (`/`)

**Resultado Esperado**:
- ✅ Navegación fluida sin errores
- ✅ Estado de autenticación se mantiene
- ✅ Cabecera se actualiza correctamente en cada página
- ✅ Link "Inicio" en dashboard navega a `/`
- ✅ Link "Perfil" en dashboard navega a `/profile`

---

### TC-INT-002: Publicar Viaje y Verlo en Feed

**Objetivo**: Verificar que un viaje recién publicado aparece en el feed

**Precondiciones**:
- Usuario autenticado con perfil público

**Pasos**:
1. Crear un viaje nuevo en estado DRAFT (via Feature 008)
2. Verificar que NO aparece en el feed público
3. Publicar el viaje (`POST /trips/{trip_id}/publish`)
4. Recargar el feed público

**Resultado Esperado**:
- ✅ Viaje NO aparece en feed mientras está en DRAFT
- ✅ Viaje SÍ aparece en feed después de publicar
- ✅ Aparece al inicio del feed (más reciente)
- ✅ Contador de viajes se incrementa en 1

---

### TC-INT-003: Cambiar Perfil a Privado y Verificar Feed

**Objetivo**: Verificar que cambiar a perfil privado oculta viajes del feed

**Precondiciones**:
- Usuario con perfil público y viajes publicados

**Pasos**:
1. Ver viajes del usuario en el feed público
2. Cambiar perfil a privado via API:
   ```bash
   # Iniciar sesión como testuser
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"TestPass123!"}' \
     -c cookies.txt

   # Cambiar visibilidad a privado
   curl -X PUT http://localhost:8000/users/testuser/profile \
     -H "Content-Type: application/json" \
     -b cookies.txt \
     -d '{"profile_visibility":"private"}'
   ```

   **Alternativa SQL (solo para debugging)**:

   ```sql
   UPDATE users SET profile_visibility = 'private' WHERE username = 'testuser';
   ```
3. Recargar el feed público

**Resultado Esperado**:
- ✅ Viajes del usuario desaparecen del feed
- ✅ Contador se actualiza
- ✅ Si no hay otros viajes → muestra estado vacío

---

### TC-INT-004: Eliminar Viaje y Verificar Feed

**Objetivo**: Verificar que eliminar un viaje lo quita del feed

**Precondiciones**:
- Usuario con viaje publicado visible en el feed

**Pasos**:
1. Contar viajes actuales en el feed
2. Eliminar el viaje (via Feature 008):
   ```bash
   curl -X DELETE http://localhost:8000/trips/{trip_id} \
     -H "Cookie: session_token=..."
   ```
3. Recargar el feed público

**Resultado Esperado**:
- ✅ Viaje eliminado NO aparece en el feed
- ✅ Contador se reduce en 1
- ✅ Paginación se ajusta si era el único viaje de una página

---

## Pruebas de Rendimiento

### TC-PERF-001: Tiempo de Carga del Feed

**Objetivo**: Verificar que el feed carga en menos de 2 segundos

**Precondiciones**:
- Base de datos con 100+ viajes publicados

**Pasos**:
1. Abrir DevTools → Network tab
2. Limpiar caché del navegador
3. Acceder al feed público (`/`)
4. Medir tiempo de carga

**Resultado Esperado**:
- ✅ Petición `GET /trips/public` completa en < 500ms (p95)
- ✅ Página completa carga en < 2s
- ✅ First Contentful Paint (FCP) < 1s
- ✅ Largest Contentful Paint (LCP) < 2.5s

**Herramientas**:
- Chrome DevTools Performance tab
- Lighthouse (Performance score > 90)

---

### TC-PERF-002: Lazy Loading de Imágenes

**Objetivo**: Verificar que las imágenes usan lazy loading para mejorar rendimiento

**Precondiciones**:
- Feed con 20 viajes con fotos

**Pasos**:
1. Acceder al feed público
2. Abrir DevTools → Network tab → filtrar por "Img"
3. Verificar cuántas imágenes se cargan inicialmente
4. Hacer scroll hacia abajo

**Resultado Esperado**:
- ✅ Solo las imágenes visibles en viewport se cargan inicialmente
- ✅ Imágenes fuera del viewport se cargan al hacer scroll cerca
- ✅ Atributo `loading="lazy"` presente en todas las imágenes
- ✅ Reducción de datos transferidos en carga inicial

---

### TC-PERF-003: Paginación vs Scroll Infinito

**Objetivo**: Verificar que la paginación no degrada el rendimiento

**Precondiciones**:
- Base de datos con 100 viajes

**Pasos**:
1. Navegar entre páginas 1, 2, 3
2. Medir tiempo de respuesta de API en cada página

**Resultado Esperado**:
- ✅ Tiempo de respuesta constante (< 500ms por página)
- ✅ No hay degradación de rendimiento en páginas posteriores
- ✅ Memoria del navegador estable (no crece indefinidamente)

---

## Pruebas de Accesibilidad

### TC-A11Y-001: Navegación por Teclado

**Objetivo**: Verificar que toda la interfaz es navegable con teclado

**Precondiciones**:
- Feed con viajes visibles

**Pasos**:
1. Acceder al feed público
2. Presionar `Tab` repetidamente
3. Verificar que se puede navegar a:
   - Logo
   - Botón "Iniciar sesión" (o avatar/logout si autenticado)
   - Cada tarjeta de viaje
   - Botones de paginación

**Resultado Esperado**:
- ✅ Todos los elementos interactivos son alcanzables con `Tab`
- ✅ Orden de tabulación es lógico (izquierda → derecha, arriba → abajo)
- ✅ Focus visible con borde/outline en elementos activos
- ✅ `Enter` en tarjeta de viaje navega a detalles
- ✅ `Enter` en botón de paginación cambia de página

---

### TC-A11Y-002: Screen Reader (NVDA/JAWS/VoiceOver)

**Objetivo**: Verificar que la información es accesible para lectores de pantalla

**Precondiciones**:
- Screen reader instalado (NVDA en Windows, VoiceOver en Mac)

**Pasos**:
1. Activar screen reader
2. Navegar al feed público
3. Usar comandos de navegación del screen reader

**Resultado Esperado**:
- ✅ Cabecera anunciada correctamente (`<header>` semántico)
- ✅ Logo con texto alternativo
- ✅ Botones con aria-label descriptivos:
  - "Iniciar sesión"
  - "Ir al dashboard de [username]"
  - "Cerrar sesión"
- ✅ Tarjetas de viaje anunciadas como `<article>`
- ✅ Imágenes con alt text (título del viaje)
- ✅ Loading state con `aria-live="polite"` o `role="status"`
- ✅ Error state con `aria-live="assertive"` o `role="alert"`
- ✅ Botones de paginación con aria-disabled cuando corresponde

---

### TC-A11Y-003: Contraste de Colores

**Objetivo**: Verificar que todos los textos cumplen con WCAG AA (ratio 4.5:1)

**Precondiciones**:
- Navegador con extensión de accesibilidad (ej: Axe DevTools)

**Pasos**:
1. Acceder al feed público
2. Ejecutar análisis de contraste con Axe DevTools

**Resultado Esperado**:
- ✅ Texto de título en tarjetas: ratio ≥ 4.5:1
- ✅ Texto de metadata (ubicación, distancia): ratio ≥ 4.5:1
- ✅ Texto en cabecera (crema sobre gradiente): ratio ≥ 4.5:1
- ✅ Texto en botones: ratio ≥ 4.5:1
- ✅ No hay warnings de contraste en el reporte de Axe

**Herramientas**:
- Axe DevTools (extensión Chrome/Firefox)
- WebAIM Contrast Checker

---

## Pruebas en Dispositivos Móviles

### TC-MOBILE-001: Layout Responsive en Smartphone

**Objetivo**: Verificar diseño responsive en dispositivos móviles

**Precondiciones**:
- Feed con viajes visibles

**Pasos**:
1. Acceder al feed en dispositivo móvil real o DevTools Device Mode
2. Probar en diferentes tamaños:
   - iPhone 12 (390 × 844)
   - Samsung Galaxy S21 (360 × 800)
   - Pixel 5 (393 × 851)

**Resultado Esperado**:
- ✅ Grid de tarjetas se convierte a 1 columna en < 768px
- ✅ Tarjetas ocupan todo el ancho (con padding lateral)
- ✅ Imágenes mantienen aspect ratio 3:2
- ✅ Texto legible sin zoom
- ✅ Botones tienen mínimo 44px de altura táctil
- ✅ Cabecera se adapta (logo más pequeño, username oculto)
- ✅ Paginación se muestra en columna vertical

**Capturas Recomendadas**:
- Vista mobile del feed (portrait)
- Cabecera mobile
- Tarjeta de viaje mobile

---

### TC-MOBILE-002: Interacción Táctil

**Objetivo**: Verificar que la interfaz es amigable para táctil

**Precondiciones**:
- Dispositivo móvil real o simulador

**Pasos**:
1. Acceder al feed en dispositivo táctil
2. Tocar tarjetas de viaje
3. Tocar botones de paginación
4. Tocar botón "Iniciar sesión" / avatar

**Resultado Esperado**:
- ✅ Todos los botones responden a toques (no requieren doble tap)
- ✅ No hay efectos hover molestos en táctil
- ✅ Targets táctiles ≥ 44px × 44px
- ✅ Scroll suave y fluido
- ✅ No hay zoom accidental al hacer tap en inputs

---

### TC-MOBILE-003: Rendimiento en Redes Lentas

**Objetivo**: Verificar experiencia en conexiones 3G/4G

**Precondiciones**:
- DevTools con throttling activado (Slow 3G)

**Pasos**:
1. Activar Network throttling → Slow 3G
2. Acceder al feed público
3. Observar estados de carga

**Resultado Esperado**:
- ✅ Loading state se muestra claramente
- ✅ Spinner animado indica progreso
- ✅ Página sigue siendo navegable (cabecera visible)
- ✅ Imágenes se cargan progresivamente (lazy loading)
- ✅ No hay timeout antes de 10 segundos

---

## Checklist de Validación Final

### ✅ Pre-Release Checklist

Antes de considerar la Feature 013 completa, verificar que:

**Backend**:
- [ ] Endpoint `GET /trips/public` funciona correctamente
- [ ] Filtrado de privacidad aplicado (`status=PUBLISHED`, `profile_visibility='public'`)
- [ ] Paginación funciona (page, limit, total)
- [ ] Eager loading implementado (no N+1 queries)
- [ ] Todos los tests unitarios pasan (pytest backend/tests/unit/test_trip_service_public.py)
- [ ] Tests de integración pasan
- [ ] Rendimiento < 500ms en p95

**Frontend**:
- [ ] PublicFeedPage renderiza correctamente
- [ ] PublicTripCard muestra toda la información
- [ ] PublicHeader funciona en estados anónimo y autenticado
- [ ] Navegación entre feed y dashboard fluida
- [ ] Estados de carga, error, y vacío funcionan
- [ ] Paginación funciona correctamente
- [ ] Todos los tests unitarios pasan (16/16 PublicTripCard, 14/14 PublicHeader)
- [ ] No hay errores en consola del navegador

**Accesibilidad**:
- [ ] Navegación por teclado completa
- [ ] ARIA labels correctos
- [ ] Contraste de colores WCAG AA
- [ ] Screen reader compatible
- [ ] Axe DevTools sin errores críticos

**Responsive**:
- [ ] Diseño adaptado a mobile (< 768px)
- [ ] Targets táctiles ≥ 44px
- [ ] Imágenes con lazy loading
- [ ] Rendimiento aceptable en 3G

**Integración**:
- [ ] Viajes publicados aparecen en feed
- [ ] Viajes DRAFT no aparecen
- [ ] Perfiles privados excluidos
- [ ] Navegación a detalles funciona
- [ ] Flujo de autenticación correcto

**Documentación**:
- [ ] README actualizado con Feature 013
- [ ] CLAUDE.md incluye información de la feature
- [ ] Comentarios en código claros
- [ ] Tests documentados con docstrings

---

## Herramientas Recomendadas

- **DevTools**: Chrome/Firefox Developer Tools
- **Screen Readers**: NVDA (Windows), VoiceOver (Mac), JAWS
- **Accesibilidad**: Axe DevTools, WAVE, Lighthouse
- **Rendimiento**: Lighthouse, WebPageTest
- **Testing API**: Postman, curl, httpie
- **Database**: SQLite Browser, DBeaver

---

## Contacto y Soporte

Para reportar bugs o solicitar clarificaciones sobre las pruebas:

- **Repositorio**: https://github.com/jfdelafuente/contravento-application-python
- **Branch**: `013-public-trips-feed`
- **Issues**: Crear issue con etiqueta `feature-013`

---

**Última Actualización**: 2026-01-13
**Versión del Documento**: 1.0
**Feature**: 013 - Public Trips Feed
