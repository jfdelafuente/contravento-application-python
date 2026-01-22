# Análisis: Integración de GPX en Flujo de Creación de Viajes

**Fecha de análisis**: 2026-01-22
**Branch**: `003-gps-routes` (activa)
**Solicitud**: Integrar carga de GPX en el wizard de creación de viajes
**Estado actual**: GPX se carga DESPUÉS de crear viaje (TripDetailPage)

---

## 📊 Resumen Ejecutivo

### Situación Actual

El flujo actual de ContraVento separa la creación de viajes (Feature 002 - Travel Diary) de la carga de archivos GPX (Feature 003 - GPS Routes):

**Wizard de Creación de Viajes** (4 pasos):
- Step 1: Información básica (título, fechas, distancia, dificultad, ubicaciones)
- Step 2: Historia y tags (descripción, tags)
- Step 3: Fotos (selección de fotos para subir)
- Step 4: Revisión y publicación (guardar como DRAFT o publicar)

**Carga de GPX** (separada):
- Se realiza en TripDetailPage DESPUÉS de crear el viaje
- Componente `GPXUploader` visible solo para owner si trip NO tiene GPX
- Restricción: 1 GPX máximo por trip

### Constraint Técnico Crítico

**El endpoint de GPX requiere `trip_id` existente**:

```python
POST /trips/{trip_id}/gpx
```

Esto significa que el trip **DEBE** ser creado primero en la base de datos antes de poder subir el GPX. No es posible subir GPX durante la creación del viaje a menos que se reestructure el flujo.

---

## 🔍 Análisis de Implicaciones

### 1. Implicaciones Técnicas Backend

#### 1.1 Restricción de Foreign Key

```python
# backend/src/models/gpx.py línea 40-45
trip_id = Column(
    String(36),
    ForeignKey("trips.trip_id", ondelete="CASCADE"),
    unique=True,      # ← Solo 1 GPX por trip
    nullable=False,   # ← trip_id es obligatorio
)
```

**Implicación**: No se puede crear un GPXFile sin un trip_id válido que ya exista en la tabla `trips`.

#### 1.2 Validación de Ownership

```python
# backend/src/api/trips.py línea 1185-1196
trip = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
trip = trip.scalar_one_or_none()

if trip.user_id != current_user.id:
    raise HTTPException(403, "No tienes permiso para subir GPX a este viaje")
```

**Implicación**: El user debe ser propietario del trip para subir GPX.

#### 1.3 Procesamiento de GPX

**Archivos <1MB** (procesamiento sincrónico):
- Parse con gpxpy
- Simplificación Douglas-Peucker (reducción 80-90%)
- Cálculo de estadísticas (distancia, elevación)
- Creación de GPXFile + TrackPoints
- Retorna 201 Created con datos completos
- Tiempo: <3 segundos

**Archivos >1MB** (procesamiento asincrónico):
- **NOTA**: Aún NO implementado (retorna 501 Not Implemented)
- Plan: BackgroundTasks de FastAPI
- Polling cada 2s hasta completar
- Máximo espera: 30 segundos

### 2. Implicaciones Técnicas Frontend

#### 2.1 Flujo Actual de Creación de Viajes

```typescript
// TripFormWizard - 4 pasos
const handleSubmit = async (data: TripCreateInput, isDraft: boolean) => {
  // 1. Crear trip (POST /trips)
  const trip = await createTrip(sanitizedData);

  // 2. Subir fotos (POST /trips/{trip_id}/photos × N)
  for (const photo of selectedPhotos) {
    await uploadTripPhoto(trip.trip_id, photo.file);
  }

  // 3. Publicar si no es borrador (POST /trips/{trip_id}/publish)
  if (!isDraft) {
    await publishTrip(trip.trip_id);
  }

  // 4. Navegar a detail page
  navigate(`/trips/${trip.trip_id}`);
};
```

**Momento crítico**: Las fotos se suben DESPUÉS de crear el trip, no durante el wizard. El wizard solo las prepara en memoria.

#### 2.2 Componente GPXUploader

```typescript
// TripDetailPage.tsx - Condiciones de visibilidad
{isOwner && !trip.gpx_file && (
  <GPXUploader
    tripId={trip.trip_id}  // ← Requiere trip_id existente
    onUploadComplete={() => {
      fetchTrip();  // Refresh trip data
    }}
  />
)}
```

