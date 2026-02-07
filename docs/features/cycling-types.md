# Cycling Types - Dynamic Management

Dynamic management of cycling types through database instead of hardcoded values.

**Audience**: Backend developers, administrators, product managers

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Default Types](#default-types)
- [API Reference](#api-reference)
- [Management Scripts](#management-scripts)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento allows dynamic management of cycling types (`cycling_type`) through:

- **Database**: `cycling_types` table for storing active types
- **Configuration File**: `config/cycling_types.yaml` for initial types
- **Admin API**: CRUD endpoints for managing types
- **Public API**: Endpoint for listing active types
- **Dynamic Validation**: Validates against database (not hardcoded values)

**Benefits**:
- Add new cycling types without code changes
- Deactivate obsolete types without breaking existing profiles
- Centralized type management for frontend/backend
- Historical data preserved (soft delete)

---

## Architecture

```
┌─────────────────────┐
│ config/             │
│ cycling_types.yaml  │ ──► Initial configuration
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ scripts/seeding/    │
│ seed_cycling_types  │ ──► Load data to database
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ cycling_types       │
│ (database table)    │ ──► Dynamic storage
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ API Admin           │
│ /admin/cycling-     │ ──► CRUD management
│ types               │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ API Public          │
│ /cycling-types      │ ──► Public query
└─────────────────────┘
```

---

## Default Types

Initial types defined in `config/cycling_types.yaml`:

| Code | Display Name | Description |
|------|--------------|-------------|
| `bikepacking` | Bikepacking | Viajes de varios días en bicicleta con equipaje completo |
| `commuting` | Desplazamiento Urbano | Uso diario de la bicicleta para ir al trabajo o moverse por la ciudad |
| `gravel` | Gravel | Ciclismo en caminos de grava y superficies mixtas |
| `mountain` | Montaña (MTB) | Ciclismo de montaña en senderos y trails |
| `road` | Carretera | Ciclismo en carretera y asfalto |
| `touring` | Cicloturismo | Viajes de larga distancia por carretera con equipaje |

**File**: `config/cycling_types.yaml`

```yaml
cycling_types:
  - code: bikepacking
    display_name: Bikepacking
    description: Viajes de varios días en bicicleta con equipaje completo
    is_active: true
  - code: commuting
    display_name: Desplazamiento Urbano
    description: Uso diario de la bicicleta para ir al trabajo o moverse por la ciudad
    is_active: true
  # ... more types
```

---

## API Reference

### List Active Types (Public)

**Endpoint**: `GET /cycling-types`

**Authentication**: None required

**Response**:
```json
[
  {
    "code": "bikepacking",
    "display_name": "Bikepacking",
    "description": "Viajes de varios días en bicicleta con equipaje completo"
  },
  {
    "code": "mountain",
    "display_name": "Montaña (MTB)",
    "description": "Ciclismo de montaña en senderos y trails"
  }
]
```

**Usage**:
```bash
curl http://localhost:8000/cycling-types
```

---

### List All Types (Admin)

**Endpoint**: `GET /admin/cycling-types?active_only=false`

**Authentication**: Required (admin)

**Query Parameters**:
- `active_only` (bool): If true, return only active types (default: true)

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "bikepacking",
    "display_name": "Bikepacking",
    "description": "Viajes de varios días en bicicleta con equipaje completo",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

**Usage**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/admin/cycling-types
```

---

### Create Type (Admin)

**Endpoint**: `POST /admin/cycling-types`

**Authentication**: Required (admin)

**Request Body**:
```json
{
  "code": "urban-trail",
  "display_name": "Urban Trail",
  "description": "Ciclismo urbano en senderos y parques de la ciudad",
  "is_active": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Tipo de ciclismo creado correctamente",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "urban-trail",
    "display_name": "Urban Trail",
    "description": "Ciclismo urbano en senderos y parques de la ciudad",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
}
```

**Usage**:
```bash
curl -X POST http://localhost:8000/admin/cycling-types \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "urban-trail",
    "display_name": "Urban Trail",
    "description": "Ciclismo urbano en senderos y parques de la ciudad",
    "is_active": true
  }'
```

**Validation**:
- `code`: Unique, alphanumeric with hyphens, max 50 chars
- `display_name`: Required, max 100 chars
- `description`: Optional, max 500 chars
- `is_active`: Boolean, default true

---

### Update Type (Admin)

**Endpoint**: `PUT /admin/cycling-types/{code}`

**Authentication**: Required (admin)

**Request Body**:
```json
{
  "display_name": "Trail Urbano",
  "description": "Nueva descripción actualizada",
  "is_active": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Tipo de ciclismo actualizado correctamente",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "urban-trail",
    "display_name": "Trail Urbano",
    "description": "Nueva descripción actualizada",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T11:30:00Z"
  }
}
```

**Usage**:
```bash
curl -X PUT http://localhost:8000/admin/cycling-types/urban-trail \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Trail Urbano",
    "description": "Nueva descripción actualizada"
  }'
