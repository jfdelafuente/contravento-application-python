# Cycling Types - Gestión Dinámica

Este documento describe cómo gestionar los tipos de ciclismo (`cycling_type`) en ContraVento.

## Visión General

ContraVento ahora permite gestionar los tipos de ciclismo de forma dinámica mediante:
- **Base de datos**: Tabla `cycling_types` para almacenar tipos activos
- **Archivo de configuración**: `config/cycling_types.yaml` para definir tipos iniciales
- **API administrativa**: Endpoints CRUD para gestionar tipos
- **API pública**: Endpoint para listar tipos activos

## Arquitectura

```
┌─────────────────────┐
│ config/             │
│ cycling_types.yaml  │ ──► Configuración inicial
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ scripts/            │
│ seed_cycling_types  │ ──► Carga datos en BD
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ cycling_types       │
│ (tabla BD)          │ ──► Almacenamiento dinámico
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ API Admin           │
│ /admin/cycling-     │ ──► Gestión CRUD
│ types               │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ API Pública         │
│ /cycling-types      │ ──► Consulta pública
└─────────────────────┘
```

## Tipos Iniciales

Los tipos predefinidos en `config/cycling_types.yaml` son:

| Code | Display Name | Descripción |
|------|--------------|-------------|
| `bikepacking` | Bikepacking | Viajes de varios días en bicicleta con equipaje completo |
| `commuting` | Desplazamiento Urbano | Uso diario de la bicicleta para ir al trabajo o moverse por la ciudad |
| `gravel` | Gravel | Ciclismo en caminos de grava y superficies mixtas |
| `mountain` | Montaña (MTB) | Ciclismo de montaña en senderos y trails |
| `road` | Carretera | Ciclismo en carretera y asfalto |
| `touring` | Cicloturismo | Viajes de larga distancia por carretera con equipaje |

## Uso

### 1. Listar Tipos Activos (Público)

**Endpoint**: `GET /cycling-types`

No requiere autenticación.

```bash
curl http://localhost:8000/cycling-types
```

**Respuesta**:
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

### 2. Listar Todos los Tipos (Admin)

**Endpoint**: `GET /admin/cycling-types?active_only=false`

Requiere autenticación.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/admin/cycling-types
```

### 3. Crear Nuevo Tipo (Admin)

**Endpoint**: `POST /admin/cycling-types`

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

**Respuesta**:
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

### 4. Actualizar Tipo Existente (Admin)

**Endpoint**: `PUT /admin/cycling-types/{code}`

```bash
curl -X PUT http://localhost:8000/admin/cycling-types/urban-trail \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Trail Urbano",
    "description": "Nueva descripción actualizada"
  }'
```

### 5. Desactivar Tipo (Admin - Soft Delete)

**Endpoint**: `DELETE /admin/cycling-types/{code}`

```bash
curl -X DELETE http://localhost:8000/admin/cycling-types/urban-trail \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Esto establece `is_active=false` sin eliminar el registro.

### 6. Eliminar Tipo Permanentemente (Admin - Hard Delete)

**Endpoint**: `DELETE /admin/cycling-types/{code}?hard=true`

```bash
curl -X DELETE "http://localhost:8000/admin/cycling-types/urban-trail?hard=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**ADVERTENCIA**: Esta acción elimina permanentemente el registro de la base de datos.

## Gestión desde Scripts

### Cargar Tipos desde YAML

```bash
cd backend
poetry run python scripts/seed_cycling_types.py
```

Esto carga los tipos definidos en `config/cycling_types.yaml` en la base de datos.

**Opciones**:
- `--force`: Actualiza tipos existentes con datos del YAML
- `--list`: Lista los tipos actuales en la base de datos

```bash
# Actualizar tipos existentes desde YAML
poetry run python scripts/seed_cycling_types.py --force

