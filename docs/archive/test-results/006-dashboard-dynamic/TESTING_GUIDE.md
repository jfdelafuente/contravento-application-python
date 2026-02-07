# Feature 006: Dashboard Dinámico - Testing Guide

**Objetivo**: Validar el MVP del dashboard con datos reales y recoger feedback

---

## Setup

### 1. Iniciar Backend

```bash
cd backend
./run-local-dev.sh
```

**Verificar**:
- Backend running en: http://localhost:8000
- API docs disponibles: http://localhost:8000/docs
- Base de datos SQLite: `backend/contravento_dev.db`

### 2. Iniciar Frontend

```bash
cd frontend
npm install  # Solo si es primera vez
npm run dev
```

**Verificar**:
- Frontend running en: http://localhost:3001
- Vite dev server activo

---

## Credenciales de Prueba

### Usuario Admin (con datos de prueba)
- **Username**: `admin`
- **Email**: `admin@contravento.com`
- **Password**: `AdminPass123!`

### Usuario Regular (sin viajes)
- **Username**: `testuser`
- **Email**: `test@example.com`
- **Password**: `TestPass123!`

---

## Test Cases - Dashboard MVP

### ✅ TC-001: Login y Navegación al Dashboard

**Objetivo**: Verificar que el usuario puede acceder al dashboard después de login

**Steps**:
1. Abrir http://localhost:3001
2. Click en "Iniciar Sesión"
3. Ingresar credenciales: `admin` / `AdminPass123!`
4. Click en "Entrar"

**Expected Result**:
- ✅ Redirección automática a `/dashboard`
- ✅ Header muestra "ContraVento" y UserMenu
- ✅ Welcome card muestra email del usuario
- ✅ Badge "Email verificado" visible

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

**Screenshots**: _______________

---

### ✅ TC-002: Stats Cards - Carga de Datos

**Objetivo**: Verificar que las stats cards muestran datos correctos del backend

**Steps**:
1. Ya logueado como `admin`
2. Observar sección "Tus Estadísticas"
3. Verificar 4 stats cards presentes

**Expected Result**:
- ✅ Card 1: "Viajes Publicados" muestra número (ej: "0" o "5")
- ✅ Card 2: "Kilómetros Recorridos" muestra distancia (ej: "0 km" o "1.234 km")
- ✅ Card 3: "Países Visitados" muestra número y lista
- ✅ Card 4: "Seguidores" muestra número
- ✅ Formato de números español: punto como separador de miles (1.234)
- ✅ Iconos SVG visibles en cada card

**Actual Result**: _______________

**Stats Values**:
- Viajes: _______________
- Kilómetros: _______________
- Países: _______________
- Seguidores: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-003: Stats Cards - Loading State

**Objetivo**: Verificar skeleton loaders durante carga de stats

**Steps**:
1. Hacer logout (UserMenu → Cerrar Sesión)
2. Volver a login como `admin`
3. **Observar rápidamente** durante los primeros milisegundos

**Expected Result**:
- ✅ Skeleton loaders aparecen brevemente
- ✅ Animación shimmer visible (gradiente movimiento)
- ✅ No layout shift al cargar datos reales
- ✅ Transición suave skeleton → datos

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

**Notes**: Si la carga es muy rápida, usar Network throttling en DevTools para simular conexión lenta

---

### ✅ TC-004: Stats Cards - Responsive Design

**Objetivo**: Verificar grid responsive en diferentes breakpoints

**Steps**:
1. Desktop (>1024px): Observar layout
2. Reducir ventana a tablet (768px)
3. Reducir a mobile (375px)

**Expected Result**:

**Desktop (≥1024px)**:
- ✅ 4 columnas (stats cards en línea horizontal)

**Tablet (640px - 1023px)**:
- ✅ 2x2 grid (2 filas, 2 columnas)

**Mobile (<640px)**:
- ✅ 1 columna (stats cards apilados verticalmente)

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-005: Recent Trips - Con Viajes

**Objetivo**: Verificar sección de viajes recientes con datos

**Prerequisite**: Usuario `admin` debe tener al menos 1 viaje publicado

**Steps**:
1. Como `admin`, scroll a "Viajes Recientes"
2. Observar cards de viajes

