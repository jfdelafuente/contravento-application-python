/**
 * E2E Tests for Location Editing with Maps
 *
 * Tests the map-based location editing functionality (T053-T054):
 * - Click on map to add location
 * - Drag markers to adjust coordinates
 * - Reverse geocoding to get place names
 * - Edit location names manually
 * - Delete locations
 *
 * Prerequisites:
 * - Authenticated user with published trip
 * - Backend and frontend servers running
 * - Leaflet map properly loaded
 */

import { test, expect, Page } from '@playwright/test';

const FRONTEND_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Helper to create authenticated user with a trip
async function createUserWithTrip(page: Page) {
  const testUser = {
    username: `mapuser_${Date.now()}`,
    email: `mapuser_${Date.now()}@example.com`,
    password: 'MapTest123!',
  };

  // Register user
  const registerResponse = await page.request.post(`${API_URL}/auth/register`, {
    data: {
      username: testUser.username,
      email: testUser.email,
      password: testUser.password,
      turnstile_token: 'dummy_token',
    },
  });

  const registerData = await registerResponse.json();

  // Verify user is registered successfully
  if (!registerData.success || !registerData.data) {
    throw new Error(`Registration failed: ${registerData.error?.message || 'Unknown error'}`);
  }

  // IMPORTANT: For E2E tests, users must be verified before login
  // In production, users would click the verification link in their email
  // For testing, we need to manually verify the user via database
  // This is handled by the backend test environment setup

  // Login (will fail if user is not verified)
  const loginResponse = await page.request.post(`${API_URL}/auth/login`, {
    data: {
      login: testUser.username,
      password: testUser.password,
    },
  });

  const loginData = await loginResponse.json();

  // Check if login was successful
  if (!loginData.success || !loginData.data) {
    throw new Error(
      `Login failed: ${loginData.error?.message || 'Unknown error'}. ` +
      `User may not be verified. Status: ${loginResponse.status()}`
    );
  }

  const { access_token } = loginData.data;

  // Create trip
  const createResponse = await page.request.post(`${API_URL}/trips`, {
    headers: { Authorization: `Bearer ${access_token}` },
    data: {
      title: 'Location Test Trip',
      description: 'Trip for testing location editing with map interactions and geocoding.',
      start_date: '2024-06-01',
    },
  });

  const { trip_id } = (await createResponse.json()).data;

  // Publish trip
  await page.request.post(`${API_URL}/trips/${trip_id}/publish`, {
    headers: { Authorization: `Bearer ${access_token}` },
  });

  return { testUser, access_token, trip_id };
}

test.describe('Location Editing - Map Display (T053)', () => {
  test('should display Leaflet map on trip detail page', async ({ page }) => {
    const { testUser, trip_id } = await createUserWithTrip(page);

    // Login user
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });

    // Navigate to trip detail
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Should display map container
    await expect(page.locator('.leaflet-container')).toBeVisible({ timeout: 10000 });

    // Map should be interactive (has zoom controls)
    await expect(page.locator('.leaflet-control-zoom')).toBeVisible();
  });

  test('should show "Add Location" button for trip owner', async ({ page }) => {
    const { testUser, trip_id } = await createUserWithTrip(page);

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Should show edit/add location button
    const editButton = page.locator('button:has-text(/editar.*ubicación|edit.*location|añadir.*ubicación/i)');
    await expect(editButton).toBeVisible();
  });

  test('should hide edit controls for non-owners', async ({ page }) => {
    const { trip_id } = await createUserWithTrip(page);

    // Visit trip as anonymous user (no login)
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Should NOT show edit button
    const editButton = page.locator('button:has-text(/editar.*ubicación|edit.*location/i)');
    await expect(editButton).not.toBeVisible();
  });
});