**Restricciones**:
- Solo visible si user es owner
- Solo visible si trip NO tiene GPX (restricción 1 GPX/trip)
- Requiere `trip_id` para funcionar

### 3. Implicaciones de UX

#### 3.1 Flujo Actual (GPX en TripDetailPage)

**Ventajas**:
- ✅ Desacoplamiento: GPX es completamente opcional
- ✅ Simplicidad: User crea trip sin pensar en GPX
- ✅ Flexibilidad: Puede agregar GPX en cualquier momento después
- ✅ Menos presión: No alargar wizard de creación
- ✅ Coherencia: Fotos también se suben después del wizard

**Desventajas**:
- ❌ Fragmentación: User debe ir a detail page para subir GPX
- ❌ Dos pasos: Crear trip → ir a detail → subir GPX
- ❌ Falta de discoveryability: User puede no saber que puede subir GPX

#### 3.2 Flujo Propuesto (GPX en Wizard)

**Ventajas**:
- ✅ Todo en un lugar: User completa todo en un flujo
- ✅ Inmediatez: GPX disponible al crear trip
- ✅ Mejor onboarding: User sabe desde el inicio que puede subir GPX

**Desventajas**:
- ❌ Complejidad del wizard: De 4 a 5 pasos (o Step 3 más cargado)
- ❌ Riesgo de abandono: Wizard más largo puede desmotivar
- ❌ Manejo de errores complejo: ¿Qué pasa si GPX falla pero trip ya se creó?
- ❌ Inconsistencia: Fotos se suben después, pero GPX durante wizard

---

## 💡 Alternativas de Desarrollo

### Alternativa A: Post-Creation Modal (RECOMENDADO)

**Descripción**: Después de crear el trip con éxito, mostrar un modal preguntando si quiere subir GPX ahora.

**Flujo**:

```
1. User completa wizard de 4 pasos
2. Trip se crea como DRAFT o PUBLISHED
3. Modal aparece: "¿Deseas agregar una ruta GPX a tu viaje?"
   - Botón: "Sí, subir ahora" → Abre GPXUploader en modal
   - Botón: "No, después" → Ir a TripDetailPage
4. Si user sube GPX: espera procesamiento → navega a detail page
5. Si user cancela: navega directo a detail page
```

**Implementación**:

**Frontend** - Crear `PostCreationGPXModal.tsx`:

```typescript
interface PostCreationGPXModalProps {
  tripId: string;
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const PostCreationGPXModal: React.FC<PostCreationGPXModalProps> = ({
  tripId,
  isOpen,
  onClose,
  onComplete
}) => {
  const [uploadStarted, setUploadStarted] = useState(false);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <h2>¿Agregar ruta GPX?</h2>
      <p>Puedes subir un archivo GPX con la ruta de tu viaje para visualizarla en el mapa.</p>

      {!uploadStarted ? (
        <>
          <button onClick={() => setUploadStarted(true)}>Sí, subir ahora</button>
          <button onClick={onClose}>No, lo haré después</button>
        </>
      ) : (
        <GPXUploader
          tripId={tripId}
          onUploadComplete={() => {
            onComplete();
            onClose();
          }}
        />
      )}
    </Modal>
  );
};
```

**Modificar `useTripForm.ts`**:

```typescript
const handleSubmit = async (data, isDraft, photos) => {
  // 1. Create trip
  const trip = await createTrip(data);

  // 2. Upload photos
  // ...

  // 3. Publish if needed
  // ...

  // 4. Show GPX modal INSTEAD of immediate navigation
  setShowGPXModal(true);
  setCreatedTripId(trip.trip_id);
};

const handleGPXModalClose = () => {
  setShowGPXModal(false);
  navigate(`/trips/${createdTripId}`);
};
```

**Ventajas**:
- ✅ Mínimo cambio en flujo existente
- ✅ No alarga wizard (sigue siendo 4 pasos)
- ✅ User tiene opción inmediata de subir GPX
- ✅ Fácil de implementar (1 componente nuevo)
- ✅ Opcional: User puede ignorar modal y subir después

**Desventajas**:
- ⚠️ Modal puede ser percibido como intrusivo
- ⚠️ Requiere manejo de estado adicional (showGPXModal)

**Estimación**: 2-3 horas

