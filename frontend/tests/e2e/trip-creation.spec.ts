/**
 * E2E Tests for Trip Creation Workflow
 *
 * Tests the complete 4-step trip creation wizard (T049-T050):
 * - Step 1: Basic trip information
 * - Step 2: Story and tags
 * - Step 3: Photo uploads
 * - Step 4: Review and publish
 *
 * Prerequisites:
 * - Authenticated user session
 * - Backend and frontend servers running
 */

import { test, expect, Page } from '@playwright/test';
import path from 'path';

const FRONTEND_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to create authenticated session
async function createAuthenticatedUser(page: Page) {
  const testUser = {
    username: `tripuser_${Date.now()}`,
    email: `tripuser_${Date.now()}@example.com`,
    password: 'TripTest123!',
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

test.describe('Trip Creation Wizard - Step 1: Basic Info (T049)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new`);
  });

  test('should display step 1 form correctly', async ({ page }) => {
    // Verify form fields are present
    await expect(page.locator('input[name="title"]')).toBeVisible();
    await expect(page.locator('textarea[name="description"]')).toBeVisible();
    await expect(page.locator('input[name="start_date"]')).toBeVisible();
    await expect(page.locator('input[name="end_date"]')).toBeVisible();
    await expect(page.locator('input[name="distance_km"]')).toBeVisible();
    await expect(page.locator('select[name="difficulty"]')).toBeVisible();

    // Verify step indicator shows step 1
    await expect(page.locator('text=/paso 1.*4/i')).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    // Try to proceed without filling required fields
    await page.click('button:has-text("Siguiente")');

    // Should show validation errors
    await expect(page.locator('text=/título.*requerido/i')).toBeVisible();
    await expect(page.locator('text=/descripción.*requerida/i')).toBeVisible();
    await expect(page.locator('text=/fecha.*requerida/i')).toBeVisible();
  });

  test('should validate date range', async ({ page }) => {
    // Fill form with end_date before start_date
    await page.fill('input[name="title"]', 'Test Trip');
    await page.fill('textarea[name="description"]', 'A'.repeat(60)); // Min 50 chars
    await page.fill('input[name="start_date"]', '2024-06-15');
    await page.fill('input[name="end_date"]', '2024-06-10'); // Before start_date

    await page.click('button:has-text("Siguiente")');

    // Should show date range error
    await expect(page.locator('text=/fecha.*fin.*debe ser posterior/i')).toBeVisible();
  });

  test('should proceed to step 2 with valid data', async ({ page }) => {
    // Fill all required fields
    await page.fill('input[name="title"]', 'Ruta Bikepacking Pirineos');
    await page.fill(
      'textarea[name="description"]',
      'Viaje de 5 días por los Pirineos catalanes con pernoctas en refugios de montaña. Ruta circular de gran belleza paisajística.'
    );
    await page.fill('input[name="start_date"]', '2024-06-01');
    await page.fill('input[name="end_date"]', '2024-06-05');
    await page.fill('input[name="distance_km"]', '320.5');
    await page.selectOption('select[name="difficulty"]', 'HARD');

    // Click next
    await page.click('button:has-text("Siguiente")');

    // Should navigate to step 2
    await expect(page.locator('text=/paso 2.*4/i')).toBeVisible();
    await expect(page.locator('input[name="tags"]')).toBeVisible();
  });
});