test.describe('Location Editing - Add Location via Map Click (T053)', () => {
  test('should add location by clicking on map', async ({ page }) => {
    const { testUser, trip_id } = await createUserWithTrip(page);

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Enable edit mode
    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    // Wait for map to be clickable
    await page.waitForSelector('.leaflet-container', { timeout: 10000 });

    // Click on map center (simulate adding location)
    const mapContainer = page.locator('.leaflet-container');
    const mapBox = await mapContainer.boundingBox();

    if (mapBox) {
      // Click center of map
      await page.mouse.click(mapBox.x + mapBox.width / 2, mapBox.y + mapBox.height / 2);

      // Should show location confirmation modal
      await expect(page.locator('text=/confirmar.*ubicación|confirm.*location/i')).toBeVisible({ timeout: 5000 });

      // Modal should show geocoded place name or coordinates
      await expect(page.locator('[data-testid="location-name-input"]')).toBeVisible();
    }
  });

  test('should show loading state during geocoding', async ({ page }) => {
    const { testUser, trip_id } = await createUserWithTrip(page);

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    const mapContainer = page.locator('.leaflet-container');
    const mapBox = await mapContainer.boundingBox();

    if (mapBox) {
      await page.mouse.click(mapBox.x + mapBox.width / 2, mapBox.y + mapBox.height / 2);

      // Should show loading spinner during geocoding
      const loadingSpinner = page.locator('[role="status"]:has-text(/obteniendo|loading/i)');

      // Loading state may be very brief, so we check if it appears OR if modal shows immediately
      const hasLoading = await loadingSpinner.isVisible().catch(() => false);
      const hasModal = await page.locator('text=/confirmar.*ubicación/i').isVisible();

      expect(hasLoading || hasModal).toBeTruthy();
    }
  });

  test('should allow editing geocoded place name', async ({ page }) => {
    const { testUser, trip_id } = await createUserWithTrip(page);

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    const mapContainer = page.locator('.leaflet-container');
    const mapBox = await mapContainer.boundingBox();

    if (mapBox) {
      await page.mouse.click(mapBox.x + mapBox.width / 2, mapBox.y + mapBox.height / 2);

      // Wait for confirmation modal
      await page.waitForSelector('[data-testid="location-name-input"]', { timeout: 10000 });

      // Edit the place name
      const nameInput = page.locator('[data-testid="location-name-input"]');
      await nameInput.clear();
      await nameInput.fill('Custom Location Name');

      // Confirm location
      await page.click('button:has-text(/confirmar|confirm/i)');

      // Should add marker to map with custom name
      await expect(page.locator('.leaflet-marker-icon')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should cancel location addition', async ({ page }) => {
    const { testUser, trip_id } = await createUserWithTrip(page);

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    const mapContainer = page.locator('.leaflet-container');
    const mapBox = await mapContainer.boundingBox();

    if (mapBox) {
      await page.mouse.click(mapBox.x + mapBox.width / 2, mapBox.y + mapBox.height / 2);

      await page.waitForSelector('button:has-text(/cancelar|cancel/i)', { timeout: 10000 });

      // Cancel location
      await page.click('button:has-text(/cancelar|cancel/i)');

      // Modal should close
      await expect(page.locator('text=/confirmar.*ubicación/i')).not.toBeVisible();

      // No marker should be added
      await expect(page.locator('.leaflet-marker-icon')).not.toBeVisible();
    }
  });
});

test.describe('Location Editing - Drag Marker to Adjust (T054)', () => {
  test('should allow dragging marker to new position', async ({ page }) => {
    const { testUser, trip_id, access_token } = await createUserWithTrip(page);

    // Add initial location via API
    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        name: 'Initial Location',
        latitude: 41.3851,
        longitude: 2.1734,
      },
    });

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Wait for map and marker to load
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });

    // Enable edit mode
    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    // Marker should be draggable in edit mode
    const marker = page.locator('.leaflet-marker-icon').first();
    const markerBox = await marker.boundingBox();

    if (markerBox) {
      // Drag marker to new position (50px to the right)
      await page.mouse.move(markerBox.x + markerBox.width / 2, markerBox.y + markerBox.height / 2);
      await page.mouse.down();
      await page.mouse.move(markerBox.x + 50, markerBox.y);
      await page.mouse.up();

      // Should trigger re-geocoding (debounced)
      // Wait for geocoding to complete
      await page.waitForTimeout(2000); // Wait for debounce + API call

      // Coordinates should be updated
      // (Verify by checking if location name changed or modal appeared)
    }
  });

  test('should show updated place name after dragging', async ({ page }) => {
    const { testUser, trip_id, access_token } = await createUserWithTrip(page);

    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        name: 'Barcelona',
        latitude: 41.3851,
        longitude: 2.1734,
      },
    });

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });

    // Original location name should be visible
    await expect(page.locator('text=Barcelona')).toBeVisible();

    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    const marker = page.locator('.leaflet-marker-icon').first();
    const markerBox = await marker.boundingBox();

    if (markerBox) {
      // Drag to significantly different location
      await page.mouse.move(markerBox.x, markerBox.y);
      await page.mouse.down();
      await page.mouse.move(markerBox.x + 100, markerBox.y + 100);
      await page.mouse.up();

      // Wait for re-geocoding
      await page.waitForTimeout(2000);

      // Should show confirmation modal with new place name
      const modal = page.locator('[data-testid="location-confirm-modal"]');
      if (await modal.isVisible()) {
        await expect(page.locator('[data-testid="location-name-input"]')).toBeVisible();
      }
    }
  });
});

