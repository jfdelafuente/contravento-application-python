# Frontend Quickstart Guide: Authentication System
**Feature**: 005-frontend-user-profile
**Created**: 2026-01-08
**Status**: READY FOR IMPLEMENTATION

## Overview

This guide walks you through setting up the ContraVento frontend development environment for the authentication and user profile system.

**What you'll build**: React 18 + TypeScript SPA with authentication, registration, email verification, and password management.

**Prerequisites**:
- Node.js 18+ and npm 9+ installed
- Backend API running (see [backend/CLAUDE.md](../../../CLAUDE.md#local-development-options))
- Cloudflare Turnstile site key (for CAPTCHA)

---

## Table of Contents

1. [Quick Start (5 minutes)](#1-quick-start-5-minutes)
2. [Project Setup](#2-project-setup)
3. [Environment Configuration](#3-environment-configuration)
4. [Backend Connection](#4-backend-connection)
5. [Development Workflow](#5-development-workflow)
6. [Testing](#6-testing)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Quick Start (5 minutes)

```bash
# Navigate to project root
cd /path/to/contravento-application-python

# Create frontend directory
mkdir frontend && cd frontend

# Initialize Vite + React + TypeScript project
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Install additional packages
npm install react-router-dom axios @marsidev/react-turnstile react-hook-form @hookform/resolvers zod

# Install dev dependencies
npm install --save-dev @types/node

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your settings
nano .env.local

# Start dev server
npm run dev
# Open http://localhost:3000
```

---

## 2. Project Setup

### A. Create Vite Project

```bash
# From contravento-application-python/
npm create vite@latest frontend -- --template react-ts

cd frontend
```

**Why Vite?** Fastest dev server, optimized production builds, zero config TypeScript support.

### B. Install Core Dependencies

```bash
# React ecosystem
npm install react@^18.2.0 react-dom@^18.2.0

# Routing
npm install react-router-dom@^6.21.0

# HTTP client
npm install axios@^1.6.5

# CAPTCHA
npm install @marsidev/react-turnstile@^0.7.0

# Form handling and validation
npm install react-hook-form@^7.50.0 @hookform/resolvers@^3.3.4 zod@^3.22.4
```

### C. Install Dev Dependencies

```bash
# TypeScript types
npm install --save-dev @types/node@^20.10.0

# Testing (optional but recommended)
npm install --save-dev vitest@^1.1.0 @testing-library/react@^14.1.0 @testing-library/jest-dom@^6.1.5 @testing-library/user-event@^14.5.1

# Linting (optional)
npm install --save-dev eslint@^8.56.0 @typescript-eslint/eslint-plugin@^6.18.0 @typescript-eslint/parser@^6.18.0
```

### D. Project Structure

Create this directory structure inside `frontend/`:

```bash
mkdir -p src/{components/{auth,routing},pages,contexts,hooks,services,utils,types,styles}
mkdir -p public
```

**Expected structure**:

```
frontend/
├── public/                     # Static assets
├── src/
│   ├── components/
│   │   ├── auth/              # Auth-specific components
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── LoginForm.tsx
│   │   │   ├── PasswordStrengthMeter.tsx
│   │   │   ├── TurnstileWidget.tsx
│   │   │   └── AccountBlockedMessage.tsx
│   │   └── routing/           # Routing utilities
│   │       └── ProtectedRoute.tsx
│   ├── pages/                 # Page components
│   │   ├── RegisterPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── VerifyEmailPage.tsx
│   │   ├── ForgotPasswordPage.tsx
│   │   ├── ResetPasswordPage.tsx
│   │   └── DashboardPage.tsx
│   ├── contexts/              # React Context providers
│   │   └── AuthContext.tsx
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useDebounce.ts
│   │   └── useCountdown.ts
│   ├── services/              # API service layer
│   │   ├── api.ts            # Axios config
│   │   └── authService.ts    # Auth API calls
│   ├── utils/                 # Utility functions
│   │   ├── validators.ts
│   │   ├── passwordStrength.ts
│   │   └── typeGuards.ts
│   ├── types/                 # TypeScript types
│   │   ├── user.ts
│   │   ├── auth.ts
│   │   ├── forms.ts
│   │   ├── api.ts
│   │   └── errors.ts
│   ├── styles/                # Global styles
│   │   └── global.css
│   ├── App.tsx                # Main app component
│   ├── main.tsx               # Entry point
│   └── vite-env.d.ts          # Vite types
├── .env.example               # Environment template
├── .env.local                 # Local environment (gitignored)
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

---

## 3. Environment Configuration

### A. Create `.env.example`

```bash
# frontend/.env.example
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=your_turnstile_site_key_here
VITE_ENV=development
VITE_DEBUG=false
```

### B. Create `.env.local`

```bash
# Copy template
cp .env.example .env.local

# Edit with your values
nano .env.local
```

**Required values**:

- **VITE_API_URL**: Backend API URL
  - Local dev: `http://localhost:8000`
  - Docker local-dev: `http://localhost:8000`
  - Dev environment: `https://api-dev.contravento.com`

- **VITE_TURNSTILE_SITE_KEY**: Get from Cloudflare Turnstile dashboard
  - Sign up: https://www.cloudflare.com/products/turnstile/
  - Create site → Copy site key
  - Testing key (always passes): `1x00000000000000000000AA`

### C. Update `.gitignore`

```bash
# frontend/.gitignore
# Add to existing .gitignore
.env.local
.env.production.local
.env.development.local
```

---

## 4. Backend Connection

### A. Start Backend API

**Option 1: Quick SQLite (Recommended for frontend dev)**

```bash
# From contravento-application-python/backend/
./run-local-dev.sh        # Linux/Mac
.\run-local-dev.ps1       # Windows

# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Option 2: Docker with PostgreSQL**

```bash
# From contravento-application-python/
./deploy.sh local-minimal

# Backend runs at http://localhost:8000
```

See [backend/docs/DEPLOYMENT.md](../../../backend/docs/DEPLOYMENT.md) for full backend setup.

### B. Verify Backend Connection

```bash
# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test CORS (should return 404 but not CORS error)
curl -H "Origin: http://localhost:3000" http://localhost:8000/auth/me
```

### C. Configure CORS in Backend

Ensure backend `.env` has:

```env
# backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Why two ports?**
- Vite dev server typically uses 5173
- You can customize to 3000 in `vite.config.ts`

---

## 5. Development Workflow

### A. Start Dev Server

```bash
cd frontend
npm run dev

# Output:
# VITE v5.0.0  ready in 500 ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
```

**Custom port (optional)**:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Use port 3000 instead of 5173
    open: true, // Auto-open browser
  },
});
```

### B. Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

### C. Hot Module Replacement (HMR)

Vite automatically reloads changes. Edit any `.tsx` file and see instant updates without full page reload.

### D. Development Tips

1. **Use React DevTools**: Install browser extension for component inspection
2. **Enable SourceMaps**: Already enabled in dev mode for debugging
3. **Network tab**: Monitor API calls in browser DevTools
4. **Console errors**: Fix TypeScript errors as you code (Vite shows them in browser)

---

## 6. Testing

### A. Test User Accounts

Create test users in backend:

```bash
# From backend/
poetry run python scripts/create_verified_user.py

# Creates:
# - testuser / test@example.com / TestPass123! (verified)
# - maria_garcia / maria@example.com / SecurePass456! (verified)
```

### B. Manual Testing Checklist

**Registration Flow**:
- [ ] Form validation (username, email, password)
- [ ] Password strength meter (red/yellow/green)
- [ ] Debounced email availability check
- [ ] CAPTCHA widget loads
- [ ] Success message after registration
- [ ] Verification email sent (check MailHog at http://localhost:8025)

**Login Flow**:
- [ ] Valid credentials → redirects to dashboard
- [ ] Invalid credentials → error message
- [ ] Unverified email → blocks login with message
- [ ] Remember Me checkbox → long-lived session
- [ ] Account blocking after 5 failed attempts

**Email Verification**:
- [ ] Click link in email → verifies account
- [ ] Expired token → shows error
- [ ] Invalid token → shows error
- [ ] Resend verification email button works

**Password Reset**:
- [ ] Enter email → sends reset link
- [ ] Click link → shows reset form
- [ ] Valid new password → resets successfully
- [ ] Expired token → shows error

### C. Automated Testing (Optional)

```bash
# Install testing dependencies
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event happy-dom

# Create vitest.config.ts
cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'happy-dom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
});
EOF

# Run tests
npm run test

# Run with coverage (≥90% target)
npm run test -- --coverage
```

---

## 7. Troubleshooting

### Problem: CORS Errors

**Symptom**: `Access to XMLHttpRequest blocked by CORS policy`

**Solutions**:
1. Ensure backend `.env` includes `CORS_ORIGINS=http://localhost:3000`
2. Restart backend after changing CORS config
3. Check Axios config has `withCredentials: true`
4. Clear browser cache and cookies

```typescript
// src/services/api.ts - Verify this is set
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // CRITICAL for HttpOnly cookies
});
```

### Problem: HttpOnly Cookies Not Sent

**Symptom**: 401 Unauthorized on protected routes

**Solutions**:
1. Verify `withCredentials: true` in Axios config
2. Check `Set-Cookie` header in login response (DevTools → Network tab)
3. Ensure `Secure` flag is off in local dev (or use HTTPS)
4. Check browser allows third-party cookies (shouldn't matter for same-origin)

**Debug**:
```bash
# Check cookies in browser DevTools
# Application tab → Cookies → http://localhost:3000
# Should see: access_token, refresh_token
```

### Problem: Vite Environment Variables Not Loading

**Symptom**: `import.meta.env.VITE_API_URL` is undefined

**Solutions**:
1. Ensure variable starts with `VITE_` prefix
2. Restart dev server after changing `.env.local`
3. Check file is named `.env.local` not `.env`
4. Verify syntax (no spaces around `=`)

### Problem: TypeScript Errors

**Symptom**: `Cannot find module 'react'` or similar

**Solutions**:
1. Run `npm install` to ensure all deps installed
2. Restart VS Code TypeScript server: `Ctrl+Shift+P` → "Restart TS Server"
3. Check `tsconfig.json` includes `"jsx": "react-jsx"`

### Problem: Turnstile Widget Not Loading

**Symptom**: CAPTCHA widget doesn't appear

**Solutions**:
1. Verify `VITE_TURNSTILE_SITE_KEY` is set in `.env.local`
2. Check browser console for errors
3. Use test key for local dev: `1x00000000000000000000AA`
4. Check network tab for Cloudflare script loading

### Problem: 401 After Token Refresh

**Symptom**: Axios interceptor triggers infinite loop

**Solutions**:
1. Add `_retry` flag to prevent infinite retries
2. Check refresh token is still valid (check cookies)
3. Logout and login again to get fresh tokens

```typescript
// Verify interceptor has retry guard
if (error.response?.status === 401 && !error.config._retry) {
  error.config._retry = true;
  // ... refresh logic
}
```

### Problem: Backend Not Running

**Symptom**: `ERR_CONNECTION_REFUSED` in Network tab

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
cd backend
./run-local-dev.sh  # or .\run-local-dev.ps1 on Windows

# Check backend logs for errors
```

---

## Next Steps

### Phase 1: Core Setup ✅
- [x] Initialize Vite project
- [x] Install dependencies
- [x] Configure environment variables
- [x] Verify backend connection

### Phase 2: Type Definitions
- [ ] Copy types from [data-model.md](./data-model.md) to `src/types/`
- [ ] Create `src/types/user.ts`
- [ ] Create `src/types/auth.ts`
- [ ] Create `src/types/forms.ts`
- [ ] Create `src/types/api.ts`
- [ ] Create `src/types/errors.ts`

### Phase 3: Services Layer
- [ ] Implement `src/services/api.ts` (Axios config with interceptors)
- [ ] Implement `src/services/authService.ts` (API calls)

### Phase 4: Utilities
- [ ] Implement `src/utils/passwordStrength.ts`
- [ ] Implement `src/hooks/useDebounce.ts`
- [ ] Implement `src/hooks/useCountdown.ts`

### Phase 5: Auth Context
- [ ] Implement `src/contexts/AuthContext.tsx`
- [ ] Wrap `<App>` with `<AuthProvider>`

### Phase 6: Components
- [ ] Implement `src/components/auth/PasswordStrengthMeter.tsx`
- [ ] Implement `src/components/auth/TurnstileWidget.tsx`
- [ ] Implement `src/components/auth/RegisterForm.tsx`
- [ ] Implement `src/components/auth/LoginForm.tsx`
- [ ] Implement `src/components/auth/AccountBlockedMessage.tsx`
- [ ] Implement `src/components/routing/ProtectedRoute.tsx`

### Phase 7: Pages
- [ ] Implement `src/pages/RegisterPage.tsx`
- [ ] Implement `src/pages/LoginPage.tsx`
- [ ] Implement `src/pages/VerifyEmailPage.tsx`
- [ ] Implement `src/pages/ForgotPasswordPage.tsx`
- [ ] Implement `src/pages/ResetPasswordPage.tsx`
- [ ] Implement `src/pages/DashboardPage.tsx`

### Phase 8: Routing
- [ ] Configure React Router in `src/App.tsx`
- [ ] Set up protected routes
- [ ] Test navigation flows

### Phase 9: Testing & Polish
- [ ] Write component tests
- [ ] Manual testing with checklist
- [ ] Fix accessibility issues
- [ ] Optimize bundle size
- [ ] Add loading states and transitions

---

## Additional Resources

- **Specification**: [spec.md](./spec.md) - Feature requirements
- **Implementation Plan**: [plan.md](./plan.md) - Technical architecture
- **Research Decisions**: [research.md](./research.md) - Technology choices
- **API Contract**: [contracts/auth-api.yaml](./contracts/auth-api.yaml) - OpenAPI spec
- **Data Model**: [data-model.md](./data-model.md) - TypeScript types

**External Docs**:
- Vite: https://vitejs.dev/guide/
- React 18: https://react.dev/
- React Router 6: https://reactrouter.com/
- React Hook Form: https://react-hook-form.com/
- Axios: https://axios-http.com/
- Cloudflare Turnstile: https://developers.cloudflare.com/turnstile/

---

**Document Status**: ✅ COMPLETE
**Ready for Implementation**: YES
**Reviewed By**: Implementation Planning Agent
**Approved**: 2026-01-08