---

### Alternativa B: Nuevo Step 4 en Wizard (GPX)

**Descripción**: Agregar un quinto paso al wizard dedicado exclusivamente a GPX.

**Flujo**:

```
Step 1: Información básica
Step 2: Historia y tags
Step 3: Fotos
Step 4: Ruta GPX (NUEVO) ← Opcional
Step 5: Revisión y publicación (antes Step 4)
```

**Implementación**:

**Frontend** - Crear `Step4GPX.tsx`:

```typescript
const Step4GPX: React.FC = () => {
  const { watch, setValue } = useFormContext<TripCreateInput>();
  const gpxFile = watch('gpxFile');

  return (
    <div>
      <h3>Ruta GPS (Opcional)</h3>
      <p>Sube un archivo GPX con la ruta de tu viaje</p>

      <input
        type="file"
        accept=".gpx"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            setValue('gpxFile', file);
          }
        }}
      />

      {gpxFile && (
        <div>
          <p>Archivo seleccionado: {gpxFile.name}</p>
          <button onClick={() => setValue('gpxFile', null)}>Eliminar</button>
        </div>
      )}

      <button onClick={handleNext}>
        {gpxFile ? 'Continuar con archivo' : 'Omitir (subir después)'}
      </button>
    </div>
  );
};
```

**Modificar `TripFormWizard.tsx`**:

```typescript
const steps = [
  <Step1BasicInfo />,
  <Step2StoryTags />,
  <Step3Photos />,
  <Step4GPX />,      // ← NUEVO
  <Step5Review />,   // ← Antes era Step4
];

const STEP_LABELS = [
  'Información',
  'Historia',
  'Fotos',
  'Ruta GPS',        // ← NUEVO
  'Revisión',
];
```

**Modificar `useTripForm.ts` - Subir GPX DESPUÉS de crear trip**:

```typescript
const handleSubmit = async (data, isDraft, photos, gpxFile?) => {
  // 1. Create trip (debe ser primero para obtener trip_id)
  const trip = await createTrip(data);

  // 2. Upload photos
  for (const photo of photos) {
    await uploadTripPhoto(trip.trip_id, photo.file);
  }

  // 3. Upload GPX if provided (NUEVO)
  if (gpxFile) {
    try {
      await uploadGPX(trip.trip_id, gpxFile);
      toast.success('Archivo GPX procesado correctamente');
    } catch (error) {
      toast.error('Error al procesar GPX. Puedes subirlo después desde la página del viaje.');
      // Continuar sin bloquear la creación del trip
    }
  }

  // 4. Publish if needed
  if (!isDraft) {
    await publishTrip(trip.trip_id);
  }

  // 5. Navigate
  navigate(`/trips/${trip.trip_id}`);
};
```

**Backend**: Sin cambios necesarios (endpoints ya existen)

**Ventajas**:
- ✅ Integración natural en el flujo de creación
- ✅ User ve GPX como parte del proceso
- ✅ Consistente con Step 3 (ambos preparan archivos)
- ✅ Opcional: User puede omitir el paso

**Desventajas**:
- ❌ Alarga wizard (de 4 a 5 pasos)
- ❌ Requiere refactorización significativa del wizard
- ❌ Renumerar todos los steps (Step4 → Step5)
- ❌ Manejo de errores: Si GPX falla, trip ya fue creado
- ❌ Riesgo de abandono: Wizard más largo

**Estimación**: 6-8 horas

---

### Alternativa C: Sección GPX en Step 3 (Fotos + GPX)

**Descripción**: Integrar GPX en el Step 3 existente junto con las fotos.

**Flujo**:

```
Step 3: Archivos
  - Sección: Fotos (actual)
  - Sección: Ruta GPX (nueva)
```

**Implementación**:

**Frontend** - Modificar `Step3Photos.tsx` → `Step3MediaFiles.tsx`:

```typescript
const Step3MediaFiles: React.FC = () => {
  const { setValue, watch } = useFormContext<TripCreateInput>();
  const [photos, setPhotos] = useState<PhotoPreview[]>([]);
  const [gpxFile, setGPXFile] = useState<File | null>(null);

  return (
    <div>
      {/* Sección Fotos (existente) */}
      <section>
        <h3>Fotos del viaje</h3>
        <PhotoDropzone onPhotosSelected={setPhotos} />
        {/* ... resto del código de fotos ... */}
      </section>

      {/* Sección GPX (nueva) */}
      <section>
        <h3>Ruta GPS (Opcional)</h3>
        <input
          type="file"
          accept=".gpx"
          onChange={(e) => {
            const file = e.target.files?.[0];
            setGPXFile(file || null);
            setValue('gpxFile', file || null);
          }}
        />
        {gpxFile && <p>Archivo: {gpxFile.name}</p>}
      </section>
    </div>
  );
};
```

**Modificar schema de form**:

```typescript
// frontend/src/schemas/tripSchema.ts
export const tripFormSchema = z.object({
  // ... campos existentes ...
  selectedPhotos: z.array(photoPreviewSchema).max(20).optional(),
  gpxFile: z.instanceof(File).optional(),  // ← NUEVO
});
```

**Ventajas**:
- ✅ No alarga wizard (sigue siendo 4 pasos)
- ✅ Menos refactorización (solo modificar Step 3)
- ✅ Fotos y GPX juntos (ambos son "archivos del viaje")

**Desventajas**:
- ❌ Step 3 se vuelve muy cargado (fotos + GPX)
- ❌ Puede confundir: ¿Por qué fotos y GPX juntos?
- ❌ Manejo de errores complejo en un solo paso

**Estimación**: 4-5 horas

---

### Alternativa D: Mantener Estado Actual (Sin Cambios)

**Descripción**: No integrar GPX en el wizard. Mantener la separación actual.

**Justificación**:

1. **Arquitectura clara**: Feature 002 (Travel Diary) vs Feature 003 (GPS Routes)
2. **Simplicidad UX**: User crea trip sin pensar en GPX
3. **Opcionabilidad**: GPX es completamente opcional (no todos los trips tienen GPX)
4. **Consistencia con fotos**: Fotos también se suben DESPUÉS del wizard
5. **Menos manejo de errores**: Si GPX falla, no afecta creación del trip

**Mejora sugerida**: Mejorar discoveryability en TripDetailPage

**Frontend** - Agregar banner informativo si trip NO tiene GPX:

```typescript
// TripDetailPage.tsx
{isOwner && !trip.gpx_file && (
  <div className="gpx-prompt-banner">
    <Icon name="route" />
    <div>
      <h4>¿Tienes la ruta GPS de este viaje?</h4>
      <p>Sube un archivo GPX para visualizar la ruta en el mapa y ver estadísticas de elevación.</p>
    </div>
    <button onClick={() => scrollToGPXUploader()}>Subir GPX</button>
  </div>
)}

{/* GPXUploader más abajo en la página */}
<section id="gpx-uploader">
  <GPXUploader tripId={trip.trip_id} />
</section>
```

**Ventajas**:
- ✅ Cero desarrollo adicional
- ✅ Mantiene arquitectura clara
- ✅ No riesgo de regresiones
- ✅ Flujo ya funciona correctamente

**Desventajas**:
- ❌ No cumple con la solicitud del usuario
- ❌ GPX sigue estando "escondido" en detail page

**Estimación**: 1 hora (solo banner informativo)

---

## 📊 Comparativa de Alternativas

| Criterio | A: Modal | B: Step 4 | C: En Step 3 | D: Sin Cambios |
|----------|----------|-----------|--------------|----------------|
| **Complejidad desarrollo** | Baja | Alta | Media | Muy Baja |
| **Impacto en UX** | Medio | Alto | Medio | Bajo |
| **Riesgo de regresión** | Bajo | Alto | Medio | Ninguno |
| **Alarga wizard** | No | Sí (+1 step) | No | No |
| **Manejo de errores** | Simple | Complejo | Medio | N/A |
| **Estimación tiempo** | 2-3h | 6-8h | 4-5h | 1h |
| **Descubribilidad GPX** | Alta | Muy Alta | Alta | Baja |
| **Opcionabilidad** | ✅ Clara | ✅ Clara | ✅ Clara | ✅ Clara |
| **Consistencia arquitectura** | ✅ | ⚠️ | ⚠️ | ✅ |

**Leyenda**:
- ✅ Bueno
- ⚠️ Aceptable con cuidado
- ❌ Problemático

---

## 🎯 Recomendación Final

### Opción Recomendada: **Alternativa A - Post-Creation Modal**

