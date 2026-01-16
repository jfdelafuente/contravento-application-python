/**
 * E2E Tests for Public Feed Browsing
 *
 * Tests the public trips feed functionality (T051-T052):
 * - Anonymous browsing of published trips
 * - Filtering by tags
 * - Pagination
 * - Trip detail viewing
 *
 * Prerequisites:
 * - Backend and frontend servers running
 * - Sample published trips in database
 */

import { test, expect, Page } from '@playwright/test';

const FRONTEND_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Helper to create sample published trips
async function createSampleTrips(page: Page, count: number = 5) {
  const testUser = {
    username: `feeduser_${Date.now()}`,
    email: `feeduser_${Date.now()}@example.com`,
    password: 'FeedTest123!',
  };

  // Register and login user
  await page.request.post(`${API_URL}/auth/register`, {
    data: {
      username: testUser.username,
      email: testUser.email,
      password: testUser.password,
      turnstile_token: 'dummy_token',
    },
  });

  const loginResponse = await page.request.post(`${API_URL}/auth/login`, {
    data: {
      login: testUser.username,
      password: testUser.password,
    },
  });

  const { access_token } = (await loginResponse.json()).data;

  // Create and publish trips
  const tripIds: string[] = [];

  for (let i = 1; i <= count; i++) {
    const tripData = {
      title: `Sample Trip ${i}`,
      description: `This is sample trip number ${i} for public feed testing with sufficient description length.`,
      start_date: `2024-0${Math.min(i, 9)}-01`,
      distance_km: 100 + i * 50,
    };

    const createResponse = await page.request.post(`${API_URL}/trips`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: tripData,
    });

    const { trip_id } = (await createResponse.json()).data;

    // Publish trip
    await page.request.post(`${API_URL}/trips/${trip_id}/publish`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });

    tripIds.push(trip_id);
  }

  return { testUser, tripIds };
}

test.describe('Public Feed - Anonymous Access (T051)', () => {
  test('should display public trips without authentication', async ({ page }) => {
    // Create sample trips first
    await createSampleTrips(page, 3);

    // Navigate to public feed (not logged in)
    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Should display trip cards
    await expect(page.locator('[data-testid="trip-card"]').first()).toBeVisible();

    // Should show trip titles
    await expect(page.locator('text=/Sample Trip/i')).toBeVisible();
  });

  test('should show trip details without authentication', async ({ page }) => {
    const { tripIds } = await createSampleTrips(page, 1);

    // Navigate to public feed
    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Click on first trip card
    await page.locator('[data-testid="trip-card"]').first().click();

    // Should navigate to trip detail page
    await expect(page).toHaveURL(/\/trips\/[a-f0-9-]+/);

    // Should display trip details
    await expect(page.locator('h1:has-text("Sample Trip")')).toBeVisible();
    await expect(page.locator('text=/descripción|description/i')).toBeVisible();
  });

  test('should hide edit/delete buttons for anonymous users', async ({ page }) => {
    await createSampleTrips(page, 1);

    await page.goto(`${FRONTEND_URL}/trips/public`);
    await page.locator('[data-testid="trip-card"]').first().click();

    // Should NOT show owner-only action buttons
    await expect(page.locator('button:has-text(/editar|edit/i)')).not.toBeVisible();
    await expect(page.locator('button:has-text(/eliminar|delete/i)')).not.toBeVisible();
    await expect(page.locator('button:has-text(/publicar|publish/i)')).not.toBeVisible();
  });

  test('should not expose user email addresses', async ({ page }) => {
    await createSampleTrips(page, 1);

    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Get page content
    const content = await page.content();

    // Should not contain email addresses
    expect(content).not.toContain('@example.com');
    expect(content).not.toMatch(/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i);
  });
});

