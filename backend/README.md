# ContraVento Backend API

Backend API para ContraVento, la plataforma social de cicloturismo.

## Stack Tecnológico

- **Python**: 3.11+
- **Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0+ (async)
- **Base de datos**:
  - **Desarrollo/Testing**: SQLite (aiosqlite)
  - **Producción**: PostgreSQL (asyncpg)
- **Autenticación**: JWT con python-jose
- **Seguridad**: bcrypt 4.0.1 (passlib compatible)
- **Validación**: Pydantic 2.0+
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Calidad de código**: black, ruff, mypy

## Estructura del Proyecto

```
backend/
├── src/                    # Código fuente
│   ├── api/               # Endpoints FastAPI
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Schemas Pydantic
│   ├── services/          # Lógica de negocio
│   ├── utils/             # Utilidades
│   ├── migrations/        # Migraciones Alembic
│   ├── config.py          # Configuración
│   ├── database.py        # Setup de base de datos
│   └── main.py            # Aplicación FastAPI
├── tests/                 # Tests
│   ├── contract/          # Tests de contrato (OpenAPI)
│   ├── integration/       # Tests de integración
│   └── unit/              # Tests unitarios
├── storage/               # Almacenamiento de archivos
│   ├── profile_photos/    # Fotos de perfil
│   └── trip_photos/       # Fotos de viajes (organizadas por año/mes/trip_id)
├── pyproject.toml         # Dependencias Poetry
├── .env.example           # Variables de entorno (ejemplo)
└── .env.test              # Variables de entorno (testing)
```

## Configuración Rápida

### 1. Instalar Poetry

**Windows (PowerShell)**:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Linux/macOS**:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Verificar instalación**:

```bash
poetry --version
```

Si el comando no se reconoce en Windows, agregar al PATH: `%APPDATA%\Python\Scripts`

### 2. Instalar Dependencias

```bash
cd backend
poetry install
```

### 3. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tu configuración
```

**Generar SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Inicializar Base de Datos

Las migraciones de Alembic se ejecutan desde el directorio `backend/`:

```bash
# Aplicar migraciones (crear tablas)
poetry run alembic upgrade head

# Seedear achievements (logros predefinidos)
poetry run python scripts/seed_achievements.py
```

> **Nota**: El archivo `alembic.ini` en la raíz de `backend/` apunta automáticamente a `src/migrations/`. No es necesario cambiar de directorio.
>
> **Importante**: El script `seed_achievements.py` debe ejecutarse **una sola vez** después de crear las tablas. Es idempotente (puede ejecutarse múltiples veces sin duplicar datos).

### 5. Ejecutar Servidor de Desarrollo

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### 6. Crear Usuarios de Prueba (Opcional)

Para desarrollo, puedes crear usuarios verificados automáticamente:

```bash
# Crear usuarios por defecto (testuser y maria_garcia)
poetry run python scripts/create_verified_user.py

# Crear usuario personalizado
poetry run python scripts/create_verified_user.py --username carlos --email carlos@example.com --password "Carlos2024!"

# Verificar usuario existente por email
poetry run python scripts/create_verified_user.py --verify-email test@example.com
```

**Usuarios por defecto**:

- Username: `testuser`, Email: `test@example.com`, Password: `TestPass123!`
- Username: `maria_garcia`, Email: `maria@example.com`, Password: `SecurePass456!`

## Testing

### Ejecutar Todos los Tests

```bash
poetry run pytest
```

### Con Cobertura

```bash
poetry run pytest --cov=src --cov-report=html --cov-report=term
```

### Solo Tests Unitarios

```bash
poetry run pytest tests/unit/ -v
```

### Solo Tests de Integración

```bash
poetry run pytest tests/integration/ -v
```

### Ver Reporte de Cobertura

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Calidad de Código

### Formatear Código

```bash
poetry run black src/ tests/
```

### Lint

```bash
poetry run ruff check src/ tests/
```

### Type Checking

```bash
poetry run mypy src/
```

### Ejecutar Todas las Verificaciones

```bash
poetry run black src/ tests/ && \
poetry run ruff check src/ tests/ && \
poetry run mypy src/ && \
poetry run pytest --cov=src
```

## Migraciones de Base de Datos

### Crear Nueva Migración

```bash
poetry run alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar Migraciones

```bash
poetry run alembic upgrade head
```

### Revertir Última Migración

```bash
poetry run alembic downgrade -1
```

### Ver Historial de Migraciones

```bash
poetry run alembic history
```

## Base de Datos

### SQLite (Desarrollo/Testing)

**Ventajas**:
- Cero configuración
- Tests rápidos (in-memory)
- Ideal para CI/CD
- No requiere Docker

**Configuración**:
```env
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db
```

### PostgreSQL (Producción)

**Ventajas**:
- UUID nativo
- Arrays nativos
- Mejor concurrencia
- Full-text search

**Configuración con Docker**:
```bash
docker-compose up -d postgres
```

