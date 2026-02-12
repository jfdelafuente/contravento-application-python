# Frontend Deployment Guide

**Deep dive into ContraVento React frontend deployment**

**Purpose**: Understand Vite build process, environment variables, Nginx configuration, and asset optimization

---

## Table of Contents

1. [Overview](#overview)
2. [Build Modes](#build-modes)
3. [Environment Variables](#environment-variables)
4. [Build Process](#build-process)
5. [Build Output Analysis](#build-output-analysis)
6. [Nginx Configuration](#nginx-configuration)
7. [Asset Optimization](#asset-optimization)
8. [Development Server](#development-server)
9. [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento frontend is a **React 18 + TypeScript** application built with **Vite 5**. It supports three deployment modes:

| Mode | Purpose | Build Command | Source Maps | Output |
|------|---------|---------------|-------------|--------|
| **development** | Local dev with hot reload | `npm run dev` | N/A (no build) | Vite dev server |
| **staging** | Pre-production testing | `npm run build:staging` | ✅ Yes | `dist/` + maps |
| **production** | Live users | `npm run build:prod` | ❌ No | `dist/` (optimized) |

---

## Build Modes

### Development Mode

**Purpose**: Fast iteration with hot module replacement (HMR)

**Command**:
```bash
cd frontend
npm run dev
```

**What happens**:
1. Vite starts dev server on port 5173
2. No build - files served directly from `src/`
3. Hot Module Replacement enabled (updates without full reload)
4. Proxy configured for `/api/*` → `http://localhost:8000`
5. Opens browser automatically (configurable)

**Environment**:
- Uses `.env.development` (auto-loaded)
- `import.meta.env.DEV === true`
- `import.meta.env.MODE === 'development'`

**Access**:
- Frontend: http://localhost:5173
- Backend (via proxy): http://localhost:5173/api/*

---

### Staging Mode

**Purpose**: Test production build with source maps for debugging

**Command**:
```bash
cd frontend
npm run build:staging
```

**What happens**:
1. TypeScript compilation (`tsc`)
2. Vite build with `--mode staging`
3. Loads `.env.staging` variables
4. **Generates source maps** for debugging
5. Minifies code (Terser)
6. Outputs to `dist/` directory

**Environment**:
- Uses `.env.staging`
- `import.meta.env.DEV === false`
- `import.meta.env.MODE === 'staging'`
- `import.meta.env.PROD === true`

**Build size**: ~360 KB gzipped (with source maps: +200 KB)

**Deployment**:
```bash
# From project root
./deploy.sh staging
```

---

### Production Mode

**Purpose**: Maximum optimization for live users

**Command**:
```bash
cd frontend
npm run build:prod
```

**What happens**:
1. TypeScript compilation (`tsc`)
2. Vite build with `--mode production`
3. Loads `.env.production` variables
4. **No source maps** (security + size)
5. Aggressive minification
6. Tree-shaking (removes unused code)
7. Code splitting (vendor chunks)
8. Outputs to `dist/` directory

**Environment**:
- Uses `.env.production`
- `import.meta.env.DEV === false`
- `import.meta.env.MODE === 'production'`
- `import.meta.env.PROD === true`

**Build size**: ~360 KB gzipped (66% reduction from uncompressed)

**Deployment**:
```bash
# From project root
./deploy.sh prod
```

---

## Environment Variables

### Naming Convention

**CRITICAL**: All frontend variables must be prefixed with `VITE_`:

```env
# ✅ CORRECT - Exposed to frontend
VITE_API_URL=https://api.contravento.com
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA

# ❌ WRONG - Not exposed to frontend
API_URL=https://api.contravento.com
TURNSTILE_SITE_KEY=1x00000000000000000000AA
```

**Why**: Vite only exposes variables with `VITE_` prefix to prevent accidental exposure of secrets.

---

### Environment Files

| File | Loaded When | Purpose |
|------|-------------|---------|
| `.env.development` | `npm run dev` | Auto-loaded in dev mode |
| `.env.staging` | `npm run build:staging` | Staging build variables |
| `.env.production` | `npm run build:prod` | Production build variables |
| `.env.example` | Never | Template for creating .env files |

---

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://api.contravento.com` |
| `VITE_TURNSTILE_SITE_KEY` | Cloudflare Turnstile public key | `1x00000000000000000000AA` |

---

### Accessing Variables in Code

```typescript
// src/config.ts
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY;

// Usage in components
import { API_URL } from '@/config';

const response = await fetch(`${API_URL}/users/me`);
```

**Special Variables** (always available):
```typescript
import.meta.env.MODE        // 'development', 'staging', 'production'
import.meta.env.DEV         // true in dev mode
import.meta.env.PROD        // true in production/staging
import.meta.env.BASE_URL    // Base URL for assets (usually '/')
```

---

## Build Process

### Step-by-Step Breakdown

#### 1. TypeScript Compilation

```bash
tsc
```

**Purpose**: Type-check code before building

**Output**: No files generated (just type checking)

**Errors block build**: Yes

---

#### 2. Vite Build

```bash
vite build --mode production
```

**Steps**:
1. **Load environment variables** from `.env.production`
2. **Bundle modules** using Rollup
3. **Minify JavaScript** with Terser
4. **Minify CSS** (built-in)
5. **Generate hashed filenames** for cache busting
6. **Code splitting** into chunks:
   - Main bundle (`index-[hash].js`)
   - React vendor (`react-vendor-[hash].js`)
   - Form vendor (`form-vendor-[hash].js`)
   - Map vendor (`map-vendor-[hash].js`)
7. **Optimize images** (inline small images as base64)
8. **Generate `index.html`** with correct script tags

---

### Code Splitting Strategy

**Configured in `vite.config.ts`**:

```typescript
rollupOptions: {
  output: {
    manualChunks: {
      'react-vendor': ['react', 'react-dom', 'react-router-dom'],
      'form-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
      'map-vendor': ['react-leaflet', 'leaflet'],
    },
  },
},
```

**Benefits**:
- **Better caching**: Vendor code changes less frequently
- **Parallel downloads**: Browser loads multiple chunks simultaneously
- **Smaller initial load**: User only downloads what they need

**Example output**:
```
dist/
├── index.html                          # Entry point (15 KB)
├── assets/
│   ├── index-a1b2c3d4.js             # Main app code (120 KB)
│   ├── react-vendor-e5f6g7h8.js      # React libraries (180 KB)
│   ├── form-vendor-i9j0k1l2.js       # Form libraries (40 KB)
│   ├── map-vendor-m3n4o5p6.js        # Map libraries (80 KB)
│   └── index-q7r8s9t0.css            # Styles (40 KB)
```

---

## Build Output Analysis

### Directory Structure

```
frontend/dist/
├── index.html                  # Entry point (NOT cached)
├── assets/
│   ├── index-[hash].css       # Hashed CSS (cached 1 year)
│   ├── index-[hash].js        # Hashed JS bundle (cached 1 year)
│   ├── react-vendor-[hash].js # React libraries bundle
│   ├── form-vendor-[hash].js  # Form libraries bundle
│   ├── map-vendor-[hash].js   # Map libraries bundle
│   └── [images]               # Hashed images (if any)
└── assets/*.map               # Source maps (staging only)
```

---

### File Sizes

**Production build** (after gzip):

| File | Uncompressed | Gzipped | Percentage |
|------|--------------|---------|------------|
| **index.html** | 15 KB | 5 KB | - |
| **index-[hash].js** | 360 KB | 120 KB | 33% |
| **react-vendor-[hash].js** | 540 KB | 180 KB | 33% |
| **form-vendor-[hash].js** | 120 KB | 40 KB | 33% |
| **map-vendor-[hash].js** | 240 KB | 80 KB | 33% |
| **index-[hash].css** | 120 KB | 40 KB | 33% |
| **Total** | ~1.4 MB | ~465 KB | 33% |

**Why gzip matters**:
- Nginx serves files with gzip compression
- JavaScript compresses well (~70% reduction)
- User downloads ~465 KB instead of ~1.4 MB

---

### Cache Busting with Hashes

**Problem**: Browser caches old versions after deployment

**Solution**: Vite adds content hash to filenames:

```
Before deploy:  index-a1b2c3d4.js
After deploy:   index-e5f6g7h8.js  # Different hash = different file
```

**Browser behavior**:
1. User visits site
2. Browser sees `index-e5f6g7h8.js` (new name)
3. Browser downloads new file (cache miss)
4. Browser caches new file for 1 year

**Result**: Automatic cache invalidation on deployment

---

## Nginx Configuration

ContraVento uses Nginx to serve the production build.

### Complete Configuration

**File**: `frontend/nginx.conf`

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
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript
               image/svg+xml;
    gzip_min_length 256;

    # Proxy API requests to backend
    location /api/ {
        client_max_body_size 10M;  # GPX files can be 1-10 MB
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SPA routing: serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets aggressively
    location ~* \.(js|css|png|jpe?g|gif|ico|svg|woff2?|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # CRITICAL: Do NOT cache index.html
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        expires 0;
    }
}
```

---

### Key Features Explained

#### 1. Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
```

**Purpose**: Prevents clickjacking attacks

**Behavior**: Page can only be embedded in frames from same origin

---

```nginx
add_header X-Content-Type-Options "nosniff" always;
```

**Purpose**: Prevents MIME type sniffing

**Behavior**: Browser respects declared Content-Type

---

```nginx
add_header X-XSS-Protection "1; mode=block" always;
```

**Purpose**: Enables browser XSS filter

**Behavior**: Blocks pages if XSS attack detected

---

#### 2. Gzip Compression

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 256;
```

**Purpose**: Reduce transfer size

**Behavior**:
- Compress responses before sending
- Only compress files >256 bytes (overhead not worth it for tiny files)
- Skip images (already compressed)

**Result**: ~70% size reduction for JS/CSS

---

#### 3. API Proxy

```nginx
location /api/ {
    proxy_pass http://backend:8000/;
}
```

**Purpose**: Eliminate CORS errors

**Behavior**:
- Request to `https://contravento.com/api/users/me`
- Nginx forwards to `http://backend:8000/users/me`
- Same-origin for browser (no CORS preflight)

**Important**: Note the trailing `/` in `proxy_pass` - it strips `/api` prefix

---

#### 4. SPA Routing

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

**Purpose**: Support React Router

**Behavior**:
1. Try to serve file at exact path (e.g., `/logo.png`)
2. Try to serve directory index (e.g., `/blog/` → `/blog/index.html`)
3. Fall back to `index.html` (let React Router handle routing)

**Result**: Refreshing on `/trips/123` works (doesn't 404)

---

#### 5. Aggressive Asset Caching

```nginx
location ~* \.(js|css|png|...)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Purpose**: Maximum performance for static assets

**Behavior**:
- Cache for 1 year
- `immutable` = never revalidate (hash in filename guarantees uniqueness)

**Safe because**: Filenames have content hash (changed content = new filename)

---

#### 6. Never Cache HTML

```nginx
location = /index.html {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    expires 0;
}
```

**Purpose**: Always fetch latest HTML on deployment

**Behavior**:
- Browser always requests fresh `index.html`
- `index.html` references new hashed assets
- User gets latest version immediately

**CRITICAL**: Without this, users might see old `index.html` with references to deleted assets

---

## Asset Optimization

### 1. Code Splitting

**What**: Split code into multiple bundles

**How**: Vite automatically splits vendor code

**Benefits**:
- Smaller initial download
- Better caching (vendor code changes less)
- Parallel downloads

---

### 2. Tree Shaking

**What**: Remove unused code

**How**: Vite uses Rollup tree-shaking

**Example**:
```typescript
// lodash has 100 functions, but you only import 1
import { debounce } from 'lodash';

// Vite only bundles `debounce`, not the other 99 functions
```

**Savings**: ~40-50% reduction in bundle size

---

### 3. Minification

**What**: Remove whitespace, shorten variable names

**How**: Terser minifier (configured in `vite.config.ts`)

**Example**:
```typescript
// Before minification (120 KB)
function calculateTotalDistance(trips) {
  return trips.reduce((total, trip) => total + trip.distance, 0);
}

// After minification (40 KB)
function c(t){return t.reduce((t,e)=>t+e.distance,0)}
```

**Savings**: ~70% size reduction

---

### 4. Lazy Loading

**What**: Load components only when needed

**How**: React.lazy + Suspense

**Example**:
```typescript
// Eager loading (included in main bundle)
import TripDetailPage from './pages/TripDetailPage';

// Lazy loading (separate chunk)
const TripDetailPage = React.lazy(() => import('./pages/TripDetailPage'));

// Usage with Suspense
<Suspense fallback={<Spinner />}>
  <TripDetailPage />
</Suspense>
```

**Benefits**:
- Faster initial load
- Download components only when user navigates to them

---

### 5. Image Optimization

**What**: Optimize images for web

**How**: Manual (not automated in build)

**Recommendations**:
- Use WebP format (better compression than JPEG)
- Resize to maximum display size
- Use responsive images (`srcset`)

**Example**:
```tsx
<img
  src="/images/logo.webp"
  srcSet="/images/logo@1x.webp 1x, /images/logo@2x.webp 2x"
  alt="ContraVento"
/>
```

---

## Development Server

### Proxy Configuration

**Purpose**: Avoid CORS errors in development

**Configuration** (`vite.config.ts`):
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
},
```

**Behavior**:
- Request: `http://localhost:5173/api/users/me`
- Vite proxy: `http://localhost:8000/users/me`
- Response: Same-origin (no CORS)

**Important**: Only works in dev mode (`npm run dev`)

---

### Hot Module Replacement (HMR)

**What**: Update code without full page reload

**How**: Vite's built-in HMR

**Example**:
1. Edit `App.tsx`
2. Save file
3. Browser updates in <2 seconds without reload
4. React state preserved

**Benefits**:
- Instant feedback
- Preserves application state
- Faster development

---

## Troubleshooting

### Build Fails with TypeScript Errors

**Symptom**:
```
error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'
Build failed with 5 errors
```

**Solution**:
```bash
# Check type errors
npm run type-check

# Fix errors in code
# Add null checks, fix type definitions, etc.

# Then build
npm run build:prod
```

---

### Environment Variable Not Defined

**Symptom**:
```
Error: VITE_API_URL is required but not defined
Build failed
```

**Solution**:
```bash
# Ensure .env file exists
ls frontend/.env.production

# Verify file contains required variables
cat frontend/.env.production

# Should contain:
# VITE_API_URL=https://api.contravento.com
# VITE_TURNSTILE_SITE_KEY=...
```

---

### Assets Not Loading (404)

**Symptom**: Images/fonts show 404 errors

**Solution**:

**1. Use import (not hardcoded paths)**:
```typescript
// ✅ CORRECT - Vite processes this
import logo from '@/assets/logo.png';
<img src={logo} alt="Logo" />

// ❌ WRONG - Path won't be resolved
<img src="/assets/logo.png" alt="Logo" />
```

**2. Check Nginx configuration**:
```nginx
# Ensure static assets are served
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

### Build Size Too Large

**Symptom**: Build output >1 MB (gzipped)

**Solution**:

**1. Analyze bundle**:
```bash
npm run build -- --mode production

# Check output:
# dist/assets/index-abc123.js  360.00 KB │ gzip: 120.00 KB
```

**2. Add code splitting** (if not configured):
```typescript
// vite.config.ts
rollupOptions: {
  output: {
    manualChunks: {
      'vendor': ['react', 'react-dom'],
      'utils': ['lodash', 'date-fns'],
    },
  },
},
```

**3. Use lazy loading** for large components

---

## See Also

- **[Getting Started](getting-started.md)** - Initial frontend setup
- **[Troubleshooting](troubleshooting.md)** - Frontend-specific issues
- **[Environment Variables](environment-variables.md)** - VITE_* variables reference
- **[Docker Compose Guide](docker-compose-guide.md)** - Frontend container setup

---

**Last Updated**: 2026-02-06

**Vite Version**: 5.0.8

**React Version**: 18.2.0

**Feedback**: Found incorrect build instructions? [Open an issue](https://github.com/your-org/contravento-application-python/issues)
