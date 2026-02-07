# Quality Gates

Code quality requirements and enforcement mechanisms for ContraVento.

**Audience**: Developers, Maintainers, CI/CD Administrators

---

## Table of Contents

- [Overview](#overview)
- [Coverage Requirements](#coverage-requirements)
- [Code Quality Standards](#code-quality-standards)
- [Enforcement Mechanisms](#enforcement-mechanisms)
- [Running Quality Checks Locally](#running-quality-checks-locally)
- [Bypassing Quality Gates](#bypassing-quality-gates)

---

## Overview

ContraVento enforces strict quality gates to maintain code quality, test coverage, and security standards. All code changes must pass these gates before merging.

**Quality Pillars**:
1. **Test Coverage** - Adequate test coverage for all code paths
2. **Code Formatting** - Consistent code style across the project
3. **Linting** - No code quality violations
4. **Type Safety** - Full type coverage with mypy/TypeScript
5. **Security** - No known vulnerabilities in dependencies

---

## Coverage Requirements

### Backend (Python)

**Minimum Coverage**: ≥90% across all modules

**Tools**: pytest with pytest-cov

**Measurement**:
```bash
cd backend
poetry run pytest --cov=src --cov-report=term --cov-report=html
```

**Coverage Breakdown**:
| Module | Target | Current | Status |
|--------|--------|---------|--------|
| `src/models/` | ≥95% | ~98% | ✅ |
| `src/services/` | ≥90% | ~95% | ✅ |
| `src/api/` | ≥90% | ~92% | ✅ |
| `src/utils/` | ≥90% | ~94% | ✅ |
| `src/schemas/` | ≥80% | ~85% | ✅ |

**Exclusions**:
- `src/main.py` (FastAPI app init)
- `src/config.py` (environment variables)
- `migrations/` (Alembic migrations)

**Configuration** (`.coveragerc`):
```ini
[run]
source = src
omit =
    */tests/*
    */migrations/*
    src/main.py
    src/config.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

**Enforcement**:
- CI/CD: Coverage report uploaded to Codecov
- PR comments: Codecov bot shows coverage diff
- Local: Run `poetry run pytest --cov` before commit

---

### Frontend (TypeScript)

**Minimum Coverage**: ≥80% (recommended, not strictly enforced)

**Tools**: Vitest + @vitest/coverage-v8

**Measurement**:
```bash
cd frontend
npm run test:unit -- --coverage
```

**Coverage Breakdown**:
| Module | Target | Status |
|--------|--------|--------|
| `src/components/` | ≥75% | 🚧 In progress |
| `src/hooks/` | ≥80% | ✅ High priority |
| `src/services/` | ≥85% | ✅ Critical |
| `src/utils/` | ≥90% | ✅ High coverage |

**Exclusions**:
- `src/main.tsx` (React app entry point)
- `src/vite-env.d.ts` (Vite types)
- `*.test.tsx` (test files themselves)

**Configuration** (`vitest.config.ts`):
```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/main.tsx',
        'src/vite-env.d.ts',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
});
```

**Enforcement**:
- CI/CD: Coverage report uploaded to Codecov
- Local: Run `npm run test:unit -- --coverage` before commit

---

### E2E Tests (Playwright)

**Minimum Pass Rate**: ≥80% (27/33 tests)

**Current Status**: ⚠️ 72.7% (24/33 passing) - **E2E tests disabled in CI**

**Failing Tests**:
- P28: Logout redirect failure
- P29: Duplicate username banner issue
- +7 other flaky tests

**Reactivation Criteria**:
1. Fix P28 and P29 (critical failures)
2. Stabilize remaining 7 tests
3. Achieve ≥80% pass rate
4. Pass 3 consecutive CI runs without failures

**Measurement**:
```bash
cd frontend
npx playwright test --reporter=html
```

---

## Code Quality Standards

### Backend (Python)

#### 1. Code Formatting (black)

**Style**: PEP 8 with 100 character line length

**Command**:
```bash
poetry run black src/ tests/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | migrations
)/
'''
```

**Enforcement**:
- CI/CD: `black --check` (fails if formatting needed)
- Pre-commit hook: Auto-format on commit (optional)
- Editor: Use black formatter extension

---

#### 2. Linting (ruff)

**Rules**: Enforce PEP 8, detect common bugs, enforce best practices

**Command**:
```bash
poetry run ruff check src/ tests/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = [
    "E501",  # Line too long (handled by black)
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports OK in __init__
```

**Common Violations**:
| Code | Description | Fix |
|------|-------------|-----|
| F401 | Unused import | Remove import |
| E402 | Module import not at top | Move import to top |
| N803 | Argument name should be lowercase | Rename variable |
| B008 | Do not use mutable defaults | Use `None` and assign in function |

**Auto-fix**:
```bash
poetry run ruff check src/ tests/ --fix
```

---

#### 3. Type Checking (mypy)

**Strictness**: Full type coverage required for `src/` modules

**Command**:
```bash
poetry run mypy src/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
check_untyped_defs = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**Common Errors**:
| Error | Description | Fix |
|-------|-------------|-----|
| `error: Function is missing a return type annotation` | No return type | Add `-> None` or `-> Type` |
| `error: Argument 1 has incompatible type` | Type mismatch | Fix type or use cast |
| `error: Need type annotation for variable` | Variable type unclear | Add `: Type` annotation |

**Type Hints Example**:
```python
# Good ✅
def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieve user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

# Bad ❌ (no type hints)
def get_user_by_email(db, email):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

---

### Frontend (TypeScript/React)

#### 1. Linting (ESLint)

**Rules**: React best practices, TypeScript conventions, accessibility checks

**Command**:
```bash
npm run lint
```

**Configuration** (`.eslintrc.cjs`):
```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'react/prop-types': 'off',  // TypeScript handles this
    'react/react-in-jsx-scope': 'off',  // Not needed in React 18+
  },
};
```

**Common Violations**:
| Rule | Description | Fix |
|------|-------------|-----|
| `@typescript-eslint/no-unused-vars` | Unused variable | Remove or prefix with `_` |
| `@typescript-eslint/no-explicit-any` | Using `any` type | Provide explicit type |
| `jsx-a11y/alt-text` | Image missing alt text | Add `alt` attribute |
| `react-hooks/exhaustive-deps` | Missing dependency in useEffect | Add to dependency array |

**Auto-fix**:
```bash
npm run lint -- --fix
```

---

#### 2. Type Checking (TypeScript)

**Strictness**: Strict mode enabled

**Command**:
```bash
npm run type-check
```

**Configuration** (`tsconfig.json`):
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**Common Errors**:
| Error | Fix |
|-------|-----|
| `Object is possibly 'null'` | Add null check: `if (obj) { ... }` |
| `Property 'X' does not exist on type` | Fix type or add to interface |
| `Type 'undefined' is not assignable to type` | Use optional chaining: `obj?.prop` |

---

## Enforcement Mechanisms

### Pre-Commit Hooks (Optional)

**Setup with husky**:
```bash
# Install husky
npm install --save-dev husky

# Enable git hooks
npx husky install

# Add pre-commit hook
npx husky add .husky/pre-commit "npm run lint && npm run type-check"
```

**Backend pre-commit** (`.git/hooks/pre-commit`):
```bash
#!/bin/sh
cd backend
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
```

---

### GitHub Actions (Automated)

**Quality jobs run on**:
- Every pull request
- Every push to `main` or `develop`

**Quality gates must pass before**:
- Tests can run
- Code can be merged
- Deployment can occur

**See**: [GitHub Actions](github-actions.md) for full CI/CD configuration

---

### Branch Protection Rules

**Required for `main` and `develop` branches**:

1. **Require pull request reviews**:
   - Minimum 1 approval required
   - Dismiss stale reviews on new commits

2. **Require status checks to pass**:
   - ✅ Backend Quality Checks
   - ✅ Frontend Quality Checks
   - ✅ Backend Tests
   - ✅ Frontend Tests
   - ⚠️ E2E Tests (currently disabled)

3. **Require branches to be up to date**:
   - Prevent merge of stale code

4. **Do not allow bypassing**:
   - No force pushes
   - No deletions
   - Administrators included in protections

---

## Running Quality Checks Locally

### Backend

**Run all checks**:
```bash
cd backend

# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/

# Run tests with coverage
poetry run pytest --cov=src --cov-report=term --cov-report=html
```

**Single command** (add to `Makefile` or script):
```bash
#!/bin/bash
cd backend
poetry run black src/ tests/ && \
poetry run ruff check src/ tests/ && \
poetry run mypy src/ && \
poetry run pytest --cov=src --cov-report=term
```

---

### Frontend

**Run all checks**:
```bash
cd frontend

# Lint code
npm run lint

# Type check
npm run type-check

# Run tests with coverage
npm run test:unit -- --coverage
```

**Single command** (add to `package.json`):
```json
{
  "scripts": {
    "quality": "npm run lint && npm run type-check && npm run test:unit -- --coverage"
  }
}
```

Then run:
```bash
npm run quality
```

---

## Bypassing Quality Gates

### When to Bypass

**⚠️ RARELY JUSTIFIED** - Quality gates exist to prevent bugs and maintain standards.

**Valid reasons**:
- Hotfix for critical production bug
- Temporary workaround for external dependency issue
- Documentation-only changes (no code impact)

**Invalid reasons**:
- "I don't have time to fix it"
- "The linter is annoying"
- "It works on my machine"

---

### How to Bypass (Emergency Only)

#### 1. Disable Specific Linting Rule

**Backend (ruff)**:
```python
# Disable for single line
result = some_function()  # noqa: E501

# Disable for block
# ruff: noqa: E501
long_line_that_cannot_be_wrapped = ...
```

**Frontend (ESLint)**:
```typescript
// Disable for single line
const data = fetchData() as any;  // eslint-disable-line @typescript-eslint/no-explicit-any

// Disable for file
/* eslint-disable @typescript-eslint/no-explicit-any */
```

---

#### 2. Skip Type Checking

**Backend (mypy)**:
```python
result = some_untyped_function()  # type: ignore
```

**Frontend (TypeScript)**:
```typescript
// @ts-ignore
const value = problematicCode();
```

---

#### 3. Skip Tests (DO NOT DO THIS)

**❌ Never skip tests in production code**

**Only acceptable for**:
- Tests known to be flaky (mark with `pytest.mark.skip` and create issue)
- Tests dependent on external service (mark with `pytest.mark.integration`)

```python
@pytest.mark.skip(reason="Flaky test - see issue #123")
def test_flaky_feature():
    ...
```

---

### Documenting Bypasses

**Every bypass must include**:
1. **Comment explaining why** (inline or above)
2. **Link to tracking issue** (GitHub issue number)
3. **Plan for resolution** (in issue description)

**Example**:
```python
# TODO: Fix type inference for third-party library
# Issue: #456
# Workaround: Type ignore until library updates types
result = untyped_library_function()  # type: ignore
```

---

## Quality Metrics Dashboard

### Codecov

**URL**: `https://codecov.io/gh/{org}/contravento`

**Metrics**:
- Overall coverage percentage
- Coverage per file
- Coverage diff in PRs
- Historical coverage trends

**Integration**:
- Automatic PR comments
- GitHub status checks
- Slack notifications (optional)

---

### GitHub Insights

**Code Quality**:
- Pull Request review history
- Failed CI/CD runs
- Security alerts (Dependabot + Trivy)

**Test Results**:
- Test suite duration
- Flaky test detection
- Historical pass/fail rates

---

## Related Documentation

- **[GitHub Actions](github-actions.md)** - CI/CD pipeline configuration
- **[Backend Tests](../backend/integration-tests.md)** - Backend testing guide
- **[Frontend Tests](../frontend/e2e-tests.md)** - Frontend testing guide
- **[Accessibility Testing](../frontend/accessibility.md)** - WCAG 2.1 AA compliance

---

**Last Updated**: 2026-02-07
**Coverage Target**: Backend ≥90%, Frontend ≥80%
**Enforcement**: Automated via GitHub Actions
