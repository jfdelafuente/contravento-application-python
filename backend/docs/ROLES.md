# Sistema de Roles y Autorización

## Resumen

ContraVento implementa un sistema simple de roles (Role-Based Access Control - RBAC) con dos niveles:

- **USER**: Usuario regular (por defecto)
- **ADMIN**: Administrador del sistema

## Roles Disponibles

### USER (Usuario Regular)

**Permisos:**
- Gestionar su propio perfil
- Crear y gestionar sus propios viajes (trips)
- Seguir a otros usuarios
- Ver estadísticas públicas
- Acceder a endpoints públicos

**Restricciones:**
- No puede acceder a endpoints administrativos
- No puede gestionar cycling types
- No puede gestionar otros usuarios

### ADMIN (Administrador)

**Permisos:**
- Todos los permisos de USER
- Gestionar cycling types (crear, actualizar, eliminar)
- Acceder a todos los endpoints `/admin/*`
- Futuro: gestionar usuarios, moderación de contenido

## Gestión de Roles

### Crear Usuario Admin

**Opción 1: Al crear usuario nuevo**

```bash
# Crear usuario con rol admin directamente
cd backend
poetry run python scripts/create_verified_user.py \
  --username admin \
  --email admin@contravento.com \
  --password "AdminPass123!" \
  --role admin
```

**Opción 2: Promover usuario existente**

```bash
# Promover usuario existente a admin
poetry run python scripts/promote_to_admin.py --username testuser

# O por email
poetry run python scripts/promote_to_admin.py --email test@example.com
```

**Opción 3: Degradar admin a usuario regular**

```bash
# Degradar admin a user
poetry run python scripts/promote_to_admin.py --username admin --demote
```

### Verificar Rol de Usuario

```bash
# Usando el script de listado (futuro)
poetry run python scripts/list_users.py

# O directamente en la base de datos
sqlite3 backend/contravento_dev.db "SELECT username, email, role FROM users;"
```

## Implementación Técnica

### Modelo de Datos

```python
# backend/src/models/user.py
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
        index=True,
    )
```

### Proteger Endpoints

**Dependency Injection:**

```python
from src.api.deps import get_current_admin

@router.post("/admin/cycling-types")
async def create_cycling_type(
    data: CyclingTypeCreateRequest,
    admin: User = Depends(get_current_admin),  # ← Solo admins
    db: AsyncSession = Depends(get_db),
):
    # Solo usuarios con role=ADMIN pueden acceder
    service = CyclingTypeService(db)
    return await service.create(data)
```

**Respuesta HTTP:**

- **Sin autenticación**: `401 Unauthorized`
- **Usuario regular accediendo a admin**: `403 Forbidden`
- **Admin**: `200 OK` o `201 Created`

### Testing

**Fixtures disponibles:**

```python
# tests/conftest.py

# Usuario admin (para endpoints /admin/*)
async def test_admin_endpoint(client, auth_headers):
    response = await client.post(
        "/admin/cycling-types",
        headers=auth_headers,  # ← Usuario admin
        json={...}
    )
    assert response.status_code == 201

# Usuario regular (para verificar restricciones)
async def test_regular_user_forbidden(client, regular_user_headers):
    response = await client.post(
        "/admin/cycling-types",
        headers=regular_user_headers,  # ← Usuario regular
        json={...}
    )
    assert response.status_code == 403
```

## Endpoints Protegidos por Rol

### Endpoints Admin (Requieren ADMIN)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/admin/cycling-types` | Listar todos los cycling types |
| GET | `/admin/cycling-types/{code}` | Obtener cycling type por código |
| POST | `/admin/cycling-types` | Crear nuevo cycling type |
| PUT | `/admin/cycling-types/{code}` | Actualizar cycling type |
| DELETE | `/admin/cycling-types/{code}` | Eliminar cycling type |

### Endpoints Públicos (No requieren auth)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/cycling-types` | Listar cycling types activos |

### Endpoints de Usuario (Requieren autenticación, cualquier rol)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/users/{username}/profile` | Ver perfil |
| PUT | `/users/{username}/profile` | Actualizar propio perfil |
| POST | `/trips` | Crear viaje |
| etc. | ... | ... |

## Flujo de Autorización

