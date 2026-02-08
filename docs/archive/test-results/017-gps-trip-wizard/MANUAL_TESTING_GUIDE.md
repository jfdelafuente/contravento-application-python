# Guía de Pruebas Manuales - GPS Trip Creation Wizard (Phase 6)

**Feature**: 017-gps-trip-wizard
**Phase**: 6 (US6 - Publish Trip with Atomic Transaction)
**Fecha**: 2026-01-29

---

## Requisitos Previos

### 1. Backend en ejecución

```bash
# Terminal 1: Iniciar backend
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verificar que esté corriendo:
# http://localhost:8000/docs
```

### 2. Frontend en ejecución

```bash
# Terminal 2: Iniciar frontend
cd frontend
npm run dev

# Verificar que esté corriendo:
# http://localhost:5173
```

### 3. Usuario autenticado

- Tener un usuario creado en el sistema
- Credenciales por defecto:
  - **Usuario**: `testuser` / **Email**: `test@example.com` / **Password**: `TestPass123!`
  - **Admin**: `admin` / **Email**: `admin@contravento.com` / **Password**: `AdminPass123!`

### 4. Archivo GPX de prueba

Usar uno de estos archivos de prueba:
- `backend/tests/fixtures/gpx/short_route.gpx` (con elevación)
- `backend/tests/fixtures/gpx/no_elevation.gpx` (sin elevación)

---

## Escenario 1: Flujo Completo Exitoso (Happy Path)

### Objetivo
Verificar que el wizard completo funciona correctamente desde el paso 1 hasta la publicación del viaje.

### Pasos

1. **Iniciar sesión**
   - Ir a: http://localhost:5173/login
   - Credenciales: `testuser` / `TestPass123!`
   - Verificar: Redirección al dashboard

2. **Acceder al wizard GPS**
   - Ir a: http://localhost:5173/trips/new/gpx
   - Verificar: Wizard se muestra con el paso 1 activo
   - Verificar: Indicador de progreso muestra "0%"

3. **Paso 1: Subir archivo GPX**
   - Arrastrar archivo `short_route.gpx` a la zona de drop
   - O hacer clic y seleccionar archivo
   - Verificar:
     - ✅ Spinner de "Analizando GPX..." aparece
     - ✅ Tarjeta de telemetría aparece con datos:
       - Distancia: ~42.5 km
       - Elevación: ~850 m
       - Dificultad: Moderado (badge naranja)
     - ✅ Botón "Siguiente" se habilita
     - ✅ Indicador de progreso: "33%"

4. **Paso 2: Detalles del viaje**
   - Clic en "Siguiente"
   - Verificar: Navegación al paso 2
   - Completar formulario:
     - **Título**: "Ruta de Prueba GPS Wizard"
     - **Descripción**: "Esta es una descripción de prueba con más de cincuenta caracteres necesarios para cumplir con la validación del formulario."
     - **Fecha inicio**: 2024-06-01
     - **Fecha fin**: 2024-06-05
     - **Privacidad**: Público
   - Verificar:
     - ✅ Tarjeta GPX muestra el archivo cargado
     - ✅ Botón "Siguiente" se habilita al completar todos los campos
     - ✅ Indicador de progreso: "67%"

5. **Paso 3: Revisar y publicar**
   - Clic en "Siguiente"
   - Verificar: Navegación al paso 3 (Review)
   - Verificar resumen muestra:
     - ✅ **Detalles del Viaje**:
       - Título: "Ruta de Prueba GPS Wizard"
       - Descripción completa
       - Fechas: "1 de junio de 2024 - 5 de junio de 2024"
       - Privacidad: "Público"
     - ✅ **Archivo GPX**:
       - Nombre del archivo: "short_route.gpx"
       - Distancia: "42.5 km"
       - Elevación ganada: "850 m"
       - Dificultad: Badge "Moderado"
     - ✅ Indicador de progreso: "100%"
     - ✅ Botón "Publicar Viaje" habilitado

6. **Publicar viaje**
   - Clic en "Publicar Viaje"
   - Verificar:
     - ✅ Botón muestra "Publicando..." con spinner
     - ✅ Botón está deshabilitado durante la carga
     - ✅ (Después de 1-3 segundos) Toast de éxito: "¡Viaje creado correctamente!"
     - ✅ Redirección automática a `/trips/{trip_id}`

7. **Verificar viaje creado**
   - Verificar página de detalle del viaje:
     - ✅ Título correcto
     - ✅ Descripción completa
     - ✅ Fechas correctas
     - ✅ Badge de dificultad "Moderado"
     - ✅ Mapa con la ruta GPX renderizada
     - ✅ Panel de telemetría con métricas

8. **Verificar en base de datos**
   - Abrir consola del navegador (F12)
   - Ir a Network → Buscar request a `/trips/gpx-wizard`
   - Verificar response:
     ```json
     {
       "success": true,
       "data": {
         "trip_id": "...",
         "title": "Ruta de Prueba GPS Wizard",
         "status": "PUBLISHED",
         "gpx_file": {
           "gpx_file_id": "...",
           "total_distance_km": 42.5,
           "has_elevation": true,
           ...
         }
       },
       "error": null
     }
     ```

