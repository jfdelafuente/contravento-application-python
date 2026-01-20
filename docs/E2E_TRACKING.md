# E2E Test Results Tracking

Documento de seguimiento de resultados de tests E2E para la rama `fix/e2e-auth-frontend-backend-mismatch`.

---

## 📊 Resumen de Ejecuciones

### Ejecución #1 - Baseline (Antes de los Fixes)

**Fecha**: 2026-01-20 (inicial)
**Archivo**: `docs/errores_e2e.txt`
**Commits base**: Hasta `4e3ca90`

**Resultados**:
```
✅ 10 passed (11%)
✘ 80 failed (89%)
⏭ 0 skipped
Total: 90 tests ejecutados
```

**Principales problemas identificados**:
1. 🔴 **CRÍTICO**: Estructura de respuesta del backend (70% de tests bloqueados)
2. 🟡 **MEDIO**: Redirección post-registro no funciona
3. 🟡 **MEDIO**: Redirección post-login no funciona
4. 🟢 **BAJO**: Duplicación de heading en Landing Page

---

### Ejecución #2 - Después de Fixes Iniciales

**Fecha**: 2026-01-20 (11:47 UTC)
**Archivo**: `docs/errores_e2e_1.txt`
**Commits aplicados**: `3acde93`, `e193a61`, `5c31c1d`, `7639042`, `ac189a3`

**Fixes implementados**:
1. ✅ Auto-verificación de usuarios en testing environment (`4e3ca90`)
2. ✅ Fix duplicate heading - cambio "El camino es el destino" → "El viaje importa más" (`3acde93`)
3. ✅ Formateo Black en auth.py y auth_service.py (`e193a61`)
4. ✅ Variables de entorno SECRET_KEY + APP_ENV en CI workflows (`5c31c1d`)
5. ✅ Detección de auto-verificación en RegisterPage → redirige a /login (`7639042`)
6. ✅ LoginPage redirige a /dashboard en lugar de / (`ac189a3`)

**Resultados**:
```
✅ 14 passed (20% de tests ejecutados) → +40% vs Ejecución #1
✘ 53 failed (76% de tests ejecutados) → -34% reducción de fallos
⏭ 1 skipped
🔴 2 interrupted (timeout)
⏸ 143 did not run (timeout a 10 minutos)
Total: 70/213 tests ejecutados (33%)
Tiempo: 10.0 minutos (límite alcanzado)
```

**Mejoras confirmadas**:

| Área | Antes | Ahora | Mejora |
|------|-------|-------|--------|
| **Login Flow** | 0/3 ✘ | 2/3 ✅ | +67% |
| `should login with valid credentials` | ✘ | ✅ | ✓ |
| `should login with email instead of username` | ✘ | ✅ | ✓ |
| **Session Persistence** | 0/1 ✘ | 1/1 ✅ | +100% |
| `should maintain session across page refreshes` | ✘ | ✅ | ✓ |
| **Landing Page - CTA Journey** | 6/6 ✅ | 6/6 ✅ | Mantenido |
| **Landing Page - Complete Journey** | 0/1 ✘ | 1/1 ✅ | +100% |
| `should complete full visitor journey` | ✘ | ✅ | ✓ |
| **Registration Flow** | 0/4 ✘ | 1/4 ✅ | +25% |
| `should show validation errors` | ✅ | ✅ | Mantenido |

**Problemas persistentes**:

1. **Registration Workflow** - Test desactualizado
   ```
   Error: expect(page).toHaveURL(/\/verify-email/)
   Received: "http://localhost:5173/register"
   ```
   - **Causa**: Test espera `/verify-email` pero con auto-verificación debe esperar `/login`
   - **Archivo**: `frontend/tests/e2e/auth.spec.ts:44`
   - **Solución**: Actualizar test para detectar auto-verificación

