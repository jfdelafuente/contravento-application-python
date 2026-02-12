# Frontend Deployment Testing Guide

This guide provides smoke test checklists for validating frontend deployments across all environments.

## Purpose

Use these checklists after deploying frontend changes to ensure:
- ✅ Frontend loads correctly in each environment
- ✅ Backend API integration works
- ✅ Authentication flows function properly
- ✅ Build optimizations are applied (staging/production)
- ✅ No console errors or warnings

---

## SQLite Local (Development - No Docker)

**Environment**: Local development with Vite dev server
**Access**: <http://localhost:5173>
**Backend**: <http://localhost:8000>

### Pre-Test Setup

```bash
# Start backend (Terminal 1)
cd backend
./run-local-dev.sh              # Linux/Mac
.\run-local-dev.ps1             # Windows PowerShell

# Start frontend (Terminal 2)
cd frontend
npm run dev
```

### Smoke Test Checklist

- [ ] **Frontend loads**: Navigate to <http://localhost:5173>
- [ ] **No console errors**: Open browser DevTools → Console (should be clean)
- [ ] **Hot Module Replacement works**: Edit a `.tsx` file → changes appear without full reload
- [ ] **Backend connectivity**: Check Network tab → API calls go to `http://localhost:8000`
- [ ] **CORS configured**: No CORS errors in console
- [ ] **Authentication works**:
  - [ ] Login with test credentials (`testuser` / `TestPass123!`)
  - [ ] Check HttpOnly cookie is set (Application → Cookies)
  - [ ] Access protected route (e.g., `/trips`)
  - [ ] Logout successfully
- [ ] **Static assets load**: Check Network tab → All JS/CSS/images load with 200 status
- [ ] **Source maps available**: DevTools → Sources shows original TypeScript files
- [ ] **Vite HMR overlay works**: Introduce syntax error → See Vite error overlay

### Expected Behavior

- **Startup time**: <5 seconds
- **HMR update time**: <2 seconds
- **No build errors**: Terminal shows "VITE ready" without warnings
- **Console clean**: No React warnings or errors

---

## Docker Full (Development with Docker)

**Environment**: Docker Compose with all services
**Access**: <http://localhost:5173>
**Backend**: <http://localhost:8000>

### Pre-Test Setup

```bash
# Start environment with frontend
./deploy.sh local --with-frontend        # Linux/Mac
.\deploy.ps1 local -WithFrontend         # Windows PowerShell

# Verify frontend container is running
docker ps | grep contravento-frontend-local
```

### Smoke Test Checklist

