# Code Quality - Standards and Tools

Complete guide to code quality standards, linting, formatting, and type checking at ContraVento.

**Audience**: All developers

---

## Table of Contents

- [Quality Standards](#quality-standards)
- [Tools](#tools)
- [Daily Workflow](#daily-workflow)
- [Configuration](#configuration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## Quality Standards

ContraVento enforces strict code quality standards:

| Standard | Requirement | Tool | Command |
|----------|-------------|------|---------|
| **Formatting** | 100% compliance | black | `poetry run black` |
| **Linting** | Zero warnings | ruff | `poetry run ruff check` |
| **Type Checking** | Zero errors | mypy | `poetry run mypy` |
| **Test Coverage** | ≥90% | pytest | `poetry run pytest --cov` |
| **Documentation** | Google-style docstrings | Manual | Review in PR |

**Constitution Requirement**:

> "PEP 8 with black formatter (100 char line length). Type hints required on ALL functions. Google-style docstrings for public functions."
> — ContraVento Constitution, Section I: Code Quality

---

## Tools

### 1. Black - Code Formatter

**Purpose**: Automatic code formatting (opinionated, zero config)

**Why Black**:
- ✅ Deterministic (same input → same output)
- ✅ No configuration debates
- ✅ Saves time (no manual formatting)
- ✅ Consistent style across codebase

**Configuration**: `pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.tox
  | venv
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''
```

**Usage**:
```bash
# Format all files
poetry run black src/ tests/

# Check without modifying
poetry run black --check src/ tests/

# Format specific file
poetry run black src/services/trip_service.py
```

**Example**:

Before Black:
```python
def my_function(param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    return param1+param2+param3+param4+param5+param6+param7+param8+param9+param10
```

After Black:
```python
def my_function(
    param1,
    param2,
    param3,
    param4,
    param5,
    param6,
    param7,
    param8,
    param9,
    param10,
):
    return (
        param1
        + param2
        + param3
        + param4
        + param5
        + param6
        + param7
        + param8
        + param9
        + param10
    )
```

---

### 2. Ruff - Linter

**Purpose**: Fast Python linter (replaces Flake8, isort, pyupgrade)

**Why Ruff**:
- ✅ 10-100x faster than Flake8
- ✅ Combines multiple tools (Flake8, isort, pyupgrade)
- ✅ Auto-fix for many issues
- ✅ Over 700 lint rules

**Configuration**: `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]

ignore = [
    "E501",  # line too long (handled by black)
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
```

**Usage**:
```bash
# Check all files
poetry run ruff check src/ tests/

# Auto-fix issues
poetry run ruff check --fix src/ tests/

# Check specific file
poetry run ruff check src/services/trip_service.py
```

**Common Issues**:

```python
# ❌ BAD - Unused import
import json  # F401: imported but unused

# ✅ GOOD - Remove unused
# (no import)

# ❌ BAD - Undefined name
result = undefined_variable  # F821: undefined name

# ✅ GOOD - Define first
undefined_variable = "value"
result = undefined_variable

# ❌ BAD - Mutable default argument
def my_function(items=[]):  # B006: mutable default
    items.append(1)

# ✅ GOOD - Use None
def my_function(items=None):
    if items is None:
        items = []
    items.append(1)
```

---

### 3. Mypy - Type Checker

**Purpose**: Static type checking for Python

**Why Type Hints**:
- ✅ Catch bugs before runtime
- ✅ Better IDE autocomplete
- ✅ Self-documenting code
- ✅ Easier refactoring

**Configuration**: `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

# Ignore missing imports for third-party libraries
[[tool.mypy.overrides]]
module = [
    "sqlalchemy.*",
    "pydantic.*",
]
ignore_missing_imports = true
```

**Usage**:
```bash
# Check all files
poetry run mypy src/

# Check specific file
poetry run mypy src/services/trip_service.py

# Show error codes
poetry run mypy --show-error-codes src/
```

**Type Hints Examples**:

```python
# ✅ GOOD - Typed function
async def get_trip(trip_id: str) -> Trip:
    """Get trip by ID."""
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    return result.scalar_one()

# ❌ BAD - No types
async def get_trip(trip_id):
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    return result.scalar_one()

# ✅ GOOD - Optional types
from typing import Optional

async def find_trip(trip_id: str) -> Optional[Trip]:
    """Find trip by ID, returns None if not found."""
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    return result.scalar_one_or_none()

# ✅ GOOD - List/Dict types
from typing import List, Dict

def process_tags(tags: List[str]) -> Dict[str, int]:
    """Count tag occurrences."""
    return {tag: tags.count(tag) for tag in set(tags)}

# ✅ GOOD - Union types (Python 3.10+)
def get_value(key: str) -> str | int | None:
    """Get value by key."""
    return values.get(key)
```

---

### 4. Pytest - Test Coverage

**Purpose**: Measure test coverage

**Coverage Requirement**: ≥90% for all modules

**Configuration**: `pyproject.toml`

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
]
testpaths = ["tests"]
pythonpath = ["."]
```

**Usage**:
```bash
# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Fail if coverage < 90%
poetry run pytest --cov=src --cov-fail-under=90

# View coverage report
open htmlcov/index.html
```

**Coverage Report Example**:

```
Name                            Stmts   Miss  Cover
---------------------------------------------------
src/services/trip_service.py      156      8    95%
src/services/auth_service.py      124      2    98%
src/utils/validators.py            45      0   100%
---------------------------------------------------
TOTAL                             325     10    97%
```

**Interpreting Coverage**:
- **Green (≥95%)**: Excellent coverage
- **Yellow (90-94%)**: Acceptable, could improve
- **Red (<90%)**: Insufficient, write more tests

---

## Daily Workflow

### Before Committing

**Run all quality checks**:

```bash
cd backend

# 1. Format code
poetry run black src/ tests/

# 2. Lint code
poetry run ruff check --fix src/ tests/

# 3. Type check
poetry run mypy src/

# 4. Run tests with coverage
poetry run pytest --cov=src --cov-fail-under=90
```

**Expected Output** (all passing):

```
✅ All done! ✨ 🍰 ✨
42 files reformatted, 0 files left unchanged.

✅ All checks passed!

✅ Success: no issues found in 42 source files

✅ 156 passed in 4.23s
Coverage: 97%
```

---

### Quick Check Script

Create a convenience script for quality checks:

**File**: `backend/check_quality.sh`

```bash
#!/bin/bash
set -e

echo "🔍 Checking code quality..."

echo "📝 Formatting with black..."
poetry run black src/ tests/

echo "🔎 Linting with ruff..."
poetry run ruff check --fix src/ tests/

echo "🔬 Type checking with mypy..."
poetry run mypy src/

echo "🧪 Running tests with coverage..."
poetry run pytest --cov=src --cov-fail-under=90

echo "✅ All quality checks passed!"
```

**Usage**:
```bash
chmod +x backend/check_quality.sh
./backend/check_quality.sh
```

---

## Configuration

### pyproject.toml (Complete)

**File**: `backend/pyproject.toml`

```toml
[tool.poetry]
name = "contravento"
version = "0.1.0"
description = "Cycling social platform"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.109.0"
sqlalchemy = "^2.0.25"
pydantic = "^2.5.3"
# ... other dependencies

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.23.3"
black = "^24.1.1"
ruff = "^0.1.14"
mypy = "^1.8.0"

# Black configuration
[tool.black]
line-length = 100
target-version = ['py312']

# Ruff configuration
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]

# Mypy configuration
[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
warn_return_any = true

# Pytest configuration
[tool.pytest.ini_options]
minversion = "7.0"
addopts = ["--cov=src", "--cov-report=html"]
testpaths = ["tests"]
```

---

## Pre-commit Hooks

**Recommended** (not yet implemented):

Pre-commit hooks run quality checks automatically before each commit.

### Setup

**Install pre-commit**:
```bash
pip install pre-commit
```

**Configuration**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Install hooks**:
```bash
pre-commit install
```

**Usage**:
```bash
# Hooks run automatically on git commit

# Run manually on all files
pre-commit run --all-files
```

---

## CI/CD Integration

**GitHub Actions** (planned):

**File**: `.github/workflows/quality.yml`

```yaml
name: Code Quality

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: |
          cd backend
          poetry install

      - name: Format check (black)
        run: |
          cd backend
          poetry run black --check src/ tests/

      - name: Lint (ruff)
        run: |
          cd backend
          poetry run ruff check src/ tests/

      - name: Type check (mypy)
        run: |
          cd backend
          poetry run mypy src/

      - name: Tests with coverage
        run: |
          cd backend
          poetry run pytest --cov=src --cov-fail-under=90

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

**Quality Gates**:
- ✅ Black format check must pass
- ✅ Ruff lint with zero warnings
- ✅ Mypy type check with zero errors
- ✅ Test coverage ≥90%

**PR cannot merge** if any check fails.

---

## Troubleshooting

### Black and Ruff Conflict

**Problem**: Black formats code, Ruff reports lint errors

**Cause**: Line length mismatch

**Solution**: Ensure both use same line length (100):

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
```

---

### Mypy Import Errors

**Problem**: `error: Cannot find implementation or library stub for module`

**Cause**: Third-party library missing type stubs

**Solution**: Add to mypy overrides:

```toml
[[tool.mypy.overrides]]
module = ["problematic_module.*"]
ignore_missing_imports = true
```

---

### Coverage Too Low

**Problem**: `FAIL Required test coverage of 90% not reached`

**Cause**: Uncovered code paths

**Solution**: View coverage report and write tests:

```bash
# Generate HTML report
poetry run pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html

# Find red lines (uncovered)
# Write tests for those lines
```

---

### Ruff False Positive

**Problem**: Ruff reports issue that's actually correct

**Cause**: Linter limitation

**Solution**: Add `# noqa` comment (use sparingly):

```python
# Disable specific rule for one line
result = some_complex_logic()  # noqa: C901

# Disable all rules for one line (avoid)
result = some_complex_logic()  # noqa
```

**Better solution**: Refactor code to fix issue properly.

---

## Best Practices

### 1. Format Before Linting

```bash
# ✅ GOOD - Format first
poetry run black src/ tests/
poetry run ruff check src/ tests/

# ❌ BAD - Lint first (may get formatting errors)
poetry run ruff check src/ tests/
poetry run black src/ tests/
```

---

### 2. Type All Public Functions

```python
# ✅ GOOD - Public function with types
async def get_trip(trip_id: str) -> Trip:
    """Get trip by ID."""
    pass

# ❌ BAD - Public function without types
async def get_trip(trip_id):
    """Get trip by ID."""
    pass

# ✅ OK - Private function without types (discouraged but acceptable)
def _internal_helper(value):
    return value * 2
```

---

### 3. Use Auto-fix Where Possible

```bash
# ✅ GOOD - Let tools auto-fix
poetry run black src/  # Formats automatically
poetry run ruff check --fix src/  # Fixes automatically

# ❌ BAD - Manual fixes
# Manually formatting code to match Black
# Manually fixing import order
```

---

### 4. Run Checks Frequently

```bash
# ✅ GOOD - Run checks after each feature
# Write feature
poetry run pytest tests/unit/test_new_feature.py
poetry run black src/services/new_service.py
poetry run ruff check src/services/new_service.py

# ❌ BAD - Run checks once before commit
# Write 10 features
# Run checks (many failures)
```

---

## Related Documentation

- **[Getting Started](getting-started.md)** - Developer onboarding
- **[TDD Workflow](tdd-workflow.md)** - Test-first development
- **[Testing Strategies](../testing/README.md)** - Complete testing guide
- **[Backend Architecture](../architecture/backend/overview.md)** - Code structure

---

**Last Updated**: 2026-02-07
**Coverage Requirement**: ≥90%
**Standards**: Black + Ruff + Mypy (mandatory)