2. **Mobile Heading Duplicate** - Nuevo error descubierto
   ```
   Error: strict mode violation: getByRole('heading', { name: /el camino es el destino/i })
   resolved to 2 elements
   ```
   - **Causa**: Posible versión mobile del heading duplicado
   - **Archivo**: `frontend/tests/e2e/landing.spec.ts:128`
   - **Solución**: Investigar versiones responsive del componente

3. **Location Editing Tests** - 21 tests fallando
   - Todos fallan rápido (~2.3s cada uno)
   - Probablemente problema de autenticación no propagado
   - Requiere investigación adicional

4. **Timeout General**
   - Suite completo excede 10 minutos
   - Solo se ejecutan 70/213 tests (33%)
   - Opciones:
     - Aumentar timeout global
     - Reducir retries de 3 → 1
     - Reducir timeout individual de 10s → 5s

---

## 🎯 Estado de Problemas Identificados

### ✅ RESUELTOS

| ID | Problema | Commit | Estado |
|----|----------|--------|--------|
| P1 | Estructura respuesta backend incorrecta | N/A | ✅ Ya estaba correcto |
| P2 | Auto-verificación en testing | `4e3ca90` | ✅ Resuelto |
| P3 | Duplicate heading desktop | `3acde93` | ✅ Resuelto |
| P4 | Formateo Black | `e193a61` | ✅ Resuelto |
| P5 | Variables entorno CI | `5c31c1d` | ✅ Resuelto |
| P6 | Redirección post-registro (código) | `7639042` | ✅ Resuelto |
| P7 | Redirección post-login | `ac189a3` | ✅ Resuelto |
| P8 | Test registro espera /verify-email | `9a86db2` | ✅ Resuelto |
| P9 | Mobile layout gap (sections touching) | `6337735` | ✅ Resuelto |
| P11 | Login duplicate locator (strict mode) | `2dfb0da` | ✅ Resuelto |
| P12 | POST /trips retorna null data | `1580d1a` | ✅ Resuelto |
| P13 | CSS selector regex syntax error | `49aaa68` | ✅ Resuelto |
| P15 | Mensaje "registro exitoso" no encontrado | (pendiente) | ✅ Resuelto |
| P16 | Mensaje "nombre de usuario ya existe" no encontrado | (pendiente) | ✅ Resuelto |
| P17 | Mensaje "credenciales incorrectas" no encontrado | (pendiente) | ✅ Resuelto |
| P18 | User menu button no encontrado (logout) | (pendiente) | ✅ Resuelto |
| P19 | Protected routes no redirigen a /login | (pendiente) | ✅ Resuelto |
| P20 | Test de rutas públicas mal escrito | (pendiente) | ✅ Resuelto |
| P21 | Landing page no redirige usuarios autenticados | (pendiente) | ✅ Resuelto |
| P22 | Registro sin checkbox de términos | (pendiente) | ✅ Resuelto |
| P23 | Logout no espera navegación | (pendiente) | ✅ Resuelto |
| P24 | Public routes timeout con networkidle | (pendiente) | ✅ Resuelto |

### 🔴 PENDIENTES

| ID  | Problema                                      | Prioridad | Dificultad | Archivo                    |
|-----|-----------------------------------------------|-----------|------------|----------------------------|
| P14 | Timeout general del suite                     | 🟢 Baja   | Baja       | `playwright.config.ts`     |

---

## 📈 Métricas de Progreso

### Tasa de Éxito por Categoría

| Suite de Tests | Ejecución #1 | Ejecución #2 | Progreso |
|----------------|--------------|--------------|----------|
| **Auth** | 1/9 (11%) | 4/9 (44%) | +33% ✅ |
| **Landing** | 9/13 (69%) | 10/13 (77%) | +8% ✅ |
| **Location Editing** | 0/11 (0%) | 0/11 (0%) | Sin cambio |
| **Public Feed** | 0/16 (0%) | 0/16 (0%) | Sin cambio |
| **Trip Creation** | 0/39 (0%) | 0/39 (0%) | Sin ejecutar (timeout) |
| **TOTAL** | 10/90 (11%) | 14/70 (20%) | +9% ✅ |

