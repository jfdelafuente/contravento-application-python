# Guía de Testing Manual - Feature 003: GPS Routes Interactive

## 📋 Índice

1. [Preparación del Entorno](#preparación-del-entorno)
2. [T046: Upload de archivo pequeño (<1MB)](#t046-upload-de-archivo-pequeño-1mb)
3. [T047: Upload de archivo grande (>1MB)](#t047-upload-de-archivo-grande-1mb)
4. [T048: Descarga de archivo GPX original](#t048-descarga-de-archivo-gpx-original)
5. [T049: Eliminación con cascade](#t049-eliminación-con-cascade)
6. [Verificación de Errores](#verificación-de-errores)
7. [Checklist Final](#checklist-final)

---

## Preparación del Entorno

### 1. Iniciar Backend

```bash
cd backend

# Opción 1: Script de desarrollo (recomendado)
cd ..
.\run_backend.ps1       # Windows
./run_backend.sh        # Linux/Mac

# Opción 2: Manual
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verificar**: http://localhost:8000/health debe retornar `{"success": true, "data": {"status": "healthy"}}`

### 2. Iniciar Frontend

```bash
# Desde la raíz del proyecto
cd ..
.\run_frontend.ps1      # Windows
./run_frontend.sh       # Linux/Mac

# O manualmente
cd frontend
npm run dev
```

**Verificar**: http://localhost:5173 debe cargar la página de inicio

### 3. Crear Usuario y Viaje de Prueba

1. **Registrarse**: http://localhost:5173/register
   - Usuario: `testgpx`
   - Email: `testgpx@example.com`
   - Password: `TestGPX123!`

2. **Verificar email** (en desarrollo, revisar logs del backend o usar script):
   ```bash
   cd backend
   poetry run python scripts/create_verified_user.py --verify-email testgpx@example.com
   ```

3. **Crear viaje de prueba**:
   - Login con el usuario creado
   - Ir a "Mis Viajes" → "Nuevo Viaje"
   - Título: `Test Ruta GPS`
   - Descripción: `Viaje para probar funcionalidad de upload GPX`
   - Fecha inicio: Hoy
   - Distancia: 50 km
   - Click "Guardar borrador"
   - **Publicar** el viaje (importante: necesita estar publicado)

4. **Copiar archivos GPX a ubicación accesible**:
   ```bash
   # Crear carpeta temporal
   mkdir test-gpx-files

   # Copiar archivos de prueba
   cp backend/tests/fixtures/gpx/short_route.gpx test-gpx-files/
   cp backend/tests/fixtures/gpx/camino_del_cid.gpx test-gpx-files/
   cp backend/tests/fixtures/gpx/long_route_5mb.gpx test-gpx-files/
   ```

---

## T046: Upload de archivo pequeño (<1MB)

### Objetivo
Verificar que archivos GPX pequeños (<1MB) se procesan **sincrónicamente en <3 segundos** (SC-002)

### Pasos

1. **Abrir el viaje creado**:
   - Navegar a "Mis Viajes"
   - Click en "Test Ruta GPS"

2. **Ubicar sección GPX**:
   - Scroll hacia abajo después de la galería de fotos
   - Debe aparecer sección "Subir Archivo GPX"

3. **Upload del archivo**:
   - **Archivo**: `test-gpx-files/short_route.gpx` (2.8 KB)
   - **Método 1 - Drag & Drop**:
     - Arrastrar archivo a la zona de dropzone
     - Soltar
   - **Método 2 - Click**:
     - Click en zona de dropzone
     - Seleccionar archivo en el diálogo

4. **Observar procesamiento**:
   - ⏱️ **Cronometrar**: El proceso completo debe tomar **<3 segundos**
   - ✅ Debe aparecer barra de progreso (0% → 100%)
   - ✅ Mensaje: "Procesando archivo GPX..."
   - ✅ Al finalizar: "Archivo GPX procesado correctamente" (toast)

5. **Verificar resultados**:
   - ✅ Sección "Ruta GPS" debe aparecer automáticamente
   - ✅ Estadísticas mostradas:
     - **Distancia Total**: ~X.XX km
     - **Desnivel Positivo**: ~X m (si tiene elevación)
     - **Desnivel Negativo**: ~X m (si tiene elevación)
     - **Altitud Máxima**: ~X m (si tiene elevación)
     - **Altitud Mínima**: ~X m (si tiene elevación)
   - ✅ Cards con colores distintivos:
     - Distancia: Azul
     - Desnivel positivo: Verde
     - Desnivel negativo: Naranja
     - Altitud máxima: Morado
     - Altitud mínima: Teal

### Criterios de Éxito ✅

- [ ] Upload completo en **<3 segundos**
- [ ] Barra de progreso visible y funcional
- [ ] Toast de éxito mostrado
- [ ] Estadísticas correctas desplegadas
- [ ] Cards con colores apropiados
- [ ] Sección de upload desaparece (solo una GPX por viaje)

### Captura de Pantalla Recomendada

📸 Capturar: Vista completa de la sección "Ruta GPS" con todas las estadísticas

---

## T047: Upload de archivo grande (>1MB)

### Objetivo
Verificar comportamiento con archivos grandes (actualmente retorna 501 - no implementado)

### Pasos

1. **Crear nuevo viaje de prueba**:
   - Título: `Test GPX Grande`
   - Publicar

2. **Intentar upload**:
   - **Archivo**: `test-gpx-files/long_route_5mb.gpx` (5.1 MB)
   - Drag & drop o click para seleccionar

3. **Verificar respuesta**:
   - ❌ **Esperado**: Error 501 "Not Implemented"
   - ⚠️ Mensaje de error en español
   - ⚠️ No debe crashear la aplicación

### Criterios de Éxito ✅

- [ ] Error manejado correctamente (no crash)
- [ ] Mensaje de error claro en español
- [ ] Botón de "Reintentar" disponible

### Nota

⚠️ **Este test fallará actualmente** porque el procesamiento asíncrono no está implementado. Esto es **esperado y documentado**.

---

## T048: Descarga de archivo GPX original

### Objetivo
Verificar que se puede descargar el archivo GPX original subido (FR-039)

### Pasos

1. **Navegar al viaje con GPX** (del T046):
   - Ir a "Test Ruta GPS"

2. **Abrir DevTools (Opcional)**:
   - F12 → Network tab
   - Filtrar: `download`

3. **Buscar botón de descarga**:
   - ⚠️ **NOTA**: El botón de descarga no está implementado en el frontend aún
   - **Workaround**: Usar API directamente

4. **Descarga via API**:
   ```bash
   # Obtener GPX ID del viaje
   curl http://localhost:8000/trips/{TRIP_ID}/gpx

   # Descargar archivo original (reemplazar {GPX_FILE_ID})
   curl -o downloaded.gpx http://localhost:8000/gpx/{GPX_FILE_ID}/download
   ```

5. **Verificar archivo descargado**:
   ```bash
   # Comparar tamaño
   ls -lh downloaded.gpx
   ls -lh test-gpx-files/short_route.gpx

   # Verificar contenido (primeras 5 líneas)
   head -n 5 downloaded.gpx
   ```

### Criterios de Éxito ✅

- [ ] Archivo se descarga correctamente
- [ ] Tamaño coincide con original
- [ ] Contenido es XML válido
- [ ] Nombre del archivo: `original.gpx`

### Captura de Pantalla

📸 Capturar: Archivo descargado en carpeta de descargas

---

## T049: Eliminación con Cascade

### Objetivo
Verificar que al eliminar un viaje con GPX, se eliminan también los trackpoints en cascada (FR-036)

### Pasos

1. **Preparación - Verificar datos en BD**:
   ```bash
   cd backend

   # SQLite (desarrollo)
   poetry run python -c "
   from src.database import get_sync_db
   db = next(get_sync_db())

   # Contar GPX files
   gpx_count = db.execute('SELECT COUNT(*) FROM gpx_files').scalar()
   print(f'GPX files: {gpx_count}')

   # Contar trackpoints
   points_count = db.execute('SELECT COUNT(*) FROM track_points').scalar()
   print(f'Track points: {points_count}')
   "
   ```

2. **Eliminar viaje desde frontend**:
   - Ir a "Test Ruta GPS"
   - Click en botón "Eliminar viaje" (⚠️ solo visible para el owner)
   - Confirmar en el modal de confirmación
   - ✅ Toast: "Viaje eliminado correctamente"
   - ✅ Redirección a lista de viajes

3. **Verificar eliminación en cascada**:
   ```bash
   # Verificar que GPX y trackpoints fueron eliminados
   poetry run python -c "
   from src.database import get_sync_db
   db = next(get_sync_db())

   # Contar GPX files (debe haber disminuido)
   gpx_count = db.execute('SELECT COUNT(*) FROM gpx_files').scalar()
   print(f'GPX files después: {gpx_count}')

   # Contar trackpoints (debe haber disminuido)
   points_count = db.execute('SELECT COUNT(*) FROM track_points').scalar()
   print(f'Track points después: {points_count}')
   "
   ```

4. **Verificar archivo físico eliminado**:
   ```bash
   # El archivo en storage debe haber sido eliminado
   ls -la backend/storage/gpx_files/

   # No debe existir carpeta con el trip_id eliminado
   ```

### Criterios de Éxito ✅

- [ ] Viaje eliminado correctamente
- [ ] GPX file eliminado de BD
- [ ] Trackpoints eliminados de BD (cascade)
- [ ] Archivo físico eliminado de `storage/gpx_files/`
- [ ] Toast de confirmación mostrado
- [ ] Redirección correcta a lista

---

## Verificación de Errores

### Test 1: Archivo demasiado grande (>10MB)

1. **Crear archivo grande**:
   ```bash
   # Crear archivo de 11MB (excede límite)
   cd test-gpx-files
   dd if=/dev/zero of=oversized.gpx bs=1M count=11
   ```

2. **Intentar upload**:
   - Arrastrar `oversized.gpx`
   - ❌ **Esperado**: Error antes de enviar al servidor
   - ✅ Mensaje: "El archivo excede el tamaño máximo permitido (10 MB)"

**Criterio**: Error mostrado inmediatamente, sin llamada al backend

---

### Test 2: Archivo con formato inválido

1. **Intentar upload de archivo no-GPX**:
   ```bash
   # Crear archivo .txt y renombrar a .gpx
   echo "Esto no es XML" > test-gpx-files/fake.gpx
   ```

2. **Upload del archivo**:
   - Arrastrar `fake.gpx`
   - ❌ **Esperado**: Error del servidor
   - ✅ Mensaje español: "Error al procesar archivo GPX: formato inválido"

**Criterio**: Error manejado con mensaje claro en español

---

### Test 3: Subir GPX a viaje que ya tiene uno

1. **Preparación**:
   - Crear viaje nuevo
   - Subir `short_route.gpx`

2. **Intentar segundo upload**:
   - Refrescar página
   - ⚠️ Sección de upload debe estar **oculta**
   - ✅ Solo debe aparecer sección "Ruta GPS" con estadísticas

3. **Verificar via API** (opcional):
   ```bash
   # Intentar POST de segundo GPX
   curl -X POST http://localhost:8000/trips/{TRIP_ID}/gpx \
     -H "Authorization: Bearer {TOKEN}" \
     -F "file=@test-gpx-files/short_route.gpx"

   # Esperado: 400 Bad Request
   # Mensaje: "Este viaje ya tiene un archivo GPX asociado"
   ```

**Criterio**: UI previene múltiples uploads correctamente

---

## Checklist Final

### Funcionalidad Core ✅

- [ ] **T046**: Upload <1MB completa en <3s
- [ ] **T048**: Descarga de GPX original funciona
- [ ] **T049**: Eliminación en cascada verificada
- [ ] **T047**: Archivo >1MB retorna error esperado (501)

### UI/UX ✅

- [ ] Drag & drop funciona correctamente
- [ ] Barra de progreso visible durante upload
- [ ] Toast de éxito/error mostrados
- [ ] Sección GPX aparece automáticamente tras upload
- [ ] Sección upload desaparece si ya existe GPX
- [ ] Cards de estadísticas con colores correctos
- [ ] Responsive en móvil (opcional)

### Validaciones ✅

- [ ] Archivo >10MB rechazado con mensaje claro
- [ ] Archivo no-GPX rechazado con error descriptivo
- [ ] Solo un GPX por viaje (UI + backend)
- [ ] Owner-only: No-owners no ven botón de upload

### Performance ✅

- [ ] Upload <1MB: <3 segundos (SC-002)
- [ ] Sin crashes o errores de consola
- [ ] Memoria no aumenta significativamente

### Datos ✅

- [ ] Estadísticas correctas (distancia, elevación)
- [ ] Trackpoints simplificados (no 100% de puntos originales)
- [ ] Archivo original preservado para descarga
- [ ] Cascade deletion funciona

---

## Notas Finales

### Limitaciones Conocidas

1. **Async Processing**: Archivos >1MB retornan 501 Not Implemented
2. **Frontend Download Button**: No implementado aún (usar API directamente)
3. **Map Visualization**: Fase 4 (no incluido en User Story 1)

### Próximos Pasos

- **Fase 4**: Visualización en mapa interactivo
- **Fase 5**: Perfil de elevación con chart
- **Async processing**: Background tasks para archivos grandes

### Reportar Problemas

Si encuentras errores durante el testing manual:

1. **Captura de pantalla** del error
2. **Logs del backend** (terminal donde corre uvicorn)
3. **Consola del navegador** (F12 → Console)
4. **Pasos para reproducir**

**Formato de reporte**:
```
## Error en [Descripción]

**Pasos**:
1. ...
2. ...

**Esperado**: ...
**Actual**: ...

**Logs**: [adjuntar]
**Screenshot**: [adjuntar]
```

---

## Referencias

- **API Docs**: http://localhost:8000/docs
- **Contratos OpenAPI**: `specs/003-gps-routes/contracts/gpx-api.yaml`
- **Quickstart**: `specs/003-gps-routes/quickstart.md`
- **Tasks**: `specs/003-gps-routes/tasks.md`