**Razones**:

1. **Balance UX/Complejidad**: Ofrece la oportunidad de subir GPX inmediatamente sin alargar el wizard
2. **Bajo riesgo**: Cambios mínimos en código existente
3. **Opcional pero visible**: User ve la opción sin estar obligado
4. **Consistencia**: Mantiene separación entre creación de trip y upload de archivos
5. **Manejo de errores simple**: Si GPX falla, user puede intentar después

### Plan de Implementación (Alternativa A)

**Archivos a crear**:

1. `frontend/src/components/trips/PostCreationGPXModal.tsx` (nuevo)
   - Modal con dos opciones: "Subir ahora" o "Después"
   - Integra componente GPXUploader existente
   - Maneja loading states y errores

**Archivos a modificar**:

2. `frontend/src/hooks/useTripForm.ts`
   - Agregar estado: `showGPXModal`, `createdTripId`
   - Modificar `handleSubmit`: mostrar modal en lugar de navegar directo
   - Agregar `handleGPXModalClose`: navegar a detail page al cerrar

3. `frontend/src/pages/TripCreatePage.tsx` (o donde esté el wizard)
   - Importar y renderizar `PostCreationGPXModal`
   - Pasar props: `tripId`, `isOpen`, `onClose`

4. `frontend/src/types/trip.ts` (opcional)
   - Agregar tipo: `PostCreationGPXModalProps`

**Backend**: Sin cambios (endpoints ya implementados)

### Flujo Técnico Detallado

```
1. User completa wizard (4 pasos actuales)
   ↓
2. Click "Guardar Borrador" o "Publicar"
   ↓
3. useTripForm.handleSubmit():
   a. POST /trips → trip creado
   b. POST /trips/{id}/photos × N → fotos subidas
   c. POST /trips/{id}/publish → publicado (si corresponde)
   d. setShowGPXModal(true) → mostrar modal
   e. setCreatedTripId(trip.trip_id) → guardar trip_id
   ↓
4. PostCreationGPXModal renderiza:
   - Opción 1: "Sí, subir ahora"
     → Muestra GPXUploader en modal
     → User drag-drop archivo .gpx
     → POST /trips/{id}/gpx
     → Polling si async (>1MB)
     → Al completar: onClose → navigate

   - Opción 2: "No, después"
     → onClose → navigate directo
   ↓
5. Navigate a /trips/{trip_id}
   ↓
6. TripDetailPage muestra:
   - Trip con o sin GPX (dependiendo de elección user)
   - Si no tiene GPX: GPXUploader visible (puede intentar de nuevo)
```

### Verificación End-to-End

**Caso 1: User sube GPX en modal**:

```bash
# 1. Completar wizard → Modal aparece
# 2. Click "Sí, subir ahora"
# 3. Drag-drop archivo short_route.gpx (50KB)
# 4. Esperar procesamiento (<3s)
# 5. Ver toast: "Archivo GPX procesado correctamente"
# 6. Modal se cierra automáticamente
# 7. Redirect a TripDetailPage
# 8. Verificar: GPXStats visible, mapa con track
```

**Caso 2: User omite modal**:

```bash
# 1. Completar wizard → Modal aparece
# 2. Click "No, lo haré después"
# 3. Redirect inmediato a TripDetailPage
# 4. Verificar: GPXUploader visible (sin GPX cargado)
# 5. User puede subir GPX manualmente desde detail page
```

**Caso 3: Error en upload de GPX**:

```bash
# 1. Modal → "Sí, subir ahora"
# 2. Drag-drop archivo inválido (oversized o corrupto)
# 3. Ver toast error: "Error al procesar GPX..."
# 4. Modal permanece abierto
# 5. Opciones: Intentar otro archivo o cerrar modal
# 6. Si cierra: redirect a detail page (puede reintentar desde ahí)
```

---

## 🚀 Siguiente Acción

**Decisión requerida del usuario**:

¿Cuál de las 4 alternativas prefieres implementar?

- **A: Post-Creation Modal** (recomendado - 2-3h)
- **B: Nuevo Step 4 GPX** (más integrado - 6-8h)
- **C: GPX en Step 3** (menos pasos - 4-5h)
- **D: Sin cambios** (mejorar discoveryability - 1h)

O si tienes una alternativa diferente en mente, podemos diseñarla.