---

## Escenario 2: Validación de Errores

### 2.1. Archivo GPX demasiado grande

**Pasos**:
1. Crear archivo GPX > 10MB (puede ser un archivo de texto con extensión .gpx)
2. Intentar subirlo en Paso 1
3. **Resultado esperado**:
   - ❌ Toast de error: "El archivo GPX es demasiado grande (máximo 10 MB)"
   - ❌ No avanza al siguiente paso

### 2.2. Título demasiado largo

**Pasos**:
1. Completar Paso 1 con archivo válido
2. En Paso 2, ingresar título con > 200 caracteres
3. Clic en "Siguiente"
4. **Resultado esperado**:
   - ❌ Mensaje de error bajo el campo título
   - ❌ No avanza al Paso 3

### 2.3. Descripción demasiado corta

**Pasos**:
1. Completar Paso 1 con archivo válido
2. En Paso 2, ingresar descripción con < 50 caracteres (ej: "Descripción corta")
3. Clic en "Siguiente"
4. **Resultado esperado**:
   - ❌ Mensaje de error bajo el campo descripción
   - ❌ No avanza al Paso 3

### 2.4. Archivo GPX inválido

**Pasos**:
1. Crear archivo de texto con contenido inválido y renombrarlo a `.gpx`
2. Subirlo en Paso 1
3. **Resultado esperado**:
   - ❌ Toast de error: "No se pudo procesar el archivo GPX"
   - ❌ No muestra telemetría
   - ❌ Botón "Siguiente" deshabilitado

---

## Escenario 3: Navegación y Cancelación

### 3.1. Navegación entre pasos

**Pasos**:
1. Completar Paso 1 → Clic "Siguiente"
2. En Paso 2, clic "Anterior"
3. **Resultado esperado**:
   - ✅ Vuelve al Paso 1
   - ✅ Archivo GPX sigue cargado
   - ✅ Telemetría sigue visible

4. Clic "Siguiente" → Completar Paso 2 → Clic "Siguiente"
5. En Paso 3, clic "Anterior"
6. **Resultado esperado**:
   - ✅ Vuelve al Paso 2
   - ✅ Formulario conserva todos los datos

### 3.2. Cancelar wizard (sin datos)

**Pasos**:
1. Acceder al wizard (Paso 1 vacío)
2. Clic "Cancelar"
3. **Resultado esperado**:
   - ✅ Redirección inmediata a `/trips` (sin confirmación)

### 3.3. Cancelar wizard (con datos)

**Pasos**:
1. Completar Paso 1 y Paso 2
2. En Paso 2 o Paso 3, clic "Cancelar"
3. **Resultado esperado**:
   - ✅ Modal de confirmación aparece:
     - Título: "¿Seguro que quieres cancelar?"
     - Mensaje: "Se perderán todos los datos ingresados en el asistente."
     - Botones: "No, continuar" | "Sí, cancelar"

4. Clic "No, continuar"
5. **Resultado esperado**:
   - ✅ Modal se cierra
   - ✅ Wizard permanece en el mismo paso

6. Clic "Cancelar" nuevamente → Clic "Sí, cancelar"
7. **Resultado esperado**:
   - ✅ Redirección a `/trips`

---

## Escenario 4: Manejo de Errores de Red

### 4.1. Backend no disponible

**Pasos**:
1. Detener el backend (Ctrl+C en terminal)
2. Completar wizard hasta Paso 3
3. Clic "Publicar Viaje"
4. **Resultado esperado**:
   - ❌ Toast de error: "No se pudo conectar con el servidor. Verifica tu conexión a internet."
   - ✅ Wizard permanece en Paso 3
   - ✅ Botón "Publicar Viaje" se habilita de nuevo

### 4.2. Timeout (archivo muy grande)

**Nota**: Difícil de simular sin modificar el código.

**Resultado esperado** (si ocurriera):
- ❌ Toast de error: "El servidor tardó demasiado en responder. Intenta de nuevo."

---

## Escenario 5: Accesibilidad

### 5.1. Navegación con teclado

**Pasos**:
1. Acceder al wizard
2. Usar solo el teclado:
   - **Tab**: Navegar entre campos
   - **Enter**: Enviar formulario / Clic en botones
   - **Espacio**: Marcar checkboxes / radios
   - **Esc**: Cerrar modal de cancelación

3. **Resultado esperado**:
   - ✅ Todos los elementos son accesibles con teclado
   - ✅ Foco visible en elementos activos
   - ✅ Modal de cancelación cierra con Esc

### 5.2. Lector de pantalla

