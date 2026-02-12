/**
 * E2E Tests for GPX Trip Creation Wizard (Feature 017 - Phase 6 - US6)
 *
 * Tests the complete 3-step GPX wizard workflow:
 * - Step 1: GPX Upload & Analysis
 * - Step 2: Trip Details
 * - Step 3: Review & Publish
 *
 * Prerequisites:
 * - Authenticated user session
 * - Backend and frontend servers running
 * - Test GPX file in fixtures/short_route.gpx
 *
 * Success Criteria:
 * - SC-078: Upload completes in <5s for small files (<1MB)
 * - SC-079: Telemetry displays correctly (distance, elevation, timestamps)
 * - SC-080: Trip details form validation works
 * - SC-081: Atomic publish creates trip + GPX + trackpoints in single transaction
 * - SC-082: RouteStatistics calculated for GPX with timestamps
 */

import { test, expect, Page } from '@playwright/test';
import path from 'path';

const FRONTEND_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to create authenticated session
async function createAuthenticatedUser(page: Page) {
  const testUser = {
    username: `gpxuser_${Date.now()}`,
    email: `gpxuser_${Date.now()}@example.com`,
    password: 'GPXTest123!',
  };

  // Register user via API
  await page.request.post(`${API_URL}/auth/register`, {
    data: {
      username: testUser.username,
      email: testUser.email,
      password: testUser.password,
      turnstile_token: 'dummy_token',
    },
  });

  // Login
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[name="login"]', testUser.username);
  await page.fill('input[name="password"]', testUser.password);
  await page.click('button[type="submit"]');

  await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });

  return testUser;
}

test.describe('GPX Wizard - Step 1: Upload & Analysis (T075)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);
  });

  test('should display step 1 upload zone correctly', async ({ page }) => {
    // Verify wizard header
    await expect(page.locator('h1:has-text("Crear Viaje desde GPX")')).toBeVisible();
    await expect(
      page.locator('text=/Sube tu archivo GPX y completa los detalles/i')
    ).toBeVisible();

    // Verify step indicator shows step 1 of 3
    await expect(page.locator('.wizard-step--active:has-text("Archivo GPX")')).toBeVisible();

    // Verify upload zone
    await expect(page.locator('text=/Arrastra.*archivo GPX|Selecciona.*archivo/i')).toBeVisible();
    await expect(page.locator('input[type="file"][accept=".gpx"]')).toBeAttached();

    // Verify Next button is disabled initially
    await expect(page.locator('button:has-text("Siguiente")')).toBeDisabled();
  });

  test('should reject non-GPX files', async ({ page }) => {
    // Try to upload a non-GPX file
    const testImagePath = path.join(__dirname, '../fixtures/test-image.jpg');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');

    // This should be rejected by the browser's accept attribute
    // But if it somehow gets through, backend should reject it
    await fileInput.setInputFiles(testImagePath);

    // Should show error message
    await expect(
      page.locator('text=/solo.*archivos GPX|only.*GPX.*files/i')
    ).toBeVisible({ timeout: 5000 });
  });

  test('should upload and analyze GPX file successfully (SC-078, SC-079)', async ({ page }) => {
    const startTime = Date.now();

    // Upload GPX file
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);

    // Should show analyzing state
    await expect(page.locator('text=/Analizando.*GPX/i')).toBeVisible();

    // Wait for analysis to complete
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });

    const uploadTime = Date.now() - startTime;
    console.log(`GPX upload and analysis took ${uploadTime}ms`);

    // SC-078: Should complete in <5s (5000ms)
    expect(uploadTime).toBeLessThan(5000);

    // SC-079: Verify telemetry displays correctly
    // Distance
    await expect(page.locator('text=/Distancia.*km/i')).toBeVisible();

    // Elevation gain (short_route.gpx has elevation data)
    await expect(page.locator('text=/Desnivel.*positivo/i')).toBeVisible();
    await expect(page.locator('text=/m/i')).toBeVisible(); // meters unit

    // Duration (short_route.gpx has timestamps)
    await expect(page.locator('text=/Duración/i')).toBeVisible();

    // Points count
    await expect(page.locator('text=/Puntos/i')).toBeVisible();

    // Verify telemetry is displayed in single row on desktop
    const telemetryGrid = page.locator('.step1-upload__telemetry-grid');
    await expect(telemetryGrid).toBeVisible();

    // Next button should now be enabled
    await expect(page.locator('button:has-text("Siguiente")')).toBeEnabled();
  });

  test('should allow removing uploaded file', async ({ page }) => {
    // Upload file
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);

    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });

    // Click remove button
    await page.click('button:has-text(/eliminar|remove/i)');

    // Should return to upload zone
    await expect(page.locator('text=/Arrastra.*archivo GPX/i')).toBeVisible();

    // Next button should be disabled again
    await expect(page.locator('button:has-text("Siguiente")')).toBeDisabled();
  });

  test('should proceed to step 2 after successful upload', async ({ page }) => {
    // Upload file
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);

    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });

    // Click Next
    await page.click('button:has-text("Siguiente")');

    // Should navigate to step 2
    await expect(page.locator('.wizard-step--active:has-text("Detalles del Viaje")')).toBeVisible();
    await expect(page.locator('h2:has-text("Detalles del Viaje")')).toBeVisible();
  });
});

