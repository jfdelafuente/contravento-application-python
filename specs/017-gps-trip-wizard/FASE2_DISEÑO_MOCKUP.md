# 🎨 Fase 2: Diseño Visual - Mapa en Paso 1

## 📊 Comparativa: Antes vs Después

### ANTES (Estado Actual - 5 Pasos)
```
┌─────────────────────────────────────────────────────┐
│ Paso 1: Upload GPX                                  │
│ ├─ Drag & Drop                                      │
│ ├─ Título Sugerido                                  │
│ └─ Telemetría (distancia, desnivel, altitudes)     │
├─────────────────────────────────────────────────────┤
│ Paso 2: Detalles del Viaje                         │
│ └─ Formulario (título, descripción, fechas)        │
├─────────────────────────────────────────────────────┤
│ Paso 3: Resumen de Ruta  ← ESTE PASO SE ELIMINA    │
│ ├─ Telemetría (repetida)                           │
│ └─ Mapa Preview (no interactivo)                   │
├─────────────────────────────────────────────────────┤
│ Paso 4: POIs                                        │
│ └─ Mapa Interactivo + Añadir POIs                  │
├─────────────────────────────────────────────────────┤
│ Paso 5: Review & Publish                           │
│ └─ Resumen Final + Publicar                        │
└─────────────────────────────────────────────────────┘
```

### DESPUÉS (Propuesta Fase 2 - 4 Pasos)
```
┌─────────────────────────────────────────────────────┐
│ Paso 1: Upload GPX + Análisis + MAPA ✨ NUEVO      │
│ ├─ Drag & Drop                                      │
│ ├─ Título Sugerido                                  │
│ ├─ Telemetría (distancia, desnivel, altitudes)     │
│ └─ MAPA PREVIEW (visualización inmediata) ← AQUÍ   │
├─────────────────────────────────────────────────────┤
│ Paso 2: Detalles del Viaje                         │
│ └─ Formulario (título, descripción, fechas)        │
├─────────────────────────────────────────────────────┤
│ Paso 3: POIs (antes era Paso 4)                    │
│ └─ Mapa Interactivo + Añadir POIs                  │
├─────────────────────────────────────────────────────┤
│ Paso 4: Review & Publish (antes era Paso 5)        │
│ └─ Resumen Final + Publicar                        │
└─────────────────────────────────────────────────────┘
```

---

## 🖼️ Mockup Detallado: Nuevo Paso 1

### Layout Visual