- [ ] **Frontend container running**: `docker ps` shows frontend with status "Up" and "healthy"
- [ ] **Frontend loads**: Navigate to <http://localhost:5173>
- [ ] **No console errors**: Open browser DevTools → Console (should be clean)
- [ ] **Hot reload works inside container**: Edit file → changes appear within 2 seconds
- [ ] **Backend connectivity**: Network tab → API calls go to `http://backend:8000` (internal Docker network)
- [ ] **CORS configured**: `CORS_ORIGINS` includes `http://localhost:5173`
- [ ] **Authentication works**:
  - [ ] Register new user
  - [ ] Check email in MailHog UI (<http://localhost:8025>)
  - [ ] Verify account using email token
  - [ ] Login with verified credentials
- [ ] **Database integration**: pgAdmin (<http://localhost:5050>) shows user data
- [ ] **Volume mounts work**: Edit file in host → Changes reflected in container
- [ ] **Logs accessible**: `docker logs contravento-frontend-local` shows Vite output

### Expected Behavior

- **Container startup**: <30 seconds
- **Healthcheck passes**: `docker inspect contravento-frontend-local` shows "healthy"
- **HMR works**: Volume mounts allow hot reload
- **No CORS errors**: Backend allows localhost:5173

### Troubleshooting

**Frontend container not starting:**
```bash
docker logs contravento-frontend-local
# Check for npm install errors or port conflicts
```

**Hot reload not working:**
```bash
# Verify volume mounts
docker inspect contravento-frontend-local | grep -A 10 Mounts
# Should show ./frontend:/app mount
```

---

## Staging (Production Build)

**Environment**: Production build with source maps
**Access**: <https://staging.contravento.com>
**Backend**: <https://staging.contravento.com/api> (via Nginx proxy)

### Pre-Test Setup

```bash
# Deploy to staging
./deploy.sh staging                      # Linux/Mac
.\deploy.ps1 staging                     # Windows PowerShell

# Verify frontend build succeeded
ls -lh frontend/dist/
# Should show ~1 MB of built assets
```

### Smoke Test Checklist

- [ ] **Production build created**: `frontend/dist/` contains built files
- [ ] **Build size acceptable**: Total dist/ size is 800 KB - 1.2 MB (uncompressed)
- [ ] **Frontend loads**: Navigate to <https://staging.contravento.com>
- [ ] **HTTPS works**: Browser shows secure padlock icon
- [ ] **No console errors**: DevTools → Console shows no errors
- [ ] **Backend connectivity**: Network tab → API calls go to `https://staging.contravento.com/api`
- [ ] **Source maps available**: DevTools → Sources shows original TypeScript files (for debugging)
- [ ] **Authentication works**:
  - [ ] Login with test credentials
  - [ ] Cookie domain is `staging.contravento.com`
  - [ ] Logout successfully
- [ ] **Code splitting applied**: Network tab → Multiple vendor chunks loaded
  - [ ] `react-vendor-*.js` (~200 KB)
  - [ ] `form-vendor-*.js` (~150 KB)
  - [ ] `map-vendor-*.js` (~250 KB)
  - [ ] `index-*.js` (~400 KB)
- [ ] **Cache headers correct**:
  - [ ] Static assets (JS/CSS): `Cache-Control: public, max-age=31536000, immutable`
  - [ ] `index.html`: `Cache-Control: no-cache, no-store, must-revalidate`
- [ ] **Gzip compression enabled**: Response headers show `Content-Encoding: gzip`
- [ ] **Security headers present**:
  - [ ] `X-Frame-Options: SAMEORIGIN`
  - [ ] `X-Content-Type-Options: nosniff`
  - [ ] `X-XSS-Protection: 1; mode=block`
- [ ] **Assets load from CDN/cache**: Subsequent page loads are instant

### Expected Behavior

- **Build time**: 30-60 seconds
- **First load**: ~350 KB transferred (gzipped)
- **Subsequent loads**: <50 KB (cached assets)
- **Lighthouse score**: Performance >90, Accessibility >90

### Build Verification

```bash
# Check build output
cd frontend
npm run build:staging

# Expected output:
# dist/index.html                   ~2.00 KB
# dist/assets/index-abc123.js       ~400.00 KB  (main bundle)
# dist/assets/react-vendor-def.js   ~200.00 KB
# dist/assets/form-vendor-ghi.js    ~150.00 KB
# dist/assets/map-vendor-jkl.js     ~250.00 KB
# dist/assets/index-mno.css         ~50.00 KB

# Verify source maps exist
ls dist/assets/*.map
# Should show .map files for all JS bundles
```

---

## Production (Production Build - No Source Maps)

**Environment**: Production build with maximum optimization
**Access**: <https://contravento.com>
**Backend**: <https://api.contravento.com> (via Nginx proxy)

### Pre-Test Setup

```bash
# Deploy to production
./deploy.sh prod                         # Linux/Mac
.\deploy.ps1 prod                        # Windows PowerShell

# Verify frontend containers running (3 replicas for HA)
docker ps | grep contravento-frontend-prod
# Should show 3 containers
```

### Smoke Test Checklist

- [ ] **Production build created**: `frontend/dist/` contains built files
- [ ] **Build size acceptable**: Total dist/ size is 800 KB - 1.2 MB (uncompressed)
- [ ] **No source maps in dist/**: `ls dist/assets/*.map` returns empty (security)
- [ ] **High availability**: 3 frontend replicas running
- [ ] **Frontend loads**: Navigate to <https://contravento.com>
- [ ] **HTTPS works**: Browser shows secure padlock icon (Let's Encrypt certificate)
- [ ] **No console errors**: DevTools → Console shows no errors or warnings
- [ ] **Backend connectivity**: Network tab → API calls go to `https://api.contravento.com`
- [ ] **Source maps NOT available**: DevTools → Sources shows minified code only (no TypeScript)
- [ ] **Authentication works**:
  - [ ] Register new user (real email verification)
  - [ ] Login with credentials
  - [ ] Cookie domain is `contravento.com`
  - [ ] Session persists across page reloads
  - [ ] Logout successfully
- [ ] **Code splitting applied**: Same as staging (react-vendor, form-vendor, map-vendor)
- [ ] **Cache headers correct**: Same as staging
- [ ] **Gzip compression enabled**: Same as staging
- [ ] **Security headers present**: Same as staging
- [ ] **Performance optimized**:
  - [ ] First Contentful Paint (FCP) <1.8s
  - [ ] Time to Interactive (TTI) <3.8s
  - [ ] Total Blocking Time (TBT) <300ms
- [ ] **Load balancing works**: Refresh multiple times → Different replica may serve request
- [ ] **Rolling updates work**: Deploy new version → Zero downtime

### Expected Behavior

- **Build time**: 30-60 seconds
- **First load**: ~300 KB transferred (gzipped, more aggressive compression than staging)
- **Subsequent loads**: <50 KB (cached assets)
- **Lighthouse score**: Performance >95, Accessibility >95, Best Practices >95, SEO >95
- **Uptime**: 99.9% (3 replicas with health checks)

### Production Verification Commands

```bash
# Check replica count
docker ps | grep contravento-frontend-prod | wc -l
# Expected: 3

# Check healthcheck status
docker inspect contravento-frontend-prod-1 | grep -A 5 Health
# Expected: "Status": "healthy"

# Check resource usage
docker stats --no-stream | grep contravento-frontend
# Expected: <50% CPU, <128 MB RAM per replica

# Verify no source maps in build
find frontend/dist -name "*.map"
# Expected: empty result
```

### Security Verification

```bash
# Test security headers with curl
curl -I https://contravento.com | grep -E "(X-Frame|X-Content|X-XSS)"
# Expected:
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block

# Verify HTTPS redirect
curl -I http://contravento.com
# Expected: 301 Moved Permanently → https://contravento.com

# Check SSL certificate
curl -vI https://contravento.com 2>&1 | grep "SSL certificate verify"
# Expected: certificate verify ok
```

---

## Performance Benchmarks

Use these benchmarks to validate build optimizations:

| Metric | Development | Staging | Production | Target |
|--------|-------------|---------|------------|--------|
| **Bundle Size (uncompressed)** | N/A (dev server) | ~1.05 MB | ~1.05 MB | <1.5 MB |
| **Bundle Size (gzipped)** | N/A | ~350 KB | ~300 KB | <400 KB |
| **First Contentful Paint** | N/A | <2.0s | <1.8s | <2.5s |
| **Time to Interactive** | N/A | <4.0s | <3.8s | <5.0s |
| **Lighthouse Performance** | N/A | >90 | >95 | >85 |
| **HMR Update Time** | <2s | N/A | N/A | <3s |

---

## Common Issues & Solutions

### Issue: "Failed to fetch" errors in production

**Symptoms**: Network errors when calling API endpoints

**Solutions**:
1. Check `VITE_API_URL` in build:
   ```bash
   grep VITE_API_URL frontend/dist/assets/index-*.js
   # Should show https://api.contravento.com
   ```

2. Verify CORS configuration on backend:
   ```bash
   # Check backend .env
   grep CORS_ORIGINS .env.prod
   # Should include https://contravento.com
   ```

3. Check Nginx proxy configuration:
   ```bash
   docker exec contravento-nginx-prod cat /etc/nginx/nginx.conf | grep proxy_pass
   ```

### Issue: Build size exceeds 1.5 MB

**Symptoms**: `npm run build` shows bundle >1.5 MB

**Solutions**:
1. Check for accidentally imported dev dependencies
2. Verify tree shaking is working (no `console.log` in production)
3. Analyze bundle composition:
   ```bash
   npm run build -- --analyze
   # Opens bundle analyzer in browser
   ```

### Issue: Hot reload not working in Docker Full

**Symptoms**: File changes don't trigger Vite HMR

**Solutions**:
1. Verify volume mounts in docker-compose.local.yml:
   ```yaml
   volumes:
     - ./frontend:/app
     - /app/node_modules  # Anonymous volume for node_modules
   ```

2. Check Vite is running in watch mode:
   ```bash
   docker logs contravento-frontend-local | grep "watching for file changes"
   ```

3. Restart frontend container:
   ```bash
   docker restart contravento-frontend-local
   ```

### Issue: Source maps visible in production

**Symptoms**: DevTools shows TypeScript source in production

**Solutions**:
1. Verify build command uses `build:prod`:
   ```bash
   grep "npm run build" deploy.sh
   # Should show: npm run build:prod (not build:staging)
   ```

2. Check vite.config.ts:
   ```typescript
   sourcemap: mode === 'staging'  // Should be false for prod
   ```

3. Rebuild with correct environment:
   ```bash
   cd frontend
   npm run build:prod
   # Verify no .map files in dist/
   ls dist/assets/*.map  # Should be empty
   ```

---

## Automated Testing (Future Enhancement)

Consider adding these automated tests for CI/CD pipeline:

```bash
# Bundle size check
npm run build:prod
SIZE=$(du -sb frontend/dist | cut -f1)
if [ $SIZE -gt 1500000 ]; then
  echo "ERROR: Bundle size exceeds 1.5 MB"
  exit 1
fi

# Lighthouse CI
npx lighthouse-ci https://staging.contravento.com --min-score=0.9

# Security headers check
curl -I https://contravento.com | grep "X-Frame-Options: SAMEORIGIN" || exit 1
```

---

## Rollback Procedure

If deployment fails smoke tests:

```bash
# Staging rollback
docker-compose -f docker-compose.yml -f docker-compose.staging.yml down
git checkout <previous-commit>
./deploy.sh staging

# Production rollback (zero downtime)
docker service rollback contravento-frontend-prod
# Automatic rollback to previous version

# Verify rollback succeeded
curl -I https://contravento.com
```

---

**Last Updated**: 2026-01-13
**Maintained By**: DevOps Team
**Related Docs**: [QUICK_START.md](../QUICK_START.md), [DEPLOYMENT.md](../backend/docs/DEPLOYMENT.md)
