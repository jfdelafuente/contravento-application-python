# Guía de Testing Manual - Feed Personalizado (US1)

## Objetivo

Verificar que el Feed Personalizado cumple con los criterios de éxito de rendimiento:

- **SC-001**: Feed carga en menos de 1 segundo con 10 viajes
- **SC-002**: Infinite scroll carga siguiente página en menos de 500ms

## Prerequisitos

### 1. Datos de Prueba

✅ Ya ejecutados automáticamente:

```bash
# Usuario de prueba
cd backend
poetry run python scripts/create_verified_user.py

# 5 viajes de ejemplo (4 publicados + 1 borrador)
poetry run python scripts/seed_trips.py --user testuser
```

### 2. Servidores Activos

**Backend** (Terminal 1):
```bash
.\run_backend.ps1
# Debe estar corriendo en http://localhost:8000
```

**Frontend** (Terminal 2):
```bash
.\run_frontend.ps1
# Debe estar corriendo en http://localhost:5173
```

## T039: Manual Test - Feed Loads in <1s (SC-001)

### Objetivo
Verificar que la carga inicial del feed (10 viajes) toma menos de 1 segundo.

### Pasos

1. **Abrir DevTools** en navegador:
   - Chrome/Edge: F12 → Tab "Network"
   - Firefox: F12 → Tab "Red"

2. **Hacer login**:
   - Ir a: http://localhost:5173/login
   - Usuario: `testuser`
   - Contraseña: `TestPass123!`
   - Click "Iniciar Sesión"

3. **Navegar al Feed**:
   - Click en enlace "Feed" en navigation
   - O directamente: http://localhost:5173/feed

4. **Medir tiempo de carga**:

   **Opción A - Network Tab**:
   - En DevTools > Network tab
   - Buscar request: `GET /feed?page=1&limit=10`
   - Verificar columna "Time" o "Tiempo"
   - ✅ PASS si tiempo < 1000ms
   - ❌ FAIL si tiempo >= 1000ms

   **Opción B - Console Timing**:
   ```javascript
   // En Console de DevTools:
   console.time('feed-load');
   // Hacer click en "Feed" en navegación
   // Cuando aparezcan los viajes:
   console.timeEnd('feed-load');
   ```
   - ✅ PASS si tiempo < 1000ms

5. **Verificar contenido**:
   - Deben aparecer 4 viajes (solo publicados)
   - Cada viaje muestra: título, autor, distancia, fechas, tags
   - El borrador "Transpirenaica" NO debe aparecer (es privado)

### Resultados Esperados

| Métrica | Esperado | Criterio |
|---------|----------|----------|
| Tiempo de respuesta | < 1000ms | SC-001 |
| Viajes mostrados | 4 trips | Solo publicados |
| Estado HTTP | 200 OK | Éxito |

### Troubleshooting

**Si tarda > 1s**:
- Verificar que backend está en modo desarrollo (no debug logging excesivo)
- Revisar si hay N+1 queries en backend logs
- Verificar que frontend no hace múltiples requests innecesarios

**Si no aparecen viajes**:
- Verificar autenticación: debe haber token en localStorage
- Revisar Console por errores JavaScript
- Verificar que backend devuelve datos: `curl http://localhost:8000/feed -H "Authorization: Bearer TOKEN"`

---

## T040: Manual Test - Infinite Scroll <500ms (SC-002)

### Objetivo
Verificar que el infinite scroll carga la siguiente página en menos de 500ms.

### Pasos

1. **Prerequisito - Más datos**:
   ```bash
   # Crear más viajes para testuser (total: 15 viajes)
   cd backend
   poetry run python scripts/seed_trips.py --user testuser
   poetry run python scripts/seed_trips.py --user testuser
   ```

2. **Abrir Feed**:
   - Login como `testuser`
   - Navegar a http://localhost:5173/feed
   - Abrir DevTools > Network tab

3. **Clear Network Log**:
   - Click en icono "Clear" (🚫) en Network tab
   - Esto limpia requests anteriores

4. **Activar Infinite Scroll**:
   - Scroll down hasta el final de la lista de viajes
   - El scroll debe activarse ~200px antes del final (rootMargin)
   - Debería aparecer "Cargando más viajes..." con spinner

5. **Medir tiempo**:
   - En Network tab, buscar: `GET /feed?page=2&limit=10`
   - Verificar columna "Time"
   - ✅ PASS si tiempo < 500ms
   - ❌ FAIL si tiempo >= 500ms