# Listar tipos en base de datos
poetry run python scripts/seed_cycling_types.py --list
```

## Añadir Nuevos Tipos

### Opción 1: Via YAML + Script (Recomendado para setup inicial)

1. Editar `config/cycling_types.yaml`:

```yaml
cycling_types:
  - code: cyclocross
    display_name: Ciclocross
    description: Carreras en circuitos mixtos con obstáculos
    is_active: true
```

2. Ejecutar seed con --force:

```bash
poetry run python scripts/seed_cycling_types.py --force
```

### Opción 2: Via API (Recomendado para gestión operativa)

Usar el endpoint `POST /admin/cycling-types` como se describe arriba.

## Validación

Los tipos de ciclismo se validan dinámicamente:

1. **En schemas Pydantic**: Validación legacy con valores hardcodeados (compatibilidad)
2. **En ProfileService**: Validación dinámica contra base de datos

Cuando un usuario actualiza su perfil:

```python
# ProfileService valida contra BD
validated_type = await validate_cycling_type_async(update_data.cycling_type, db)
```

Esto asegura que solo se acepten códigos de tipos activos en la base de datos.

## Modelo de Datos

**Tabla**: `cycling_types`

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

## Migraciones

La migración inicial crea la tabla:

```bash
# Aplicar migración
poetry run alembic upgrade head

# Ver historial
poetry run alembic history
```

**Migración**: `20260108_1046_572d49f6a7f3_add_cycling_types_table_for_dynamic_.py`

## Consideraciones

### Compatibilidad hacia atrás

- El validador legacy `validate_cycling_type()` sigue funcionando con valores hardcodeados
- El validador nuevo `validate_cycling_type_async()` consulta la base de datos
- Los perfiles existentes siguen siendo válidos

### Seguridad

- Endpoints administrativos requieren autenticación
- Endpoint público no requiere autenticación (solo lectura)
- Soft delete por defecto para preservar integridad referencial

### Performance

- Los tipos activos se cachean en memoria al inicio del validador
- Los índices en `code` e `is_active` optimizan las búsquedas
- La tabla es pequeña (< 50 registros esperados)

## Flujo de Trabajo Recomendado

1. **Setup inicial**:
   - Aplicar migración: `alembic upgrade head`
   - Cargar tipos desde YAML: `python scripts/seed_cycling_types.py`

2. **Añadir tipo nuevo**:
   - Usar API POST `/admin/cycling-types`
   - O editar YAML y ejecutar seed con `--force`

3. **Modificar tipo**:
   - Usar API PUT `/admin/cycling-types/{code}`

4. **Desactivar tipo**:
   - Usar API DELETE `/admin/cycling-types/{code}` (soft delete)

5. **Listar tipos**:
   - Público: `GET /cycling-types` (solo activos)
   - Admin: `GET /admin/cycling-types` (todos)

## Ejemplos de Uso en Frontend

```javascript
// Obtener tipos para selector
const response = await fetch('/cycling-types');
const types = await response.json();

types.forEach(type => {
  console.log(`${type.code}: ${type.display_name}`);
  // bikepacking: Bikepacking
  // mountain: Montaña (MTB)
  // ...
});
```

## Troubleshooting

### Error: "El tipo de ciclismo debe ser uno de..."

Los tipos en la base de datos no coinciden con el código enviado. Verificar:

```bash
# Listar tipos activos
poetry run python scripts/seed_cycling_types.py --list

# O usar la API
curl http://localhost:8000/cycling-types
```

### Error: "Ya existe un tipo de ciclismo con el código..."

El código debe ser único. Usar otro código o actualizar el existente con PUT.

### No se ven nuevos tipos en la aplicación

Verificar que `is_active=true`:

```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/admin/cycling-types?active_only=false"
```

## Referencias

- **Modelo**: `src/models/cycling_type.py`
- **Schemas**: `src/schemas/cycling_type.py`
- **Servicio**: `src/services/cycling_type_service.py`
- **API**: `src/api/cycling_types.py`
- **Configuración**: `config/cycling_types.yaml`
- **Script seed**: `scripts/seed_cycling_types.py`
- **Migración**: `src/migrations/versions/20260108_1046_*_add_cycling_types_table.py`