```

**Note**: `code` cannot be changed after creation (immutable)

---

### Deactivate Type (Admin - Soft Delete)

**Endpoint**: `DELETE /admin/cycling-types/{code}`

**Authentication**: Required (admin)

**Response**:
```json
{
  "success": true,
  "message": "Tipo de ciclismo desactivado correctamente"
}
```

**Usage**:
```bash
curl -X DELETE http://localhost:8000/admin/cycling-types/urban-trail \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Effect**: Sets `is_active=false` without deleting the record

**Preservation**: Existing user profiles with this type remain valid

---

### Delete Type Permanently (Admin - Hard Delete)

**Endpoint**: `DELETE /admin/cycling-types/{code}?hard=true`

**Authentication**: Required (admin)

**Response**:
```json
{
  "success": true,
  "message": "Tipo de ciclismo eliminado permanentemente"
}
```

**Usage**:
```bash
curl -X DELETE "http://localhost:8000/admin/cycling-types/urban-trail?hard=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**WARNING**: Permanently deletes the record from database. Use with caution.

---

## Management Scripts

### Load Types from YAML

**Script**: `scripts/seeding/seed_cycling_types.py`

**Usage**:
```bash
cd backend
poetry run python scripts/seeding/seed_cycling_types.py
```

**What it does**:
1. Reads types from `config/cycling_types.yaml`
2. Creates missing types in database
3. Skips existing types (unless `--force`)

**Options**:
- `--force`: Update existing types with YAML data
- `--list`: List current types in database

**Examples**:
```bash
# Load types on first setup
poetry run python scripts/seeding/seed_cycling_types.py

# Update existing types from YAML
poetry run python scripts/seeding/seed_cycling_types.py --force

# List current database types
poetry run python scripts/seeding/seed_cycling_types.py --list
```

**Output**:
```
Loading cycling types from config/cycling_types.yaml...
Created type: bikepacking
Created type: commuting
Created type: gravel
Skipped existing type: mountain
Updated type: road (--force enabled)

Summary: 3 created, 1 updated, 1 skipped
```

---

## Usage

### Adding New Types

#### Option 1: Via YAML + Script (Recommended for Initial Setup)

1. Edit `config/cycling_types.yaml`:
```yaml
cycling_types:
  - code: cyclocross
    display_name: Ciclocross
    description: Carreras en circuitos mixtos con obstáculos
    is_active: true
```

2. Run seed script with `--force`:
```bash
poetry run python scripts/seeding/seed_cycling_types.py --force
```

#### Option 2: Via API (Recommended for Operational Management)

Use the admin endpoint `POST /admin/cycling-types` (see API Reference above).

**Best for**: Adding types during runtime without redeploying

---

### Validation in Profile Updates

Cycling types are validated dynamically when users update their profile:

**Backend Validation**:
```python
# src/services/profile_service.py
from src.utils.validators import validate_cycling_type_async

async def update_profile(username: str, update_data: ProfileUpdateRequest):
    if update_data.cycling_type is not None:
        # Validate against database (not hardcoded list)
        validated_type = await validate_cycling_type_async(
            update_data.cycling_type,
            self.db
        )
        profile.cycling_type = validated_type
```

**Validation Logic**:
```python
# src/utils/validators.py
async def validate_cycling_type_async(value: str, db: AsyncSession) -> str:
    """
    Validate cycling_type against active types in database.

    Raises:
        ValueError: If type code is not active in database
    """
    result = await db.execute(
        select(CyclingType).where(
            CyclingType.code == value,
            CyclingType.is_active == True
        )
    )
    cycling_type = result.scalar_one_or_none()

    if not cycling_type:
        # Get list of valid codes for error message
        valid_result = await db.execute(
            select(CyclingType.code).where(CyclingType.is_active == True)
        )
        valid_codes = [row[0] for row in valid_result.all()]

        raise ValueError(
            f"El tipo de ciclismo debe ser uno de: {', '.join(valid_codes)}"
        )

    return value
