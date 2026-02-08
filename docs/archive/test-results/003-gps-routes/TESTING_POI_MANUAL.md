# Testing Manual - Feature 003 User Story 4: Points of Interest (POIs)

**Fecha**: 2026-01-26
**Feature**: Puntos de Interés en Rutas de Viaje
**Versión**: MVP - Funcionalidad básica CRUD

---

## 📋 Pre-requisitos

### 1. Backend Setup

```bash
cd backend

# Aplicar migración de POIs
poetry run alembic upgrade head

# Verificar que la migración se aplicó
poetry run alembic current
# Debe mostrar: eee2b0a9b8cc (head)

# Iniciar backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verificar backend está corriendo
# http://localhost:8000/docs
# Debe mostrar endpoint /trips/{trip_id}/pois
```

### 2. Frontend Setup

```bash
cd frontend

# Iniciar frontend
npm run dev

# Acceder a http://localhost:5173
```

### 3. Crear Datos de Prueba

Necesitas tener:
- ✅ Usuario registrado y verificado
- ✅ Al menos 1 viaje **publicado** (no draft) donde seas propietario
- ✅ El viaje debe tener ubicaciones o GPX (para ver el mapa)

**Crear viaje de prueba:**

```bash
# Opción 1: Usar la interfaz web
1. Login con tu usuario
2. Ir a "Crear Viaje"
3. Llenar título, descripción, fechas
4. Status: PUBLICADO (importante)
5. Añadir al menos 1 ubicación o subir GPX

# Opción 2: Usar script Python (rápido)
cd backend
poetry run python scripts/create_test_trip.py --user-id YOUR_USER_ID
```

---

## 🧪 Test Cases

### TC-001: Ver Botón "Añadir POI" (Solo Propietarios)

**Objetivo**: Verificar que el botón solo aparece para propietarios de viajes publicados

**Pasos:**

1. Login con tu usuario
2. Navegar a un viaje publicado tuyo: `http://localhost:5173/trips/{trip_id}`
3. Scroll hasta la sección de acciones (debajo del título)

**Resultado Esperado:**
```
✅ Debe aparecer botón "Añadir POI (0/20)"
✅ El botón debe estar habilitado (no grayed out)
✅ El contador debe mostrar "0/20" inicialmente
```

**Variaciones:**

- **Draft Trip**: Navega a un viaje tuyo en estado DRAFT
  - ❌ NO debe aparecer el botón "Añadir POI"

- **Trip de Otro Usuario**: Navega a un viaje de otro usuario
  - ❌ NO debe aparecer el botón "Añadir POI"

---

### TC-002: Flujo Completo - Añadir POI

**Objetivo**: Crear un POI desde cero haciendo click en el mapa

**Pasos:**

1. En un viaje publicado tuyo, click botón **"Añadir POI (0/20)"**
2. Verificar cambios visuales:
   - ✅ Botón cambia a **"Cancelar POI"** con estilo rojo
   - ✅ Botón "Editar ubicaciones" se deshabilita (grayed out)
   - ✅ Cursor sobre el mapa debe cambiar (indica modo de selección)

3. **Click en cualquier punto del mapa** (puede ser sobre la ruta o fuera de ella)

4. **Formulario POI debe aparecer** con:
   - ✅ Modal centrado con fondo oscuro con blur
   - ✅ Animación de entrada suave (slide up + fade in)
   - ✅ Header con título "Añadir POI"
   - ✅ Botón × de cierre (top-right)

5. **Verificar coordenadas pre-llenadas:**
   - ✅ Campo "Ubicación" con coordenadas del click (ej: `40.67641, -3.97087`)
   - ✅ Campo es read-only (fondo gris claro)

6. **Llenar formulario:**

   | Campo | Valor de Prueba | Validación |
   |-------|-----------------|------------|
   | **Nombre** | `Mirador del Valle` | ✅ Campo blanco con borde visible |
   | **Tipo** | `Mirador` (dropdown) | ✅ Dropdown con 6 opciones |
   | **Descripción** | `Un mirador impresionante con vistas...` | ✅ Textarea con min-height |

7. **Verificar contadores de caracteres:**
   - ✅ Nombre: `18/100 caracteres` (alineado a la derecha)
   - ✅ Descripción: `42/500 caracteres` (alineado a la derecha)

8. **Click en botón "Añadir POI"**

**Resultado Esperado:**

```
✅ Toast verde: "POI añadido correctamente"
✅ Formulario se cierra con animación
✅ Modo edición se desactiva (botón vuelve a "Añadir POI (1/20)")
✅ Marcador POI aparece en el mapa
✅ El marcador tiene:
   - Color azul (porque es tipo "Mirador")
   - Icono de binoculares (Font Awesome)
   - Forma de pin de ubicación
```

