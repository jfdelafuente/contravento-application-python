# E2E Tests with Playwright

End-to-end tests for ContraVento application using Playwright Test.

## Test Coverage

### Authentication (auth.spec.ts)
- User registration flow (T046)
- Login/logout flows (T047)
- Session persistence (T048)
- Protected routes access control

### Trip Creation (trip-creation.spec.ts)
- 4-step wizard workflow (T049-T050)
  - Step 1: Basic trip information
  - Step 2: Story and tags
  - Step 3: Photo uploads
  - Step 4: Review and publish
- Draft vs. published trips
- Form validation

### Public Feed (public-feed.spec.ts)
- Anonymous browsing (T051)
- Tag filtering (T051)
- Pagination (T051)
- Trip detail viewing (T052)
- Responsive design

### Location Editing (location-editing.spec.ts)
- Click to add location on map (T053)
- Drag markers to adjust coordinates (T054)
- Reverse geocoding integration (T053)
- Edit location names (T054)
- Delete locations (T054)
- Multiple locations per trip

### GPS Wizard (gpx-wizard.spec.ts) - **Feature 017**

**26 tests totales** cubriendo el flujo completo del GPS Trip Creation Wizard:

#### Step 1: Upload & Analysis (5 tests)

- Display upload zone correctly
- Reject non-GPX files
- Upload and analyze GPX successfully (SC-078: <5s upload, SC-079: telemetry display)
- Allow removing uploaded file
- Proceed to step 2 after upload

#### Step 2: Trip Details (7 tests)

- Display form with GPX telemetry
- Validate required fields (SC-080)
- Validate description length (min 50 chars)
- Validate date range
- Allow removing GPX from step 2
- Navigate back to step 1
- Proceed to step 3 with valid data

#### Step 3: Review & Publish (6 tests)

- Display trip summary for review
- Truncate long descriptions to 50 words
- Navigate back to step 2 to edit
- Publish trip atomically (SC-081: atomic transaction, SC-082: RouteStatistics)
- Show error message on publish failure
- Verify RouteStatistics after publish

#### Cancel Flow (3 tests)

- Cancel without data (no confirmation)
- Show confirmation when canceling with data
- Cancel and redirect when confirmed

#### End-to-End Flow (1 test)

- Complete full wizard and create trip with statistics

**Success Criteria Cubiertos**:

- ✅ SC-078: Upload completes in <5s for small files (<1MB)
- ✅ SC-079: Telemetry displays correctly (distance, elevation, timestamps)
- ✅ SC-080: Trip details form validation works
- ✅ SC-081: Atomic publish creates trip + GPX + trackpoints
- ✅ SC-082: RouteStatistics calculated for GPX with timestamps

## Prerequisites

Before running E2E tests, ensure the following services are running:

### 1. Backend Server
```bash
# Terminal 1: Start backend
cd backend
poetry run uvicorn src.main:app --reload

# Or use the convenience script:
./run_backend.sh  # Linux/Mac
.\run_backend.ps1  # Windows PowerShell
```

**Backend must be running at**: `http://localhost:8000`

### 2. Frontend Server
```bash
# Terminal 2: Start frontend
cd frontend
npm run dev

# Or use the convenience script:
./run_frontend.sh  # Linux/Mac
.\run_frontend.ps1  # Windows PowerShell
```

**Frontend must be running at**: `http://localhost:5173`

## Running Tests

### Run All E2E Tests
```bash
cd frontend

# Run all tests (all browsers)
npx playwright test

# Run all tests with UI mode (interactive)
npx playwright test --ui
```

### Run Specific Test File

```bash
# Run only authentication tests
npx playwright test auth.spec.ts

# Run only trip creation tests
npx playwright test trip-creation.spec.ts

# Run only public feed tests
npx playwright test public-feed.spec.ts

# Run only location editing tests
npx playwright test location-editing.spec.ts

# Run only GPS Wizard tests (Feature 017)
npx playwright test gpx-wizard.spec.ts
```

### Run GPS Wizard Tests (Feature 017)

El GPS Wizard tiene 26 tests E2E. Comandos recomendados:

```bash
# Desarrollo: Modo UI (recomendado)
npx playwright test gpx-wizard.spec.ts --ui

# Desarrollo: Ver navegador
npx playwright test gpx-wizard.spec.ts --headed --project=chromium

# CI/CD: Solo Chromium (más rápido)
npx playwright test gpx-wizard.spec.ts --project=chromium

# Debug: Ejecutar test específico
npx playwright test gpx-wizard.spec.ts --grep "should publish trip atomically"

# Todos los navegadores (Chrome, Firefox, Safari)
npx playwright test gpx-wizard.spec.ts
```

**Nota**: Asegúrate de que el archivo `frontend/tests/fixtures/short_route.gpx` existe antes de ejecutar estos tests.

### Run Specific Browser
```bash
# Run on Chromium only
npx playwright test --project=chromium

# Run on Firefox only
npx playwright test --project=firefox

# Run on WebKit (Safari) only
npx playwright test --project=webkit
```

### Run in Debug Mode
```bash
# Debug a specific test
npx playwright test auth.spec.ts --debug

# Debug with Playwright Inspector
npx playwright test --debug

# Run in headed mode (see browser)
npx playwright test --headed
```

### Run Tests in Parallel
```bash
# Run with 4 workers (default is auto-detected)
npx playwright test --workers=4

# Run tests sequentially (useful for debugging)
npx playwright test --workers=1
```

## Test Reports

### HTML Report
After running tests, view the HTML report:

```bash
npx playwright show-report
```