```

---

### Frontend Integration

**Fetch types for dropdown**:
```javascript
// Get cycling types for selector
const response = await fetch('/cycling-types');
const types = await response.json();

types.forEach(type => {
  console.log(`${type.code}: ${type.display_name}`);
  // bikepacking: Bikepacking
  // mountain: Montaña (MTB)
  // ...
});
```

**React Component Example**:
```typescript
import { useState, useEffect } from 'react';

function CyclingTypeSelector() {
  const [types, setTypes] = useState([]);

  useEffect(() => {
    fetch('/cycling-types')
      .then(res => res.json())
      .then(data => setTypes(data));
  }, []);

  return (
    <select name="cycling_type">
      <option value="">Selecciona tipo</option>
      {types.map(type => (
        <option key={type.code} value={type.code}>
          {type.display_name}
        </option>
      ))}
    </select>
  );
}
```

---

## Data Model

### Database Schema

**Table**: `cycling_types`

```sql
CREATE TABLE cycling_types (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_cycling_types_code ON cycling_types (code);
CREATE INDEX ix_cycling_types_is_active ON cycling_types (is_active);
```

**Indexes**:
- `ix_cycling_types_code`: Optimize lookups by code (unique constraint)
- `ix_cycling_types_is_active`: Optimize filtering by active status

**Migration**: `20260108_1046_572d49f6a7f3_add_cycling_types_table_for_dynamic_.py`

---

## Considerations

### Backward Compatibility

- **Legacy Validator**: `validate_cycling_type()` still works with hardcoded values
- **New Validator**: `validate_cycling_type_async()` queries database
- **Existing Profiles**: Remain valid even if type is deactivated

### Security

- Admin endpoints require authentication
- Public endpoint is read-only (no auth needed)
- Soft delete by default (preserves referential integrity)

### Performance

- Types are small dataset (<50 records expected)
- Indexes on `code` and `is_active` optimize queries
- Caching can be added if needed (types rarely change)

---

## Troubleshooting

### Error: "El tipo de ciclismo debe ser uno de..."

**Cause**: The type code sent doesn't exist or is inactive in database.

**Solution**: List active types and use a valid code.

```bash
# Option 1: List via script
poetry run python scripts/seeding/seed_cycling_types.py --list

# Option 2: List via API
curl http://localhost:8000/cycling-types
```

---

### Error: "Ya existe un tipo de ciclismo con el código..."

**Cause**: Code must be unique. Another type already uses that code.

**Solution**: Use a different code or update the existing one with PUT.

```bash
# Update existing type instead of creating
curl -X PUT http://localhost:8000/admin/cycling-types/existing-code \
  -H "Authorization: Bearer TOKEN" \
  -d '{"display_name": "Updated Name"}'
```

---

### New types not showing in application

**Cause**: Type is inactive (`is_active=false`).

**Solution**: Check type status via admin API.

```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/admin/cycling-types?active_only=false"
```

**Fix**: Update type to set `is_active=true`.

```bash
curl -X PUT http://localhost:8000/admin/cycling-types/TYPE_CODE \
  -H "Authorization: Bearer TOKEN" \
  -d '{"is_active": true}'
```

---

## Workflow Recommendations

### 1. Initial Setup

```bash
# Apply migration
poetry run alembic upgrade head

# Load types from YAML
poetry run python scripts/seeding/seed_cycling_types.py
```

### 2. Add New Type

**Production**: Use API POST `/admin/cycling-types`

**Development**: Edit YAML + run seed with `--force`

### 3. Modify Type

Use API PUT `/admin/cycling-types/{code}`

### 4. Deactivate Type

Use API DELETE `/admin/cycling-types/{code}` (soft delete)

### 5. List Types

- **Public**: `GET /cycling-types` (active only)
- **Admin**: `GET /admin/cycling-types` (all types)

---

## Related Documentation

- **[Backend Architecture](../architecture/backend/overview.md)** - Service Layer patterns
- **[API Reference](../api/endpoints/users.md)** - Profile update endpoints
- **[Development Scripts](../development/scripts/overview.md)** - Seeding scripts

---

**Last Updated**: 2026-02-07
**Status**: ✅ Complete
**Migration**: `20260108_1046_*_add_cycling_types_table.py`