6. **Verificar comportamiento**:
   - Nuevos viajes se agregan al final de la lista (no reemplaza)
   - Spinner desaparece cuando carga completa
   - Si no hay más viajes: muestra mensaje "Has llegado al final del feed"

### Resultados Esperados

| Métrica | Esperado | Criterio |
|---------|----------|----------|
| Tiempo de paginación | < 500ms | SC-002 |
| Viajes acumulados | 10 + N más | Append, no replace |
| Estado HTTP | 200 OK | Éxito |
| End of feed | Mensaje correcto | Si hasMore=false |

### Casos de Prueba Adicionales

**Test 1: Scroll rápido repetido**
- Hacer scroll down muy rápido varias veces
- ✅ No debe hacer múltiples requests simultáneos
- ✅ Solo 1 request a la vez (isLoadingMore flag)

**Test 2: Final del feed**
- Scroll hasta que no haya más viajes
- ✅ Debe mostrar: "Has llegado al final del feed. ¡No hay más viajes por ahora!"
- ✅ No debe intentar cargar más (hasMore=false)

**Test 3: Performance bajo load**
- Tener 30+ viajes cargados
- Scroll down para cargar página 4
- ✅ Debe seguir siendo < 500ms (backend pagina, no carga todo)

### Troubleshooting

**Si no se activa infinite scroll**:
- Verificar que hasMore=true en estado del hook
- Revisar Console: ¿hay errores de Intersection Observer?
- Verificar que el sentinel element existe en DOM

**Si hace múltiples requests**:
- Bug: isLoadingMore no está evitando requests concurrentes
- Verificar lógica en FeedList.tsx línea 83: `&& !isLoadingMore && !isLoading`

**Si tarda > 500ms**:
- Verificar índices en base de datos (idx_trip_published)
- Revisar eager loading de relaciones (tags, user, photos)
- Verificar que limit=10 está aplicándose correctamente

---

## Verificación de Cumplimiento

### Checklist Final

- [ ] **T039**: Feed carga inicial < 1s ✅
- [ ] **T040**: Infinite scroll pagination < 500ms ✅
- [ ] Viajes publicados visibles
- [ ] Borradores NO visibles (solo owner)
- [ ] Intersection Observer funciona correctamente
- [ ] Mensajes de loading/end apropiados
- [ ] No hay N+1 queries en backend logs
- [ ] Frontend no hace requests duplicados

### Evidencia de Pruebas

**Screenshots requeridos**:
1. DevTools Network tab mostrando tiempo < 1s para GET /feed
2. DevTools Network tab mostrando tiempo < 500ms para paginación
3. Feed page mostrando viajes correctamente

**Backend logs a revisar**:
```bash
# Buscar estas queries en logs del backend:
# ✅ GOOD - Single query con JOIN:
SELECT trips.*, users.username, COUNT(photos)
FROM trips
JOIN users ON trips.user_id = users.id
LEFT JOIN trip_photos ON trips.trip_id = trip_photos.trip_id
WHERE trips.status = 'published'
ORDER BY trips.created_at DESC
LIMIT 10

# ❌ BAD - N+1 queries:
SELECT * FROM trips LIMIT 10
SELECT * FROM users WHERE id = ?  -- Repeated 10 times!
```

---

## Notas de Implementación

### Optimizaciones Aplicadas

**Backend**:
- Eager loading con `selectinload()` para user, photos, tags
- Índice compuesto en (user_id, status) para queries optimizadas
- Paginación con LIMIT/OFFSET

**Frontend**:
- Intersection Observer API (mejor que scroll listener)
- Debounce implícito via isLoadingMore flag
- Skeleton loaders para perceived performance
- Lazy loading de FeedPage component

### Métricas de Referencia

En desarrollo local (SQLite + React dev server):
- Feed inicial: ~200-400ms típico
- Paginación: ~100-200ms típico
- Targets de producción más estrictos (PostgreSQL + build optimizado)

---

## Próximos Pasos

Una vez completadas T039 y T040:

1. Marcar tareas como completadas en tasks.md
2. Crear commit con evidencia de pruebas
3. Continuar con Phase 4: User Story 2 - Likes/Me Gusta

```bash
# Commit de testing
git add specs/004-social-network/MANUAL_TESTING_GUIDE.md
git commit -m "docs: add manual testing guide for feed performance (T039-T040)

- SC-001: Feed loads in <1s
- SC-002: Infinite scroll <500ms
- Includes troubleshooting and verification steps"
```
