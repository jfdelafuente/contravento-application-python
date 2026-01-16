// frontend/tests/e2e/landing.spec.ts

import { test, expect } from '@playwright/test';

/**
 * E2E Test Suite: Landing Page User Journeys (Feature 014)
 *
 * User Stories:
 * - US4: Visitor clicks CTA and is redirected to /register
 * - US1: Authenticated user is redirected to /trips/public
 * - US3: Mobile responsive behavior works correctly
 */

test.describe('Landing Page - Visitor CTA Journey (US4)', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to landing page
    await page.goto('http://localhost:5173/');
  });

  test('should display CTA section with "Formar parte del viaje" button', async ({ page }) => {
    // Verify CTA section is visible
    const ctaSection = page.locator('section.cta-section');
    await expect(ctaSection).toBeVisible();

    // Verify CTA button is visible
    const ctaButton = page.getByRole('link', { name: /formar parte del viaje/i });
    await expect(ctaButton).toBeVisible();
  });

  test('should redirect to /register when clicking CTA button', async ({ page }) => {
    // Click CTA button
    const ctaButton = page.getByRole('link', { name: /formar parte del viaje/i });
    await ctaButton.click();

    // Verify redirect to /register
    await expect(page).toHaveURL('http://localhost:5173/register');
  });

  test('should display login link in CTA section', async ({ page }) => {
    // Verify login link is visible
    const loginLink = page.getByRole('link', { name: /inicia sesión/i });
    await expect(loginLink).toBeVisible();
  });

  test('should redirect to /login when clicking login link', async ({ page }) => {
    // Click login link
    const loginLink = page.getByRole('link', { name: /inicia sesión/i });
    await loginLink.click();

    // Verify redirect to /login
    await expect(page).toHaveURL('http://localhost:5173/login');
  });

  test('should display CTA button with terracota background color', async ({ page }) => {
    // Verify CTA button has terracota color (#D35400)
    const ctaButton = page.locator('.cta-button');
    const backgroundColor = await ctaButton.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    // RGB equivalent of #D35400 is rgb(211, 84, 0)
    expect(backgroundColor).toBe('rgb(211, 84, 0)');
  });

  test('should have accessible CTA button text', async ({ page }) => {
    const ctaButton = page.getByRole('link', { name: /formar parte del viaje/i });
    const buttonText = await ctaButton.textContent();
    expect(buttonText).toMatch(/formar parte del viaje/i);
  });
});

test.describe('Landing Page - Authenticated User Redirect (US1)', () => {
  test('should redirect authenticated users to /trips/public', async ({ page, context }) => {
    // Mock authenticated user by setting auth token in localStorage
    await context.addCookies([
      {
        name: 'auth_token',
        value: 'mock-jwt-token',
        domain: 'localhost',
        path: '/',
      },
    ]);

    // Navigate to landing page
    await page.goto('http://localhost:5173/');

    // Verify redirect to /trips/public
    await expect(page).toHaveURL('http://localhost:5173/trips/public');
  });

  test('should display landing page for unauthenticated users', async ({ page }) => {
    // Navigate to landing page (no auth)
    await page.goto('http://localhost:5173/');

    // Verify landing page sections are visible
    const heroSection = page.locator('section.hero-section');
    await expect(heroSection).toBeVisible();

    const manifestoSection = page.locator('section.manifesto-section');
    await expect(manifestoSection).toBeVisible();

    const ctaSection = page.locator('section.cta-section');
    await expect(ctaSection).toBeVisible();
  });
});

test.describe('Landing Page - Mobile Responsive Behavior (US3)', () => {
  test('should display mobile-optimized layout on viewport < 768px', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Navigate to landing page
    await page.goto('http://localhost:5173/');

    // Verify hero section is visible
    const heroSection = page.locator('section.hero-section');
    await expect(heroSection).toBeVisible();

    // Verify CTA button is visible and accessible on mobile
    const ctaButton = page.getByRole('link', { name: /formar parte del viaje/i });
    await expect(ctaButton).toBeVisible();

    // Verify CTA button is large enough for touch (min 44px height)
    const buttonBox = await ctaButton.boundingBox();
    expect(buttonBox?.height).toBeGreaterThanOrEqual(44);
  });

  test('should stack sections vertically on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Navigate to landing page
    await page.goto('http://localhost:5173/');

    // Verify sections are stacked (check vertical positions)
    const heroSection = page.locator('section.hero-section');
    const manifestoSection = page.locator('section.manifesto-section');
    const ctaSection = page.locator('section.cta-section');

    const heroBox = await heroSection.boundingBox();
    const manifestoBox = await manifestoSection.boundingBox();
    const ctaBox = await ctaSection.boundingBox();

    // Manifesto should be below hero
    expect(manifestoBox!.y).toBeGreaterThan(heroBox!.y + heroBox!.height);

    // CTA should be below manifesto
    expect(ctaBox!.y).toBeGreaterThan(manifestoBox!.y);
  });

  test('should display desktop layout on viewport >= 1024px', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1440, height: 900 });

    // Navigate to landing page
    await page.goto('http://localhost:5173/');

    // Verify all sections are visible
    const heroSection = page.locator('section.hero-section');
    const ctaSection = page.locator('section.cta-section');

    await expect(heroSection).toBeVisible();
    await expect(ctaSection).toBeVisible();

    // Verify CTA button has appropriate desktop size
    const ctaButton = page.locator('.cta-button');
    await expect(ctaButton).toBeVisible();
  });
});

test.describe('Landing Page - Complete User Journey', () => {
  test('should complete full visitor journey: view landing → click CTA → register', async ({ page }) => {
    // Step 1: Navigate to landing page
    await page.goto('http://localhost:5173/');

    // Step 2: Verify landing page content
    const heroTitle = page.getByRole('heading', { name: /el camino es el destino/i });
    await expect(heroTitle).toBeVisible();

    // Step 3: Scroll to CTA section
    const ctaSection = page.locator('section.cta-section');
    await ctaSection.scrollIntoViewIfNeeded();

    // Step 4: Click CTA button
    const ctaButton = page.getByRole('link', { name: /formar parte del viaje/i });
    await ctaButton.click();

    // Step 5: Verify redirect to register page
    await expect(page).toHaveURL('http://localhost:5173/register');
  });
});
