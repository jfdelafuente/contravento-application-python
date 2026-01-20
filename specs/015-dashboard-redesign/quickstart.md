# Quick Start Guide: Dashboard Redesign

**Feature**: 015-dashboard-redesign
**Branch**: `015-dashboard-redesign`
**Date**: 2026-01-20

## Prerequisites

- Node.js 18+ installed
- Backend running at `http://localhost:8000` (Python/FastAPI)
- Git repository cloned
- Branch `015-dashboard-redesign` checked out

## Setup (First Time)

```bash
# 1. Ensure you're on the correct branch
git checkout 015-dashboard-redesign
git pull origin 015-dashboard-redesign

# 2. Install frontend dependencies (if not done)
cd frontend
npm install

# 3. Verify backend is running
curl http://localhost:8000/docs
# Should return Swagger UI

# 4. Start frontend dev server
npm run dev
# Access at http://localhost:5173
```

## Development Workflow

### 1. Backend Setup (Local Dev)

```bash
# Terminal 1 - Start backend with SQLite
cd backend
poetry run python -m src.main
# OR use run-local-dev.sh for auto-setup

# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Test Backend Endpoints**:

```bash
# Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123!"}'

# Get dashboard stats (replace TOKEN)
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "Authorization: Bearer TOKEN"
```

### 2. Frontend Development

```bash
# Terminal 2 - Start frontend
cd frontend
npm run dev

# Frontend: http://localhost:5173
# Auto-reload on file changes
```

### 3. Component Development Pattern

**Example: Creating `DashboardHeader` component**

```bash
# 1. Create component file (Tailwind CSS - NO .css file)
mkdir -p src/components/dashboard
touch src/components/dashboard/DashboardHeader.tsx

# 2. Create custom hook
touch src/hooks/useGlobalSearch.ts

# 3. Create TypeScript types
touch src/types/dashboard.ts

# 4. Create service
touch src/services/dashboardService.ts

# 5. Create cn() utility (first time only)
mkdir -p src/lib
touch src/lib/cn.ts

# 6. Create tests
touch tests/unit/components/DashboardHeader.test.tsx
touch tests/e2e/dashboard-navigation.spec.ts
```

**Component Template (Tailwind CSS)**:

```typescript
// src/components/dashboard/DashboardHeader.tsx
import React from 'react';
import { cn } from '@/lib/cn';

export interface DashboardHeaderProps {
  className?: string;
  // Other props
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  className,
  ...props
}) => {
  return (
    <header
      className={cn(
        // Sticky positioning
        'sticky top-0 z-50',

        // Base styles
        'bg-white px-6 py-4',

        // Border & shadow
        'shadow-sm border-b border-gray-200',

        // Custom classes from props
        className
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Component content */}
      </div>
    </header>
  );
};

export default DashboardHeader;
```

**cn() Helper Function** (create once, reuse everywhere):

```typescript
// src/lib/cn.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combina clases de Tailwind evitando conflictos
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
```

**Tailwind Configuration** (already set up in [tailwind-setup.md](tailwind-setup.md)):

```css
/* src/index.css - Tailwind entry point */
@import "tailwindcss";

@theme {
  --color-primary: #6B8E23;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --font-family-serif: 'Merriweather', serif;
}

@source "src/**/*.{js,ts,jsx,tsx}";
```

### 4. Testing Workflow (TDD)

**Write tests FIRST** before implementing:

```bash
# 1. Write failing test
npm run test:unit -- DashboardHeader.test.tsx --watch

# 2. Implement component until test passes
# (Edit DashboardHeader.tsx)

# 3. Run all tests
npm run test:unit
npm run test:coverage

# 4. E2E tests (after component done)
npm run test:e2e -- dashboard-navigation.spec.ts --headed
```

**Unit Test Template** (Vitest + React Testing Library):

```typescript
// tests/unit/components/DashboardHeader.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardHeader } from '../../../src/components/dashboard/DashboardHeader';

describe('DashboardHeader', () => {
  it('should render logo and navigation', () => {
    render(<DashboardHeader />);

    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByAltText('ContraVento')).toBeInTheDocument();
  });

  it('should show search bar', () => {
    render(<DashboardHeader />);

    const searchInput = screen.getByPlaceholderText(/buscar/i);
    expect(searchInput).toBeInTheDocument();
  });
});
```

**E2E Test Template** (Playwright):

```typescript
// tests/e2e/dashboard-navigation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('header remains sticky on scroll', async ({ page }) => {
    const header = page.locator('header.dashboard-header');

    // Get initial position
    const initialTop = await header.boundingBox().then(box => box?.y);

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 1000));

    // Header should still be visible at top
    const scrolledTop = await header.boundingBox().then(box => box?.y);
    expect(scrolledTop).toBe(0); // Sticky at top
  });

  test('global search shows results', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar"]');

    await searchInput.fill('test');
    await page.waitForTimeout(400); // Wait for debounce

    const results = page.locator('.search-results');
    await expect(results).toBeVisible();
  });
});
```

### 5. API Service Pattern

```typescript
// src/services/dashboardService.ts
import axios from 'axios';
import type { DashboardStats, FeedResponse } from '../types/dashboard';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await axios.get<{ success: boolean; data: DashboardStats }>(
    `${API_BASE}/api/v1/dashboard/stats`,
    {
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    }
  );

  if (!response.data.success) {
    throw new Error('Failed to fetch dashboard stats');
  }

  return response.data.data;
};