```
┌──────────────────────────────────────────────────────────────────┐
│                     CREAR VIAJE CON GPX                          │
│                                                                   │
│  Progreso: [████░░░░░░░░] 0%                                    │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────── PASO 1: SUBE TU ARCHIVO GPX ───────────────┐  │
│  │                                                             │  │
│  │  Selecciona un archivo GPX de tu recorrido en bicicleta.  │  │
│  │  Lo analizaremos automáticamente para obtener distancia,  │  │
│  │  elevación y dificultad.                                  │  │
│  │                                                             │  │
│  │  ┌────────────────────────────────────────────────────┐   │  │
│  │  │  📁  Macha_Cicloturista_Castillos...gpx  [X]       │   │  │
│  │  │      2.3 MB                                         │   │  │
│  │  └────────────────────────────────────────────────────┘   │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────── TÍTULO SUGERIDO ───────────────────────────┐  │
│  │                                                             │  │
│  │         Macha Cicloturista Castillos De Ayora             │  │
│  │                                                             │  │
│  │  Podrás editarlo en el siguiente paso                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────── INFORMACIÓN DEL RECORRIDO ─────────────────┐  │
│  │                                                             │  │
│  │  DISTANCIA                                                 │  │
│  │  ┌──────────────────────────────┐                         │  │
│  │  │ Distancia Total: 45.2 km     │                         │  │
│  │  └──────────────────────────────┘                         │  │
│  │                                                             │  │
│  │  DESNIVEL                                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐                  │  │
│  │  │ Positivo (+)   │  │ Negativo (-)   │                  │  │
│  │  │ 1,250 m        │  │ 1,100 m        │                  │  │
│  │  └────────────────┘  └────────────────┘                  │  │
│  │                                                             │  │
│  │  ALTITUDES                                                 │  │
│  │  ┌────────────────┐  ┌────────────────┐                  │  │
│  │  │ Máxima         │  │ Mínima         │                  │  │
│  │  │ 1,850 m        │  │ 450 m          │                  │  │
│  │  └────────────────┘  └────────────────┘                  │  │
│  │                                                             │  │
│  │  DIFICULTAD                                                │  │
│  │  ┌──────────────────────────────┐                         │  │
│  │  │ Nivel: Difícil 🔴            │                         │  │
│  │  └──────────────────────────────┘                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────── VISTA PREVIA DEL MAPA ✨ NUEVO ───────────┐  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                                                       │  │  │
│  │  │                    🗺️ MAPA                           │  │  │
│  │  │                                                       │  │  │
│  │  │         ╭─────────────────────────╮                 │  │  │
│  │  │         │ ●─────●────●────●────● │                 │  │  │
│  │  │         │   \  /  \  /  \  /      │                 │  │  │
│  │  │         │    ●    ●    ●          │                 │  │  │
│  │  │         │      \  /  \            │                 │  │  │
│  │  │         │       ●    ●            │                 │  │  │
│  │  │         │         \               │                 │  │  │
│  │  │         │          ●  (ruta)      │                 │  │  │
│  │  │         ╰─────────────────────────╯                 │  │  │
│  │  │                                                       │  │  │
│  │  │  [−] [+]  Zoom: 12  🔍                              │  │  │
│  │  │                                                       │  │  │
│  │  │  ℹ️ Vista preliminar de tu recorrido. Podrás        │  │  │
│  │  │     añadir puntos de interés en el Paso 3.          │  │  │
│  │  │                                                       │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  • Mapa NO interactivo (solo visualización)               │  │
│  │  • Muestra la ruta completa con zoom automático           │  │
│  │  • Tiles de OpenStreetMap                                 │  │
│  │  • Skeleton loader durante carga (~500ms)                 │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                                                             │  │
│  │  [← Cancelar]                           [Siguiente →]     │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📐 Especificaciones Técnicas

### Estructura de Componentes

```typescript
<Step1Upload>
  {/* Existing components */}
  <GPXWizardUploader />
  <SuggestedTitleCard />
  <TelemetrySkeleton />  {/* if loading */}

  {/* Telemetry Display */}
  <MetricGroup title="Distancia">
    <MetricCard label="Distancia Total" value="45.2 km" />
  </MetricGroup>

  <MetricGroup title="Desnivel">
    <MetricCard label="Positivo (+)" value="1,250 m" />
    <MetricCard label="Negativo (-)" value="1,100 m" />
  </MetricGroup>

  {/* ... more metrics ... */}

  {/* NEW: Map Preview Section */}
  <MapPreviewCard>
    <h3>Vista Previa del Mapa</h3>
    <MapContainer
      center={centerCoordinates}
      zoom={autoCalculatedZoom}
      interactive={false}  {/* KEY: No pan/zoom for user */}
      scrollWheelZoom={false}
      dragging={false}
      touchZoom={false}
      doubleClickZoom={false}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Polyline
        positions={trackpoints}
        color="#dc2626"  {/* Red route */}
        weight={4}
      />
    </MapContainer>
    <p className="map-preview-hint">
      ℹ️ Vista preliminar de tu recorrido. Podrás añadir puntos de
      interés en el Paso 3.
    </p>
  </MapPreviewCard>
</Step1Upload>
```

### CSS Classes Nuevas

```css
/* Map Preview Card */
.step1-upload__map-preview {
  background-color: #ffffff;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.step1-upload__map-preview-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 1rem 0;
  text-align: center;
}

.step1-upload__map-container {
  width: 100%;
  height: 400px;  /* Desktop */
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #cbd5e0;
}

.step1-upload__map-hint {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #eef2ff;
  border-left: 4px solid #667eea;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #4a5568;
  line-height: 1.5;
}

/* Responsive: Mobile */
@media (max-width: 768px) {
  .step1-upload__map-container {
    height: 300px;  /* Smaller on mobile */
  }
}