test.describe('Public Feed - Filtering (T051)', () => {
  test.beforeEach(async ({ page }) => {
    // Create trips with different tags
    const testUser = {
      username: `filteruser_${Date.now()}`,
      email: `filteruser_${Date.now()}@example.com`,
      password: 'FilterTest123!',
    };

    await page.request.post(`${API_URL}/auth/register`, {
      data: {
        username: testUser.username,
        email: testUser.email,
        password: testUser.password,
        turnstile_token: 'dummy_token',
      },
    });

    const loginResponse = await page.request.post(`${API_URL}/auth/login`, {
      data: {
        login: testUser.username,
        password: testUser.password,
      },
    });

    const { access_token } = (await loginResponse.json()).data;

    // Create trips with different tags
    const tripsData = [
      { title: 'Bikepacking Trip', tags: ['bikepacking', 'montaña'] },
      { title: 'Road Cycling', tags: ['carretera', 'velocidad'] },
      { title: 'MTB Adventure', tags: ['mtb', 'montaña'] },
    ];

    for (const tripData of tripsData) {
      const createResponse = await page.request.post(`${API_URL}/trips`, {
        headers: { Authorization: `Bearer ${access_token}` },
        data: {
          title: tripData.title,
          description: `Trip description for ${tripData.title} with enough characters.`,
          start_date: '2024-06-01',
        },
      });

      const { trip_id } = (await createResponse.json()).data;

      // Add tags
      for (const tag of tripData.tags) {
        await page.request.post(`${API_URL}/trips/${trip_id}/tags`, {
          headers: { Authorization: `Bearer ${access_token}` },
          data: { tag_name: tag },
        });
      }

      await page.request.post(`${API_URL}/trips/${trip_id}/publish`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });
    }
  });

  test('should filter trips by tag', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Click on "montaña" tag
    await page.click('a:has-text("montaña")');

    // Should filter to show only trips with "montaña" tag
    await expect(page.locator('text=Bikepacking Trip')).toBeVisible();
    await expect(page.locator('text=MTB Adventure')).toBeVisible();
    await expect(page.locator('text=Road Cycling')).not.toBeVisible();

    // URL should include tag filter
    await expect(page).toHaveURL(/tag=montaña/i);
  });

  test('should show all trips when clearing filter', async ({ page }) => {
    // Navigate with tag filter
    await page.goto(`${FRONTEND_URL}/trips/public?tag=montaña`);

    // Click "clear filters" or "all trips" button
    await page.click('button:has-text(/todos.*viajes|all.*trips|limpiar/i)');

    // Should show all trips again
    await expect(page.locator('text=Bikepacking Trip')).toBeVisible();
    await expect(page.locator('text=Road Cycling')).toBeVisible();
    await expect(page.locator('text=MTB Adventure')).toBeVisible();

    // URL should not include tag parameter
    await expect(page).toHaveURL(/^(?!.*tag=)/);
  });

  test('should show popular tags', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Should display tag cloud or popular tags section
    await expect(page.locator('text=/etiquetas.*populares|popular.*tags/i')).toBeVisible();

    // Should show tags with usage counts
    await expect(page.locator('text=montaña')).toBeVisible();
    await expect(page.locator('text=bikepacking')).toBeVisible();
  });
});

test.describe('Public Feed - Pagination (T051)', () => {
  test('should paginate trips when exceeding page limit', async ({ page }) => {
    // Create 15 trips (assuming page size is 10)
    await createSampleTrips(page, 15);

    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Should show pagination controls
    await expect(page.locator('text=/página.*1/i')).toBeVisible();
    await expect(page.locator('button:has-text(/siguiente|next/i)')).toBeVisible();

    // Click next page
    await page.click('button:has-text(/siguiente|next/i)');

    // Should navigate to page 2
    await expect(page).toHaveURL(/page=2/);
    await expect(page.locator('text=/página.*2/i')).toBeVisible();

    // Should show different trips
    await expect(page.locator('[data-testid="trip-card"]')).toHaveCount(5); // Remaining trips
  });

  test('should allow direct page navigation', async ({ page }) => {
    await createSampleTrips(page, 15);

    // Navigate directly to page 2
    await page.goto(`${FRONTEND_URL}/trips/public?page=2`);

    // Should show page 2 content
    await expect(page.locator('text=/página.*2/i')).toBeVisible();
    await expect(page.locator('[data-testid="trip-card"]')).toBeVisible();
  });

  test('should show "no more trips" on last page', async ({ page }) => {
    await createSampleTrips(page, 3);

    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Next button should be disabled (only 3 trips, fits on one page)
    const nextButton = page.locator('button:has-text(/siguiente|next/i)');
    await expect(nextButton).toBeDisabled();
  });
});