test.describe('GPX Wizard - Step 2: Trip Details (T075)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);

    // Complete step 1
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('.wizard-step--active:has-text("Detalles del Viaje")');
  });

  test('should display trip details form with GPX telemetry', async ({ page }) => {
    // Verify form fields
    await expect(page.locator('input[name="title"]')).toBeVisible();
    await expect(page.locator('textarea[name="description"]')).toBeVisible();
    await expect(page.locator('input[name="start_date"]')).toBeVisible();
    await expect(page.locator('input[name="end_date"]')).toBeVisible();
    await expect(page.locator('select[name="difficulty"]')).toBeVisible();

    // Verify GPX telemetry card is shown
    await expect(page.locator('.step2-details__gpx-card')).toBeVisible();
    await expect(page.locator('text=/short_route.gpx/i')).toBeVisible();

    // Verify start_date is auto-populated from GPX timestamp (2024-06-15)
    const startDateInput = page.locator('input[name="start_date"]');
    await expect(startDateInput).toHaveValue('2024-06-15');

    // Verify end_date defaults to same as start_date
    const endDateInput = page.locator('input[name="end_date"]');
    await expect(endDateInput).toHaveValue('2024-06-15');
  });

  test('should validate required fields (SC-080)', async ({ page }) => {
    // Try to proceed without filling required fields
    await page.click('button:has-text("Siguiente")');

    // Should show validation errors
    await expect(page.locator('text=/título.*requerido/i')).toBeVisible();
    await expect(page.locator('text=/descripción.*requerida/i')).toBeVisible();
  });

  test('should validate description length (min 50 chars)', async ({ page }) => {
    await page.fill('input[name="title"]', 'GPX Test Trip');
    await page.fill('textarea[name="description"]', 'Too short'); // Only 9 chars

    await page.click('button:has-text("Siguiente")');

    // Should show length error
    await expect(page.locator('text=/descripción.*mínimo.*50/i')).toBeVisible();
  });

  test('should validate date range', async ({ page }) => {
    await page.fill('input[name="title"]', 'GPX Test Trip');
    await page.fill('textarea[name="description"]', 'A'.repeat(60));
    await page.fill('input[name="start_date"]', '2024-06-20');
    await page.fill('input[name="end_date"]', '2024-06-15'); // Before start_date

    await page.click('button:has-text("Siguiente")');

    // Should show date range error
    await expect(page.locator('text=/fecha.*fin.*debe ser posterior/i')).toBeVisible();
  });

  test('should allow removing GPX file from step 2', async ({ page }) => {
    // Click "Eliminar GPX" button
    await page.click('button:has-text(/eliminar.*gpx/i)');

    // Should show confirmation dialog
    await expect(page.locator('text=/¿Seguro.*eliminar.*GPX/i')).toBeVisible();

    // Confirm removal
    await page.click('button:has-text(/sí.*eliminar/i)');

    // Should return to step 1
    await expect(page.locator('.wizard-step--active:has-text("Archivo GPX")')).toBeVisible();
    await expect(page.locator('text=/Arrastra.*archivo GPX/i')).toBeVisible();
  });

  test('should navigate back to step 1', async ({ page }) => {
    await page.click('button:has-text("Anterior")');

    // Should return to step 1 with uploaded file preserved
    await expect(page.locator('.wizard-step--active:has-text("Archivo GPX")')).toBeVisible();
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible();
  });

  test('should proceed to step 3 with valid data', async ({ page }) => {
    await page.fill('input[name="title"]', 'Ruta GPX de Prueba');
    await page.fill(
      'textarea[name="description"]',
      'Esta es una ruta de prueba cargada desde un archivo GPX con datos de elevación y timestamps para verificar el flujo completo del wizard.'
    );
    // Dates are already auto-populated
    await page.selectOption('select[name="difficulty"]', 'moderate');

    await page.click('button:has-text("Siguiente")');

    // Should navigate to step 3
    await expect(
      page.locator('.wizard-step--active:has-text("Revisar y Publicar")')
    ).toBeVisible();
  });
});