9. **Click en el marcador POI recién creado**

**Popup debe mostrar:**
```
┌─────────────────────────┐
│ [MIRADOR]               │ ← Badge azul con texto "MIRADOR"
│ Mirador del Valle       │ ← Título en bold
│ Un mirador impresion... │ ← Descripción truncada
│ ──────────────────────  │
│ [✏️ Editar] [🗑️ Eliminar]│ ← Botones de acción (solo propietario)
└─────────────────────────┘
```

---

### TC-003: Validaciones del Formulario

**Objetivo**: Verificar que las validaciones funcionan correctamente

#### 3.1. Nombre Vacío

**Pasos:**
1. Añadir POI
2. Click en mapa
3. Dejar campo "Nombre" vacío
4. Click "Añadir POI"

**Resultado:**
```
❌ Error: "El nombre es obligatorio"
❌ Formulario NO se cierra
❌ Campo "Nombre" debe tener borde rojo
```

#### 3.2. Nombre Muy Largo

**Pasos:**
1. Llenar nombre con 101 caracteres
2. Click "Añadir POI"

**Resultado:**
```
❌ Error: "El nombre debe tener máximo 100 caracteres"
❌ Contador muestra "101/100 caracteres" en rojo
```

#### 3.3. Descripción Muy Larga

**Pasos:**
1. Llenar descripción con 501 caracteres
2. Click "Añadir POI"

**Resultado:**
```
❌ Error: "La descripción debe tener máximo 500 caracteres"
❌ Contador muestra "501/500 caracteres" en rojo
```

---

### TC-004: Tipos de POI con Colores e Iconos

**Objetivo**: Verificar que cada tipo tiene su propio color e icono

**Pasos:**
Crear 6 POIs diferentes, uno de cada tipo:

