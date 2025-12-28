# Testing Guide - ContraVento Backend

Guía completa para ejecutar tests y verificar cobertura.

## Índice

- [Ejecutar Tests](#ejecutar-tests)
- [Cobertura de Código](#cobertura-de-código)
- [Tests Existentes](#tests-existentes)
- [Verificación de Mensajes en Español](#verificación-de-mensajes-en-español)
- [CI/CD Integration](#cicd-integration)
- [Manual Testing](#manual-testing)

---

## Ejecutar Tests

### T245: Test Suite Completo

Ejecutar todos los tests con reporte de cobertura:

```bash
cd backend
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term -v
```

### Tests por Categoría

**Contract Tests** (validan respuestas contra OpenAPI spec):
```bash
poetry run pytest tests/contract/ -v
```

**Integration Tests** (workflows completos con DB):
```bash
poetry run pytest tests/integration/ -v
```

**Unit Tests** (servicios aislados):
```bash
poetry run pytest tests/unit/ -v
```

**Performance Tests** (Locust - requiere servidor corriendo):
```bash
locust -f tests/performance/locustfile.py --host http://localhost:8000
```

### Tests por User Story

```bash
# User Story 1: Authentication
poetry run pytest tests/contract/test_auth_contracts.py -v
poetry run pytest tests/integration/test_auth_workflow.py -v

# User Story 2: Profiles
poetry run pytest tests/contract/test_profile_contracts.py -v
poetry run pytest tests/integration/test_profile_management.py -v

# User Story 3: Stats & Achievements
poetry run pytest tests/contract/test_stats_contracts.py -v
poetry run pytest tests/integration/test_stats_calculation.py -v

# User Story 4: Social Features
poetry run pytest tests/contract/test_social_contracts.py -v
poetry run pytest tests/integration/test_follow_workflow.py -v
```

---

## Cobertura de Código

### T246: Verificar ≥90% Coverage

```bash
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

**Ver reporte HTML:**
```bash
# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html
```

### Target de Cobertura (Constitución)

| Módulo | Target | Status |
|--------|--------|--------|
| **Overall** | ≥90% | ⏳ |
| api/ | ≥95% | ⏳ |
| services/ | 100% | ⏳ |
| models/ | ≥85% | ⏳ |
| schemas/ | ≥90% | ⏳ |
| utils/ | 100% | ⏳ |

### Configuración de Coverage (.coveragerc)

```ini
[run]
source = src
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

---

## Tests Existentes

### Resumen de Tests Implementados

#### User Story 1: Authentication (Phase 3)

**Contract Tests:**
- ✅ POST /auth/register - Success, username taken, email taken
- ✅ POST /auth/login - Success, invalid credentials, inactive user
- ✅ POST /auth/refresh - Success, invalid token
- ✅ POST /auth/request-verification - Success, already verified
- ✅ POST /auth/verify-email - Success, invalid token
- ✅ POST /auth/request-password-reset - Success, user not found
- ✅ POST /auth/reset-password - Success, invalid token

**Integration Tests:**
- ✅ Complete registration → verification → login flow
- ✅ Password reset request → verify token → reset password
- ✅ Refresh token flow
- ✅ Failed login attempts rate limiting

**Unit Tests:**
- ✅ AuthService.register_user()
- ✅ AuthService.verify_email()
- ✅ AuthService.request_password_reset()
- ✅ AuthService.reset_password()
- ✅ Password hashing validation
- ✅ JWT token creation/validation

#### User Story 2: Profiles (Phase 4)

**Contract Tests:**
- ✅ GET /users/{username} - Success, not found
- ✅ PATCH /users/{username} - Success, unauthorized
- ✅ POST /users/{username}/photo - Success, invalid format
- ✅ DELETE /users/{username}/photo - Success
- ✅ PATCH /users/{username}/privacy - Success

**Integration Tests:**
- ✅ Profile update workflow
- ✅ Photo upload → resize → storage
- ✅ Privacy settings update
- ✅ Profile view with stats preview

**Unit Tests:**
- ✅ ProfileService.get_profile()
- ✅ ProfileService.update_profile()
- ✅ ProfileService.upload_photo()
- ✅ ProfileService.delete_photo()
- ✅ File validation, resize, storage

#### User Story 3: Stats & Achievements (Phase 5)

**Contract Tests:**
- ✅ GET /users/{username}/stats - Success
- ✅ GET /users/{username}/achievements - Success
- ✅ GET /achievements - List all 9 achievements

**Integration Tests:**
- ✅ Stats update on trip publish
- ✅ Achievement awarding on milestones
- ✅ Country code mapping
- ✅ Zero-state handling

**Unit Tests:**
- ✅ StatsService.update_stats_on_trip_publish()
- ✅ StatsService.check_achievements()
- ✅ StatsService.award_achievement()
- ✅ Achievement criteria validation
- ✅ Idempotent achievement awarding

#### User Story 4: Social Features (Phase 6)

**Contract Tests:**
- ✅ POST /users/{username}/follow - Success, self-follow error
- ✅ DELETE /users/{username}/follow - Success
- ✅ GET /users/{username}/followers - Pagination
- ✅ GET /users/{username}/following - Pagination
- ✅ GET /users/{username}/follow-status - Following/not following

**Integration Tests:**
- ✅ Complete follow → verify lists → unfollow workflow
- ✅ Counter updates (followers_count, following_count)
- ✅ Pagination with 50+ users
- ✅ Self-follow prevention
- ✅ Unauthenticated redirect (401)

**Unit Tests:**
- ✅ SocialService.follow_user()
- ✅ SocialService.unfollow_user()
- ✅ SocialService.get_followers()
- ✅ SocialService.get_following()
- ✅ SocialService.get_follow_status()
- ✅ Duplicate follow prevention
- ✅ Transactional counter updates

### Total Tests Count

```
Contract Tests:   ~35 tests
Integration Tests: ~25 tests
Unit Tests:       ~40 tests
----------------------------
TOTAL:           ~100 tests
```

---

## T247: Edge Cases & Coverage Gaps

### Posibles Edge Cases a Añadir

#### Authentication
- [ ] Login con usuario que tiene cuenta bloqueada por intentos fallidos
- [ ] Registro con espacios en username/email
- [ ] Token expirado durante uso
- [ ] Múltiples verificaciones de email simultáneas

#### Profiles
- [ ] Upload de foto mientras otra está procesándose
- [ ] Bio con caracteres especiales (emoji, unicode)
- [ ] Actualización de perfil concurrente
- [ ] Foto corrupta o malformada

#### Stats
- [ ] Trip con distancia negativa
- [ ] Country code inválido
- [ ] Múltiples trips publicados simultáneamente
- [ ] Achievement desbloqueado múltiples veces en race condition

#### Social
- [ ] Follow/unfollow concurrente del mismo par de usuarios
- [ ] Paginación con total_count cambiando durante iteración
- [ ] Usuario borrado mientras se está siguiendo
- [ ] Counter inconsistency recovery

### Verificar Coverage de Líneas Críticas

```bash
# Ver líneas no cubiertas
poetry run pytest --cov=src --cov-report=term-missing | grep "TOTAL"

# Coverage detallado por archivo
poetry run pytest --cov=src --cov-report=annotate
```

---

## T248: Mensajes de Error en Español

### Verificación Automática

Script para buscar mensajes en inglés:

```bash
# Buscar strings en inglés en archivos de código
grep -r "raise ValueError\|raise HTTPException" src/ | \
  grep -v "\.py:.*#" | \
  grep -E "\"[A-Z][a-z]+ " | \
  grep -v "El usuario\|La contraseña\|No puedes\|Ya existe"
```

### Checklist de Mensajes en Español

#### Autenticación ✅
- ✅ "El usuario ya existe"
- ✅ "El correo ya está registrado"
- ✅ "Credenciales inválidas"
- ✅ "La cuenta no está verificada"
- ✅ "Token inválido o expirado"
- ✅ "El usuario no existe"

#### Perfiles ✅
- ✅ "El usuario '{username}' no existe"
- ✅ "No tienes permiso para modificar este perfil"
- ✅ "La foto debe ser JPG, PNG o WebP"
- ✅ "La foto es muy grande (máximo 5MB)"
- ✅ "Error al procesar la imagen"

#### Stats ✅
- ✅ "El usuario '{username}' no existe"
- ✅ "No se encontraron estadísticas"
- ✅ "Logro ya otorgado"

#### Social ✅
- ✅ "No puedes seguirte a ti mismo"
- ✅ "Ya sigues a {username}"
- ✅ "No sigues a {username}"
- ✅ "El usuario '{username}' no existe"

### Test para Verificar Mensajes

```python
# tests/test_spanish_errors.py
import pytest
from src.services.auth_service import AuthService

def test_all_errors_are_in_spanish():
    """Verify all error messages are in Spanish."""
    # Collect all error messages
    errors = []

    # Test various error scenarios
    # Should raise Spanish errors

    for error in errors:
        assert not error.startswith("The ")
        assert not error.startswith("Invalid ")
        assert not error.startswith("User ")
        # Verify Spanish patterns
        assert any([
            "El " in error,
            "La " in error,
            "No " in error,
            "Ya " in error,
            error.endswith("existe"),
            error.endswith("válido"),
        ])
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -

    - name: Install dependencies
      run: |
        cd backend
        poetry install

    - name: Run tests with coverage
      run: |
        cd backend
        poetry run pytest tests/ --cov=src --cov-report=xml --cov-report=term

    - name: Check coverage threshold
      run: |
        cd backend
        poetry run coverage report --fail-under=90

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

---

## Test Execution Checklist

Antes de marcar Testing & Coverage como completo:

- [ ] T245: ✅ Test suite completo ejecutado sin errores
- [ ] T246: ✅ Cobertura ≥90% en todos los módulos
- [ ] T247: ✅ Edge cases identificados y tests añadidos si necesario
- [ ] T248: ✅ Todos los mensajes de error en español verificados

### Comandos de Verificación

```bash
# 1. Run all tests
poetry run pytest tests/ -v

# 2. Check coverage
poetry run pytest tests/ --cov=src --cov-report=term | grep "TOTAL"

# 3. Verify Spanish errors
grep -r "raise ValueError\|raise HTTPException" src/ | \
  grep -E "\"[A-Z][a-z]+ " | \
  grep -v "El usuario\|La contraseña\|No puedes\|Ya existe"

# 4. Run quality checks
poetry run black src/ tests/ --check
poetry run ruff check src/ tests/
poetry run mypy src/
```

---

## Coverage Report Example

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/__init__.py                          0      0   100%
src/api/auth.py                         89      2    98%   145-146
src/api/profile.py                      76      1    99%   203
src/api/social.py                       98      0   100%
src/api/stats.py                        67      0   100%
src/services/auth_service.py           145      3    98%   234-236
src/services/profile_service.py        112      2    98%   267-268
src/services/social_service.py         156      0   100%
src/services/stats_service.py          189      4    98%   312-315
src/models/user.py                      45      5    89%   67-71
src/schemas/auth.py                     34      0   100%
src/utils/security.py                   28      0   100%
------------------------------------------------------------------
TOTAL                                 1039     17    98%
```

**Target: ≥90% ✅ PASSED (98%)**

---

## Manual Testing

Para testing manual interactivo de la API, consulta la documentación en `api/`:

### Guías de Testing Manual

- **[api/MANUAL_TESTING.md](api/MANUAL_TESTING.md)** - Testing con comandos `curl`
  - Prerequisitos y configuración
  - Todos los endpoints con ejemplos completos
  - Scripts bash para flujos end-to-end
  - Validaciones y casos de error
  - Troubleshooting

- **[api/POSTMAN_COLLECTION.md](api/POSTMAN_COLLECTION.md)** - Testing con Postman/Insomnia
  - Colección JSON lista para importar
  - Environment variables con auto-update scripts
  - Flujos de testing paso a paso
  - Tips para testing eficiente

### Quick Start - Manual Testing

```bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# 2. Guardar token
export TOKEN="<access_token_from_response>"

# 3. Crear trip
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Trip",
    "description": "Descripción de al menos 50 caracteres para testing...",
    "start_date": "2024-05-15"
  }'

# 4. Upload foto
curl -X POST "http://localhost:8000/trips/<TRIP_ID>/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_photo.jpg"
```

Ver [api/README.md](api/README.md) para documentación completa.

---

## Next Steps

Después de completar Testing & Coverage:
1. Deployment Preparation (T249-T253)
2. Final Validation (T254-T258)
