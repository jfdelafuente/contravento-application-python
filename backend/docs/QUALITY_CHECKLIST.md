# Code Quality Checklist - Phase 7

Este documento lista todas las verificaciones de calidad de código que deben ejecutarse antes del release.

## Pre-requisitos

Asegúrate de tener instaladas todas las herramientas:

```bash
cd backend
poetry install  # Instala todas las dependencias incluyendo dev tools
```

## T239: Black Formatter ✅

Formatear todo el código Python con Black (100 caracteres por línea).

### Comando

```bash
poetry run black src/ tests/ scripts/ --line-length 100
```

### Verificación

```bash
poetry run black src/ tests/ scripts/ --check --line-length 100
```

### Criterio de Éxito

- ✅ Todos los archivos formateados
- ✅ No hay diferencias pendientes
- ✅ Output: "All done! ✨ 🍰 ✨"

---

## T240: Ruff Linter ✅

Ejecutar ruff para detectar issues de código.

### Comando (Fix automático)

```bash
poetry run ruff check src/ tests/ scripts/ --fix
```

### Comando (Solo verificación)

```bash
poetry run ruff check src/ tests/ scripts/
```

### Configuración (.ruff.toml o pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/**/*.py" = ["S101"]  # Allow assert in tests
```

### Criterio de Éxito

- ✅ 0 errores
- ✅ 0 warnings (o warnings documentados como aceptables)

---

## T241: MyPy Type Checker ✅

Verificar tipos estáticos con MyPy.

### Comando

```bash
poetry run mypy src/ --strict
```

### Configuración (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Allow some flexibility for SQLAlchemy
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "alembic.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "passlib.*"
ignore_missing_imports = true
```

### Criterio de Éxito

- ✅ 0 type errors
- ✅ Todas las funciones tienen type hints
- ✅ Todos los parámetros y returns están tipados

---

## T242: Remove Commented Code & TODOs ✅

Revisar y limpiar código comentado y TODOs.

### Buscar código comentado

```bash
# Buscar bloques comentados (pueden ser legítimos o no)
grep -r "^#.*[a-z]" src/ | grep -v "Copyright\|TODO\|FIXME\|NOTE\|WARNING"
```

### Buscar TODOs

```bash
# Listar todos los TODOs/FIXMEs
grep -rn "TODO\|FIXME" src/
```

### Acción Requerida

Para cada TODO/FIXME encontrado:

1. **Resolver inmediatamente** si es trivial
2. **Crear issue** en GitHub si requiere trabajo
3. **Documentar** la razón si es intencional
4. **Eliminar** si ya no es relevante

### TODOs Aceptables (Documentados)

```python
# ✅ ACEPTABLE - Documentado con issue
# TODO: Implement rate limiting (#42)

# ✅ ACEPTABLE - Futuro conocido
# TODO: Add WebSocket support in v2.0

# ❌ NO ACEPTABLE - Vago
# TODO: Fix this
```

### Criterio de Éxito

- ✅ 0 bloques de código comentado sin justificación
- ✅ Todos los TODOs documentados o resueltos
- ✅ No hay código debug (print, console.log)

---

## T243: Google-Style Docstrings ✅

Verificar que todas las funciones públicas tengan docstrings.

### Formato Google-Style

```python
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two geographic points.

    Uses Haversine formula to compute great-circle distance.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        Distance in kilometers

    Raises:
        ValueError: If coordinates are out of valid range

    Example:
        >>> calculate_distance(40.7128, -74.0060, 34.0522, -118.2437)
        3935.746254609722
    """
    # Implementation...
```

### Verificar faltantes

```bash
# Buscar funciones públicas sin docstring
grep -Pzo "(?s)^def [a-z_]+\([^)]*\):\n(?!\s+\"\"\")" src/**/*.py
```

### Criterio de Éxito

- ✅ Todas las funciones/métodos públicos tienen docstrings
- ✅ Docstrings siguen formato Google-style
- ✅ Parámetros, returns, y raises documentados

---

## T244: No Magic Numbers ✅

Verificar que no haya números mágicos en el código.

### Buscar números mágicos

```bash
# Buscar asignaciones con números (excluir 0, 1, -1, 2 que son comunes)
grep -rn "[^0-9]\(3\|4\|5\|6\|7\|8\|9\|[0-9][0-9]\)" src/ | grep -v "test\|#"
```

### Números Aceptables vs Magic Numbers

```python
# ✅ ACEPTABLE - Constante nombrada
DEFAULT_PAGE_SIZE = 50
PROFILE_PHOTO_SIZE = 400
BCRYPT_DEFAULT_ROUNDS = 12

# ✅ ACEPTABLE - Configuración
max_size = settings.upload_max_size_mb

# ✅ ACEPTABLE - Números obvios
if count == 0:
if total > 1:

# ❌ MAGIC NUMBER - Sin contexto
if len(users) > 50:  # ¿Por qué 50?
time.sleep(300)      # ¿Por qué 300 segundos?
resize_photo(path, 400)  # ¿Por qué 400?
```

### Refactorización Necesaria

```python
# Antes (magic number)
if len(followers) > 50:
    return followers[:50]

# Después (constante)
MAX_FOLLOWERS_PER_PAGE = 50

if len(followers) > MAX_FOLLOWERS_PER_PAGE:
    return followers[:MAX_FOLLOWERS_PER_PAGE]
```

### Criterio de Éxito

- ✅ Todos los números significativos están en constantes
- ✅ Constantes tienen nombres descriptivos
- ✅ Configurables están en `config.py` o `.env`

---

## Ejecutar Todo a la Vez

Script all-in-one para verificar todo:

```bash
#!/bin/bash
# scripts/quality-check.sh

set -e  # Exit on error

echo "🔍 Running code quality checks..."

echo "📝 Black formatting..."
poetry run black src/ tests/ scripts/ --line-length 100 --check

echo "🔬 Ruff linting..."
poetry run ruff check src/ tests/ scripts/

echo "🔤 MyPy type checking..."
poetry run mypy src/

echo "✅ All quality checks passed!"
```

Hacer ejecutable:

```bash
chmod +x scripts/quality-check.sh
./scripts/quality-check.sh
```

---

## Checklist Final

Antes de marcar Phase 7 - Code Quality como completo:

- [ ] T239: Black formatter ejecutado sin errores
- [ ] T240: Ruff linter 0 issues
- [ ] T241: MyPy 0 type errors
- [ ] T242: Código comentado y TODOs revisados
- [ ] T243: Docstrings Google-style en funciones públicas
- [ ] T244: Magic numbers refactorizados a constantes

---

## Métricas de Éxito

Al completar estas tareas, el código debe cumplir:

| Métrica | Target | Status |
|---------|--------|--------|
| Black compliance | 100% | ⏳ |
| Ruff issues | 0 | ⏳ |
| MyPy errors | 0 | ⏳ |
| Docstring coverage | 100% (public functions) | ⏳ |
| Magic numbers | 0 | ⏳ |
| Code coverage | ≥90% | ⏳ |

---

## Notas

- **Estas herramientas deben ejecutarse localmente** ya que requieren Poetry y Python instalados
- **CI/CD debe ejecutar estas verificaciones** automáticamente en cada PR
- **Pre-commit hooks** pueden configurarse para ejecutar Black/Ruff automáticamente
- **MyPy strict mode** puede generar muchos warnings inicialmente - refactorizar gradualmente

---

## Next Steps

Una vez completada la calidad de código, proceder con:

- Testing & Coverage (T245-T248)
- Deployment Preparation (T249-T253)
- Final Validation (T254-T258)