```
1. Usuario hace request con JWT token
   ↓
2. get_current_user verifica token y carga User
   ↓
3. get_current_admin verifica user.role == ADMIN
   ↓
4. Si role != ADMIN → HTTP 403 Forbidden
   ↓
5. Si role == ADMIN → Procesar request
```

## Migración de Datos

**Migración**: `20260108_1154_9676fc72ca21_add_role_column_to_users_table.py`

- Agrega columna `role` a tabla `users`
- Valor por defecto: `USER`
- Usuarios existentes se convierten automáticamente en `USER`
- Índice en columna `role` para consultas eficientes

## Ejemplos de Uso

### 1. Crear Primer Admin

```bash
# Setup inicial
cd backend
poetry run alembic upgrade head

# Crear usuario admin
poetry run python scripts/create_verified_user.py \
  --username admin \
  --email admin@contravento.com \
  --password "AdminPass123!" \
  --role admin

# Verificar creación
echo "Admin creado correctamente"
```

### 2. Login y Uso de Endpoints Admin

```bash
# 1. Login como admin
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "AdminPass123!"}'

# Respuesta: {"data": {"access_token": "eyJ..."}}

# 2. Usar token para crear cycling type
curl -X POST http://localhost:8000/admin/cycling-types \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ebike",
    "display_name": "E-Bike",
    "description": "Bicicleta eléctrica",
    "is_active": true
  }'
```

### 3. Usuario Regular Intenta Acceder (Falla)

```bash
# 1. Login como usuario regular
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "testuser", "password": "TestPass123!"}'

# 2. Intentar crear cycling type (FALLA con 403)
curl -X POST http://localhost:8000/admin/cycling-types \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{...}'

# Respuesta: 403 Forbidden
# {
#   "error": {
#     "code": "FORBIDDEN",
#     "message": "Acceso denegado. Se requiere rol de administrador."
#   }
# }
```

## Mejoras Futuras

1. **Roles Adicionales**: Agregar rol `MODERATOR` para moderación de contenido
2. **Permisos Granulares**: Sistema de permisos más detallado (ej: "cycling_types:create")
3. **Audit Log**: Registrar acciones administrativas
4. **Role Management API**: Endpoints para gestionar roles desde el frontend
5. **Multi-tenancy**: Soporte para organizaciones con diferentes niveles de acceso

## Seguridad

**Buenas Prácticas:**

- ✅ No exponer IDs de admin en respuestas públicas
- ✅ Validar rol en cada request (no confiar en el cliente)
- ✅ Usar HTTPS en producción para proteger tokens
- ✅ Rotar secrets regularmente
- ✅ Limitar número de admins (principio de mínimo privilegio)

**Advertencias:**

- ⚠️ No hardcodear credenciales de admin en código
- ⚠️ No permitir auto-promoción a admin
- ⚠️ No compartir tokens entre usuarios
- ⚠️ No loggear tokens en archivos de log

## Troubleshooting

### Error: "Acceso denegado. Se requiere rol de administrador"

**Causa**: Usuario regular intentando acceder a endpoint admin

**Solución**:
1. Verificar que el usuario tiene rol ADMIN: `SELECT role FROM users WHERE username='...';`
2. Si no es admin, promover: `poetry run python scripts/promote_to_admin.py --username ...`

### Error: "Token de autenticación inválido o expirado"

**Causa**: Token inválido o expirado

**Solución**:
1. Hacer login nuevamente para obtener nuevo token
2. Verificar que el token se está enviando correctamente en el header

### Usuario admin no puede acceder después de upgrade

**Causa**: Migración aplicada pero usuario no tiene rol asignado

**Solución**:
```bash
# Verificar rol del usuario
sqlite3 backend/contravento_dev.db \
  "SELECT username, role FROM users WHERE username='admin';"

# Si role es NULL o 'user', promover a admin
poetry run python scripts/promote_to_admin.py --username admin
```

## Referencias

- [Modelo User](../src/models/user.py) - Definición de roles
- [Dependency get_current_admin](../src/api/deps.py) - Validación de rol
- [Script promote_to_admin](../scripts/promote_to_admin.py) - Gestión de roles
- [Tests de autorización](../tests/integration/test_cycling_types_api.py) - Ejemplos de testing