test.describe('GPX Wizard - Step 3: Review & Publish (T075)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);

    // Complete steps 1 and 2
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('.wizard-step--active:has-text("Detalles del Viaje")');
    await page.fill('input[name="title"]', 'Ruta GPX Final Test');
    await page.fill(
      'textarea[name="description"]',
      'Descripción completa de la ruta GPX de prueba con suficiente longitud para pasar la validación de caracteres mínimos.'
    );
    await page.selectOption('select[name="difficulty"]', 'moderate');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('.wizard-step--active:has-text("Revisar y Publicar")');
  });

  test('should display trip summary for review', async ({ page }) => {
    // Verify trip details
    await expect(page.locator('h2:has-text("Ruta GPX Final Test")')).toBeVisible();
    await expect(
      page.locator('text=/Descripción completa de la ruta GPX de prueba/i')
    ).toBeVisible();
    await expect(page.locator('text=/15.*jun.*2024/i')).toBeVisible(); // Start date

    // Verify difficulty badge
    await expect(page.locator('text=/moderado|moderate/i')).toBeVisible();

    // Verify GPX telemetry summary
    await expect(page.locator('text=/Datos.*GPX/i')).toBeVisible();
    await expect(page.locator('text=/short_route.gpx/i')).toBeVisible();
    await expect(page.locator('text=/km/i')).toBeVisible(); // Distance
    await expect(page.locator('text=/m/i')).toBeVisible(); // Elevation
  });

  test('should truncate long descriptions to 50 words', async ({ page }) => {
    // Go back and add a very long description
    await page.click('button:has-text("Anterior")');
    await page.waitForSelector('.wizard-step--active:has-text("Detalles del Viaje")');

    const longDescription =
      'Esta es una descripción muy larga que contiene muchas palabras para probar que el componente Step3Review trunca correctamente las descripciones largas a exactamente cincuenta palabras. ' +
      'El truncamiento debe agregar puntos suspensivos al final para indicar que hay más contenido. ' +
      'Esta funcionalidad es importante para mantener la interfaz limpia y evitar que las descripciones largas ocupen demasiado espacio en la pantalla de revisión antes de publicar.';

    await page.fill('textarea[name="description"]', longDescription);
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('.wizard-step--active:has-text("Revisar y Publicar")');

    // Should show truncated version with ellipsis
    const descriptionText = await page.locator('.step3-review__description').textContent();
    expect(descriptionText).toContain('...');

    // Count words (should be approximately 50)
    const words = descriptionText?.trim().replace(/\s+/g, ' ').split(' ') || [];
    expect(words.length).toBeLessThanOrEqual(51); // 50 words + "..."
  });

  test('should navigate back to step 2 to edit', async ({ page }) => {
    await page.click('button:has-text("Anterior")');

    // Should return to step 2 with data preserved
    await expect(page.locator('.wizard-step--active:has-text("Detalles del Viaje")')).toBeVisible();
    await expect(page.locator('input[name="title"]')).toHaveValue('Ruta GPX Final Test');
  });

  test('should publish trip atomically (SC-081, SC-082)', async ({ page }) => {
    const startTime = Date.now();

    // Click Publicar button
    await page.click('button:has-text("Publicar")');

    // Should show loading state
    await expect(page.locator('text=/publicando|publishing/i')).toBeVisible();

    // Should redirect to trip detail page
    await expect(page).toHaveURL(/\/trips\/[a-f0-9-]+/, { timeout: 15000 });

    const publishTime = Date.now() - startTime;
    console.log(`Trip publish took ${publishTime}ms`);

    // Verify trip details on detail page
    await expect(page.locator('h1:has-text("Ruta GPX Final Test")')).toBeVisible();

    // SC-081: Verify GPX data was created (map should be visible)
    await expect(page.locator('.trip-map')).toBeVisible({ timeout: 5000 });

    // SC-082: Verify RouteStatistics are displayed (short_route.gpx has timestamps)
    // Note: RouteStatistics display might be in a separate section
    await expect(
      page.locator('text=/Estadísticas.*Avanzadas|estadísticas.*ruta/i')
    ).toBeVisible({ timeout: 5000 });

    // Verify basic statistics
    await expect(page.locator('text=/velocidad.*media|avg.*speed/i')).toBeVisible();

    // Verify success message
    await expect(page.locator('text=/viaje.*creado.*correctamente/i')).toBeVisible();
  });

  test('should show error message on publish failure', async ({ page }) => {
    // Force an error by disconnecting network (simulate backend failure)
    await page.context().setOffline(true);

    await page.click('button:has-text("Publicar")');

    // Should show error toast
    await expect(
      page.locator('text=/error.*crear.*viaje|no se pudo.*conectar/i')
    ).toBeVisible({ timeout: 10000 });

    // Should remain on step 3
    await expect(
      page.locator('.wizard-step--active:has-text("Revisar y Publicar")')
    ).toBeVisible();
  });
});