| Tipo | Color Esperado | Icono Esperado | Posición en Mapa |
|------|----------------|----------------|-----------------|
| **Mirador** | Azul (#3b82f6) | fa-binoculars | Norte |
| **Pueblo** | Morado (#8b5cf6) | fa-house | Sur |
| **Fuente de agua** | Cian (#06b6d4) | fa-droplet | Este |
| **Alojamiento** | Ámbar (#f59e0b) | fa-bed | Oeste |
| **Restaurante** | Rojo (#ef4444) | fa-utensils | Centro |
| **Otro** | Gris (#6b7280) | fa-location-dot | Noreste |

**Resultado Esperado:**
```
✅ 6 marcadores visibles en el mapa
✅ Cada uno con color distintivo
✅ Al pasar el mouse, popup muestra badge con tipo correcto
✅ Botón contador muestra "Añadir POI (6/20)"
```

---

### TC-005: Editar POI Existente

**Objetivo**: Modificar un POI ya creado

**Pasos:**

1. Click en un marcador POI del mapa
2. En el popup, click botón **"✏️ Editar"**
3. **Formulario debe aparecer** con:
   - ✅ Título: "Editar POI" (no "Añadir POI")
   - ✅ Campos pre-llenados con datos actuales
   - ✅ NO hay campo "Ubicación" (las coordenadas no se pueden editar)

4. **Modificar datos:**
   - Cambiar nombre: `Mirador del Valle EDITADO`
   - Cambiar tipo: `Pueblo` (era Mirador)
   - Modificar descripción: `Descripción actualizada...`

5. Click **"Guardar cambios"**

**Resultado Esperado:**
```
✅ Toast verde: "POI actualizado correctamente"
✅ Formulario se cierra
✅ Marcador cambia de color (de azul a morado)
✅ Marcador cambia de icono (de binoculares a casa)
✅ Al abrir popup, muestra datos actualizados
```

---

### TC-006: Eliminar POI

**Objetivo**: Eliminar un POI del viaje

**Pasos:**

1. Click en marcador POI
2. En popup, click **"🗑️ Eliminar"**
3. **Confirmación nativa del navegador** aparece:
   ```
   ¿Eliminar este POI? Esta acción no se puede deshacer.
   [Cancelar] [Aceptar]
   ```

4. Click **"Cancelar"**

**Resultado:**
```
✅ POI NO se elimina
✅ Marcador sigue visible en mapa
✅ Contador sigue igual
```

5. Repetir pasos 1-2, ahora click **"Aceptar"**

**Resultado:**
```
✅ Toast verde: "POI eliminado correctamente"
✅ Marcador desaparece del mapa inmediatamente
✅ Contador decrementa: "Añadir POI (5/20)" → "Añadir POI (4/20)"
```

---

### TC-007: Límite de 20 POIs por Viaje

**Objetivo**: Verificar que no se pueden añadir más de 20 POIs

**Pasos:**

1. Añadir POIs hasta llegar a 20 (puede ser tedioso, mejor usar script)

```bash
# Script de ayuda (crear en backend/)
cd backend
poetry run python -c "
from src.services.poi_service import POIService
from src.database import async_session
import asyncio

async def add_20_pois():
    async with async_session() as db:
        service = POIService(db)
        for i in range(20):
            await service.create_poi(
                trip_id='YOUR_TRIP_ID',
                user_id='YOUR_USER_ID',
                data={
                    'name': f'POI Test {i+1}',
                    'poi_type': 'other',
                    'latitude': 40.0 + i*0.01,
                    'longitude': -3.0 + i*0.01,
                    'sequence': i
                }
            )
        await db.commit()

asyncio.run(add_20_pois())
"
```

2. Recargar página
3. Verificar botón **"Añadir POI (20/20)"**

**Resultado:**
```
✅ Botón está DESHABILITADO (grayed out)
✅ Tooltip al pasar mouse: "Máximo 20 POIs por viaje"
✅ Click en botón NO hace nada
✅ Mapa muestra 20 marcadores POI
```

4. Eliminar 1 POI
5. Botón debe habilitarse de nuevo: **"Añadir POI (19/20)"**

---

### TC-008: Cancelar Formulario

**Objetivo**: Verificar que cancelar limpia el estado correctamente

**Pasos:**

1. Click "Añadir POI (X/20)"
2. Click en mapa
3. Llenar parcialmente el formulario:
   - Nombre: `Test Cancelar`
   - NO llenar tipo ni descripción

4. **Opción A**: Click botón **"Cancelar"**
5. **Opción B**: Click botón **"✕"** (esquina superior derecha)
6. **Opción C**: Click fuera del modal (en el overlay oscuro)

**Resultado (cualquier opción):**
```
✅ Formulario se cierra con animación
✅ Modo "Añadir POI" se desactiva
✅ Botón vuelve a "Añadir POI (X/20)"
✅ Botón "Editar ubicaciones" se re-habilita
✅ NO se crea el POI en la base de datos
✅ Mapa vuelve a estado normal
```

7. Volver a abrir formulario (click "Añadir POI" → click mapa)

**Resultado:**
```
✅ Formulario aparece VACÍO (no tiene datos del intento anterior)
✅ Nombre: vacío
✅ Tipo: "Mirador" (valor por defecto)
✅ Descripción: vacío
```

---

### TC-009: Estética del Formulario (Mejoras Aplicadas)

**Objetivo**: Validar que las mejoras visuales se aplicaron correctamente

**Checklist Visual:**

#### Modal & Overlay
- ✅ Fondo oscuro con efecto blur (backdrop-filter)
- ✅ Modal centrado en desktop
- ✅ Modal desde abajo en mobile (<640px)
- ✅ Animación suave de entrada (slide + fade)
- ✅ Sombras en 3 capas para profundidad

#### Header
- ✅ Gradiente sutil de blanco a gris (#ffffff → #fafafa)
- ✅ Título en bold (700) con letter-spacing negativo
- ✅ Botón × con fondo gris al hover
- ✅ Tamaño 36x36px (buen target táctil)

#### Campos de Entrada
- ✅ **Fondo BLANCO** (no negro) - `background-color: #ffffff`
- ✅ **Texto oscuro legible** - `color: #1f2937`
- ✅ Bordes de 2px visibles (#e5e7eb)
- ✅ Border radius 8px (esquinas redondeadas)
- ✅ Padding generoso (12px 14px)
- ✅ Placeholder en gris claro (#9ca3af)
- ✅ Hover: borde se oscurece a #d1d5db
- ✅ Focus: borde azul (#3b82f6) + sombra azul suave
- ✅ Error: borde rojo + fondo rosa claro

#### Labels & Contadores
- ✅ Labels en bold (600) con color oscuro
- ✅ Asterisco rojo (⋆) para campos requeridos
- ✅ Contadores alineados a la derecha
- ✅ Contadores en gris (#9ca3af)

#### Coordenadas Display
- ✅ Gradiente de fondo (#f9fafb → #f3f4f6)
- ✅ Borde de 2px
- ✅ Fuente monospace con letter-spacing

#### Botones
- ✅ **Cancelar**: Fondo blanco, borde gris, hover con elevación
- ✅ **Añadir POI**: Gradiente azul (#3b82f6 → #2563eb)
- ✅ **Añadir POI hover**: Gradiente más oscuro + elevación + sombra "glow"
- ✅ Font weight bold (600)
- ✅ Padding 12px 24px
- ✅ Transiciones suaves (0.15s)

#### Mensajes de Error
- ✅ Gradiente rojo (#fef2f2 → #fee2e2)
- ✅ Borde izquierdo grueso (4px) en rojo
- ✅ Sombra con tinte rojo

---

### TC-010: POIs en Viajes Sin Ubicaciones (Solo GPX)

**Objetivo**: Verificar que POIs funcionan en viajes que solo tienen GPX (sin ubicaciones de texto)

**Pasos:**

1. Crear/navegar a un viaje que tenga:
   - ✅ GPX subido (ruta roja en mapa)
   - ❌ Sin ubicaciones de texto (locations = [])

2. Click "Añadir POI"
3. Click sobre la ruta GPX roja
4. Crear POI normalmente

**Resultado:**
```
✅ Formulario se abre correctamente
✅ Coordenadas se capturan del click
✅ POI se crea y aparece en el mapa
✅ El mapa muestra:
   - Ruta GPX en rojo
   - Marcador POI en su color correspondiente
   - NO hay marcadores azules numerados (locations)
```

---

### TC-011: Comportamiento en Mobile (<640px)

**Objetivo**: Validar responsive design en dispositivos móviles

**Pasos:**

1. Abrir DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Seleccionar "iPhone 12 Pro" o similar
4. Navegar a viaje publicado
5. Click "Añadir POI"
6. Click en mapa
7. Formulario debe aparecer

**Resultado Mobile:**
```
✅ Modal aparece desde ABAJO (no centrado)
✅ Animación: slide up desde 100% translateY
✅ Modal ocupa ancho completo (100vw)
✅ Border radius solo arriba (16px 16px 0 0)
✅ Botones apilados verticalmente
✅ Orden: [Añadir POI] arriba, [Cancelar] abajo
✅ Botones full-width
✅ Padding reducido (20px vs 28px desktop)
```

**Interacción táctil:**
- ✅ Swipe down sobre modal NO cierra (requiere click ✕)
- ✅ Tap fuera del modal (en overlay) SÍ cierra
- ✅ Inputs tienen font-size 16px (previene zoom en iOS)
- ✅ Botones tienen min-height 48px (iOS guidelines)

---

### TC-012: Persistencia de Datos

**Objetivo**: Verificar que POIs se guardan correctamente en la base de datos

**Pasos:**

1. Crear 3 POIs en un viaje
2. Anotar nombres: `POI 1`, `POI 2`, `POI 3`
3. **Recargar la página** (F5)

**Resultado:**
```
✅ Los 3 marcadores POI siguen en el mapa
✅ Posiciones exactamente iguales
✅ Colores e iconos correctos
✅ Popups con datos correctos
✅ Contador muestra "Añadir POI (3/20)"
```

4. **Cerrar navegador completamente**
5. Volver a abrir y navegar al mismo viaje

**Resultado:**
```
✅ Los 3 POIs persisten
✅ Datos intactos
```

6. **Verificar en base de datos** (opcional):

```bash
cd backend
poetry run python -c "
from src.database import sync_session
from src.models.poi import PointOfInterest

with sync_session() as db:
    pois = db.query(PointOfInterest).filter_by(trip_id='YOUR_TRIP_ID').all()
    for poi in pois:
        print(f'{poi.name} - {poi.poi_type} - ({poi.latitude}, {poi.longitude})')
"
```

---

### TC-013: Errores del Backend

**Objetivo**: Verificar manejo de errores del servidor

#### 13.1. Viaje No Publicado (400)

**Pasos:**
1. Cambiar trip status a DRAFT en la base de datos
2. Intentar añadir POI

**Resultado:**
```
❌ Toast rojo: "Solo se pueden añadir POIs a viajes publicados"
❌ POI NO se crea
```

#### 13.2. Usuario No Propietario (403)

**Pasos:**
1. Login con usuario diferente
2. Intentar añadir POI al viaje de otro usuario (usando API directamente)

```bash
curl -X POST http://localhost:8000/trips/TRIP_ID/pois \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "POI Hack",
    "poi_type": "other",
    "latitude": 40.0,
    "longitude": -3.0,
    "sequence": 0
  }'
```

**Resultado:**
```
❌ HTTP 403 Forbidden
❌ Error: "No tienes permiso para modificar este viaje"
```

#### 13.3. Viaje No Existe (404)

**Pasos:**
1. Navegar a trip_id inexistente: `/trips/00000000-0000-0000-0000-000000000000`

**Resultado:**
```
❌ Página de error: "Viaje no encontrado"
❌ No hay botón "Añadir POI" visible
```

---

### TC-014: Compatibilidad de Navegadores

**Objetivo**: Validar en diferentes navegadores

| Navegador | Versión Mínima | Estado |
|-----------|----------------|--------|
| Chrome | 90+ | ✅ DEBE FUNCIONAR |
| Firefox | 88+ | ✅ DEBE FUNCIONAR |
| Safari | 14+ | ✅ DEBE FUNCIONAR |
| Edge | 90+ | ✅ DEBE FUNCIONAR |
| Opera | 76+ | ✅ DEBE FUNCIONAR |

**Verificar en cada navegador:**
- ✅ Formulario se renderiza correctamente
- ✅ Inputs son editables con fondo blanco
- ✅ Animaciones funcionan suavemente
- ✅ Backdrop-filter blur se aplica (puede no funcionar en Firefox antiguo)
- ✅ Click en mapa captura coordenadas
- ✅ Toast notifications aparecen

---

## 📊 Resumen de Validación

### Funcionalidad Core

| Test Case | Descripción | Estado |
|-----------|-------------|--------|
| TC-001 | Botón solo para propietarios | ⬜ |
| TC-002 | Flujo completo añadir POI | ⬜ |
| TC-003 | Validaciones formulario | ⬜ |
| TC-004 | 6 tipos con colores/iconos | ⬜ |
| TC-005 | Editar POI existente | ⬜ |
| TC-006 | Eliminar POI con confirmación | ⬜ |
| TC-007 | Límite 20 POIs por viaje | ⬜ |
| TC-008 | Cancelar formulario | ⬜ |

### UX/UI

| Test Case | Descripción | Estado |
|-----------|-------------|--------|
| TC-009 | Estética formulario mejorada | ⬜ |
| TC-010 | POIs en viajes solo-GPX | ⬜ |
| TC-011 | Responsive mobile | ⬜ |
| TC-012 | Persistencia de datos | ⬜ |

### Seguridad

| Test Case | Descripción | Estado |
|-----------|-------------|--------|
| TC-013.1 | Error: Viaje no publicado | ⬜ |
| TC-013.2 | Error: No propietario | ⬜ |
| TC-013.3 | Error: Viaje no existe | ⬜ |

### Cross-Browser

| Navegador | Estado |
|-----------|--------|
| Chrome | ⬜ |
| Firefox | ⬜ |
| Safari | ⬜ |
| Edge | ⬜ |

---

## 🐛 Registro de Bugs

Si encuentras problemas durante el testing, documéntalos aquí:

### Bug Template

```markdown
**Bug ID**: POI-BUG-001
**Título**: [Descripción breve del problema]
**Severidad**: 🔴 Crítico / 🟡 Moderado / 🟢 Menor
**Pasos para Reproducir**:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Resultado Actual**: [Qué pasa]
**Resultado Esperado**: [Qué debería pasar]
**Captura de Pantalla**: [Si aplica]
**Navegador**: [Chrome 120, Firefox 115, etc.]
**Consola del Navegador**: [Errores en consola, si hay]
```

---

## ✅ Criterios de Aceptación Final

La feature se considera **COMPLETA** cuando:

- [x] ✅ Todos los test cases (TC-001 a TC-014) pasan
- [ ] ✅ No hay bugs críticos abiertos
- [ ] ✅ Performance: Crear POI < 1s
- [ ] ✅ Performance: Cargar 20 POIs en mapa < 2s
- [ ] ✅ UI: Formulario legible en todos los navegadores
- [ ] ✅ Mobile: Funciona correctamente en iOS y Android
- [ ] ✅ Accesibilidad: Navegable con teclado (Tab, Enter, Esc)

---

## 📝 Notas del Testing

**Fecha de Testing**: ___________
**Tester**: ___________
**Entorno**: ___________

**Resultados Generales**:
- Total Test Cases: 14
- Pasados: ____ / 14
- Fallidos: ____ / 14
- Bloqueados: ____ / 14

**Observaciones**:
[Notas adicionales del testing]

---

## 🚀 Siguiente Paso

Una vez completado el testing manual:

1. ✅ Marcar todos los test cases como pasados/fallidos
2. 📝 Documentar bugs encontrados
3. 🐛 Corregir bugs críticos y moderados
4. 🔄 Re-testear casos fallidos
5. ✅ Dar feature como COMPLETADA
6. 🎉 Deploy a staging/production

**Feature 003 - User Story 4: Points of Interest** - Estado: TESTING IN PROGRESS
