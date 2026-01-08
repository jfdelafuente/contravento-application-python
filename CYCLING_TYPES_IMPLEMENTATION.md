# Implementación: Gestión Dinámica de Cycling Types

## Resumen Ejecutivo

Se ha implementado un sistema completo para gestionar dinámicamente los tipos de ciclismo (`cycling_type`) en ContraVento, permitiendo agregar, modificar y eliminar tipos sin necesidad de modificar código.

## Cambios Realizados

### 1. Base de Datos

**Nueva tabla**: `cycling_types`
- Almacena tipos de ciclismo activos e inactivos
- Campos: id, code, display_name, description, is_active, timestamps
- Índices en `code` (único) e `is_active`

**Migración**: `20260108_1046_572d49f6a7f3_add_cycling_types_table_for_dynamic_.py`

### 2. Modelos

**Nuevo archivo**: [`backend/src/models/cycling_type.py`](backend/src/models/cycling_type.py)
- Modelo SQLAlchemy `CyclingType`
- Soporte para soft delete (is_active flag)
- Integrado con Alembic para autogenerate

### 3. Schemas Pydantic

**Nuevo archivo**: [`backend/src/schemas/cycling_type.py`](backend/src/schemas/cycling_type.py)
- `CyclingTypeResponse`: Respuesta completa (admin)
- `CyclingTypePublicResponse`: Respuesta simplificada (público)
- `CyclingTypeCreateRequest`: Validación para creación
- `CyclingTypeUpdateRequest`: Validación para actualización

### 4. Capa de Servicio

**Nuevo archivo**: [`backend/src/services/cycling_type_service.py`](backend/src/services/cycling_type_service.py)
- `CyclingTypeService` con métodos CRUD completos:
  - `get_all()`: Listar todos (con filtro opcional active_only)
  - `get_all_public()`: Listar solo activos (público)
  - `get_by_code()`: Obtener por código
  - `create()`: Crear nuevo tipo
  - `update()`: Actualizar tipo existente
  - `delete()`: Soft/hard delete
  - `get_active_codes()`: Obtener códigos activos para validación

### 5. API Endpoints

**Nuevo archivo**: [`backend/src/api/cycling_types.py`](backend/src/api/cycling_types.py)

**Endpoints Públicos**:
- `GET /cycling-types`: Listar tipos activos (no requiere auth)

**Endpoints Administrativos** (requieren rol ADMIN):
- `GET /admin/cycling-types`: Listar todos los tipos
- `GET /admin/cycling-types/{code}`: Obtener tipo específico
- `POST /admin/cycling-types`: Crear nuevo tipo
- `PUT /admin/cycling-types/{code}`: Actualizar tipo
- `DELETE /admin/cycling-types/{code}`: Eliminar tipo (soft delete por defecto)

**IMPORTANTE**: Los endpoints administrativos requieren:
1. Autenticación válida (JWT token)
2. Rol de administrador (UserRole.ADMIN)

Si un usuario regular intenta acceder, recibirá HTTP 403 Forbidden.

### 6. Validación Dinámica

**Actualizado**: [`backend/src/utils/validators.py`](backend/src/utils/validators.py)
- Nueva función `validate_cycling_type_async()`: Valida contra BD
- Función legacy `validate_cycling_type()`: Mantiene compatibilidad

**Actualizado**: [`backend/src/services/profile_service.py`](backend/src/services/profile_service.py)
- Ahora usa validación dinámica al actualizar perfil

### 7. Configuración Inicial

**Nuevo archivo**: [`backend/config/cycling_types.yaml`](backend/config/cycling_types.yaml)
- Define 6 tipos iniciales: bikepacking, commuting, gravel, mountain, road, touring
- Formato YAML con code, display_name, description, is_active

### 8. Script de Seed

**Nuevo archivo**: [`backend/scripts/seed_cycling_types.py`](backend/scripts/seed_cycling_types.py)
- Carga tipos desde YAML a base de datos
- Opciones:
  - Sin argumentos: Carga tipos nuevos, omite existentes
  - `--force`: Actualiza tipos existentes desde YAML
  - `--list`: Lista tipos actuales en BD

### 9. Documentación

**Nuevo archivo**: [`backend/docs/CYCLING_TYPES.md`](backend/docs/CYCLING_TYPES.md)
- Documentación completa del sistema
- Ejemplos de uso de API
- Flujo de trabajo recomendado
- Troubleshooting

**Nuevo archivo**: [`backend/config/README.md`](backend/config/README.md)
- Guía rápida del directorio config

## Cómo Usar

### Setup Inicial