**Expected Result**:
- ✅ Header "Viajes Recientes" visible
- ✅ Botón "Ver todos los viajes" visible
- ✅ Cards muestran: foto, título, fecha, distancia, tags
- ✅ Formato de fecha: DD/MM/YYYY (ej: 09/01/2026)
- ✅ Formato de distancia: "X km" o "X mil km"
- ✅ Tags: máximo 3 visibles, resto como "+N"
- ✅ Hover effect: card se eleva con sombra

**Actual Result**: _______________

**Trips Count**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-006: Recent Trips - Empty State

**Objetivo**: Verificar mensaje cuando usuario no tiene viajes

**Steps**:
1. Logout y login como `testuser` (usuario sin viajes)
2. Scroll a "Viajes Recientes"

**Expected Result**:
- ✅ Icono de casa grande visible
- ✅ Título: "Aún no has publicado viajes"
- ✅ Texto: "Comienza a documentar tus aventuras..."
- ✅ Botón: "Crear tu primer viaje"
- ✅ Borde punteado (dashed border)
- ✅ No se muestra botón "Ver todos los viajes"

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-007: Recent Trips - Lazy Loading

**Objetivo**: Verificar lazy loading de imágenes de viajes

**Steps**:
1. Como `admin`, abrir DevTools → Network tab
2. Filter: Img
3. Scroll a "Viajes Recientes"
4. Observar cuando se cargan las imágenes

**Expected Result**:
- ✅ Imágenes se cargan solo cuando la sección es visible
- ✅ Skeleton placeholder visible antes de carga
- ✅ Fade-in suave al cargar imagen
- ✅ Placeholder "Sin foto" si trip no tiene imagen

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-008: Recent Trips - Responsive Grid

**Objetivo**: Verificar grid responsive en diferentes breakpoints

**Steps**:
1. Desktop: Observar layout
2. Tablet: Reducir ventana
3. Mobile: Reducir más

**Expected Result**:

**Desktop (≥1024px)**:
- ✅ 3 columnas

**Tablet (769px - 1023px)**:
- ✅ 2 columnas

**Mobile (<769px)**:
- ✅ 1 columna (cards apilados)

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-009: Quick Actions - Navegación

**Objetivo**: Verificar que los 4 botones de acción rápida navegan correctamente

**Steps**:
1. Localizar sección "Acciones Rápidas"
2. Click en "Crear Viaje"
3. Verificar navegación
4. Volver al dashboard (botón atrás)
5. Repetir con los otros 3 botones

**Expected Result**:

**Crear Viaje**:
- ✅ Navega a `/trips/new`
- ✅ Botón con variante primary (gradiente oliva)

**Ver Perfil**:
- ✅ Navega a `/profile`
- ✅ Botón con variante secondary (crema)

**Explorar Viajes**:
- ✅ Navega a `/explore`
- ✅ Botón con variante secondary

**Editar Perfil**:
- ✅ Navega a `/profile/edit`
- ✅ Botón con variante secondary

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-010: Quick Actions - Responsive Grid

**Objetivo**: Verificar grid responsive de botones

**Steps**:
1. Desktop: Observar layout
2. Tablet: Reducir ventana
3. Mobile: Reducir más

**Expected Result**:

**Desktop (≥1024px)**:
- ✅ 4 columnas (botones en línea)

**Tablet (640px - 1023px)**:
- ✅ 2x2 grid

**Mobile (640px)**:
- ✅ 2 columnas

**Very Small (<400px)**:
- ✅ 1 columna (botones apilados)

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-011: Quick Actions - Hover & Focus States

**Objetivo**: Verificar interactividad de botones

**Steps**:
1. Hover sobre cada botón de acción
2. Tab con teclado para navegar entre botones

**Expected Result**:

**Hover**:
- ✅ Botón se eleva (transform: translateY(-4px))
- ✅ Icono escala (scale: 1.1)
- ✅ Sombra aparece
- ✅ Borde cambia a color primary

**Focus (teclado)**:
- ✅ Outline visible (2px solid primary)
- ✅ Outline offset de 2px
- ✅ Tab navega entre botones en orden lógico

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-012: Diseño Rústico - Consistencia Visual

**Objetivo**: Verificar que todos los componentes siguen el diseño rústico

**Steps**:
1. Observar colores, tipografía, texturas
2. Comparar con DESIGN_SYSTEM.md

**Expected Result**:

**Colores**:
- ✅ Oliva (#6b723b) en iconos primary
- ✅ Crema (#f5f1e8) en backgrounds
- ✅ Marrón (#8b7355) en bordes

**Tipografía**:
- ✅ Headings: Playfair Display (serif)
- ✅ Body: Inter (sans-serif)

**Texturas**:
- ✅ Repeating diagonal lines visibles en cards
- ✅ Gradientes diagonales en botón primary

**Animaciones**:
- ✅ SlideUp al cargar secciones
- ✅ Staggered delays visibles

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-013: Performance - Carga Inicial

**Objetivo**: Medir tiempo de carga del dashboard

**Steps**:
1. Abrir DevTools → Performance tab
2. Reload página (Ctrl+Shift+R)
3. Medir tiempo hasta "Fully Loaded"

**Expected Result**:
- ✅ Carga inicial < 1 segundo (con stats cached)
- ✅ No layout shift (cumulative layout shift ~0)
- ✅ First Contentful Paint < 500ms

**Actual Result**:
- Load Time: _______________ ms
- CLS: _______________
- FCP: _______________ ms

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-014: Accessibility - WCAG AA

**Objetivo**: Verificar cumplimiento de accesibilidad

**Steps**:
1. Abrir Chrome DevTools → Lighthouse
2. Run Accessibility audit
3. Verificar score

**Expected Result**:
- ✅ Accessibility Score ≥ 90%
- ✅ Color contrast ≥ 4.5:1 (WCAG AA)
- ✅ ARIA labels presentes
- ✅ Semantic HTML (<section>, <article>, <h2>)
- ✅ Focus visible con teclado

**Actual Result**:
- Score: _______________ %
- Contrast Ratio: _______________
- Issues: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

### ✅ TC-015: Error Handling - Backend Down

**Objetivo**: Verificar error states cuando backend no responde

**Steps**:
1. Detener backend server
2. Reload dashboard (Ctrl+R)
3. Observar error states

**Expected Result**:

**Stats Cards**:
- ✅ Icono de error visible
- ✅ Mensaje: "Error al cargar estadísticas"
- ✅ No crash de la app

**Recent Trips**:
- ✅ Mensaje de error con icono
- ✅ Texto descriptivo del error

**Actual Result**: _______________

**Status**: ⬜ Pass | ⬜ Fail

---

## Summary Report Template

### Testing Session Info
- **Date**: _______________
- **Tester**: _______________
- **Browser**: _______________
- **OS**: _______________
- **Screen Resolution**: _______________

### Results Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-001: Login | ⬜ Pass ⬜ Fail | |
| TC-002: Stats Data | ⬜ Pass ⬜ Fail | |
| TC-003: Stats Loading | ⬜ Pass ⬜ Fail | |
| TC-004: Stats Responsive | ⬜ Pass ⬜ Fail | |
| TC-005: Trips With Data | ⬜ Pass ⬜ Fail | |
| TC-006: Trips Empty | ⬜ Pass ⬜ Fail | |
| TC-007: Trips Lazy Loading | ⬜ Pass ⬜ Fail | |
| TC-008: Trips Responsive | ⬜ Pass ⬜ Fail | |
| TC-009: Actions Navigation | ⬜ Pass ⬜ Fail | |
| TC-010: Actions Responsive | ⬜ Pass ⬜ Fail | |
| TC-011: Actions Interaction | ⬜ Pass ⬜ Fail | |
| TC-012: Rustic Design | ⬜ Pass ⬜ Fail | |
| TC-013: Performance | ⬜ Pass ⬜ Fail | |
| TC-014: Accessibility | ⬜ Pass ⬜ Fail | |
| TC-015: Error Handling | ⬜ Pass ⬜ Fail | |

**Total**: ___ Pass / ___ Fail / 15 Total

### Issues Found

1. **Issue #1**:
   - **Description**: _______________
   - **Severity**: ⬜ Critical ⬜ High ⬜ Medium ⬜ Low
   - **Steps to Reproduce**: _______________
   - **Expected**: _______________
   - **Actual**: _______________

2. **Issue #2**:
   - ...

### User Feedback

**Positive**:
- _______________

**Improvements Needed**:
- _______________

**Feature Requests**:
- _______________

### Next Actions

- [ ] Fix critical issues
- [ ] Implement improvements
- [ ] Re-test failed cases
- [ ] Merge to main
- [ ] Plan Feature 007

---

**Testing completed**: ⬜ Yes | ⬜ No
**Ready for merge**: ⬜ Yes | ⬜ No | ⬜ Needs fixes
