# Research & Technical Decisions: Frontend Deployment Integration

**Feature**: 011-frontend-deployment
**Date**: 2026-01-11
**Status**: Complete

## Overview

This document consolidates research findings for integrating the React/Vite frontend into all deployment environments (SQLite Local, Docker Minimal/Full, staging, production). All technical unknowns from Phase 0 have been resolved with documented decisions and rationales.

---

## 1. Vite Proxy Configuration Best Practices

### Decision

Configure Vite development server to proxy all `/api/*` requests to the backend using `server.proxy` option in `vite.config.ts`.

### Configuration

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Do NOT rewrite path - backend expects /api/* routes
      }
    }
  }
})
```

### Rationale

- **CORS Elimination**: Proxy makes frontend and backend appear on same origin (localhost:5173) to the browser
- **No Backend Changes**: Backend keeps existing `/api/*` route structure without modifications
- **Simple**: No need for `changeOrigin` rewriting or complex path manipulation
- **WebSocket Support**: Vite proxy supports WebSocket upgrades if needed in future (e.g., for real-time features)

### Alternative Considered

**Backend CORS Middleware**: Configure FastAPI CORS to allow `http://localhost:5173`.

**Rejected Because**:
- Requires backend code changes (adding origin to CORS_ORIGINS)
- More error-prone (easy to forget updating CORS when changing ports)
- Doesn't simulate production architecture (where frontend and backend share same domain)

**Reference**: [Vite Server Options - Proxying](https://vitejs.dev/config/server-options.html#server-proxy)

---

## 2. Docker Multi-Stage Builds for Frontend

### Decision

Use **separate Dockerfiles** for development vs production instead of multi-stage builds:
- `frontend/Dockerfile.dev` → Vite dev server for Docker Minimal/Full
- `frontend/Dockerfile.prod` → Nginx + static build for staging/production

### Development Dockerfile (frontend/Dockerfile.dev)

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code (will be overridden by volume mount in docker-compose)
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server with host 0.0.0.0 to allow Docker network access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Production Dockerfile (frontend/Dockerfile.prod)

```dockerfile
# Stage 1: Build static assets
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Build with production environment variables
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built static files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Rationale

- **Clarity**: Separate files make dev vs prod intent explicit
- **Simpler Builds**: No conditional logic based on build args
- **Independent Evolution**: Dev and prod requirements can diverge without affecting each other
- **Docker Compose Integration**: docker-compose.yml naturally selects correct Dockerfile per environment

### Alternative Considered

**Single Multi-Stage Dockerfile** with `--target dev` or `--target prod` build arg.

**Rejected Because**:
- More complex to understand and maintain
- Harder to debug when builds fail (which stage failed?)
- No significant advantage in this use case (we're not reusing layers between stages)

**Reference**: [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

## 3. Environment Variable Management in Vite

### Decision

Use **`.env` mode files** pattern with Vite's built-in environment loading:
- `.env.development` → Auto-loaded when `npm run dev`
- `.env.staging` → Loaded when `npm run build` with `--mode staging`
- `.env.production` → Auto-loaded when `npm run build` (default mode)

### File Structure

```bash
frontend/
├── .env.development          # Local dev (VITE_API_URL=http://localhost:8000)
├── .env.staging             # Staging (VITE_API_URL=https://api-staging.contravento.com)
├── .env.production          # Production (VITE_API_URL=https://api.contravento.com)
└── .env.example             # Template with all required VITE_* variables (for docs)
```

### package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:staging": "vite build --mode staging",
    "build:prod": "vite build --mode production"
  }
}
```

### Environment Variable Access in Code

```typescript
// src/config/api.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY || '';

// Validate required env vars at startup
if (!API_BASE_URL) {
  throw new Error('VITE_API_URL is required');
}
```

### Rationale

- **Vite Native**: Uses Vite's built-in .env file loading (no additional dependencies)
- **Type Safety**: Can generate `env.d.ts` for TypeScript autocompletion
- **Security**: Only `VITE_*` prefixed variables are exposed to frontend code (prevents accidental leaks)
- **Explicit Modes**: `--mode staging` makes build target clear in CI/CD scripts

### Alternative Considered

**Build-time substitution** with shell environment variables in CI/CD.

**Rejected Because**:
- Less portable (requires CI/CD to export env vars correctly)
- No local `.env` files for developers (more setup friction)
- Harder to validate missing variables at build time

**Reference**: [Vite Env Variables and Modes](https://vitejs.dev/guide/env-and-mode.html)

---

## 4. Nginx Configuration for SPA (Single Page Application)

### Decision

Use `try_files` directive to serve `index.html` for all routes, enabling client-side routing with react-router.

### Nginx Configuration (nginx.conf)

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA routing: serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets (JS, CSS, images) aggressively
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Do NOT cache index.html (always fetch fresh for new deployments)
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        expires 0;
    }
}
```

### Rationale

- **SPA Support**: `try_files $uri $uri/ /index.html` ensures all unknown routes fall back to React app
- **Performance**: Aggressive caching for hashed assets (Vite adds content hashes to filenames)
- **Deployment Safety**: No caching on `index.html` ensures users get new deployments immediately
- **Security**: Standard headers prevent clickjacking, MIME sniffing, XSS

### Alternative Considered

**Apache with mod_rewrite** for SPA routing.

**Rejected Because**:
- Nginx is lighter and faster for static file serving
- Project already uses Nginx for backend reverse proxying
- Better documentation and community support for Nginx + Docker

**Reference**: [Nginx Beginner's Guide](https://nginx.org/en/docs/beginners_guide.html)

---

## 5. Docker Compose Service Orchestration

### Decision

Use `depends_on` with **healthchecks** to ensure backend is ready before frontend starts making API calls.

### Docker Compose Configuration

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Prevent overwriting node_modules from host
    depends_on:
      backend:
        condition: service_healthy
    environment:
      - VITE_API_URL=http://backend:8000
```

### Rationale

- **Ordered Startup**: Frontend waits for backend healthcheck to pass before starting
- **Resilience**: Backend retries 5 times with 10s intervals (handles slow DB connections)
- **Development UX**: Developers see frontend loading screen instead of API errors during startup
- **No Extra Dependencies**: Uses built-in Docker Compose features (no wait-for-it.sh scripts)

### Alternative Considered

**wait-for-it.sh script** injected into frontend container to poll backend health endpoint.

**Rejected Because**:
- More complexity (shell script in container, ENTRYPOINT overrides)
- Docker Compose native `depends_on: service_healthy` is cleaner and well-documented
- Healthchecks are reusable for production orchestration (Kubernetes, Docker Swarm)

**Reference**: [Docker Compose Healthchecks](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)

---

## 6. Windows/Linux Script Compatibility

### Decision

Maintain **separate but parallel** scripts for Windows (.ps1) and Linux (.sh) with identical logic and error handling patterns.

### Common Patterns for Both Scripts

**Error Handling** (exit on any command failure):
```bash
# Bash (run-local-dev.sh)
set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failures

# PowerShell (run-local-dev.ps1)
$ErrorActionPreference = "Stop"  # Exit on error
```

**Process Management**:
```bash
# Bash
backend_pid=$!
frontend_pid=$!
trap "kill $backend_pid $frontend_pid" EXIT

# PowerShell
$BackendProcess = Start-Process -PassThru ...
$FrontendProcess = Start-Process -PassThru ...
Register-EngineEvent PowerShell.Exiting -Action {
    Stop-Process -Id $BackendProcess.Id -Force
    Stop-Process -Id $FrontendProcess.Id -Force
}
```

**Logging**:
```bash
# Bash
echo "[INFO] Starting backend..."
echo "[ERROR] Backend failed to start" >&2

# PowerShell
Write-Host "[INFO] Starting backend..." -ForegroundColor Green
Write-Error "[ERROR] Backend failed to start"
```

### Rationale

- **Native Tools**: Each script uses platform-native features (no cross-platform abstractions)
- **Reliability**: Separate scripts are easier to test and debug per platform
- **Maintainability**: Logic is duplicated but clear (changes to .sh require mirrored changes to .ps1)
- **User Experience**: Developers use their platform's native shell (no Git Bash requirement on Windows)

### Alternative Considered

**Single cross-platform Python script** (run-local-dev.py) using subprocess and click.

**Rejected Because**:
- Adds Python dependency for infrastructure (overkill for simple orchestration)
- Harder to understand for sysadmins unfamiliar with Python
- Shell scripts integrate better with existing deployment tooling

**Reference**: [Bash Best Practices](https://google.github.io/styleguide/shellguide.html), [PowerShell Best Practices](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-development-guidelines)

---

## Summary of Decisions

| Research Area | Decision | Key Rationale |
|---------------|----------|---------------|
| **Vite Proxy** | Use `server.proxy` for `/api/*` → backend | Eliminates CORS, no backend changes |
| **Docker Strategy** | Separate `Dockerfile.dev` and `Dockerfile.prod` | Clarity, simpler builds |
| **Environment Variables** | `.env.development`, `.env.staging`, `.env.production` | Vite native, type-safe |
| **Nginx Config** | `try_files` + aggressive asset caching | SPA support, performance |
| **Service Orchestration** | `depends_on` with healthchecks | Ordered startup, resilient |
| **Script Compatibility** | Parallel .sh and .ps1 with identical logic | Native tools, reliable |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Developers forget to start frontend** | Update scripts to start both services by default (--backend-only flag to skip frontend) |
| **CORS issues in production** | Document production architecture: frontend and backend on same domain (subdomain pattern) |
| **Build env vars missing** | Add validation in `vite.config.ts` to throw error if required VITE_* vars undefined |
| **Docker volumes not syncing** | Add troubleshooting section in quickstart.md with `docker-compose logs frontend-dev` |
| **Windows scripts out of sync** | Create checklist in PR template: "If .sh changed, update .ps1" |

---

## Next Steps

All research complete. Ready for Phase 1: Design & Implementation Artifacts.

**Action Items**:
1. Create `quickstart.md` with deployment instructions
2. Update `CLAUDE.md` with frontend deployment commands
3. Proceed to `/speckit.tasks` to generate task breakdown