**Configuración**:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/contravento
```

## Variables de Entorno

Ver `.env.example` para todas las variables disponibles.

**Variables Críticas**:
- `SECRET_KEY`: Clave secreta para JWT (mín. 32 caracteres)
- `DATABASE_URL`: URL de conexión a la base de datos
- `BCRYPT_ROUNDS`: Rondas de bcrypt (12 en producción)
- `SMTP_*`: Configuración de email

## Funcionalidades Implementadas

### Travel Diary (Diario de Viajes Digital) ✅

Sistema completo para documentar viajes en bicicleta con integración de estadísticas:

- **User Story 1 - MVP**: Crear, publicar y gestionar trips
  - Crear trips en modo draft con título, descripción, fechas, dificultad, ubicaciones y tags
  - Publicar trips con validación automática de requisitos (título, descripción ≥50 chars, fecha inicio)
  - Editar trips publicados con actualización automática de estadísticas
  - Eliminar trips con rollback de estadísticas
  - Sanitización automática de HTML (XSS prevention)
  - Detección de spam y palabras bloqueadas

- **User Story 2 - Photo Gallery**: Gestión completa de fotos
  - Upload múltiple (max 20 fotos por trip, max 10MB por foto)
  - Procesamiento automático: resize a 1200px, thumbnail 400x400px
  - Almacenamiento organizado: `storage/trip_photos/{year}/{month}/{trip_id}/`
  - Formatos soportados: JPG, PNG, WebP
  - Reordenar fotos en la galería
  - Eliminar fotos con cleanup de archivos físicos

- **🎯 Integración de Estadísticas** (NUEVA FUNCIONALIDAD):
  - **Actualización automática** cuando se publican, editan o eliminan viajes
  - **Métricas rastreadas**:
    - `total_trips`: Contador de viajes publicados
    - `total_kilometers`: Kilómetros acumulados
    - `total_photos`: Fotos totales en viajes publicados
    - `countries_visited`: Lista de países únicos visitados
    - `last_trip_date`: Fecha del viaje más reciente
  - **Sistema de Logros**: Verificación y otorgamiento automático de achievements
    - Logros de distancia (100km, 1000km, 5000km)
    - Logros de viajes (1, 10, 25 trips)
    - Logros de países (5, 10 países)
    - Logros de fotos (50 fotos)
  - **Operaciones soportadas**:
    - Trip publicado → +1 trip, +X km, +N fotos, +país
    - Foto agregada (trip publicado) → +1 foto
    - Foto eliminada (trip publicado) → -1 foto
    - Trip editado → recalcular delta (km, fotos, países)
    - Trip eliminado → revertir estadísticas

**Manual de Testing**: Ver [docs/api/MANUAL_TESTING.md](docs/api/MANUAL_TESTING.md) para comandos curl y [docs/api/POSTMAN_COLLECTION.md](docs/api/POSTMAN_COLLECTION.md) para colección Postman/Insomnia.

**Documentación**:

- **OpenAPI Spec**: `specs/002-travel-diary/contracts/trips-api.yaml`
- **Especificación**: `specs/002-travel-diary/spec.md`
- **Plan de Implementación**: `specs/002-travel-diary/plan.md`
- **Tareas**: `specs/002-travel-diary/tasks.md`

## Desarrollo

### Convenciones de Código

- **Estilo**: PEP 8 con black (100 caracteres por línea)
- **Type Hints**: Obligatorios en todas las funciones
- **Docstrings**: Google-style para funciones públicas
- **Tests**: TDD - tests primero, luego implementación
- **Cobertura**: Mínimo 90%

### Flujo de Trabajo TDD

1. Escribir test (Red) ✗
2. Ejecutar test - debe fallar
3. Implementar código (Green) ✓
4. Ejecutar test - debe pasar
5. Refactorizar (Refactor) ♻️
6. Repetir

### Git Workflow

```bash
# Crear rama de feature
git checkout -b feature/001-user-profiles

# Hacer cambios y commits
git add .
git commit -m "feat: add user registration endpoint"

# Push y crear PR
git push -u origin feature/001-user-profiles
```

## Arquitectura

### Capas

1. **API (Routers)**: Endpoints FastAPI - capa delgada
2. **Services**: Lógica de negocio
3. **Models**: Modelos SQLAlchemy (ORM)
4. **Schemas**: Validación Pydantic
5. **Utils**: Funciones reutilizables

### Principios

- **Single Responsibility**: Cada servicio maneja un dominio
- **Dependency Injection**: Usar FastAPI Depends()
- **Separation of Concerns**: API → Service → Model
- **DRY**: No duplicar código

## Seguridad

- Contraseñas hasheadas con bcrypt (12 rondas)
- JWT con tokens de acceso (15min) y refresh (30 días)
- Rate limiting en login (5 intentos, 15min bloqueo)
- Validación de entrada con Pydantic
- SQL injection prevention (solo ORM)
- XSS prevention en inputs de usuario

## Performance

- Queries optimizados con eager loading
- Índices en columnas frecuentemente consultadas
- Paginación en listas (max 50 items)
- Procesamiento asíncrono de imágenes
- Connection pooling en PostgreSQL

## Licencia

Propietario - ContraVento Team

## Soporte

Para preguntas o issues, contactar al equipo de desarrollo.