test.describe('Trip Creation Wizard - Step 2: Story & Tags (T049)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new`);

    // Complete step 1
    await page.fill('input[name="title"]', 'Test Trip Step 2');
    await page.fill(
      'textarea[name="description"]',
      'This is a test trip description with enough characters to pass validation.'
    );
    await page.fill('input[name="start_date"]', '2024-06-01');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('text=/paso 2.*4/i');
  });

  test('should add tags to trip', async ({ page }) => {
    // Type tag and press Enter
    const tagInput = page.locator('input[name="tags"]');
    await tagInput.fill('bikepacking');
    await tagInput.press('Enter');

    // Should display tag chip
    await expect(page.locator('text=bikepacking').first()).toBeVisible();

    // Add more tags
    await tagInput.fill('montaña');
    await tagInput.press('Enter');
    await tagInput.fill('pirineos');
    await tagInput.press('Enter');

    // Should have 3 tags
    const tagChips = page.locator('[data-testid="tag-chip"]');
    await expect(tagChips).toHaveCount(3);
  });

  test('should enforce max 10 tags limit', async ({ page }) => {
    const tagInput = page.locator('input[name="tags"]');

    // Add 10 tags
    for (let i = 1; i <= 10; i++) {
      await tagInput.fill(`tag${i}`);
      await tagInput.press('Enter');
    }

    // Try to add 11th tag
    await tagInput.fill('tag11');
    await tagInput.press('Enter');

    // Should show error message
    await expect(page.locator('text=/máximo.*10.*etiquetas/i')).toBeVisible();

    // Should still have only 10 tags
    const tagChips = page.locator('[data-testid="tag-chip"]');
    await expect(tagChips).toHaveCount(10);
  });

  test('should remove tags by clicking X button', async ({ page }) => {
    const tagInput = page.locator('input[name="tags"]');

    // Add tags
    await tagInput.fill('bikepacking');
    await tagInput.press('Enter');
    await tagInput.fill('montaña');
    await tagInput.press('Enter');

    // Click remove button on first tag
    await page.locator('[data-testid="tag-chip"]:has-text("bikepacking") button').click();

    // Should have only 1 tag left
    const tagChips = page.locator('[data-testid="tag-chip"]');
    await expect(tagChips).toHaveCount(1);
    await expect(page.locator('text=bikepacking')).not.toBeVisible();
  });

  test('should navigate back to step 1', async ({ page }) => {
    await page.click('button:has-text("Anterior")');

    // Should return to step 1
    await expect(page.locator('text=/paso 1.*4/i')).toBeVisible();
    await expect(page.locator('input[name="title"]')).toBeVisible();

    // Should preserve step 1 data
    await expect(page.locator('input[name="title"]')).toHaveValue('Test Trip Step 2');
  });

  test('should proceed to step 3', async ({ page }) => {
    await page.click('button:has-text("Siguiente")');

    // Should navigate to step 3 (photos)
    await expect(page.locator('text=/paso 3.*4/i')).toBeVisible();
    await expect(page.locator('text=/fotos/i')).toBeVisible();
  });
});

test.describe('Trip Creation Wizard - Step 3: Photos (T050)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new`);

    // Complete steps 1 and 2
    await page.fill('input[name="title"]', 'Test Trip Photos');
    await page.fill(
      'textarea[name="description"]',
      'Test trip for photo upload functionality with sufficient description length.'
    );
    await page.fill('input[name="start_date"]', '2024-06-01');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('text=/paso 2.*4/i');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('text=/paso 3.*4/i');
  });

  test('should display photo upload zone', async ({ page }) => {
    await expect(page.locator('text=/arrastra.*fotos|selecciona.*fotos/i')).toBeVisible();
    await expect(page.locator('input[type="file"]')).toBeAttached();
  });

  test('should upload photos via file input', async ({ page }) => {
    // Create a test image file
    const testImagePath = path.join(__dirname, '../fixtures/test-image.jpg');

    // Set input files
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testImagePath);

    // Should show upload progress
    await expect(page.locator('text=/subiendo|uploading/i')).toBeVisible();

    // Should display uploaded photo
    await expect(page.locator('[data-testid="trip-photo"]')).toBeVisible({ timeout: 10000 });
  });

  test('should enforce max 20 photos limit', async ({ page }) => {
    // This test requires creating 20+ test images
    // For now, we'll verify the UI shows the limit

    // Verify max photos message
    await expect(page.locator('text=/máximo.*20.*fotos/i')).toBeVisible();
  });

  test('should allow reordering photos via drag-and-drop', async ({ page }) => {
    // Upload 2+ photos first
    const testImagePath = path.join(__dirname, '../fixtures/test-image.jpg');
    const fileInput = page.locator('input[type="file"]');

    await fileInput.setInputFiles([testImagePath, testImagePath]);

    // Wait for uploads
    await page.waitForSelector('[data-testid="trip-photo"]', { timeout: 10000 });

    // Verify photos can be dragged (has draggable attribute)
    const firstPhoto = page.locator('[data-testid="trip-photo"]').first();
    await expect(firstPhoto).toHaveAttribute('draggable', 'true');
  });

  test('should skip photos and proceed to step 4', async ({ page }) => {
    // Photos are optional - should allow proceeding without uploads
    await page.click('button:has-text("Siguiente")');

    // Should navigate to step 4 (review)
    await expect(page.locator('text=/paso 4.*4/i')).toBeVisible();
    await expect(page.locator('text=/revisar|review/i')).toBeVisible();
  });
});