test.describe('GPX Wizard - Cancel Flow (T075)', () => {
  test('should cancel without data loss confirmation', async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);

    // No data entered - cancel should work immediately
    await page.click('button:has-text("Cancelar")');

    // Should redirect to trips list
    await expect(page).toHaveURL(/\/trips$/, { timeout: 5000 });
  });

  test('should show confirmation when canceling with data', async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);

    // Upload file
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });

    // Try to cancel
    await page.click('button:has-text("Cancelar")');

    // Should show confirmation dialog
    await expect(page.locator('text=/¿Seguro.*cancelar/i')).toBeVisible();
    await expect(page.locator('text=/se perderán.*datos/i')).toBeVisible();

    // Decline cancellation
    await page.click('button:has-text(/no.*continuar/i)');

    // Should stay on wizard
    await expect(page.locator('h1:has-text("Crear Viaje desde GPX")')).toBeVisible();
  });

  test('should cancel and redirect when confirmed', async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);

    // Upload file
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });

    // Cancel and confirm
    await page.click('button:has-text("Cancelar")');
    await page.click('button:has-text(/sí.*cancelar/i)');

    // Should redirect to trips list
    await expect(page).toHaveURL(/\/trips$/, { timeout: 5000 });
  });
});

test.describe('GPX Wizard - End-to-End Flow (T075)', () => {
  test('should complete full GPX wizard and create trip with statistics', async ({ page }) => {
    const testUser = await createAuthenticatedUser(page);

    // Navigate to GPX wizard
    await page.goto(`${FRONTEND_URL}/trips/new/gpx`);

    // Step 1: Upload GPX
    const gpxPath = path.join(__dirname, '../fixtures/short_route.gpx');
    const fileInput = page.locator('input[type="file"][accept=".gpx"]');
    await fileInput.setInputFiles(gpxPath);

    // Wait for analysis
    await expect(page.locator('.step1-upload__telemetry')).toBeVisible({ timeout: 10000 });

    // Verify telemetry shows correct data
    await expect(page.locator('text=/km/i')).toBeVisible(); // Distance
    await expect(page.locator('text=/Desnivel/i')).toBeVisible(); // Elevation gain

    await page.click('button:has-text("Siguiente")');

    // Step 2: Trip details
    await page.waitForSelector('.wizard-step--active:has-text("Detalles del Viaje")');

    await page.fill('input[name="title"]', 'E2E GPX Complete Trip');
    await page.fill(
      'textarea[name="description"]',
      'Este es un viaje completo de prueba end-to-end para el wizard de GPX, incluyendo análisis de telemetría, detalles del viaje, y publicación atómica con cálculo de estadísticas avanzadas.'
    );
    // Dates already auto-populated from GPX
    await page.selectOption('select[name="difficulty"]', 'difficult');

    await page.click('button:has-text("Siguiente")');

    // Step 3: Review
    await page.waitForSelector('.wizard-step--active:has-text("Revisar y Publicar")');

    // Verify all data is shown correctly
    await expect(page.locator('h2:has-text("E2E GPX Complete Trip")')).toBeVisible();
    await expect(page.locator('text=/short_route.gpx/i')).toBeVisible();
    await expect(page.locator('text=/difícil|difficult/i')).toBeVisible();

    // Publish
    await page.click('button:has-text("Publicar")');

    // Wait for redirect to trip detail
    await expect(page).toHaveURL(/\/trips\/[a-f0-9-]+/, { timeout: 15000 });

    // Verify trip was created successfully
    await expect(page.locator('h1:has-text("E2E GPX Complete Trip")')).toBeVisible();

    // Verify map is displayed
    await expect(page.locator('.trip-map')).toBeVisible();

    // Verify elevation profile is displayed (short_route.gpx has elevation)
    await expect(page.locator('.elevation-profile')).toBeVisible();

    // Verify route statistics are displayed (short_route.gpx has timestamps)
    await expect(page.locator('text=/Estadísticas.*Avanzadas/i')).toBeVisible();
    await expect(page.locator('text=/velocidad.*media/i')).toBeVisible();

    // Verify trip appears in user's trips list
    await page.goto(`${FRONTEND_URL}/users/${testUser.username}/trips`);
    await expect(page.locator('text=E2E GPX Complete Trip')).toBeVisible();
  });
});