The report includes:
- Test results summary
- Screenshots on failure
- Videos of failed tests
- Network logs
- Console output

### JSON Report
JSON results are saved to: `test-results/results.json`

## Environment Variables

Configure test environment with these variables:

```bash
# Frontend URL (default: http://localhost:5173)
export VITE_APP_URL=http://localhost:5173

# Backend API URL (default: http://localhost:8000)
export VITE_API_URL=http://localhost:8000

# Playwright base URL (for relative navigation)
export PLAYWRIGHT_BASE_URL=http://localhost:5173
```

## CI/CD Integration

Tests are configured to run in GitHub Actions with:

- Retries on failure (2 retries on CI)
- Parallel execution (2 workers on CI)
- HTML report artifacts
- Test result JSON for analysis

See: `.github/workflows/e2e-tests.yml`

## Troubleshooting

### Backend/Frontend Not Running
```
Error: Backend server is not running at http://localhost:8000
```

**Solution**: Start backend server first:
```bash
./run_backend.sh  # or .\run_backend.ps1
```

### Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::5173
```

**Solution**: Kill process using the port:
```bash
# Linux/Mac
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Test Images Missing
```
Error: ENOENT: no such file or directory 'tests/fixtures/test-image.jpg'
```

**Solution**: Test images are auto-generated by global setup. If missing:
```bash
npx playwright test --global-setup
```

### Flaky Tests
If tests fail intermittently:

1. **Increase timeouts** (in playwright.config.ts):
   ```typescript
   timeout: 60 * 1000, // Increase to 60s
   ```

2. **Use `waitFor` assertions**:
   ```typescript
   await expect(page.locator('text=Success')).toBeVisible({ timeout: 10000 });
   ```

3. **Check network stability**: Slow network can cause timeouts

### Authentication Failures

If authentication tests fail consistently:

1. Check Turnstile configuration (should use dummy token in test)
2. Verify database is clean (no duplicate test users)
3. Check JWT secret key in backend `.env`

### GPS Wizard Tests Failures (gpx-wizard.spec.ts)

Si los tests del GPS Wizard fallan:

#### 1. Archivo GPX no encontrado

```
Error: ENOENT: no such file or directory 'tests/fixtures/short_route.gpx'
```

**Solución**: Verificar que el archivo existe:

```bash
ls -la frontend/tests/fixtures/short_route.gpx

# Si no existe, copiarlo desde backend
cp backend/tests/fixtures/gpx/short_route.gpx frontend/tests/fixtures/
```

#### 2. Backend no procesa GPX correctamente

```
Error: 500 Internal Server Error during GPX upload
```

**Solución**: Verificar logs del backend:

```bash
# Ver logs del backend
tail -f backend/logs/app.log

# Verificar endpoint de análisis de GPX
curl -X POST http://localhost:8000/gpx/analyze \
  -F "file=@frontend/tests/fixtures/short_route.gpx"
```

#### 3. Timeout durante upload de GPX

```
Error: Timeout 10000ms exceeded while waiting for telemetry
```

**Solución**: Aumentar timeout en el test o verificar que el backend está respondiendo rápido:

- Backend debe procesar GPX <1MB en <5 segundos (SC-078)
- Verificar que no hay procesos lentos en el backend
- Revisar logs: puede ser un problema de Douglas-Peucker simplification

#### 4. RouteStatistics no se calculan

```
Error: Expected RouteStatistics section to be visible
```

**Causas**:

- GPX no tiene timestamps (short_route.gpx SÍ los tiene)
- Error en cálculo de estadísticas en backend

**Solución**:

```bash
# Verificar que short_route.gpx tiene timestamps
grep "<time>" frontend/tests/fixtures/short_route.gpx

# Debe mostrar múltiples líneas con timestamps
```

#### 5. Tests pasan en local pero fallan en CI

**Posibles causas**:

- Proxy corporativo bloqueando instalación de navegadores
- Problemas de certificados SSL

**Solución para CI**:

```yaml
# En .github/workflows/e2e-tests.yml
- name: Install Playwright browsers
  run: npx playwright install chromium --with-deps
  env:
    NODE_TLS_REJECT_UNAUTHORIZED: 0  # Solo si hay problemas de SSL
```

## Writing New Tests

### Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Navigate to page, login user, etc.
  });

  test('should do something', async ({ page }) => {
    // Arrange
    await page.goto('/some-page');

    // Act
    await page.click('button');

    // Assert
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

### Best Practices

1. **Use data-testid attributes** for stable selectors:
   ```typescript
   await page.click('[data-testid="submit-button"]');
   ```

2. **Wait for navigation** before assertions:
   ```typescript
   await page.waitForURL('/success');
   await expect(page).toHaveURL('/success');
   ```

3. **Use meaningful assertions**:
   ```typescript
   // Good
   await expect(page.locator('h1')).toHaveText('Trip Created');

   // Avoid
   await page.waitForTimeout(5000); // Anti-pattern!
   ```

4. **Clean up test data**:
   ```typescript
   test.afterEach(async ({ page }) => {
     // Delete created resources via API
   });
   ```

## Performance

### Optimization Tips

1. **Reuse authentication state** (save login session):
   ```typescript
   // In global-setup.ts
   await context.storageState({ path: 'auth.json' });

   // In test
   test.use({ storageState: 'auth.json' });
   ```

2. **Parallelize independent tests**:
   ```typescript
   test.describe.configure({ mode: 'parallel' });
   ```

3. **Skip visual tests on CI** (if slow):
   ```typescript
   test.skip(!!process.env.CI, 'Skipping visual test on CI');
   ```

## References

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API](https://playwright.dev/docs/api/class-playwright)