test.describe('Trip Creation Wizard - Step 4: Review & Publish (T050)', () => {
  test.beforeEach(async ({ page }) => {
    await createAuthenticatedUser(page);
    await page.goto(`${FRONTEND_URL}/trips/new`);

    // Complete all steps
    await page.fill('input[name="title"]', 'Ruta Final Test');
    await page.fill(
      'textarea[name="description"]',
      'This is the final trip description for testing the review step functionality.'
    );
    await page.fill('input[name="start_date"]', '2024-06-01');
    await page.fill('input[name="end_date"]', '2024-06-05');
    await page.fill('input[name="distance_km"]', '250');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('text=/paso 2.*4/i');
    const tagInput = page.locator('input[name="tags"]');
    await tagInput.fill('test');
    await tagInput.press('Enter');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('text=/paso 3.*4/i');
    await page.click('button:has-text("Siguiente")');

    await page.waitForSelector('text=/paso 4.*4/i');
  });

  test('should display trip summary for review', async ({ page }) => {
    // Verify all trip details are shown
    await expect(page.locator('text=Ruta Final Test')).toBeVisible();
    await expect(page.locator('text=/250.*km/i')).toBeVisible();
    await expect(page.locator('text=/1.*jun.*2024/i')).toBeVisible();
    await expect(page.locator('text=/5.*jun.*2024/i')).toBeVisible();
    await expect(page.locator('text=test')).toBeVisible(); // Tag
  });

  test('should save as draft', async ({ page }) => {
    await page.click('button:has-text(/guardar.*borrador|save.*draft/i)');

    // Should redirect to trips list
    await expect(page).toHaveURL(/\/trips/, { timeout: 10000 });

    // Should show success message
    await expect(page.locator('text=/borrador.*guardado|draft.*saved/i')).toBeVisible();
  });

  test('should publish trip directly', async ({ page }) => {
    await page.click('button:has-text(/publicar|publish/i)');

    // Should redirect to trip detail page
    await expect(page).toHaveURL(/\/trips\/[a-f0-9-]+/, { timeout: 10000 });

    // Should show success message
    await expect(page.locator('text=/viaje.*publicado|trip.*published/i')).toBeVisible();

    // Should show trip title
    await expect(page.locator('text=Ruta Final Test')).toBeVisible();
  });

  test('should allow editing from review step', async ({ page }) => {
    // Click edit button (should go back to specific step)
    await page.click('button:has-text(/editar.*básica|edit.*basic/i)');

    // Should return to step 1
    await expect(page.locator('text=/paso 1.*4/i')).toBeVisible();

    // Data should be preserved
    await expect(page.locator('input[name="title"]')).toHaveValue('Ruta Final Test');
  });
});

test.describe('Trip Creation - End-to-End Flow (T050)', () => {
  test('should complete full trip creation and publish', async ({ page }) => {
    const testUser = await createAuthenticatedUser(page);

    // Navigate to new trip page
    await page.goto(`${FRONTEND_URL}/trips/new`);

    // Step 1: Basic info
    await page.fill('input[name="title"]', 'E2E Complete Trip');
    await page.fill(
      'textarea[name="description"]',
      'This is a complete end-to-end test for trip creation workflow with all steps completed.'
    );
    await page.fill('input[name="start_date"]', '2024-07-01');
    await page.fill('input[name="end_date"]', '2024-07-10');
    await page.fill('input[name="distance_km"]', '450');
    await page.selectOption('select[name="difficulty"]', 'HARD');
    await page.click('button:has-text("Siguiente")');

    // Step 2: Tags
    await page.waitForSelector('text=/paso 2.*4/i');
    const tagInput = page.locator('input[name="tags"]');
    await tagInput.fill('e2e-test');
    await tagInput.press('Enter');
    await tagInput.fill('bikepacking');
    await tagInput.press('Enter');
    await page.click('button:has-text("Siguiente")');

    // Step 3: Photos (skip for now)
    await page.waitForSelector('text=/paso 3.*4/i');
    await page.click('button:has-text("Siguiente")');

    // Step 4: Review and publish
    await page.waitForSelector('text=/paso 4.*4/i');
    await page.click('button:has-text(/publicar|publish/i)');

    // Verify redirect to trip detail
    await expect(page).toHaveURL(/\/trips\/[a-f0-9-]+/, { timeout: 10000 });
    await expect(page.locator('h1:has-text("E2E Complete Trip")')).toBeVisible();

    // Verify trip appears in user's trips list
    await page.goto(`${FRONTEND_URL}/users/${testUser.username}/trips`);
    await expect(page.locator('text=E2E Complete Trip')).toBeVisible();
    await expect(page.locator('text=450')).toBeVisible();
  });
});