**Nota**: Ejecución #2 solo ejecutó 70 tests vs 90 de Ejecución #1 debido a timeout.

### Evolución de Tests Pasando

```
Ejecución #1: ██░░░░░░░░ 10/90  (11%)
Ejecución #2: ████░░░░░░ 14/70  (20%)
```

**Proyección**: Si los 143 tests restantes se ejecutaran, estimamos ~35-40 tests pasando (16-18% total).

---

## 🔍 Análisis de Errores Comunes

### Error Pattern #1: Redirección Fallida

**Frecuencia**: 6 tests
**Ejemplo**:
```
Error: expect(page).toHaveURL(expected) failed
Expected: /\/verify-email/
Received: "http://localhost:5173/register"
```

**Causa raíz**: Tests no actualizados para flujo de auto-verificación

**Tests afectados**:
- `auth.spec.ts:29` - should complete full registration workflow
- `auth.spec.ts:60` - should prevent duplicate username registration

---

### Error Pattern #2: Elementos Duplicados

**Frecuencia**: 1 test
**Ejemplo**:
```
Error: strict mode violation: getByRole('heading', { name: /el camino es el destino/i })
resolved to 2 elements
```

**Causa raíz**: Versiones responsive del mismo contenido

**Tests afectados**:
- `landing.spec.ts:128` - should stack sections vertically on mobile

---

### Error Pattern #3: Timeout Rápido (~2.3s)

**Frecuencia**: 21 tests
**Ejemplo**: Todos los tests de Location Editing fallan en ~2.3s

**Causa raíz**: Probablemente no se puede crear usuario autenticado correctamente

**Tests afectados**: Todos en `location-editing.spec.ts`

---

## 🛠️ Próximas Acciones Recomendadas

### Prioridad ALTA 🔴

1. **Actualizar test de registro para soportar auto-verificación**
   - Archivo: `frontend/tests/e2e/auth.spec.ts`
   - Cambio: Detectar `is_verified` en respuesta y esperar `/login` o `/verify-email` según corresponda
   - Impacto estimado: +2-3 tests pasando

### Prioridad MEDIA 🟡

2. **Investigar duplicate heading en mobile**
   - Archivo: `frontend/src/components/landing/*`
   - Búsqueda: Versiones responsive del texto "El camino es el destino"
   - Impacto estimado: +1 test pasando

3. **Diagnosticar fallos de Location Editing**
   - Agregar logging en helper `createAuthenticatedUser()`
   - Verificar que el usuario se crea y autentica correctamente
   - Impacto estimado: +21 tests pasando si se resuelve la autenticación

### Prioridad BAJA 🟢

4. **Optimizar timeouts para ejecutar más tests**
   - Opción A: Aumentar timeout global de 10min → 15min
   - Opción B: Reducir retries de 3 → 1
   - Opción C: Reducir timeout individual de 10s → 5s
   - Impacto estimado: +143 tests ejecutados

---

## 📝 Notas de Desarrollo

### Decisiones Tomadas

1. **Auto-verificación en Testing** (`4e3ca90`)
   - Decisión: Auto-verificar usuarios cuando `APP_ENV=testing`
   - Razón: Simplifica flujo E2E, evita dependencia de email
   - Trade-off: No testea flujo completo de verificación por email

2. **Redirección post-login a /dashboard** (`ac189a3`)
   - Decisión: Cambiar destino por defecto de `/` a `/dashboard`
   - Razón: Evita loop de redirección con LandingPage
   - Trade-off: Cambia experiencia de usuario autenticado

### Lecciones Aprendidas

1. **CI Workflows necesitan SECRET_KEY explícito**
   - Pydantic Settings requiere variables de entorno incluso en tests
   - Solución: Agregar env vars a todos los jobs de test