#### Opción 1: Usando `run-local-dev.sh` (Recomendado)

```bash
# Desde el directorio raíz del proyecto
./run-local-dev.sh --setup      # Linux/Mac
.\run-local-dev.ps1 -Setup      # Windows PowerShell

# Los cycling types se cargarán automáticamente junto con achievements y usuarios
```

#### Opción 2: Usando Docker

```bash
# Los cycling types se cargan automáticamente durante el inicio
./deploy.sh local-minimal
# o
./deploy.sh local
```

#### Opción 3: Manualmente

```bash
cd backend

# 1. Aplicar migración
poetry run alembic upgrade head

# 2. Cargar tipos iniciales desde YAML
poetry run python scripts/seed_cycling_types.py

# 3. Verificar tipos cargados
poetry run python scripts/seed_cycling_types.py --list
```

### Gestionar Tipos

#### Via Script (Recomendado para setup)

```bash
# Editar config/cycling_types.yaml
nano config/cycling_types.yaml

# Cargar cambios
poetry run python scripts/seed_cycling_types.py --force
```

#### Via API (Recomendado para operaciones)

```bash
# Crear nuevo tipo
curl -X POST http://localhost:8000/admin/cycling-types \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "cyclocross",
    "display_name": "Ciclocross",
    "description": "Carreras en circuitos mixtos",
    "is_active": true
  }'

# Actualizar tipo
curl -X PUT http://localhost:8000/admin/cycling-types/cyclocross \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Ciclocross Pro"}'

# Desactivar tipo (soft delete)
curl -X DELETE http://localhost:8000/admin/cycling-types/cyclocross \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Consultar Tipos (Público)

```bash
# Listar tipos activos (no requiere auth)
curl http://localhost:8000/cycling-types
```

## Arquitectura

```
Usuario edita perfil
       ↓
ProfileService.update_profile()
       ↓
validate_cycling_type_async() ──► Consulta BD
       ↓
CyclingTypeService.get_active_codes()
       ↓
cycling_types tabla (PostgreSQL/SQLite)
```

## Ventajas de la Implementación

1. **Flexibilidad**: Añadir/modificar tipos sin cambios de código
2. **Validación Dinámica**: Los tipos se validan contra BD en tiempo real
3. **API Completa**: CRUD completo con autenticación
4. **Compatibilidad**: Validación legacy mantiene funcionamiento anterior
5. **Soft Delete**: Desactivar sin eliminar datos
6. **Seed desde YAML**: Setup inicial fácil y reproducible
7. **Documentación**: Completa y con ejemplos

## Testing

Para probar la implementación:

```bash
# 1. Listar tipos actuales
curl http://localhost:8000/cycling-types

# 2. Actualizar perfil con tipo válido
curl -X PUT http://localhost:8000/users/{username}/profile \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cycling_type": "mountain"}'

# 3. Intentar con tipo inválido (debe fallar)
curl -X PUT http://localhost:8000/users/{username}/profile \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cycling_type": "invalid"}'
```

## Próximos Pasos Recomendados

1. **Tests Unitarios**: Añadir tests para `CyclingTypeService`
2. **Tests de Integración**: Añadir tests para endpoints API
3. **Cache**: Implementar cache Redis para `get_active_codes()`
4. **Audit Log**: Registrar cambios en cycling_types
5. **Frontend**: Selector dinámico que consulte `/cycling-types`

## Archivos Modificados

- `backend/src/main.py`: Registro de routers
- `backend/src/models/__init__.py`: Export de CyclingType
- `backend/src/utils/validators.py`: Validador async
- `backend/src/services/profile_service.py`: Validación dinámica

## Archivos Nuevos

- `backend/src/models/cycling_type.py`
- `backend/src/schemas/cycling_type.py`
- `backend/src/services/cycling_type_service.py`
- `backend/src/api/cycling_types.py`
- `backend/config/cycling_types.yaml`
- `backend/config/README.md`
- `backend/scripts/seed_cycling_types.py`
- `backend/docs/CYCLING_TYPES.md`
- `backend/src/migrations/versions/20260108_1046_572d49f6a7f3_*.py`

## Compatibilidad

- ✅ SQLite (desarrollo/testing)
- ✅ PostgreSQL (producción)
- ✅ Backward compatible con perfiles existentes
- ✅ Validador legacy sigue funcionando

## Conclusión

El sistema está completamente implementado y listo para usar. Los tipos de ciclismo ahora se pueden gestionar dinámicamente mediante API administrativa o mediante el archivo YAML de configuración, proporcionando máxima flexibilidad sin sacrificar la validación y seguridad de datos.