/* Loading State */
.step1-upload__map-skeleton {
  width: 100%;
  height: 400px;
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 8px;
}
```

---

## 🎯 Características del Mapa Preview

### Interactividad: NO (Solo Visualización)

| Característica | Paso 1 (Preview) | Paso 3 (POIs) |
|---------------|------------------|---------------|
| **Pan (arrastrar)** | ❌ No | ✅ Sí |
| **Zoom (rueda/pinch)** | ❌ No | ✅ Sí |
| **Click en mapa** | ❌ No | ✅ Sí (añadir POI) |
| **Drag markers** | ❌ No | ✅ Sí |
| **Visualizar ruta** | ✅ Sí | ✅ Sí |
| **Auto-fit bounds** | ✅ Sí | ✅ Sí |

**Razón**: En Paso 1 solo queremos que el usuario **vea** la ruta para confirmar que el GPX es correcto. La interacción completa viene en Paso 3 (POIs).

### Zoom Automático

```typescript
// Calculate bounds from trackpoints
const bounds = L.latLngBounds(
  trackpoints.map(tp => [tp.latitude, tp.longitude])
);

// Auto-fit with padding
map.fitBounds(bounds, {
  padding: [50, 50],  // 50px padding on all sides
  maxZoom: 13,        // Don't zoom too close
  animate: true,
  duration: 0.5
});
```

### Performance

- **Trackpoints simplificados**: Usa los mismos ~200-500 puntos del backend (RDP algorithm)
- **Tiles cacheadas**: OpenStreetMap con cache del navegador
- **Skeleton loader**: Muestra placeholder durante carga (~500ms)
- **Lazy rendering**: El mapa se renderiza solo cuando `telemetry` está disponible

---

## 🔄 Flujo de Usuario (Paso 1)

```
1. Usuario arrastra archivo GPX
   ↓
2. Backend analiza archivo (2-10s típico)
   ↓
3. Se muestra:
   ├─ Título Sugerido ✅
   ├─ Telemetría Completa ✅
   └─ MAPA PREVIEW ✨ NUEVO
   ↓
4. Usuario verifica visualmente:
   • "¿Es la ruta correcta?"
   • "¿Los datos se ven bien?"
   • "¿El título tiene sentido?"
   ↓