2. **Tests E2E deben adaptarse a entorno de testing**
   - Los tests asumen flujo de producción (verificación por email)
   - Necesitan lógica condicional para testing vs production

3. **Heading duplicados causan strict mode violations**
   - Playwright en modo strict no permite seleccionar elementos duplicados
   - Solución: Usar nombres únicos o selectores más específicos

---

## 🔗 Referencias

- **Archivo de errores Ejecución #1**: `docs/errores_e2e.txt`
- **Archivo de errores Ejecución #2**: `docs/errores_e2e_1.txt`
- **Guía de CI**: `docs/CI_GUIDE.md`
- **Rama de trabajo**: `fix/e2e-auth-frontend-backend-mismatch`
- **Commits**: Ver `git log --oneline -n 10`

---

---

### Ejecución #3 - Regresión Detectada

**Fecha**: 2026-01-20 (13:00 UTC aprox)
**Archivo**: `docs/errores_e2e_2.txt`
**Commits**: Mismos que Ejecución #2 (sin cambios en código)

**Resultados**:
```
✅ 15 passed (8% de 186 ejecutados) → +1 vs Ejecución #2
✘ 171 failed (92% de 186 ejecutados) → +118 tests fallando
⏭ 1 skipped
Total: 186/213 tests ejecutados (87%) vs 70/213 en Ejecución #2
Tiempo: No reportado (probablemente <10 min por completarse)
```

**🔴 REGRESIÓN CRÍTICA**: Tests que pasaban ahora fallan

| Test | Ejecución #2 | Ejecución #3 | Cambio |
|------|--------------|--------------|--------|
| should login with valid credentials | ✅ | ✘ | 🔴 REGRESIÓN |
| should maintain session across page refreshes | ✅ | ✘ | 🔴 REGRESIÓN |
| Location Editing (21 tests) | No ejecutado | ✘ (todos) | Nuevo fallo |
| Public Feed (16 tests) | No ejecutado | ✘ (todos) | Nuevo fallo |
| Trip Creation (39 tests) | No ejecutado | ✘ (todos) | Nuevo fallo |

**Nuevos errores descubiertos**:

1. **Login Flow - Duplicate Username Locator**
   ```
   Error: strict mode violation: locator('text=loginuser_1768911555722') resolved to 2 elements:
     1) <span class="username">@loginuser_1768911555722</span>
     2) <strong>loginuser_1768911555722@example.com</strong>
   ```
   - **Archivo**: `auth.spec.ts:128`
   - **Problema**: Test usa selector demasiado genérico
   - **Solución**: Usar selector más específico (ej: `.username`, role-based selector)

2. **Create Trip Returns Null Data** (CRÍTICO - bloquea 76 tests)
   ```
   TypeError: Cannot destructure property 'trip_id' of '(intermediate value).data' as it is null.
   ```
   - **Archivo**: `location-editing.spec.ts:82` (helper `createUserWithTrip`)
   - **Endpoint**: `POST /trips`
   - **Problema**: Backend retorna `{ success: true, data: null }` en lugar de trip data
   - **Causa raíz**: `_load_trip_relationships()` no cargaba relación `user` ni `user.profile`
   - **Impacto**: Bloquea todos los tests de Location Editing, Public Feed, Trip Creation (76 tests)
   - **Solución**: Agregar `selectinload(Trip.user).selectinload(User.profile)` en trip_service.py

**Análisis de Progreso**:
- Más tests ejecutados (186 vs 70) → timeout resuelto ✅
- Pero tasa de éxito bajó dramáticamente (20% → 8%)
- Problemas de backend no detectados antes ahora visibles

---

### Ejecución #4 - Fixes Críticos (POST /trips + Registration Test)

**Fecha**: 2026-01-20 (14:00 UTC aprox)

**Commits**:

- `1580d1a` - Fix `_load_trip_relationships` to load `user` and `user.profile` relationships
- `9a86db2` - Fix E2E registration test to support auto-verification flow

**Problemas resueltos**:

1. **P12 - POST /trips retorna null data** (backend)
   - `POST /trips` ahora retorna trip data completo con `author` field
   - TripResponse.model_validate() puede serializar correctamente el Trip con user data

2. **P8 - Test registro espera /verify-email** (E2E test)
   - Test ahora detecta auto-verificación y espera redirect correcto
   - Funciona en testing (→ /login) y producción (→ /verify-email)

**Impacto esperado**:

- +76 tests desbloqueados (Location Editing, Public Feed, Trip Creation)
- +2-3 tests de registro arreglados

**Resultados reales** (archivo: `errores_e2e_e5445f5.txt`):

```text
✅ 16 passed (11% de ~140 ejecutados) → +1 vs Ejecución #3
✘ 124 failed tests únicos (~197 con retries)
⏭ 1 skipped
Total: ~140/213 tests ejecutados (66%)
```

**✅ Validación de fixes**:

- **P12 (POST /trips)**: ✅ CONFIRMADO - Tests de Location Editing ahora SE EJECUTAN (endpoint funciona)
- **P8 (Test registro)**: ✅ CONFIRMADO - Lógica de auto-verificación detectada correctamente

**🔴 Nuevo bloqueador identificado**:

- **P13 - CSS Selector Regex Syntax Error**: 18 tests de Location Editing fallaban con syntax error de Playwright
  - Causa: `button:has-text(/regex/i)` no es soportado
  - Solución: Usar `getByRole()` y `filter()` APIs

---

### Ejecución #5 - Fix CSS Selector Syntax (P13)

**Fecha**: 2026-01-20 (15:00 UTC aprox)

**Commit**:

- `49aaa68` - Fix CSS selector regex syntax in location-editing.spec.ts

**Problema resuelto**:

- **P13 - CSS Selector Regex Syntax Error** (E2E test)
  - Reemplazadas 18 ocurrencias de selectores CSS inválidos
  - Ahora usa APIs semánticas de Playwright (getByRole, getByTestId, filter)
- **P11 - Login Duplicate Locator** (E2E test)
  - Reemplazadas 2 ocurrencias de selector genérico `text=${username}`
  - Ahora usa `.username` class selector específico
  - Evita strict mode violation (2 elementos con el mismo texto)

**Impacto esperado**:

- +18 tests de Location Editing desbloqueados (P13)
- +2 tests de Auth desbloqueados (P11 - login y session persistence)

---

### Ejecución #6 - Fix Login Duplicate Locator (P11)

**Fecha**: 2026-01-20 (15:15 UTC aprox)

**Commit**:

- `2dfb0da` - Fix generic text selector in auth.spec.ts

**Problema resuelto**:

- **P11 - Login Duplicate Locator** (E2E test)
  - Selector genérico `text=${username}` coincidía con 2 elementos:
    1. `<span class="username">@username</span>`
    2. `<strong>username@example.com</strong>`
  - Causaba strict mode violation en Playwright
  - Solución: usar `.username` class selector específico
  - Afectaba 2 tests: login y session persistence

**Impacto esperado**:

- +2 tests de Auth desbloqueados

---

### Ejecución #7 - Fix Mobile Layout Gap (P9)

**Fecha**: 2026-01-20 (15:30 UTC aprox)

**Commit**:

- `6337735` - Add bottom margin to hero section on mobile

**Problema resuelto**:

- **P9 - Duplicate heading mobile / Mobile layout gap** (E2E test)
  - Test "should stack sections vertically on mobile" fallaba porque las secciones se tocaban exactamente
  - Error: `manifestoBox.y === heroBox.y + heroBox.height` (812.390625 === 812.390625)
  - Test esperaba: `manifestoBox.y > heroBox.y + heroBox.height` (debe haber gap)
  - Solución: Agregar `margin-bottom: var(--space-1)` a `.hero-section` en viewport móvil (< 768px)
  - Archivo: `frontend/src/components/landing/HeroSection.css`

**Impacto esperado**:

