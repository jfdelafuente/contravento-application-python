# Production Deployment Checklist

**Purpose**: Pre-deployment verification to prevent production incidents

**Audience**: DevOps engineers, release managers, deployment leads

**Prerequisites**:
- Production environment configured (see [modes/prod.md](../modes/prod.md))
- Staging deployment tested and validated
- Release branch ready for merge

**Related Documentation**:
- [Production Deployment Mode](../modes/prod.md) - Production environment setup
- [Staging Deployment Mode](../modes/staging.md) - Pre-production testing
- [Database Management Guide](./database-management.md) - Migration and backup procedures
- [Environment Variables Guide](./environment-variables.md) - Secret configuration
- [Frontend Deployment Guide](./frontend-deployment.md) - Build optimization

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Code Quality Verification](#1-code-quality-verification)
3. [Database Readiness](#2-database-readiness)
4. [Security Hardening](#3-security-hardening)
5. [Performance Validation](#4-performance-validation)
6. [Monitoring & Observability](#5-monitoring--observability)
7. [Rollback Preparation](#6-rollback-preparation)
8. [Deployment Execution](#7-deployment-execution)
9. [Post-Deployment Validation](#8-post-deployment-validation)
10. [Emergency Procedures](#emergency-procedures)
11. [Deployment Sign-Off](#deployment-sign-off)

---

## Pre-Deployment Checklist

**Timeline**: Complete 24-48 hours before production deployment

### Quick Validation

Run this command to get a quick health check:

```bash
# From project root
./scripts/deployment/pre-deploy-check.sh prod

# Or manually verify each section below
```

**Estimated Time**: 2-4 hours for full checklist completion

---

## 1. Code Quality Verification

**Purpose**: Ensure code meets quality standards before release

### 1.1 Backend Tests

```bash
cd backend

# Run full test suite with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Verify coverage meets requirements
# REQUIRED: ≥90% coverage across all modules
```

**Success Criteria**:
- [ ] All tests passing (0 failures, 0 errors)
- [ ] Code coverage ≥90% (check `htmlcov/index.html`)
- [ ] No skipped tests (`@pytest.mark.skip` removed)
- [ ] Contract tests validate OpenAPI schemas

**If Tests Fail**:
- Fix failing tests before proceeding
- Re-run full suite to verify fixes
- Update coverage if new code added

### 1.2 Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests (requires backend running)
npm run test:e2e

# Run type checking
npm run type-check

# Run linting
npm run lint
```

**Success Criteria**:
- [ ] All unit tests passing
- [ ] E2E tests passing (critical user flows)
- [ ] No TypeScript errors (`tsc --noEmit`)
- [ ] No ESLint errors or warnings

**If Tests Fail**:
- Review test failures in console output
- Fix type errors before deployment
- Address linting issues (run `npm run lint:fix` if safe)

### 1.3 Code Linting & Formatting

```bash
# Backend (Python)
cd backend
poetry run black src/ tests/ --check
poetry run ruff check src/ tests/
poetry run mypy src/

# Frontend (TypeScript)
cd frontend
npm run lint
npm run format:check
```

**Success Criteria**:
- [ ] Black formatting compliant (or auto-fix with `black src/ tests/`)
- [ ] Ruff linting clean (no errors)
- [ ] MyPy type checking passing
- [ ] ESLint/Prettier formatting consistent

**Common Issues**:
- **Black formatting**: Run `poetry run black src/ tests/` to auto-fix
- **Ruff errors**: Review and fix manually (often unused imports, undefined variables)
- **MyPy errors**: Add type hints or use `# type: ignore` if justified

### 1.4 Dependency Audit

```bash
# Backend - Check for security vulnerabilities
cd backend
poetry show --outdated
poetry audit  # If available, or use safety

# Frontend - Check for vulnerabilities
cd frontend
npm audit
npm outdated
```

**Success Criteria**:
- [ ] No high/critical severity vulnerabilities in dependencies
- [ ] Production dependencies up-to-date (security patches applied)
- [ ] Known vulnerabilities documented with mitigation plan

**If Vulnerabilities Found**:
- **High/Critical**: Must fix before deployment (upgrade packages)
- **Medium**: Review and document risk acceptance or fix
- **Low**: Can defer to next release if low risk

---

## 2. Database Readiness

**Purpose**: Ensure database migrations are safe and backups are current

### 2.1 Migration Verification

```bash
cd backend

# Check migration status (staging environment)
poetry run alembic current

# Verify all migrations applied
poetry run alembic history

# Test migration on staging database FIRST
poetry run alembic upgrade head  # On staging

# If new migrations exist, review SQL
poetry run alembic upgrade head --sql > migration.sql
cat migration.sql  # Review DDL statements
```

**Success Criteria**:
- [ ] All migrations tested on staging environment
- [ ] No migration conflicts (alembic history clean)
- [ ] DDL reviewed for destructive operations (DROP TABLE, ALTER COLUMN)
- [ ] Rollback plan documented for each migration

**Migration Safety Checks**:
- ✅ **Safe**: `CREATE TABLE`, `ADD COLUMN` (nullable)
- ⚠️ **Caution**: `ALTER COLUMN` (may lock table), `CREATE INDEX` (lock time)
- ❌ **Dangerous**: `DROP TABLE`, `DROP COLUMN`, `ALTER COLUMN NOT NULL`

**If Migrations Are Risky**:
- Create rollback migration (`alembic downgrade -1` tested on staging)
- Schedule deployment during low-traffic window
- Document downtime expectations (if any)

### 2.2 Database Backup

```bash
# PostgreSQL production backup
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB \
  -F c -b -v -f "backups/prod_pre_deploy_$(date +%Y%m%d_%H%M%S).backup"

# Verify backup integrity
pg_restore --list "backups/prod_pre_deploy_*.backup" | head -n 20

# Upload to S3 or backup storage
aws s3 cp "backups/prod_pre_deploy_*.backup" s3://contravento-backups/prod/
```

**Success Criteria**:
- [ ] Full database backup completed
- [ ] Backup verified (can list tables)
- [ ] Backup uploaded to remote storage (S3, GCS, or equivalent)
- [ ] Backup retention policy followed (keep ≥7 days)

**Backup Locations** (see [database-management.md](./database-management.md)):
- Local: `backend/backups/` (temporary)
- Remote: `s3://contravento-backups/prod/` (permanent)
- Retention: 7 daily, 4 weekly, 12 monthly

### 2.3 Seed Data Validation

```bash
# Verify admin user exists (production database)
cd backend
poetry run python -c "
from src.database import SessionLocal
from src.models.user import User
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
print('Admin exists:', admin is not None)
db.close()
"

# Verify cycling types seeded
poetry run python scripts/seeding/seed_cycling_types.py --list
```

**Success Criteria**:
- [ ] Admin user exists in production database
- [ ] Cycling types seeded (bikepacking, gravel, road, mountain, etc.)
- [ ] Essential reference data loaded (countries, tags, etc.)

**If Seed Data Missing**:
- Run seed scripts on production database (carefully!)
- Verify idempotency (scripts won't duplicate data)

---

## 3. Security Hardening

**Purpose**: Validate security configurations before exposing to public

### 3.1 Environment Variables

```bash
# Verify production .env file
cat .env.production

# Check for required secrets
grep -E "(SECRET_KEY|DATABASE_URL|SMTP_PASSWORD|CORS_ORIGINS)" .env.production
```

**Success Criteria**:
- [ ] `SECRET_KEY` is strong (32+ characters, generated with `secrets.token_urlsafe(32)`)
- [ ] `SECRET_KEY` is unique to production (not shared with staging/dev)
- [ ] `DATABASE_URL` uses production database (not staging)
- [ ] `SMTP_PASSWORD` is valid (test email sending)
- [ ] `CORS_ORIGINS` lists only production domains (e.g., `https://contravento.com`)
- [ ] No `.env` files committed to git (verify with `git status`)

**Security Checklist**:
- [ ] `DEBUG=false` (disable debug mode in production)
- [ ] `BCRYPT_ROUNDS=12` (production hashing strength)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=15` (short-lived tokens)
- [ ] `ALLOWED_HOSTS` configured (if using Django/similar)

**Common Mistakes**:
- ❌ Using staging `SECRET_KEY` in production
- ❌ Allowing `CORS_ORIGINS=*` (wildcard allows all origins)
- ❌ Forgetting to set `SMTP_HOST` (emails won't send)

### 3.2 CORS Configuration

```bash
# Verify CORS origins in .env.production
echo $CORS_ORIGINS

# Should be production domains only:
# CORS_ORIGINS=https://contravento.com,https://www.contravento.com
```

**Success Criteria**:
- [ ] `CORS_ORIGINS` lists only production domains (no `localhost`, no `http://`)
- [ ] No wildcard `*` allowed (security risk)
- [ ] HTTPS enforced (all origins use `https://`)

**Test CORS** (after deployment):
```bash
# Should succeed from production domain
curl -H "Origin: https://contravento.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS https://api.contravento.com/auth/login

# Should fail from unauthorized domain
curl -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS https://api.contravento.com/auth/login
```

### 3.3 Rate Limiting

**Currently Not Implemented** - Future enhancement

**Recommended** (for next release):
- Login endpoints: 5 attempts per 15 minutes
- Registration: 3 attempts per hour
- File uploads: 10 per minute per user

### 3.4 File Upload Validation

```bash
# Verify file upload validation in code
cd backend
grep -r "UPLOAD_MAX_SIZE" src/

# Check storage permissions
ls -la storage/
# Should be writable by backend user, not world-readable
```

**Success Criteria**:
- [ ] `UPLOAD_MAX_SIZE_MB=5` (prevent large file DoS)
- [ ] File type validation enabled (only allow images for profile/trip photos)
- [ ] MIME type verification in code (don't trust client-provided type)
- [ ] Storage directory has correct permissions (`750` or `700`)

**Security Validation**:
```python
# Verify this logic exists in src/services/file_service.py
# - Max file size check
# - MIME type whitelist (image/jpeg, image/png, image/webp)
# - Content validation (Pillow opens image to verify)
# - Filename sanitization (remove path traversal attempts)
```

---

## 4. Performance Validation

**Purpose**: Ensure production environment meets performance targets

### 4.1 Frontend Build Optimization

```bash
cd frontend

# Build for production (with optimizations)
npm run build:prod

# Verify build output size
du -sh dist/
# Expected: ~1 MB uncompressed, ~350 KB gzipped

# Analyze bundle size
npx vite-bundle-visualizer dist/stats.html
```

**Success Criteria**:
- [ ] Production build completes without errors
- [ ] Build size ≤1.5 MB uncompressed (target: ~1 MB)
- [ ] Gzipped size ≤500 KB (target: ~350 KB)
- [ ] No source maps in production build (`dist/*.js.map` should not exist)
- [ ] Code splitting enabled (multiple JS chunks: `react-vendor`, `form-vendor`, etc.)

**Build Breakdown** (expected):
- `index.html`: ~2 KB
- `assets/index-*.js`: ~300 KB (main app bundle)
- `assets/react-vendor-*.js`: ~200 KB (React, React DOM, React Router)
- `assets/form-vendor-*.js`: ~80 KB (React Hook Form, Zod)
- `assets/map-vendor-*.js`: ~150 KB (Leaflet, react-leaflet)
- `assets/index-*.css`: ~50 KB (global styles)

**If Build Size Too Large**:
- Review bundle analyzer for large dependencies
- Enable tree-shaking (verify `"sideEffects": false` in package.json)
- Lazy load heavy features (maps, photo galleries)

### 4.2 Database Indexes

```bash
# Verify indexes exist for frequently queried columns
cd backend
poetry run python -c "
from sqlalchemy import inspect
from src.database import engine
from src.models import User, Trip, TripPhoto, Tag

inspector = inspect(engine)

# Check User indexes
print('User indexes:', inspector.get_indexes('users'))

# Check Trip indexes
print('Trip indexes:', inspector.get_indexes('trips'))
"
```

**Success Criteria**:
- [ ] Indexes on foreign keys (e.g., `trips.user_id`)
- [ ] Indexes on frequently filtered columns (e.g., `trips.status`, `users.is_verified`)
- [ ] Composite indexes for common query patterns (e.g., `user_id + status`)

**Expected Indexes**:
- `users.username` (UNIQUE)
- `users.email` (UNIQUE)
- `trips.user_id` (foreign key)
- `trips.status`
- `trip_photos.trip_id` (foreign key)
- `tags.normalized` (tag filtering)

**If Indexes Missing**:
- Create migration to add indexes
- Test on staging first (index creation can lock tables)

### 4.3 Load Testing (Optional but Recommended)

```bash
# Use Apache Bench or k6 for load testing
ab -n 1000 -c 10 https://api.contravento.com/health

# Or use k6 (more advanced)
k6 run scripts/load-tests/api-load.js
```

**Success Criteria** (see spec.md performance targets):
- [ ] Simple queries: <200ms p95
- [ ] Auth endpoints: <500ms p95
- [ ] Photo uploads: <2s for 5MB files
- [ ] No memory leaks (monitor with `docker stats` during load test)

**If Performance Degrades**:
- Review slow query logs (PostgreSQL)
- Add database connection pooling (pool_size=20 recommended)
- Enable query result caching (Redis)

---

## 5. Monitoring & Observability

**Purpose**: Ensure visibility into production system health

### 5.1 Health Check Endpoints

```bash
# Verify backend health endpoint
curl https://api.contravento.com/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2026-02-06T12:00:00Z"
# }

# Verify frontend serving
curl -I https://contravento.com
# Expected: HTTP 200, Content-Type: text/html
```

**Success Criteria**:
- [ ] Backend `/health` endpoint returns 200
- [ ] Database connection verified in health check
- [ ] Frontend root `/` returns 200
- [ ] Static assets loading (check Network tab in browser DevTools)

**Health Check URLs**:
- Backend API: `https://api.contravento.com/health`
- Frontend: `https://contravento.com`

### 5.2 Error Tracking (Optional - Future Enhancement)

**Recommended**: Integrate Sentry or similar error tracking

```bash
# Verify SENTRY_DSN configured
echo $SENTRY_DSN

# Test error reporting (staging environment)
curl -X POST https://api.contravento.com/test-error
# Should trigger Sentry alert
```

**Success Criteria**:
- [ ] Sentry (or equivalent) configured
- [ ] Test error sent and visible in Sentry dashboard
- [ ] Error notifications configured (email, Slack)

**If Not Configured**:
- Can deploy without error tracking (monitor logs manually)
- Plan to add in next sprint

### 5.3 Logging Configuration

```bash
# Verify logging level in .env.production
echo $LOG_LEVEL
# Expected: INFO (not DEBUG)

echo $LOG_FORMAT
# Expected: json (structured logging)

# Test log output
docker-compose -f docker-compose.prod.yml logs backend | head -n 10
```

**Success Criteria**:
- [ ] `LOG_LEVEL=INFO` (not DEBUG in production)
- [ ] `LOG_FORMAT=json` (machine-readable)
- [ ] Logs writing to stdout (Docker captures to `docker-compose logs`)
- [ ] Sensitive data not logged (passwords, tokens redacted)

**Log Forwarding** (optional):
- Recommended: Forward to Elasticsearch, CloudWatch, or Datadog
- Configure in `docker-compose.prod.yml` with logging driver

---

## 6. Rollback Preparation

**Purpose**: Enable quick recovery if deployment fails

### 6.1 Git Tagging

```bash
# Tag current production version before deploy
git tag -a v1.2.3 -m "Release v1.2.3 - Pre-production stable"
git push origin v1.2.3

# Verify tag exists
git tag -l "v1.*"
```

**Success Criteria**:
- [ ] Previous production version tagged (e.g., `v1.2.2`)
- [ ] New release version tagged (e.g., `v1.2.3`)
- [ ] Tags pushed to remote (`git push origin --tags`)

**Tag Naming Convention**:
- Format: `vMAJOR.MINOR.PATCH` (semantic versioning)
- Example: `v1.3.0` (new feature), `v1.2.4` (bug fix)

### 6.2 Rollback Commands

**Document rollback procedure before deployment:**

```bash
# Rollback to previous version (v1.2.2)
git checkout v1.2.2
./deploy.sh prod

# Rollback database migration (if needed)
cd backend
poetry run alembic downgrade -1  # Or specific revision

# Verify rollback
curl https://api.contravento.com/health
```

**Success Criteria**:
- [ ] Rollback commands documented in deployment notes
- [ ] Rollback tested on staging environment
- [ ] Database rollback strategy documented (if migrations applied)
- [ ] Estimated rollback time documented (e.g., "5 minutes")

**Database Rollback Strategy**:
- **No migrations**: Simple code rollback (git checkout)
- **Additive migrations** (CREATE TABLE): Safe to rollback code without DB rollback
- **Destructive migrations** (DROP COLUMN): Must rollback DB migration too

### 6.3 Communication Plan

**Notify stakeholders before deployment:**

- [ ] Deployment window scheduled (e.g., "Feb 6, 2026 10:00-11:00 UTC")
- [ ] Stakeholders notified (team, users if downtime expected)
- [ ] Status page updated (if available)
- [ ] Rollback decision-maker identified (who approves rollback?)

**Deployment Communication Checklist**:
1. **24 hours before**: Email team about deployment schedule
2. **1 hour before**: Slack/Teams message to confirm deployment starting
3. **During deployment**: Status updates every 15 minutes
4. **After deployment**: Confirmation message with health check results

---

## 7. Deployment Execution

**Timeline**: Execute during low-traffic window (recommend weekday morning UTC)

### 7.1 Pre-Deployment Steps

```bash
# 1. Confirm all checklist items above completed
# 2. Backup production database (CRITICAL - see section 2.2)
# 3. Tag release version in git (see section 6.1)
# 4. Notify team deployment is starting
```

### 7.2 Production Deployment

```bash
# Pull latest code
git checkout main  # Or release branch
git pull origin main

# Build and deploy
./deploy.sh prod

# Monitor deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

**Deployment Steps** (automated by `deploy.sh prod`):
1. Pull latest Docker images (or build locally)
2. Apply database migrations (`alembic upgrade head`)
3. Start new containers (backend, frontend, nginx)
4. Wait for health checks to pass
5. Stop old containers (if zero-downtime supported)

**Expected Duration**: 5-10 minutes

### 7.3 Monitor Deployment

**Watch for errors during deployment:**

```bash
# Watch container status
watch -n 2 'docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps'

# Monitor logs for errors
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs backend | grep -i error

# Check resource usage
docker stats
```

**Success Indicators**:
- ✅ All containers show `healthy` status
- ✅ No error logs in backend/frontend
- ✅ Health endpoint returns 200

**Failure Indicators**:
- ❌ Container status shows `unhealthy` or `restarting`
- ❌ Error logs contain "connection refused", "migration failed"
- ❌ Health endpoint returns 500 or times out

**If Deployment Fails**:
- STOP immediately (don't wait)
- Execute rollback procedure (section 6.2)
- Capture logs for post-mortem

---

## 8. Post-Deployment Validation

**Purpose**: Verify production system is working correctly

### 8.1 Smoke Tests

**Manual verification of critical user flows:**

```bash
# 1. Health check
curl https://api.contravento.com/health
# Expected: {"status": "healthy", "database": "connected"}

# 2. Frontend loads
curl -I https://contravento.com
# Expected: HTTP 200, Content-Type: text/html

# 3. Login flow (use production credentials)
curl -X POST https://api.contravento.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "PRODUCTION_PASSWORD"}'
# Expected: 200, returns access_token

# 4. Create trip (authenticated request)
# Test with Postman or frontend UI
```

**Success Criteria**:
- [ ] Health check returns 200
- [ ] Frontend page loads (no 404 or 500 errors)
- [ ] Login works with production credentials
- [ ] Create trip flow works (end-to-end test)
- [ ] Photo upload works (upload 1 photo, verify storage)

**Critical User Flows to Test**:
1. **Registration**: New user can sign up
2. **Login**: Existing user can log in
3. **Create Trip**: User can create draft trip
4. **Publish Trip**: User can publish draft trip
5. **Upload Photo**: User can upload trip photo
6. **View Public Feed**: Anyone can view public trips

### 8.2 Performance Verification

```bash
# Check response times (should be <500ms p95)
time curl https://api.contravento.com/trips

# Monitor server resources
docker stats --no-stream

# Check database connections
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec postgres \
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT count(*) FROM pg_stat_activity;"
```

**Success Criteria**:
- [ ] API response times <500ms for simple queries
- [ ] CPU usage <70% under normal load
- [ ] Memory usage <80% of allocated
- [ ] Database connections <50% of pool size

**If Performance Issues Detected**:
- Review slow query logs
- Check for N+1 query problems (missing eager loading)
- Verify connection pooling enabled

### 8.3 Security Verification

```bash
# Verify HTTPS redirect
curl -I http://contravento.com
# Expected: HTTP 301 → https://contravento.com

# Verify security headers
curl -I https://contravento.com | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)"
# Expected:
# - Strict-Transport-Security: max-age=31536000
# - X-Frame-Options: DENY
# - X-Content-Type-Options: nosniff

# Verify CORS (from unauthorized domain)
curl -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS https://api.contravento.com/auth/login
# Expected: No Access-Control-Allow-Origin header
```

**Success Criteria**:
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers present (HSTS, X-Frame-Options, etc.)
- [ ] CORS allows only production domains
- [ ] No sensitive data exposed in error responses

---

## Emergency Procedures

**If production is down or critically broken:**

### Immediate Actions (within 5 minutes)

1. **Assess Severity**:
   - Complete outage (site unreachable) → Execute rollback immediately
   - Partial issue (one feature broken) → Evaluate impact before rollback

2. **Execute Rollback**:
   ```bash
   # Rollback to previous version
   git checkout v1.2.2  # Previous stable tag
   ./deploy.sh prod

   # If database migrations applied, rollback migration
   cd backend
   poetry run alembic downgrade -1
   ```

3. **Notify Team**:
   - Post in Slack/Teams: "Production deployment failed, executing rollback"
   - Update status page (if available)

### Post-Rollback (within 30 minutes)

4. **Verify System Healthy**:
   ```bash
   curl https://api.contravento.com/health
   # Should return 200
   ```

5. **Capture Logs**:
   ```bash
   # Save logs for post-mortem analysis
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs \
     > logs/failed_deployment_$(date +%Y%m%d_%H%M%S).log
   ```

6. **Post-Mortem**:
   - Schedule meeting within 24 hours
   - Review what went wrong
   - Update checklist to prevent recurrence

### Contact Information

**Escalation Path**:
1. DevOps Lead: [email/phone]
2. Backend Lead: [email/phone]
3. CTO/Technical Lead: [email/phone]

**On-Call Schedule**: [Link to PagerDuty or on-call rotation]

---

## Deployment Sign-Off

**Before marking deployment complete, verify all sections:**

### Final Checklist

- [ ] **Code Quality**: All tests passing, linting clean, dependencies audited
- [ ] **Database**: Migrations tested, backup completed, seed data verified
- [ ] **Security**: Environment variables correct, CORS configured, file uploads validated
- [ ] **Performance**: Frontend build optimized, database indexes verified, load testing passed
- [ ] **Monitoring**: Health checks working, logging configured, error tracking enabled
- [ ] **Rollback**: Git tagged, rollback commands documented, communication plan ready
- [ ] **Deployment**: Production deployed successfully, no errors in logs
- [ ] **Post-Deploy**: Smoke tests passed, performance verified, security validated

### Sign-Off

**Deployment Lead**: ________________________
**Date**: ________________
**Version Deployed**: v_______

**Approval**:
- [ ] DevOps Lead approved
- [ ] Backend Lead approved
- [ ] Product Owner notified

---

## Appendix: Common Issues

### Issue: Database Migration Fails

**Symptoms**: `alembic upgrade head` returns error

**Resolution**:
```bash
# Check current migration version
poetry run alembic current

# Review migration history
poetry run alembic history

# If conflict, manually resolve:
# 1. Backup database (CRITICAL)
# 2. Apply migrations one-by-one
poetry run alembic upgrade +1

# If still fails, rollback deployment
```

### Issue: Frontend Build Fails

**Symptoms**: `npm run build:prod` exits with error

**Resolution**:
```bash
# Clear cache and rebuild
rm -rf node_modules dist .vite
npm install
npm run build:prod

# If TypeScript errors, fix before deploying
npm run type-check
```

### Issue: CORS Errors in Production

**Symptoms**: Browser console shows "CORS policy blocked"

**Resolution**:
```bash
# Verify CORS_ORIGINS in .env.production
echo $CORS_ORIGINS

# Should be:
# CORS_ORIGINS=https://contravento.com,https://www.contravento.com

# Restart backend to apply changes
docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart backend
```

### Issue: High Memory Usage

**Symptoms**: Backend container uses >90% memory

**Resolution**:
```bash
# Increase memory limit in docker-compose.prod.yml
# backend:
#   deploy:
#     resources:
#       limits:
#         memory: 2G  # Increase from 1G

# Restart containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Related Documentation

- **[Production Deployment Mode](../modes/prod.md)**: Complete production setup guide
- **[Staging Deployment Mode](../modes/staging.md)**: Pre-production testing environment
- **[Database Management Guide](./database-management.md)**: Migration and backup procedures
- **[Environment Variables Guide](./environment-variables.md)**: Configuration reference
- **[Frontend Deployment Guide](./frontend-deployment.md)**: Build optimization techniques
- **[Troubleshooting Guide](./troubleshooting.md)**: Common production issues

---

**Last Updated**: 2026-02-06
**Document Version**: 1.0
**Feedback**: Report issues or suggest improvements via GitHub Issues