5. Hace clic en "Siguiente" → Paso 2
```

---

## 💡 Ventajas UX

### ✅ Pros

1. **Validación Visual Inmediata**
   - Usuario confirma que subió el GPX correcto al ver el mapa
   - Detecta errores (ruta equivocada) antes de rellenar formulario

2. **Reduce Pasos del Wizard**
   - De 5 pasos → 4 pasos (20% menos)
   - Elimina redundancia (telemetría repetida en Paso 3)

3. **Menor Carga Cognitiva**
   - Todo el análisis visual en un solo paso
   - Usuario no tiene que "recordar" cómo era la ruta

4. **Feedback Inmediato**
   - "¡Wow, mi ruta se ve genial!"
   - Aumenta confianza en el sistema

### ⚠️ Consideraciones

1. **Scroll Vertical Más Largo**
   - Solución: Diseño colapsable opcional (acordeón)
   - Orden: Mapa al final, después de métricas

2. **Carga Perceptual**
   - Solución: Skeleton loader para mapa
   - Animación de entrada suave (slideIn)

3. **Datos Móviles**
   - Solución: Tiles de OpenStreetMap son ligeras
   - ~50-100KB para vista típica

---

## 🆚 Alternativas Consideradas

### Opción A: Mapa Grande (Propuesta Actual)
```
[Uploader]
[Título]
[Telemetría]
[MAPA: 400px altura] ← PROPUESTA
```
**Pros**: Mapa muy visible, validación clara
**Contras**: Scroll largo

### Opción B: Mapa Pequeño (Thumbnail)
```
[Uploader]
[Título]
[Telemetría + MAPA: 200px al lado]
```
**Pros**: Compacto
**Contras**: Mapa demasiado pequeño, difícil de validar

### Opción C: Mapa Colapsable (Click para expandir)
```
[Uploader]
[Título]
[Telemetría]
[▶ Ver Mapa Preview] ← Click para expandir
```
**Pros**: Usuario controla cuándo ver
**Contras**: Paso extra, menos discoverability

### 🎯 Recomendación: Opción A (Mapa Grande)

**Razón**: El objetivo de Fase 2 es dar validación visual **inmediata**. Un mapa colapsado o pequeño derrota el propósito.

---

## 📱 Responsive Design

### Desktop (≥1024px)
```
┌─────────────────────────────────────────┐
│ [Telemetría en 2 columnas]              │
│                                          │
│ [Mapa: 100% ancho × 400px alto]        │
└─────────────────────────────────────────┘
```

### Tablet (768px - 1023px)
```
┌───────────────────────────────┐
│ [Telemetría en 1 columna]     │
│                                │
│ [Mapa: 100% × 350px]          │
└───────────────────────────────┘
```

### Mobile (<768px)
```
┌─────────────────────┐
│ [Telemetría stack]  │
│                      │
│ [Mapa: 100% × 300px]│
└─────────────────────┘
```

---

## 🚀 Plan de Implementación

Si apruebas este diseño, el plan sería:

### Fase 2A: Frontend (6-8 horas)
1. **T1**: Crear componente MapPreview (~2h)
   - Leaflet.js con interactividad deshabilitada
   - Auto-fit bounds
   - Skeleton loader

2. **T2**: Integrar en Step1Upload (~2h)
   - Añadir MapPreview después de telemetría
   - Pasar trackpoints desde telemetry
   - Manejar estado de carga

3. **T3**: CSS Responsive (~1h)
   - Estilos para map-preview-card
   - Breakpoints móvil/tablet/desktop
   - Hint text styling

4. **T4**: Eliminar Paso 3 actual (~1h)
   - Remover Step3Map component (obsoleto)
   - Ajustar numeración de pasos en wizard
   - Actualizar progress bar (4 pasos en lugar de 5)

5. **T5**: Testing (~2h)
   - Verificar en diferentes tamaños de pantalla
   - Probar con archivos grandes (performance)
   - Validar que mapa no es interactivo

### Fase 2B: Documentación (1-2 horas)
6. **T6**: Actualizar docs
   - Customer journey (custormer_jorney_gpx.md)
   - Especificaciones técnicas

---

## ❓ Preguntas para Decisión

Antes de implementar, necesito tu feedback en:

1. **¿Te gusta el diseño propuesto?** (Mapa grande, no colapsable)
2. **¿Altura del mapa OK?** (400px desktop / 300px móvil)
3. **¿Texto del hint correcto?** ("Vista preliminar... podrás añadir POIs en Paso 3")
4. **¿Algún ajuste visual que prefieras?**

---

## 📊 Resumen Ejecutivo

| Aspecto | Valor |
|---------|-------|
| **Reducción de pasos** | 5 → 4 (20% menos) |
| **Nuevo contenido Paso 1** | Mapa preview (no interactivo) |
| **Paso eliminado** | Paso 3 actual (Resumen de Ruta) |
| **Beneficio principal** | Validación visual inmediata |
| **Esfuerzo estimado** | 8-10 horas |
| **Riesgo** | 🟢 Bajo (cambio aislado) |

¿Qué te parece? ¿Aprobamos este diseño para implementar?

---

## ✅ IMPLEMENTACIÓN FINAL (Opción C - Implementada 2026-02-02)

### Decisión del Usuario

El usuario revisó las 3 opciones propuestas y seleccionó **Opción C**:

```
Opción C: Telemetría SOLO en Review (Step 4)
├─ Paso 1: Upload + Título Sugerido + MAPA Preview ✅
│  └─ Sin telemetría numérica (solo mapa)
├─ Paso 2: Detalles del Viaje ✅
├─ Paso 3: POIs (renumerado desde Paso 4) ✅
└─ Paso 4: Review & Publish con TELEMETRÍA COMPLETA ✅
   └─ Aquí se muestra toda la telemetría (distancia, desnivel, altitudes, dificultad)
