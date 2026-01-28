# API Testing Documentation

Documentación para testing manual de la API de ContraVento.

## Guías Disponibles

### [MANUAL_TESTING.md](MANUAL_TESTING.md)
Guía completa de testing manual con comandos `curl`.

**Contenido:**
- Prerequisitos y configuración inicial
- Endpoints de Trip CRUD (crear, obtener, publicar)
- Endpoints de Photo Management (upload, reorder, delete)
- Casos de prueba completos con scripts bash
- Validación de permisos y errores
- Troubleshooting y referencia rápida

**Ideal para:**
- Testing desde terminal/línea de comandos
- CI/CD pipelines
- Debugging rápido
- Scripts de automatización

---

### [POSTMAN_COLLECTION.md](POSTMAN_COLLECTION.md)
Guía para usar Postman/Insomnia con la API.

**Contenido:**
- Configuración de colección y environment variables
- Auto-update scripts para tokens y IDs
- Colección JSON completa lista para importar
- Flujo de testing paso a paso
- Tests de validación incluidos
- Tips para testing eficiente

**Ideal para:**
- Testing interactivo con GUI
- Exploración de la API
- Colaboración en equipo
- Documentación visual

---

### [TAGS_TESTING.md](TAGS_TESTING.md)

Guía de testing manual para tags y categorización. ⭐ NUEVO

**Contenido:**

- Endpoints de tags y filtrado de viajes
- Casos de prueba de filtrado por tag (case-insensitive)
- Filtrado por status (DRAFT vs PUBLISHED)
- Filtros combinados (tag + status)
- Paginación (limit/offset)
- Script automatizado de testing

**Ideal para:**

- Validar funcionalidad de tags
- Testing de filtros y búsquedas
- Verificar case-insensitivity
- Probar paginación

---

## Features Documentadas

### Travel Diary - Trip Management (v0.4.0)

**Trip CRUD Endpoints:**
- `POST /trips` - Crear trip
- `GET /trips/{trip_id}` - Obtener trip
- `PUT /trips/{trip_id}` - Editar trip
- `DELETE /trips/{trip_id}` - Eliminar trip
- `POST /trips/{trip_id}/publish` - Publicar trip

**Photo Management Endpoints:**
- `POST /trips/{trip_id}/photos` - Upload foto
- `DELETE /trips/{trip_id}/photos/{photo_id}` - Eliminar foto
- `PUT /trips/{trip_id}/photos/reorder` - Reordenar fotos

**Tags & Filtering Endpoints:** ⭐ NUEVO

- `GET /users/{username}/trips` - Listar trips con filtros
  - Query params: `tag`, `status`, `limit`, `offset`
  - Filtrado case-insensitive por tags
  - Filtrado por status (DRAFT/PUBLISHED)
  - Paginación con limit/offset
- `GET /tags` - Obtener todos los tags disponibles
  - Ordenados por `usage_count` (más populares primero)

**Functional Requirements:**
- FR-001, FR-002, FR-003: Trip creation
- FR-007, FR-008: Trip publication and visibility
- FR-009, FR-010, FR-011: Photo upload and processing
- FR-012: Photo reordering
- FR-013: Photo deletion
- FR-016, FR-020: Trip editing with optimistic locking
- FR-017, FR-018: Trip deletion with stats update
- FR-025: User trip listing with tag/status filtering ⭐ NUEVO
- FR-027: Tag browsing and popularity ranking ⭐ NUEVO

**Características:**
- Upload: Max 20 fotos/trip, max 10MB/foto, formatos JPG/PNG/WebP
- Procesamiento: Resize a 1200px, thumbnail 400x400px
- Reordenamiento automático al eliminar
- Validación de permisos (solo owner)
- Tags: Case-insensitive matching, many-to-many relationships ⭐ NUEVO
- Filtrado: Combinación de tag + status, paginación ⭐ NUEVO

---

## Quick Start

### 1. Setup

```bash
# Iniciar servidor
cd backend
poetry run uvicorn src.main:app --reload

# Crear usuarios de prueba
poetry run python scripts/user-mgmt/create_verified_user.py
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'
```

### 3. Crear Trip

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Viaje",
    "description": "Descripción de al menos 50 caracteres para poder publicar...",
    "start_date": "2024-05-15"
  }'
```

### 4. Upload Foto

```bash
curl -X POST "http://localhost:8000/trips/<TRIP_ID>/photos" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "photo=@foto.jpg"
```

---

## Documentación Relacionada

- **OpenAPI Spec**: `../../specs/002-travel-diary/contracts/trips-api.yaml`
- **Specification**: `../../specs/002-travel-diary/spec.md`
- **Implementation Plan**: `../../specs/002-travel-diary/plan.md`
- **Main README**: `../../README.md`

---

## Soporte

Para preguntas o issues:
- Ver troubleshooting en [MANUAL_TESTING.md](MANUAL_TESTING.md#troubleshooting)
- Ver documentación técnica en `../`
- Contactar al equipo de desarrollo

---

**Última actualización:** 2025-12-30
**Versión API:** 0.4.0 (User Story 4 - Tags & Categorization) ✅ COMPLETE
**Test Coverage:** 25 tests (9 contract + 3 integration + 13 unit) + Phase 5-6 pending