- +1 test de Landing Page desbloqueado (mobile responsive behavior)

---

## 🆕 Nuevos Problemas Identificados (Post Push P9, P11, P13)

### P15 - Mensaje "registro exitoso" no encontrado

**Prioridad**: 🔴 Alta
**Archivo**: `frontend/tests/e2e/auth.spec.ts:44`
**Test afectado**: `should complete full registration workflow`

**Error**:
```
Error: expect(locator).toBeVisible() failed
Locator: locator('text=/registro exitoso/i')
Expected: visible
Timeout: 10000ms
Error: element(s) not found
```

**Análisis**:
- El test busca el texto "registro exitoso" con regex case-insensitive
- El mensaje NO aparece en el DOM durante los 10 segundos de timeout
- RegisterPage tiene el mensaje: `'Registro exitoso! Tu cuenta ha sido verificada automáticamente...'`
- Posibles causas:
  1. El mensaje está en `.success-banner` pero el selector no lo encuentra
  2. Timing issue - el mensaje aparece y desaparece muy rápido (redirect después de 3s)
  3. El banner no se renderiza correctamente

**Solución propuesta**:
- Verificar que RegisterPage renderiza el banner con clase correcta
- Ajustar selector del test para usar clase específica: `.success-banner`
- Considerar aumentar timeout o esperar antes del redirect

---

### P16 - Mensaje "nombre de usuario ya existe" no encontrado

**Prioridad**: 🔴 Alta
**Archivo**: `frontend/tests/e2e/auth.spec.ts:95`
**Test afectado**: `should prevent duplicate username registration`

**Error**:
```
Error: expect(locator).toBeVisible() failed
Locator: locator('text=/nombre de usuario.*ya existe/i')
Expected: visible
```

**Análisis**:
- El test espera mensaje de error cuando se intenta registrar username duplicado
- Backend retorna error pero frontend no lo muestra o usa texto diferente
- Necesita verificar:
  1. Qué mensaje exacto retorna el backend
  2. Cómo RegisterForm maneja y muestra errores del backend
  3. Si el mensaje se muestra en `.error-banner`

**Solución propuesta**:
- Verificar mensaje exacto del backend en endpoint `/auth/register`
- Asegurar que RegisterForm muestra error en banner visible
- Ajustar test para buscar mensaje exacto del backend

---

### P17 - Mensaje "credenciales incorrectas" no encontrado

**Prioridad**: 🔴 Alta
**Archivo**: `frontend/tests/e2e/auth.spec.ts:153`
**Test afectado**: `should show error for invalid credentials`

**Error**:
```
Error: expect(locator).toBeVisible() failed
Locator: locator('text=/credenciales.*incorrectas/i')
Expected: visible
```

**Análisis**:
- Similar a P16 - mensaje de error de login no encontrado
- Backend retorna error de credenciales inválidas
- LoginPage tiene `errorMessage` state pero el banner no aparece
- Verificar LoginForm y cómo maneja errores

**Solución propuesta**:
- Verificar que LoginForm llama `onError()` callback correctamente
- Verificar que LoginPage renderiza `.error-banner` con el mensaje
- Ajustar test para usar selector de clase específico

---

### P18 - User menu button no encontrado (logout)

**Prioridad**: 🟡 Media
**Archivo**: `frontend/tests/e2e/auth.spec.ts:209`
**Test afectado**: `should logout and clear session`

**Error**:
```
TimeoutError: page.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[aria-label="User menu"]')
```

**Análisis**:
- El test busca botón con `aria-label="User menu"`
- Ese botón no existe en el DOM (diferente aria-label o no tiene)
- Probablemente el navbar/header usa un selector diferente

**Solución propuesta**:
- Inspeccionar componente Navbar/Header para encontrar aria-label correcto
- Opciones: `"Menú de usuario"`, `"User options"`, o usar data-testid
- Actualizar test con el selector correcto

---

### P19 - Protected routes no redirigen a /login

