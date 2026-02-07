# Frontend E2E Tests

End-to-end testing guide for ContraVento frontend with Playwright.

**Migrated from**: `frontend/TESTING_GUIDE.md` (Phase 3 consolidation)

---

## Table of Contents

- [Overview](#overview)
- [Running E2E Tests](#running-e2e-tests)
- [Test Structure](#test-structure)
- [Common Test Patterns](#common-test-patterns)
- [GPS & Maps Testing](#gps--maps-testing)
- [Authentication Testing](#authentication-testing)
- [Form Testing](#form-testing)
- [Accessibility Testing](#accessibility-testing)

---

## Overview

Frontend E2E tests use **Playwright** for cross-browser testing with:

- ✅ **Multi-browser support** - Chromium, Firefox, WebKit
- ✅ **Auto-waiting** - Waits for elements automatically
- ✅ **Network interception** - Mock API responses
- ✅ **Screenshot/video** - Capture failures
- ✅ **Parallel execution** - Run tests concurrently

**Test Pyramid**:
```
E2E Tests (Playwright)     ← Few, critical user journeys
       ↓
Component Tests (Vitest)   ← More, isolated component logic
       ↓
Unit Tests (Vitest)        ← Many, pure functions
```

---

## Running E2E Tests

### Prerequisites

**Backend running**:
```bash
cd backend
./run-local-dev.sh  # or .\run-local-dev.ps1 on Windows
```

**Frontend running**:
```bash
cd frontend
npm run dev  # Should be on http://localhost:5173
```

### Execute Tests

**All E2E tests**:
```bash
cd frontend
npx playwright test
```

**Specific test file**:
```bash
npx playwright test tests/e2e/trips.spec.ts
```

**Headed mode** (see browser):
```bash
npx playwright test --headed
```

**Debug mode**:
```bash
npx playwright test --debug
```

**Specific browser**:
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

---

## Test Structure

### Basic Test Template

```typescript
// tests/e2e/trips.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Trip Management', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Login before each test
    await page.goto('http://localhost:5173');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard');
  });

  test('should create a new trip', async ({ page }) => {
    // Navigate to trip creation
    await page.click('text=Crear Viaje');

    // Fill form
    await page.fill('input[name="title"]', 'Test Trip');
    await page.fill('textarea[name="description"]', 'This is a test trip description with enough characters to pass validation.');
    await page.fill('input[name="start_date"]', '2024-06-01');

    // Submit
    await page.click('button:has-text("Crear")');

    // Verify success
    await expect(page.locator('text=Viaje creado correctamente')).toBeVisible();
  });
});
```

---

## Common Test Patterns

### 1. Login Flow

```typescript
async function login(page, email = 'test@example.com', password = 'TestPass123!') {
  await page.goto('http://localhost:5173/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
}

test('user can login', async ({ page }) => {
  await login(page);
  await expect(page.locator('text=Bienvenido')).toBeVisible();
});
```

### 2. Form Validation

```typescript
test('should show validation errors', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Submit empty form
  await page.click('button[type="submit"]');

  // Verify error messages
  await expect(page.locator('text=El título es obligatorio')).toBeVisible();
  await expect(page.locator('text=La descripción es obligatoria')).toBeVisible();
});
```

### 3. API Mocking

```typescript
test('should handle API errors gracefully', async ({ page }) => {
  // Mock API failure
  await page.route('**/api/trips', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({
        success: false,
        error: { message: 'Error del servidor' }
      })
    });
  });

  await page.goto('http://localhost:5173/trips');

  // Verify error message displayed
  await expect(page.locator('text=Error del servidor')).toBeVisible();
});
```

### 4. File Upload

```typescript
test('should upload photo', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/123/photos');

  // Upload file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('tests/fixtures/test-photo.jpg');

  // Wait for upload to complete
  await expect(page.locator('text=Foto subida correctamente')).toBeVisible({ timeout: 10000 });

  // Verify photo appears in gallery
  await expect(page.locator('img[alt*="test-photo"]')).toBeVisible();
});
```

### 5. Wait for Network

```typescript
test('should wait for API call', async ({ page }) => {
  // Wait for specific API call
  const responsePromise = page.waitForResponse(
    response => response.url().includes('/api/trips') && response.status() === 200
  );

  await page.click('text=Cargar más viajes');

  const response = await responsePromise;
  const data = await response.json();

  expect(data.success).toBe(true);
});
```

---

## GPS & Maps Testing

### Test GPS Coordinate Input

```typescript
test('should add GPS coordinates to location', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Fill basic info
  await page.fill('input[name="title"]', 'GPS Test Trip');
  await page.fill('textarea[name="description"]', 'Testing GPS coordinates functionality.');

  // Add location
  await page.click('button:has-text("Añadir Ubicación")');

  // Fill location name (required)
  await page.fill('input[name="locations[0].name"]', 'Madrid');

  // Fill GPS coordinates (optional)
  await page.fill('input[name="locations[0].latitude"]', '40.416775');
  await page.fill('input[name="locations[0].longitude"]', '-3.703790');

  // Submit form
  await page.click('button:has-text("Siguiente")');

  // Verify location appears in review step
  await expect(page.locator('text=Madrid')).toBeVisible();
  await expect(page.locator('text=40.416775°, -3.703790°')).toBeVisible();
});
```

### Test GPS Validation

```typescript
test('should validate GPS coordinate ranges', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  await page.click('button:has-text("Añadir Ubicación")');
  await page.fill('input[name="locations[0].name"]', 'Test Location');

  // Test invalid latitude (> 90)
  await page.fill('input[name="locations[0].latitude"]', '100.5');
  await page.fill('input[name="locations[0].longitude"]', '0');

  await page.click('button:has-text("Siguiente")');

  // Verify error message
  await expect(page.locator('text=La latitud debe estar entre -90 y 90')).toBeVisible();

  // Test invalid longitude (< -180)
  await page.fill('input[name="locations[0].latitude"]', '40.4');
  await page.fill('input[name="locations[0].longitude"]', '-200');

  await page.click('button:has-text("Siguiente")');

  await expect(page.locator('text=La longitud debe estar entre -180 y 180')).toBeVisible();
});
```

### Test GPX File Upload

```typescript
test('should upload and display GPX route', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/123/gpx');

  // Upload GPX file
  const fileInput = page.locator('input[type="file"][accept=".gpx"]');
  await fileInput.setInputFiles('tests/fixtures/sample-route.gpx');

  // Wait for processing
  await expect(page.locator('text=Archivo GPX procesado correctamente')).toBeVisible({ timeout: 15000 });

  // Verify route stats displayed
  await expect(page.locator('text=/Distancia total:.*km/')).toBeVisible();
  await expect(page.locator('text=/Desnivel positivo:.*m/')).toBeVisible();

  // Verify map rendered
  await expect(page.locator('.leaflet-container')).toBeVisible();
  await expect(page.locator('.leaflet-polyline')).toBeVisible();
});
```

### Test Map Interactions

```typescript
test('should interact with map markers', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/123');

  // Wait for map to load
  await page.waitForSelector('.leaflet-container');

  // Click on marker
  await page.click('.leaflet-marker-icon');

  // Verify popup appears
  await expect(page.locator('.leaflet-popup')).toBeVisible();
  await expect(page.locator('.leaflet-popup-content:has-text("Madrid")')).toBeVisible();
});
```

---

## Authentication Testing

### Test Protected Routes

```typescript
test('should redirect to login when not authenticated', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Should redirect to login
  await page.waitForURL('**/login');
  await expect(page.locator('text=Inicia sesión')).toBeVisible();
});
```

### Test Token Refresh

```typescript
test('should refresh expired access token', async ({ page, context }) => {
  await login(page);

  // Manually expire access token in localStorage
  await page.evaluate(() => {
    localStorage.setItem('token_expires_at', String(Date.now() - 1000));
  });

  // Make API request (should trigger refresh)
  await page.goto('http://localhost:5173/trips');

  // Verify request succeeded (token refreshed)
  await expect(page.locator('text=Mis Viajes')).toBeVisible();
});
```

---

## Form Testing

### Multi-Step Wizard

```typescript
test('should navigate through trip creation wizard', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Step 1: Basic Info
  await page.fill('input[name="title"]', 'Wizard Test Trip');
  await page.fill('textarea[name="description"]', 'Testing multi-step wizard navigation and validation.');
  await page.fill('input[name="start_date"]', '2024-06-01');
  await page.click('button:has-text("Siguiente")');

  // Step 2: Story & Tags
  await page.fill('textarea[name="story"]', 'This is the trip story...');
  await page.fill('input[name="tags"]', 'test,wizard');
  await page.click('button:has-text("Siguiente")');

  // Step 3: Photos (skip)
  await page.click('button:has-text("Siguiente")');

  // Step 4: Review
  await expect(page.locator('text=Wizard Test Trip')).toBeVisible();
  await expect(page.locator('text=test')).toBeVisible();

  // Submit
  await page.click('button:has-text("Crear Viaje")');

  await expect(page.locator('text=Viaje creado correctamente')).toBeVisible();
});
```

### React Hook Form Integration

```typescript
test('should show real-time validation errors', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Trigger validation by focusing and blurring
  await page.focus('input[name="title"]');
  await page.blur('input[name="title"]');

  // Should show error immediately (React Hook Form)
  await expect(page.locator('text=El título es obligatorio')).toBeVisible();

  // Fix error
  await page.fill('input[name="title"]', 'Fixed Title');

  // Error should disappear
  await expect(page.locator('text=El título es obligatorio')).not.toBeVisible();
});
```

---

## Accessibility Testing

### Keyboard Navigation

```typescript
test('should be keyboard navigable', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Tab through form fields
  await page.keyboard.press('Tab'); // Title input
  await expect(page.locator('input[name="title"]')).toBeFocused();

  await page.keyboard.press('Tab'); // Description textarea
  await expect(page.locator('textarea[name="description"]')).toBeFocused();

  await page.keyboard.press('Tab'); // Date input
  await expect(page.locator('input[name="start_date"]')).toBeFocused();

  // Submit with Enter
  await page.keyboard.press('Enter');
});
```

### ARIA Attributes

```typescript
test('should have proper ARIA labels', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Check form has aria-label
  await expect(page.locator('form[aria-label="Crear nuevo viaje"]')).toBeVisible();

  // Check inputs have aria-labels or associated labels
  const titleInput = page.locator('input[name="title"]');
  const ariaLabel = await titleInput.getAttribute('aria-label');
  expect(ariaLabel).toBeTruthy();

  // Check error messages have aria-live
  await page.click('button[type="submit"]');
  await expect(page.locator('[role="alert"]')).toBeVisible();
});
```

**See also**: [Accessibility Testing Guide](accessibility.md) for detailed a11y testing

---

## Related Documentation

- **[Component Tests](component-tests.md)** - Vitest component testing
- **[Accessibility](accessibility.md)** - WCAG 2.1 AA compliance testing
- **[Manual QA](../manual-qa/)** - Manual testing procedures
- **[CI/CD](../ci-cd/github-actions.md)** - Automated E2E in CI

---

**Last Updated**: 2026-02-06 (Migrated from frontend/)
**Test Framework**: Playwright
**Browsers**: Chromium, Firefox, WebKit
