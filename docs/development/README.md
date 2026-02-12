# Development Documentation - ContraVento

Developer workflows, tools, and best practices for contributing to ContraVento.

**Audience**: Developers (new and existing contributors)

---

## Quick Start for New Developers

1. **[Getting Started](getting-started.md)** - First-time setup from zero to coding
2. **[TDD Workflow](tdd-workflow.md)** - Test-Driven Development process
3. **[Code Quality](code-quality.md)** - Linting, formatting, type checking

**Estimated Setup Time**: 10-15 minutes (with local-dev mode)

---

## Developer Workflows

### Daily Development

```bash
# 1. Start development environment
./run-local-dev.sh  # Backend (SQLite, instant startup)

# 2. Make changes (TDD: test first!)
cd backend
poetry run pytest tests/unit/test_my_feature.py  # Write test (Red)
# Write implementation code                       # Make it pass (Green)
poetry run pytest tests/unit/test_my_feature.py  # Verify (Green)
# Refactor while keeping tests passing            # Refactor

# 3. Quality checks
poetry run black src/ tests/        # Format
poetry run ruff check src/ tests/   # Lint
poetry run mypy src/                # Type check

# 4. Run all tests
poetry run pytest --cov=src --cov-fail-under=90
```

### Git Workflow

```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Make commits (with Co-Authored-By)
git add .
git commit -m "feat: add new feature

Co-Authored-By: Claude (claude-sonnet-4-5) <noreply@anthropic.com>"

# Push and create PR
git push -u origin feature/my-feature
gh pr create --title "feat: add new feature" --body "Description..."
```

---

## Documentation

- **[Getting Started](getting-started.md)** - ✅ Onboarding guide for new developers
- **[TDD Workflow](tdd-workflow.md)** - ✅ Test-Driven Development process
- **[Code Quality](code-quality.md)** - ✅ Linting, formatting, type checking requirements
- **[Database Migrations](database-migrations.md)** - Alembic workflow (planned)
- **[Scripts](scripts/)** - ✅ Utility scripts documentation
- **[Troubleshooting](troubleshooting/)** - ✅ Common development issues

---

## Tools & Scripts

### Scripts Documentation

- **[Overview](scripts/overview.md)** - ✅ Complete utility scripts catalog (20+ scripts)
  - Analysis scripts: GPX diagnostics, performance analysis
  - Development tools: Data verification, cleanup utilities
  - Seeding scripts: Test data creation, database seeding
  - User management: Admin/user creation, role management
  - Testing scripts: Verification, test data checks

### User Management Scripts

```bash
cd backend

# Create admin
poetry run python scripts/user-mgmt/create_admin.py

# Create verified user
poetry run python scripts/user-mgmt/create_verified_user.py

# Promote to admin
poetry run python scripts/user-mgmt/promote_to_admin.py --username testuser
```

### Database Management

```bash
# Apply migrations
cd backend
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Add new table"

# Rollback last migration
poetry run alembic downgrade -1
```

---

## Troubleshooting

Common development issues and solutions:

- **[Common Issues](troubleshooting/common-issues.md)** - ✅ FAQ and quick fixes (20+ issues, 8 categories)
  - Server issues: Port conflicts, hangs, hot reload
  - Database issues: Connection errors, migrations
  - Dependency issues: Poetry cache, version conflicts
  - Testing issues: Coverage, fixtures
  - Frontend issues: CORS, React re-rendering
  - GPX upload issues: File size, parsing, statistics
  - Authentication issues: JWT tokens, HttpOnly cookies
  - Email testing issues: MailHog configuration
- **[Database Issues](troubleshooting/database-issues.md)** - ✅ DB troubleshooting (SQLite, PostgreSQL, migrations)
  - SQLite: Locked database, foreign keys, corruption
  - PostgreSQL: Connection refused, authentication, disk full
  - Migrations: Sync issues, column conflicts, autogenerate
  - Connection pool: Timeouts, SSL errors
  - Data integrity: Duplicate keys, orphaned records
  - Performance: N+1 queries, missing indexes

### Quick Fixes

**Port conflict (8000)**:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

**Database reset**:
```bash
./run-local-dev.sh --reset
```

**Dependency issues**:
```bash
cd backend
poetry install --sync
```

---

## Code Quality Standards

### Requirements

| Tool | Purpose | Requirement |
|------|---------|-------------|
| **black** | Code formatting | 100% compliance |
| **ruff** | Linting | Zero warnings |
| **mypy** | Type checking | Zero errors |
| **pytest** | Test coverage | ≥90% coverage |

### Pre-commit Hooks (Planned)

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

---

## Development Modes

ContraVento supports multiple development environments:

| Mode | Database | Docker | Use When |
|------|----------|--------|----------|
| **local-dev** | SQLite | ❌ | Daily development (recommended) |
| **local-minimal** | PostgreSQL | ✅ | PostgreSQL testing |
| **local-full** | PostgreSQL | ✅ | Email/cache testing |

See [Deployment Documentation](../deployment/README.md) for complete mode details.

---

## Migration from Old Documentation

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `backend/scripts/README.md` | `docs/development/scripts/overview.md` | ✅ Migrated |
| `backend/scripts/GPS_ANALYSIS_SCRIPTS.md` | Consolidated in `docs/development/scripts/overview.md` | ✅ Migrated |
| `backend/docs/POSTGRESQL_QUICKSTART.md` | `docs/development/troubleshooting/database-issues.md` | ✅ Migrated |
| `backend/docs/MAILHOG_SETUP.md` | `docs/development/troubleshooting/email-testing.md` | ⏳ Pending |

**Note**: MAILHOG_SETUP.md migration deferred to Phase 7 (email-specific troubleshooting guide).

---

## Related Documentation

- **[Deployment](../deployment/README.md)** - Running development environments
- **[Testing](../testing/README.md)** - Testing strategies
- **[Architecture](../architecture/README.md)** - System design
- **[API Reference](../api/README.md)** - API documentation

---

**Last Updated**: 2026-02-07
**Consolidation Plan**: Phase 6 (Development) - ✅ Complete (workflows, scripts, troubleshooting)