export const getActivityFeed = async (page: number = 1, limit: number = 50): Promise<FeedResponse> => {
  const response = await axios.get<{ success: boolean; data: FeedResponse }>(
    `${API_BASE}/api/v1/dashboard/feed`,
    {
      params: { page, limit },
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    }
  );

  return response.data.data;
};

function getAuthToken(): string {
  // Get from AuthContext or localStorage
  return localStorage.getItem('auth_token') || '';
}
```

### 6. Custom Hook Pattern

```typescript
// src/hooks/useDashboardStats.ts
import { useState, useEffect } from 'react';
import { getDashboardStats } from '../services/dashboardService';
import type { DashboardStats } from '../types/dashboard';

export const useDashboardStats = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const data = await getDashboardStats();
        setStats(data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Error al cargar estadísticas');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const refetch = () => {
    setIsLoading(true);
    setError(null);
    fetchStats();
  };

  return { stats, isLoading, error, refetch };
};
```

## Common Tasks

### Run Tests

```bash
# Unit tests (watch mode)
npm run test:unit -- --watch

# Unit tests with coverage
npm run test:coverage

# E2E tests (all browsers)
npm run test:e2e

# E2E tests (headed mode - see browser)
npm run test:e2e:headed

# E2E tests (debug mode)
npm run test:e2e:debug

# E2E tests (specific file)
npm run test:e2e -- dashboard-stats.spec.ts
```

### Linting & Formatting

```bash
# Lint TypeScript
npm run lint

# Type check
npm run type-check

# Auto-fix linting issues
npm run lint -- --fix
```

### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

## Debugging

### Browser DevTools

1. Open http://localhost:5173
2. Press F12 (DevTools)
3. Sources tab → Set breakpoints in `.tsx` files
4. Console tab → View console.log outputs

### React DevTools

```bash
# Install React DevTools browser extension
# Chrome: https://chrome.google.com/webstore/detail/react-developer-tools
# Firefox: https://addons.mozilla.org/firefox/addon/react-devtools/
```

### Playwright Debug Mode

```bash
# Debug specific test
npm run test:e2e:debug -- dashboard-navigation.spec.ts

# Opens Playwright Inspector
# Step through test execution
# View selectors, screenshots, traces
```

## Troubleshooting

### Backend Not Running

**Error**: `ERR_CONNECTION_REFUSED` on API calls

**Solution**:

```bash
cd backend
poetry run python -m src.main
# Verify at http://localhost:8000/docs
```

### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**: Backend CORS already configured for `http://localhost:5173`. Verify backend logs show CORS middleware active.

### Authentication Errors

**Error**: `401 Unauthorized` on dashboard endpoints

**Solution**:

```bash
# 1. Login via UI: http://localhost:5173/login
#    Username: testuser
#    Password: TestPass123!

# 2. Check token in localStorage (DevTools → Application → Local Storage)
# 3. Verify token not expired (JWT expires after 15 minutes)
```

### Type Errors

**Error**: `Property 'xyz' does not exist on type...`

**Solution**:

```bash
# 1. Ensure types are imported
import type { DashboardStats } from '../types/dashboard';

# 2. Run type check
npm run type-check

# 3. Restart VSCode TypeScript server
# Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"
```

### Test Failures

**Error**: Tests failing with "Element not found"

**Solution**:

```typescript
// Use proper async matchers
await expect(element).toBeVisible(); // ✅ Good
expect(element).toBeVisible(); // ❌ Bad (missing await)

// Wait for element
await page.waitForSelector('.dashboard-header');

// Use Playwright auto-waiting
await page.click('button'); // Auto-waits for clickable
```

## Git Workflow

```bash
# 1. Create feature branch from 015-dashboard-redesign
git checkout 015-dashboard-redesign
git checkout -b feat/dashboard-header

# 2. Make changes and commit
git add src/components/dashboard/DashboardHeader.tsx
git commit -m "feat(dashboard): add sticky header component"

# 3. Push and create PR
git push -u origin feat/dashboard-header
# Create PR via GitHub targeting 015-dashboard-redesign

# 4. After PR approved, merge to 015-dashboard-redesign
git checkout 015-dashboard-redesign
git merge feat/dashboard-header
git push origin 015-dashboard-redesign
```

## Performance Monitoring

### Lighthouse (Chrome DevTools)

```bash
# 1. Build production bundle
npm run build

# 2. Serve production build
npm run preview

# 3. Open http://localhost:4173 in Chrome
# 4. DevTools → Lighthouse tab → Generate report
# 5. Target: FCP <1.5s, TTI <3.5s
```

### Bundle Analyzer

```bash
# Analyze bundle size
npm run build
npx vite-bundle-visualizer

# Opens treemap showing bundle composition
# Target: Total <500KB gzipped
```

## Next Steps

1. ✅ Development environment ready
2. ⏭️ Run `/speckit.tasks` to generate implementation tasks
3. ⏭️ Start with US1 (P1): Vista Rápida de Estadísticas
4. ⏭️ Follow TDD workflow (test → implement → refactor)

---

**Development environment configured** - Ready to code!
