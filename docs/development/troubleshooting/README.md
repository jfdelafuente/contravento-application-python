# Troubleshooting Guide - ContraVento

Comprehensive troubleshooting documentation for development issues encountered in ContraVento.

**Last Updated**: 2026-02-07
**Status**: Active - Updated in Phase 6-7 of Documentation Consolidation

---

## Quick Navigation

### By Issue Category

| Category | Guide | Common Issues |
|----------|-------|---------------|
| **General Development** | [Common Issues](common-issues.md) | Server startup, dependencies, testing, frontend |
| **Database** | [Database Issues](database-issues.md) | SQLite, PostgreSQL, migrations, performance |
| **Feature-Specific** | [Travel Diary](travel-diary-troubleshooting.md) | Photo display, forms, API integration |

### By Urgency

**🔴 Critical (System Down)**:
- Backend won't start → [common-issues.md#server-wont-start](common-issues.md#1-backend-server-wont-start)
- Database connection fails → [database-issues.md#postgresql-connection](database-issues.md#postgresql-connection-issues)
- All tests failing → [common-issues.md#all-tests-failing](common-issues.md#6-all-tests-failing)

**🟡 High (Feature Broken)**:
- Photos not displaying → [travel-diary-troubleshooting.md#photo-display](travel-diary-troubleshooting.md)
- Database locked → [database-issues.md#sqlite-locked](database-issues.md#sqlite-database-locked)
- Migration failures → [database-issues.md#migration-failures](database-issues.md#migration-failures)

**🟢 Medium (Development Friction)**:
- N+1 query warnings → [database-issues.md#n+1-queries](database-issues.md#n1-query-problems)
- Import errors → [common-issues.md#import-errors](common-issues.md#3-import-errors-module-not-found)
- Frontend hot reload fails → [common-issues.md#vite-issues](common-issues.md#8-vite-hot-reload-not-working-frontend)

---

## Available Troubleshooting Guides

### 1. Common Development Issues

**[common-issues.md](common-issues.md)** - General development problems (2,400+ lines)

**Categories**:
- **Server Issues**: Backend won't start, port conflicts, CORS errors
- **Database Issues**: Quick fixes for common DB problems
- **Dependencies**: Poetry, npm, version conflicts
- **Testing**: Test failures, coverage issues, fixtures
- **Frontend**: Vite, React, API integration
- **GPX Processing**: Upload failures, simplification errors
- **Authentication**: JWT, cookies, CORS
- **Email**: MailHog, SMTP configuration

**Most Common Issues**:
1. Backend won't start (port 8000 in use)
2. Database connection errors
3. Import errors after dependency changes
4. CORS errors in frontend
5. Tests failing due to missing fixtures
6. Vite hot reload not working
7. GPX upload failures
8. JWT token expired errors

**Example**:
```bash
# Backend won't start - port in use
Error: [Errno 98] Address already in use

# Solution:
lsof -i :8000              # Find process using port 8000
kill -9 <PID>              # Kill the process
poetry run uvicorn ...     # Restart backend
```

---

### 2. Database Troubleshooting

**[database-issues.md](database-issues.md)** - SQLite, PostgreSQL, migrations (2,800+ lines)

**Categories**:
- **SQLite Issues**: Locked database, foreign keys, corruption
- **PostgreSQL Issues**: Connection, authentication, disk full
- **Migration Issues**: Failed migrations, downgrade, conflicts
- **Performance**: N+1 queries, missing indexes, slow queries

**Most Common Issues**:
1. SQLite database locked (concurrent access)
2. PostgreSQL connection refused
3. Migration version conflicts
4. Foreign key constraint failures
5. N+1 query warnings
6. Missing indexes causing slow queries

**Example**:
```bash
# SQLite database locked
Error: database is locked

# Solutions:
1. Check for hung processes:
   ps aux | grep python | grep uvicorn
   kill -9 <PID>

2. Close all connections:
   # In SQLite CLI
   .quit

3. Enable WAL mode (allows concurrent reads):
   PRAGMA journal_mode=WAL;
```

---

### 3. Feature-Specific Troubleshooting

**[travel-diary-troubleshooting.md](travel-diary-troubleshooting.md)** - Travel Diary Frontend

**Migrated From**: `specs/008-travel-diary-frontend/TROUBLESHOOTING.md`
**Feature**: Trip creation, photo uploads, tag filtering, draft workflow

**Categories**:
- **Photo Display Issues**: Missing photos, broken URLs, placeholder not showing
- **Form State Problems**: Validation errors, unsaved changes, wizard navigation
- **API Integration**: 401/403 errors, CORS issues, timeout errors
- **Tag Filtering**: Tags not filtering, case sensitivity, URL encoding
- **Draft Workflow**: Can't publish, status not updating, permission errors

**Most Common Issues**:
1. Photos display placeholder instead of actual image
2. Form validation doesn't trigger on submit
3. 401 Unauthorized on trip creation (missing auth token)
4. Tags not filtering trips correctly
5. Can't publish draft (validation errors not shown)

**Example**:
```typescript
// Photo display - missing getPhotoUrl()
// ❌ WRONG - direct URL usage
<img src={trip.photos[0].photo_url} />

// ✅ CORRECT - use helper
import { getPhotoUrl } from '@/utils/tripHelpers';
<img src={getPhotoUrl(trip.photos[0]?.photo_url)} />
```

---

## Troubleshooting Workflow

### Step 1: Identify Issue Category

Ask yourself:
- **Is the server down?** → [common-issues.md#server-issues](common-issues.md#1-server-issues)
- **Database error?** → [database-issues.md](database-issues.md)
- **Feature not working?** → Check feature-specific guides
- **Tests failing?** → [common-issues.md#testing-issues](common-issues.md#6-testing-issues)

### Step 2: Check Error Messages

**Backend Errors**:
```bash
# Check backend logs
poetry run uvicorn src.main:app --reload

# Common patterns:
# - "Address already in use" → Port conflict
# - "database is locked" → SQLite concurrency
# - "relation does not exist" → Missing migration
# - "ImportError" → Missing dependency
```

**Frontend Errors**:
```bash
# Check browser console (F12)
npm run dev

# Common patterns:
# - "401 Unauthorized" → Auth token issue
# - "CORS error" → Backend CORS config
# - "404 Not Found" → Route or API endpoint issue
# - "TypeError: Cannot read property" → Missing null check
```

### Step 3: Search This Documentation

```bash
# Search all troubleshooting guides
grep -r "error message" docs/development/troubleshooting/

# Example: Find database locked solutions
grep -r "database is locked" docs/development/troubleshooting/
```

### Step 4: Check Recent Changes

```bash
# Review recent commits
git log --oneline -10

# Check what changed in problematic file
git diff HEAD~1 path/to/file.py

# Revert recent migration if DB broken
poetry run alembic downgrade -1
```

### Step 5: Verify Environment

```bash
# Backend dependencies
cd backend
poetry show                  # List installed packages
poetry install               # Reinstall dependencies

# Frontend dependencies
cd frontend
npm list                     # List installed packages
rm -rf node_modules package-lock.json
npm install                  # Fresh install

# Database state
poetry run alembic current   # Check migration version
poetry run alembic history   # View migration history
```

---

## Common Error Messages

### Backend (Python/FastAPI)

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `Address already in use` | Port 8000 occupied | `lsof -i :8000` then `kill -9 <PID>` |
| `database is locked` | SQLite concurrent access | Close all DB connections, restart server |
| `ModuleNotFoundError` | Missing dependency | `poetry install` |
| `relation "table" does not exist` | Migration not applied | `poetry run alembic upgrade head` |
| `FOREIGN KEY constraint failed` | Foreign key violation | Check SQLite PRAGMA, verify data integrity |
| `jwt.ExpiredSignatureError` | Expired JWT token | Login again to get new token |

### Frontend (React/TypeScript)

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `401 Unauthorized` | Missing/invalid JWT | Check auth token in cookies/localStorage |
| `CORS error` | CORS misconfiguration | Verify `CORS_ORIGINS` in backend `.env` |
| `Cannot read property of undefined` | Missing null check | Add optional chaining `?.` |
| `404 Not Found` | Wrong API endpoint | Verify route in `backend/src/api/` |
| `Failed to fetch` | Backend not running | Start backend with `poetry run uvicorn...` |

### Database (SQLite/PostgreSQL)

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `database is locked` | SQLite concurrency | Enable WAL mode, close connections |
| `could not connect to server` | PostgreSQL not running | `docker-compose up -d postgres` |
| `password authentication failed` | Wrong credentials | Check `DATABASE_URL` in `.env` |
| `disk full` | No disk space | Clean up logs, old backups |
| `version conflict` | Migration mismatch | `alembic downgrade` then `upgrade` |

---

## Debugging Tools

### Backend Debugging

**Interactive Debugger**:
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Run server with debugger attached
poetry run python -m pdb -m uvicorn src.main:app --reload
```

**Logging**:
```python
# In service or API code
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

**Database Queries**:
```python
# Log all SQL queries (in config.py)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Logs all SQL
)
```

### Frontend Debugging

**React DevTools**:
- Install React DevTools extension
- Inspect component state and props
- Track re-renders and performance

**Network Debugging**:
```javascript
// In browser console (F12 → Network tab)
// 1. Filter by XHR to see API calls
// 2. Click request → Preview tab → see response
// 3. Check Headers tab for cookies/authorization
```

**Console Logging**:
```typescript
// Strategic console.logs
console.log('[Component] State:', state);
console.log('[API] Request:', { method, url, data });
console.log('[API] Response:', response.data);
```

---

## Prevention Best Practices

### Avoid Common Pitfalls

1. **Always run migrations after pulling**: `poetry run alembic upgrade head`
2. **Check port availability before starting**: `lsof -i :8000` (backend), `lsof -i :5173` (frontend)
3. **Use virtual environments**: Never install globally
4. **Verify environment variables**: Check `.env` files after updates
5. **Test locally before committing**: Run tests with `poetry run pytest`
6. **Read error messages carefully**: Most errors are self-explanatory
7. **Check git status regularly**: `git status` before making changes
8. **Keep dependencies updated**: Run `poetry update` monthly

### Environment Checklist

Before reporting an issue, verify:

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:5173
- [ ] Database migrations applied (`alembic current`)
- [ ] Dependencies installed (`poetry install`, `npm install`)
- [ ] Environment variables set (`.env` file exists)
- [ ] No port conflicts (`lsof -i :8000`, `lsof -i :5173`)
- [ ] No stale processes (`ps aux | grep uvicorn`)
- [ ] Latest code pulled (`git pull`)

---

## Getting Help

### Self-Service Resources

1. **Search this documentation**:
   ```bash
   grep -r "your error" docs/development/troubleshooting/
   ```

2. **Check git history**:
   ```bash
   git log --all --grep="related feature"
   ```

3. **Review test files**:
   ```bash
   # Often contain usage examples
   cat tests/integration/test_trips.py
   ```

4. **API documentation**:
   - http://localhost:8000/docs (Swagger UI)
   - [API Reference](../../api/README.md)

### Escalation Path

If issue persists after checking documentation:

1. **Check if known issue**:
   - Search GitHub Issues: https://github.com/contravento/issues
   - Check CHANGELOG.md for recent breaking changes

2. **Gather debugging info**:
   - Error messages (full stack trace)
   - Steps to reproduce
   - Environment details (`poetry show`, `npm list`)
   - Recent changes (`git log --oneline -5`)

3. **Create minimal reproducible example**:
   - Simplify to smallest code that shows issue
   - Include test case if possible

4. **Report issue**:
   - Open GitHub issue with template
   - Include all gathered information
   - Tag with severity label

---

## Related Documentation

- **[Development README](../README.md)** - Getting started, workflows
- **[Scripts Overview](../scripts/overview.md)** - Utility scripts catalog
- **[Testing Guide](../../testing/README.md)** - Testing strategies
- **[API Reference](../../api/README.md)** - API documentation
- **[Architecture](../../architecture/README.md)** - System design decisions

---

## Contributing to Troubleshooting Docs

### When to Add New Troubleshooting Content

Add to these guides when you:
1. Encounter a non-obvious issue that took >30min to solve
2. Find a common error pattern (seen 3+ times)
3. Discover a workaround not documented elsewhere
4. Solve an issue not covered in existing guides

### How to Add Content

**For general issues**: Add to [common-issues.md](common-issues.md)
```markdown
### New Issue Title

**Symptoms**:
- Error message or behavior

**Cause**:
- Root cause explanation

**Solution**:
\`\`\`bash
# Step-by-step fix
command1
command2
\`\`\`

**Prevention**:
- How to avoid in future
```

**For database issues**: Add to [database-issues.md](database-issues.md)

**For feature-specific**: Create new file or add to existing feature guide

### Style Guidelines

- Use clear, descriptive titles
- Include error messages verbatim (helps search)
- Provide step-by-step solutions
- Add prevention tips when possible
- Use code blocks for commands
- Test solutions before documenting

---

## Troubleshooting Guide Statistics

| Guide | Lines | Issues Covered | Categories |
|-------|-------|----------------|------------|
| [common-issues.md](common-issues.md) | 2,400+ | 20+ | 8 |
| [database-issues.md](database-issues.md) | 2,800+ | 15+ | 4 |
| [travel-diary-troubleshooting.md](travel-diary-troubleshooting.md) | ~800 | 10+ | 5 |
| **TOTAL** | **6,000+** | **45+** | **17** |

**Coverage**:
- Backend: ✅ Comprehensive
- Database: ✅ Comprehensive
- Frontend: ✅ Feature-specific (Travel Diary)
- Deployment: → See [docs/deployment/](../../deployment/README.md)
- Testing: → See [docs/testing/](../../testing/README.md)

---

**Last Updated**: 2026-02-07
**Phase 7**: Archive and Cleanup - Added feature-specific troubleshooting
**Maintainers**: ContraVento Development Team