**Prioridad**: 🔴 Alta (Seguridad)
**Archivo**: `frontend/tests/e2e/auth.spec.ts:285`
**Test afectado**: `should redirect unauthenticated users to login`

**Error**:
```
Error: expect(page).toHaveURL(expected) failed
Expected pattern: /\/login/
Received string:  "http://localhost:5173/"
```

**Análisis**:
- Usuario NO autenticado intenta acceder a rutas protegidas (`/trips/new`, `/profile`, `/settings`)
- Esperado: redirect a `/login`
- Recibido: se queda en `/` (landing page)
- **CRÍTICO**: Las rutas protegidas NO están funcionando correctamente

**Causas posibles**:
1. ProtectedRoute component no redirige correctamente
2. useAuth() no detecta que usuario no está autenticado
3. Router config no usa ProtectedRoute wrapper

**Solución propuesta**:
- Verificar implementación de ProtectedRoute component
- Asegurar que verifica autenticación y redirige a `/login` con `state.from`
- Verificar que Router usa ProtectedRoute en rutas sensibles

---

### P20 - Test de rutas públicas mal escrito

**Prioridad**: 🟡 Media
**Archivo**: `frontend/tests/e2e/auth.spec.ts:301`
**Test afectado**: `should allow access to public routes`

**Error**:
```
Error: expect(page).not.toHaveURL(expected) failed
Expected pattern: not /\/login/
Received string: "http://localhost:5173/login"
```

**Análisis**:
- El test visita `/login` y espera que NO esté en `/login`
- Esto es ilógico - `/login` es una ruta pública y DEBERÍA estar en `/login`
- El test está MAL ESCRITO

**Código del test**:
```typescript
const publicRoutes = ['/', '/login', '/register', '/trips/public'];
for (const route of publicRoutes) {
  await page.goto(`${FRONTEND_URL}${route}`);
  // Should NOT redirect to login
  await expect(page).not.toHaveURL(/\/login/);
}
```

**Problema**: Cuando visita `/login`, el test espera `not.toHaveURL(/\/login/)` pero obviamente SÍ está en `/login`

**Solución propuesta**:
- Cambiar lógica del test para verificar que rutas públicas NO redirigen a OTRA parte
- Opción 1: Verificar que URL coincide con la ruta visitada
- Opción 2: Verificar que NO redirige a una página de error/404

**Fix sugerido**:
```typescript
for (const route of publicRoutes) {
  await page.goto(`${FRONTEND_URL}${route}`);
  // Should stay on the same route (not redirect away)
  await expect(page).toHaveURL(new RegExp(route));
}
```

---

### P21 - Landing page no redirige usuarios autenticados

**Prioridad**: 🟡 Media (UX)
**Archivo**: `frontend/tests/e2e/landing.spec.ts:88`
**Test afectado**: `should redirect authenticated users to /trips/public`

**Error**:
```
Error: expect(page).toHaveURL(expected) failed
Expected: "http://localhost:5173/trips/public"
Received: "http://localhost:5173/"
```

**Análisis**:
- Usuario autenticado visita `/` (landing page)
- Esperado: redirect automático a `/trips/public`
- Recibido: se queda en `/`
- Esto es UX - usuarios autenticados no deberían ver landing page

**Solución propuesta**:
- Agregar lógica en LandingPage para detectar usuario autenticado
- Usar useAuth() hook y useEffect para redirigir
- Ejemplo:
```typescript
const { user } = useAuth();
useEffect(() => {
  if (user) {
    navigate('/trips/public');
  }
}, [user, navigate]);
```

---

**Última actualización**: 2026-01-20
**Próxima ejecución programada**: Después de fix P9 - EJECUTAR AHORA

**Resumen de problemas nuevos**: 7 problemas adicionales identificados (P15-P21)
- 🔴 Alta prioridad: 4 (P15, P16, P17, P19)
- 🟡 Media prioridad: 3 (P18, P20, P21)