```

### Cambios Implementados

#### Frontend

1. **Step1Upload.tsx** ✅
   - ❌ Removida telemetría (MetricGroup/MetricCard)
   - ✅ Añadido MapPreview component
   - ✅ Mantiene título sugerido
   - CSS actualizado (`.step1-upload__preview` en lugar de `.step1-upload__telemetry`)

2. **MapPreview.tsx** ✅ (NUEVO)
   - Componente de mapa estático (no interactivo)
   - Leaflet.js con interacciones deshabilitadas:
     - `dragging: false`
     - `touchZoom: false`
     - `scrollWheelZoom: false`
     - `zoomControl: false`
   - Altura: 400px (desktop), 300px (tablet), 250px (móvil)
   - Ruta trazada en naranja (#d35400)
   - Auto-fit bounds con padding de 20px

3. **MapPreview.css** ✅ (NUEVO)
   - Responsive design (768px, 480px breakpoints)
   - Dark mode support
   - Print styles

4. **GPXWizard.tsx** ✅
   - ❌ Eliminado Step3Map (Resumen de Ruta)
   - ✅ Renumerado pasos: 5 → 4
   - ✅ Step3POIs ahora es currentStep === 2
   - ✅ Step4Review ahora es currentStep === 3
   - ✅ Progress bar actualizado para 4 pasos

5. **useGPXWizard.ts** ✅
   - `TOTAL_STEPS` cambiado de 5 a 4
   - Comentarios actualizados

6. **Step4Review.tsx** ✅
   - ✅ Añadida telemetría completa con MetricGroup/MetricCard
   - Secciones:
     1. Detalles del Viaje
     2. Archivo GPX
     3. **Telemetría del Recorrido** (NUEVO)
        - Grupo Distancia (variant primary, size large)
        - Grupo Desnivel (variant success/default)
        - Grupo Altitudes
        - Grupo Dificultad (variant según nivel)
        - Mensaje "no elevation" si aplica
     4. Puntos de Interés (si hay POIs)

7. **Step3Review.css** ✅
   - Añadidos estilos para `.step3-review__no-elevation`

#### Tests

1. **GPXWizard.test.tsx** ✅
   - ❌ Eliminado mock de Step3Map
   - ✅ Actualizado flujo de navegación (4 pasos)
   - ✅ Eliminadas verificaciones de `step3-map`

2. **Step3Map.test.tsx** ❌ ELIMINADO
   - Archivo de test eliminado (componente obsoleto)

#### Archivos Eliminados

- ❌ `/frontend/src/components/trips/GPXWizard/Step3Map.tsx`
- ❌ `/frontend/tests/unit/Step3Map.test.tsx`

#### Documentación

1. **custormer_jorney_gpx.md** ✅
   - Tabla de pasos actualizada (5 → 4)
   - Sección "Optimizaciones Fase 2" añadida
   - Paso 1: Descripción actualizada (mapa preview, sin telemetría)
   - Paso 3: Eliminado "Resumen de Ruta"
   - Paso 3 (antes 4): POIs renumerado
   - Paso 4 (antes 5): Review con telemetría completa

2. **FASE2_DISEÑO_MOCKUP.md** ✅ (este archivo)
   - Añadida sección "IMPLEMENTACIÓN FINAL"

### Métricas de Implementación

| Métrica | Valor |
|---------|-------|
| **Pasos totales** | 4 (antes 5, reducción 20%) |
| **Archivos creados** | 2 (MapPreview.tsx, MapPreview.css) |
| **Archivos eliminados** | 2 (Step3Map.tsx, Step3Map.test.tsx) |
| **Archivos modificados** | 8 (Step1Upload, GPXWizard, Step4Review, tests, docs) |
| **Tiempo de implementación** | ~3 horas (estimado 8-10h, real más rápido) |
| **Tests actualizados** | ✅ Sí (GPXWizard.test.tsx) |
| **Documentación actualizada** | ✅ Sí (customer journey, design mockup) |

### Beneficios Confirmados

1. **UX Mejorada**:
   - Mapa preview inmediato en Paso 1 (orientación espacial)
   - Wizard más corto (4 pasos vs 5)
   - Telemetría completa en Review (validación final)
   - Menos clics para completar el wizard

2. **Performance**:
   - Mapa preview sin interacciones (más ligero)
   - Trackpoints simplificados (~200-500 puntos)
   - Skeleton loader para mejor percepción de velocidad

3. **Arquitectura**:
   - Componentes reutilizables (MetricGroup/MetricCard en Step4Review)
   - Separación de responsabilidades (MapPreview vs TripMap)
   - Código más limpio (eliminado Step3Map redundante)

### Estado Final

✅ **Fase 2 - Opción C implementada y funcional**

Wizard ahora tiene 4 pasos optimizados:
1. Upload + Título + Mapa Preview
2. Detalles del Viaje
3. POIs (mapa interactivo)
4. Review + Telemetría Completa + Publicar