test.describe('Public Feed - Trip Detail View (T052)', () => {
  test('should display complete trip information', async ({ page }) => {
    const { tripIds } = await createSampleTrips(page, 1);

    await page.goto(`${FRONTEND_URL}/trips/${tripIds[0]}`);

    // Should show all trip details
    await expect(page.locator('h1:has-text("Sample Trip")')).toBeVisible();
    await expect(page.locator('text=/descripción/i')).toBeVisible();
    await expect(page.locator('text=/fecha/i')).toBeVisible();
    await expect(page.locator('text=/distancia|distance/i')).toBeVisible();
  });

  test('should display trip photos if available', async ({ page }) => {
    // Create trip with photo via API
    const testUser = {
      username: `photouser_${Date.now()}`,
      email: `photouser_${Date.now()}@example.com`,
      password: 'PhotoTest123!',
    };

    await page.request.post(`${API_URL}/auth/register`, {
      data: {
        username: testUser.username,
        email: testUser.email,
        password: testUser.password,
        turnstile_token: 'dummy_token',
      },
    });

    const loginResponse = await page.request.post(`${API_URL}/auth/login`, {
      data: {
        login: testUser.username,
        password: testUser.password,
      },
    });

    const { access_token } = (await loginResponse.json()).data;

    const createResponse = await page.request.post(`${API_URL}/trips`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        title: 'Trip with Photos',
        description: 'This trip has photos for testing the photo gallery display.',
        start_date: '2024-06-01',
      },
    });

    const { trip_id } = (await createResponse.json()).data;

    await page.request.post(`${API_URL}/trips/${trip_id}/publish`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });

    // Navigate to trip detail
    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Should show photo gallery or placeholder
    const photoGallery = page.locator('[data-testid="trip-photos"]');
    await expect(photoGallery).toBeVisible();
  });

  test('should show map if location is set', async ({ page }) => {
    // Trip with GPS coordinates
    const testUser = {
      username: `mapuser_${Date.now()}`,
      email: `mapuser_${Date.now()}@example.com`,
      password: 'MapTest123!',
    };

    await page.request.post(`${API_URL}/auth/register`, {
      data: {
        username: testUser.username,
        email: testUser.email,
        password: testUser.password,
        turnstile_token: 'dummy_token',
      },
    });

    const loginResponse = await page.request.post(`${API_URL}/auth/login`, {
      data: {
        login: testUser.username,
        password: testUser.password,
      },
    });

    const { access_token } = (await loginResponse.json()).data;

    const createResponse = await page.request.post(`${API_URL}/trips`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        title: 'Trip with Location',
        description: 'This trip has GPS coordinates for testing map display functionality.',
        start_date: '2024-06-01',
      },
    });

    const { trip_id } = (await createResponse.json()).data;

    // Add location
    await page.request.post(`${API_URL}/trips/${trip_id}/locations`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        name: 'Barcelona',
        latitude: 41.3851,
        longitude: 2.1734,
      },
    });

    await page.request.post(`${API_URL}/trips/${trip_id}/publish`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });

    await page.goto(`${FRONTEND_URL}/trips/${trip_id}`);

    // Should show Leaflet map
    await expect(page.locator('.leaflet-container')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.leaflet-marker-icon')).toBeVisible();
  });

  test('should allow navigating back to public feed', async ({ page }) => {
    const { tripIds } = await createSampleTrips(page, 1);

    await page.goto(`${FRONTEND_URL}/trips/${tripIds[0]}`);

    // Click back to feed button
    await page.click('a:has-text(/volver|back|feed/i)');

    // Should return to public feed
    await expect(page).toHaveURL(/\/trips\/public/);
  });
});

test.describe('Public Feed - Responsive Design (T052)', () => {
  test('should display mobile-friendly layout on small screens', async ({ page }) => {
    await createSampleTrips(page, 3);

    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Trip cards should stack vertically
    const tripCards = page.locator('[data-testid="trip-card"]');
    await expect(tripCards.first()).toBeVisible();

    // Should show mobile menu button (if header has one)
    const menuButton = page.locator('button[aria-label*="menu"]');
    if (await menuButton.isVisible()) {
      await menuButton.click();
      // Menu should expand
      await expect(page.locator('nav')).toBeVisible();
    }
  });

  test('should display tablet layout on medium screens', async ({ page }) => {
    await createSampleTrips(page, 3);

    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad

    await page.goto(`${FRONTEND_URL}/trips/public`);

    // Should display trip cards in grid (2 columns)
    const tripCards = page.locator('[data-testid="trip-card"]');
    await expect(tripCards.first()).toBeVisible();
  });
});
