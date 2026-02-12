# Contributing to ContraVento

¡Gracias por tu interés en contribuir a ContraVento! Este documento proporciona guías y mejores prácticas para contribuir al proyecto.

---

## 📋 Tabla de Contenidos

1. [Código de Conducta](#código-de-conducta)
2. [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
3. [Branching Strategy](#branching-strategy)
4. [Commit Messages](#commit-messages)
5. [Pull Request Process](#pull-request-process)
6. [Coding Standards](#coding-standards)
7. [Testing Requirements](#testing-requirements)

---

## Código de Conducta

Este proyecto sigue principios de colaboración respetuosa y profesional. Esperamos que todos los contributors:

- Sean respetuosos y constructivos en sus comentarios
- Acepten críticas constructivas con profesionalismo
- Se enfoquen en lo mejor para el proyecto y la comunidad
- Ayuden a otros contributors cuando sea posible

---

## ¿Cómo Puedo Contribuir?

### Reportar Bugs

1. **Busca primero**: Verifica que el bug no esté ya reportado en [Issues](https://github.com/jfdelafuente/contravento-application-python/issues)
2. **Usa el template**: Crea un nuevo issue con el template de bug report
3. **Proporciona contexto**:
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots/logs si aplica
   - Entorno (browser, OS, versión)

### Sugerir Features

1. **Verifica primero**: Revisa [ROADMAP.md](ROADMAP.md) y existing issues
2. **Crea un issue**: Usa el template de feature request
3. **Proporciona detalles**:
   - Problema que resuelve
   - Propuesta de solución
   - Alternativas consideradas
   - Mockups/wireframes (si aplica)

### Contribuir Código

Ver secciones siguientes para proceso detallado.

---

## Branching Strategy

ContraVento sigue un **Git Flow simplificado**. Ver [documentación completa](docs/operations/BRANCHING_STRATEGY_CICD.md).

### Ramas Principales

- **`main`**: Producción (https://contravento.com)
- **`develop`**: Staging (https://staging.contravento.com)

### Tipos de Ramas

| Tipo | Naming | Ejemplo |
|------|--------|---------|
| Feature | `feature/NNN-short-description` | `feature/019-followers-tooltip` |
| Bugfix | `bugfix/fix-specific-issue` | `bugfix/fix-gpx-timeout` |
| Hotfix | `hotfix/vX.Y.Z-critical-issue` | `hotfix/v1.2.1-auth-bypass` |

### Workflow

```bash
# 1. Sincronizar develop
git checkout develop
git pull origin develop

# 2. Crear feature branch
git checkout -b feature/NNN-my-feature

# 3. Desarrollo (commits pequeños)
git add .
git commit -m "feat(scope): description"

# 4. Push a GitHub
git push origin feature/NNN-my-feature

# 5. Crear Pull Request
# GitHub UI: feature/NNN-my-feature → develop
```

---

## Commit Messages

Seguimos **Conventional Commits** para mensajes estructurados.

### Formato

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

- **feat**: Nueva feature
- **fix**: Bug fix
- **docs**: Cambios en documentación
- **chore**: Tareas de mantenimiento (deps, configs)
- **refactor**: Refactoring sin cambios funcionales
- **test**: Añadir o modificar tests
- **perf**: Mejoras de performance
- **style**: Cambios de formato (no afectan lógica)

### Scopes (Ejemplos)

- `dashboard`, `auth`, `trips`, `gpx`, `profile`
- `backend`, `frontend`, `api`, `db`
- `docs`, `ci`, `deploy`

### Ejemplos

```bash
✅ GOOD:
feat(dashboard): add followers tooltip on hover
fix(gpx): resolve upload timeout for large files
docs(api): update authentication endpoint examples
chore(deps): bump react from 18.2.0 to 18.3.0
refactor(trips): extract TripCard to separate component
test(auth): add unit tests for JWT validation

❌ BAD:
Update stuff
Fixed bug
WIP
Changes
```

### Reglas

- **Subject**: Imperativo presente ("add" no "added" ni "adds")
- **Subject**: Lowercase (excepto nombres propios)
- **Subject**: Sin punto final
- **Subject**: Max 72 caracteres
- **Body**: Opcional, explicar el "por qué" no el "qué"
- **Footer**: Referencias a issues (`Fixes #123`, `Closes #456`)

---

## Pull Request Process

### 1. Antes de Crear el PR

- [ ] ✅ Todos los tests pasan localmente
- [ ] ✅ Código formateado (black, eslint)
- [ ] ✅ Type checking pasa (mypy, tsc)
- [ ] ✅ Coverage ≥90% (backend) / ≥80% (frontend)
- [ ] ✅ No warnings en consola/logs
- [ ] ✅ Documentación actualizada (si aplica)

```bash
# Backend checks
cd backend
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
poetry run pytest --cov=src --cov-fail-under=90

# Frontend checks
cd frontend
npm run lint
npm run type-check
npm run test -- --coverage
```

### 2. Crear el PR

**Title**: Descriptivo y conciso
```
✅ Feature 019: Dashboard Followers/Following Tooltips
✅ Fix: GPX upload timeout for files >10MB
✅ Docs: Update deployment guide for staging environment

❌ Update
❌ Fix stuff
❌ PR
```

**Description**: Usar template

```markdown
## Descripción
Implementa tooltips interactivos en las tarjetas de seguidores/siguiendo del dashboard...

## Tipo de Cambio
- [x] Nueva feature (non-breaking)
- [ ] Bug fix (non-breaking)
- [ ] Breaking change
- [ ] Requiere actualización de documentación

## ¿Cómo se ha testeado?
- [x] Unit tests (23 tests añadidos)
- [x] E2E tests (hover behavior, keyboard nav)
- [x] Manual testing en Chrome, Firefox, Safari
- [x] Accessibility testing (WCAG 2.1 AA)

## Checklist
- [x] Código sigue style guide del proyecto
- [x] Self-review completado
- [x] Comentarios añadidos en código complejo
- [x] Documentación actualizada
- [x] Tests añadidos (coverage ≥90%)
- [x] CI/CD pipeline pasa

## Screenshots (si aplica)
[Adjuntar screenshots de UI changes]

## Referencias
- Closes #59
- Spec: specs/019-followers-tooltip/spec.md
```

**Labels**: Añadir labels apropiados
- `feature`, `bugfix`, `documentation`
- `frontend`, `backend`, `full-stack`
- `high priority`, `medium priority`, `low priority`

**Reviewers**: Asignar 1+ reviewers

### 3. Durante Code Review

**Como Autor**:
- Responde a comentarios en <24 horas
- Marca conversaciones como resueltas cuando aplicas cambios
- Haz commits adicionales (no force push durante review)
- Pide clarificación si no entiendes un comentario

**Como Reviewer**:
- Revisa en <48 horas
- Sé constructivo y específico
- Usa "Suggest change" para propuestas concretas
- Aprueba solo cuando todo está listo (no "LGTM con cambios menores")

### 4. Merge

**Criterios para Mergear**:
- ✅ Al menos 1 approval
- ✅ Todos los CI checks pasan
- ✅ Conversaciones resueltas
- ✅ Branch actualizado con base (develop)

**Merge Strategy**: **Squash and merge** (preferido)
- Mantiene historia limpia en develop/main
- Un commit por PR
- Edita mensaje final si necesario

**Después de Merge**:
```bash
# Eliminar rama local
git branch -d feature/NNN-my-feature

# Eliminar rama remota (se hace auto en GitHub, pero si no:)
git push origin --delete feature/NNN-my-feature

# Sincronizar develop
git checkout develop
git pull origin develop
```

---

## Coding Standards

### Backend (Python)

**Style Guide**: PEP 8 + Black formatter

```python
# Formatting
poetry run black src/ tests/

# Linting
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/
```

**Reglas Específicas**:
- Type hints obligatorios en funciones públicas
- Docstrings en Google style para funciones públicas
- Line length: 100 caracteres (black default)
- Imports ordenados (isort config in pyproject.toml)
- No usar `type: ignore` (usar `type: ignore[specific-error]`)

**Example**:
```python
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_followers(
    db: AsyncSession,
    username: str,
    limit: int = 20
) -> List[UserSummaryForFollow]:
    """
    Get list of users following the specified user.

    Args:
        db: Database session
        username: Username to fetch followers for
        limit: Maximum number of followers to return

    Returns:
        List of follower user summaries

    Raises:
        UserNotFoundError: If username doesn't exist
    """
    # Implementation...
```

### Frontend (TypeScript + React)

**Style Guide**: Airbnb + ESLint config

```bash
# Linting
npm run lint

# Auto-fix
npm run lint:fix

# Type checking
npm run type-check
```

**Reglas Específicas**:
- Functional components con TypeScript
- Props types explícitos (interface)
- Hooks en orden (useState, useEffect, custom hooks)
- Extract custom hooks para lógica reusable
- Evitar `any` (usar `unknown` o type específico)
- CSS Modules o styled-components (no inline styles)

**Example**:
```typescript
import React, { useState, useEffect } from 'react';
import type { UserSummaryForFollow } from '../../services/followService';

interface SocialStatTooltipProps {
  users: UserSummaryForFollow[];
  totalCount: number;
  type: 'followers' | 'following';
  visible: boolean;
}

export const SocialStatTooltip: React.FC<SocialStatTooltipProps> = ({
  users,
  totalCount,
  type,
  visible,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Effect logic
  }, [users]);

  if (!visible) return null;

  return (
    <div className="social-stat-tooltip">
      {/* Component JSX */}
    </div>
  );
};
```

### Naming Conventions

| Tipo | Convention | Ejemplo |
|------|-----------|---------|
| **Variables** | camelCase | `userName`, `isLoading` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_FILE_SIZE`, `API_URL` |
| **Functions** | camelCase | `getUserFollowers()`, `handleClick()` |
| **Classes** | PascalCase | `UserService`, `TripModel` |
| **Components** | PascalCase | `SocialStatTooltip`, `TripCard` |
| **Interfaces** | PascalCase + I prefix (optional) | `UserSummary`, `IUserProps` |
| **Types** | PascalCase | `FollowersListResponse` |
| **Files** | camelCase or kebab-case | `userService.ts`, `trip-card.tsx` |

---

## Testing Requirements

### Coverage Thresholds

- **Backend**: ≥90% (enforced in CI)
- **Frontend**: ≥80% (recommended, not enforced yet)

### Test Structure

**Backend** (`pytest`):
```
tests/
├── unit/               # Business logic tests
│   ├── test_auth_service.py
│   └── test_trip_service.py
├── integration/        # API endpoint tests
│   ├── test_auth_api.py
│   └── test_trips_api.py
└── contract/           # OpenAPI schema validation
    └── test_openapi_contracts.py
```

**Frontend** (`vitest` + `playwright`):
```
tests/
├── unit/               # Component unit tests
│   ├── SocialStatTooltip.test.tsx
│   └── useFollowersTooltip.test.ts
└── e2e/                # End-to-end tests
    ├── auth.spec.ts
    └── dashboard.spec.ts
```

### Writing Tests

**Backend Example** (pytest):
```python
import pytest
from src.services.user_service import UserService

@pytest.mark.asyncio
async def test_get_user_followers(db_session, test_user):
    """Test getting followers list for a user."""
    # Arrange
    service = UserService(db_session)

    # Act
    followers = await service.get_followers(test_user.username)

    # Assert
    assert len(followers) == 2
    assert followers[0].username == "follower1"
```

**Frontend Example** (vitest + testing-library):
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { SocialStatTooltip } from './SocialStatTooltip';

describe('SocialStatTooltip', () => {
  it('renders user list correctly', () => {
    const mockUsers = [
      { user_id: '1', username: 'user1', profile_photo_url: null },
    ];

    render(
      <SocialStatTooltip
        users={mockUsers}
        totalCount={10}
        type="followers"
        visible={true}
      />
    );

    expect(screen.getByText('user1')).toBeInTheDocument();
    expect(screen.getByText('+ 9 más · Ver todos')).toBeInTheDocument();
  });
});
```

### Running Tests

```bash
# Backend - All tests
cd backend
poetry run pytest

# Backend - Specific test
poetry run pytest tests/unit/test_auth_service.py -v

# Backend - With coverage
poetry run pytest --cov=src --cov-report=html

# Frontend - All tests
cd frontend
npm run test

# Frontend - Watch mode
npm run test:watch

# Frontend - Coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

---

## Questions?

- **Branching**: Ver [Branching Strategy](docs/operations/BRANCHING_STRATEGY_CICD.md)
- **Deployment**: Ver [Deployment Guide](docs/deployment/README.md)
- **CI/CD**: Ver [GitHub Workflows](/.github/workflows/README.md)
- **Architecture**: Ver [CLAUDE.md](CLAUDE.md)

**Para dudas específicas**:
- Crea un issue en GitHub
- Contacta al team lead
- Únete a #dev-contravento en Slack

---

¡Gracias por contribuir a ContraVento! 🚴‍♂️