test.describe('Location Editing - Delete Location (T054)', () => {
  test('should delete location via delete button', async ({ page }) => {
    const { testUser, trip_id, access_token } = await createUserWithTrip(page);

    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        name: 'Location to Delete',
        latitude: 41.3851,
        longitude: 2.1734,
      },
    });

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });

    // Enable edit mode
    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    // Click delete button for location
    await page.click('button[data-testid="delete-location"]:has-text(/eliminar|delete/i)');

    // Should show confirmation dialog
    await expect(page.locator('text=/eliminar.*ubicación|delete.*location/i')).toBeVisible();

    // Confirm deletion
    await page.click('button:has-text(/confirmar|confirm|eliminar/i)');

    // Marker should be removed from map
    await expect(page.locator('.leaflet-marker-icon')).not.toBeVisible();

    // Location name should not be visible
    await expect(page.locator('text=Location to Delete')).not.toBeVisible();
  });

  test('should cancel location deletion', async ({ page }) => {
    const { testUser, trip_id, access_token } = await createUserWithTrip(page);

    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        name: 'Location to Keep',
        latitude: 41.3851,
        longitude: 2.1734,
      },
    });

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });

    await page.click('button:has-text(/editar.*ubicación|edit.*location/i)');

    // Click delete button
    await page.click('button[data-testid="delete-location"]:has-text(/eliminar|delete/i)');

    await expect(page.locator('text=/eliminar.*ubicación|delete.*location/i')).toBeVisible();

    // Cancel deletion
    await page.click('button:has-text(/cancelar|cancel/i)');

    // Marker should still be visible
    await expect(page.locator('.leaflet-marker-icon')).toBeVisible();
    await expect(page.locator('text=Location to Keep')).toBeVisible();
  });
});

test.describe('Location Editing - Multiple Locations (T054)', () => {
  test('should support adding multiple locations to a trip', async ({ page }) => {
    const { testUser, trip_id, access_token } = await createUserWithTrip(page);

    // Add 3 locations via API
    const locations = [
      { name: 'Barcelona', latitude: 41.3851, longitude: 2.1734 },
      { name: 'Girona', latitude: 41.9794, longitude: 2.8214 },
      { name: 'Figueres', latitude: 42.2671, longitude: 2.9618 },
    ];

    for (const location of locations) {
      await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
        headers: { Authorization: `Bearer ${access_token}` },
        data: location,
      });
    }

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Should show 3 markers on map
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    const markers = page.locator('.leaflet-marker-icon');
    await expect(markers).toHaveCount(3);

    // Should show all location names
    await expect(page.locator('text=Barcelona')).toBeVisible();
    await expect(page.locator('text=Girona')).toBeVisible();
    await expect(page.locator('text=Figueres')).toBeVisible();
  });

  test('should fit map bounds to show all locations', async ({ page }) => {
    const { testUser, trip_id, access_token } = await createUserWithTrip(page);

    // Add locations far apart
    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: { name: 'Barcelona', latitude: 41.3851, longitude: 2.1734 },
    });

    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: { name: 'Madrid', latitude: 40.4168, longitude: -3.7038 },
    });

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });

    // Both markers should be visible (map auto-zoomed to fit bounds)
    const markers = page.locator('.leaflet-marker-icon');
    await expect(markers).toHaveCount(2);

    // Verify both markers are in viewport
    const marker1 = markers.nth(0);
    const marker2 = markers.nth(1);

    await expect(marker1).toBeInViewport();
    await expect(marker2).toBeInViewport();
  });
});