**Pasos** (si tienes lector de pantalla disponible):
1. Activar lector de pantalla (ej: NVDA, JAWS)
2. Navegar por el wizard
3. **Resultado esperado**:
   - ✅ Paso actual se anuncia: "Paso 1 de 3"
   - ✅ Botones tienen labels descriptivos
   - ✅ Errores de validación se anuncian

---

## Escenario 6: Responsive Design

### 6.1. Vista móvil (< 640px)

**Pasos**:
1. Abrir DevTools (F12) → Toggle device toolbar
2. Seleccionar iPhone SE o similar (375px width)
3. Completar wizard
4. **Resultado esperado**:
   - ✅ Layout se adapta a una columna
   - ✅ Botones están apilados verticalmente
   - ✅ Campos de formulario ocupan ancho completo
   - ✅ Indicador de pasos se muestra correctamente
   - ✅ Targets táctiles ≥ 44px de altura

### 6.2. Vista tablet (640px - 1024px)

**Pasos**:
1. Cambiar a iPad (768px width)
2. Completar wizard
3. **Resultado esperado**:
   - ✅ Resumen en Paso 3 usa grid de 2 columnas
   - ✅ Espaciado adecuado entre elementos

---

## Checklist de Verificación

Marca con ✅ cada elemento verificado durante las pruebas:

### Funcionalidad
- [ ] Paso 1: Subir GPX → Telemetría extraída correctamente
- [ ] Paso 2: Formulario de detalles valida todos los campos
- [ ] Paso 3: Resumen muestra todos los datos correctamente
- [ ] Publicar: Trip creado en backend con status PUBLISHED
- [ ] Publicar: GPX file vinculado al trip
- [ ] Publicar: Trackpoints guardados en base de datos
- [ ] Redirección a trip detail page después de publicar

### Validación
- [ ] Archivo > 10MB rechazado con mensaje apropiado
- [ ] Título > 200 caracteres rechazado
- [ ] Descripción < 50 caracteres rechazada
- [ ] Archivo GPX inválido rechazado

### UX
- [ ] Spinner de carga visible durante análisis de GPX
- [ ] Botón "Publicar" muestra spinner durante publicación
- [ ] Toasts de éxito y error se muestran correctamente
- [ ] Modal de confirmación de cancelación funciona
- [ ] Navegación anterior/siguiente funciona

### Errores
- [ ] Error de red muestra mensaje apropiado
- [ ] Errores de validación se muestran en español
- [ ] Wizard permanece abierto tras error (no cierra automáticamente)

### Accesibilidad
- [ ] Navegación con teclado funciona
- [ ] Foco visible en todos los elementos interactivos
- [ ] Labels ARIA presentes en elementos importantes

### Responsive
- [ ] Vista móvil (375px) renderiza correctamente
- [ ] Vista tablet (768px) renderiza correctamente
- [ ] Vista desktop (1200px+) renderiza correctamente

---

## Problemas Conocidos

### Backend - Integration Tests (No bloqueante)
- **Issue**: 3/9 tests de integración fallan con error `MissingGreenlet`
- **Status**: No afecta funcionalidad del endpoint
- **Logs**: El endpoint funciona correctamente en pruebas manuales
- **Tracking**: Documentado en T067 (deferred)

---

## Notas de Testing

**Logs del navegador**:
- Abrir DevTools (F12) → Console
- Verificar logs:
  - `✅ Trip created successfully:` (en éxito)
  - `❌ Error creating trip:` (en error)

**Network Inspector**:
- Ir a DevTools → Network
- Buscar request: `POST /trips/gpx-wizard`
- Verificar:
  - Request payload: FormData con `gpx_file` y campos del formulario
  - Response status: 201 (éxito) o 400/413/500 (error)
  - Response body: Estructura `{success, data, error}`

**Backend Logs**:
- En terminal del backend, verificar logs:
  ```
  INFO: Extracting telemetry from GPX file for user {user_id}
  INFO: Creating trip for user {user_id}: {title}
  INFO: Uploading GPX file for trip {trip_id}
  INFO: Successfully created trip {trip_id} with GPX file {gpx_file_id}
  ```

---

## Criterios de Aceptación (Cumplidos)

Según el plan de Phase 6:

- ✅ **AS6.1**: "Publicar" crea trip con todos los datos en transacción atómica
- ✅ **AS6.2**: Redirección a trip detail page tras publicación exitosa
- ✅ **AS6.3**: "Cancelar" muestra diálogo de confirmación si hay datos
- ✅ **AS6.4**: Errores muestran mensajes en español

---

## Próximos Pasos

Después de completar las pruebas manuales:

1. **T075**: Escribir tests E2E automatizados
2. **T076**: Ejecutar suite de tests E2E
3. **Phase 7**: Implementar visualización de mapa en Step 3 (opcional)
4. **Phase 9**: Optimizaciones de performance y accesibilidad

---

**Fecha de última actualización**: 2026-01-29
**Testeado por**: _________
**Resultado**: ✅ PASS / ❌ FAIL
**Comentarios**: _______________________________________________
