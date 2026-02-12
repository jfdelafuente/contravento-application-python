/**
 * E2E Tests for Authentication Flows
 *
 * Tests complete user authentication workflows including:
 * - User registration (T046)
 * - Login/logout flows (T047)
 * - Session persistence (T048)
 *
 * Prerequisites:
 * - Backend server running at http://localhost:8000
 * - Frontend server running at http://localhost:5173
 * - Database in clean state
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const FRONTEND_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Test data
const TEST_USER = {
  username: `e2euser_${Date.now()}`,
  email: `e2euser_${Date.now()}@example.com`,
  password: 'E2ETestPass123!',
};

test.describe('User Registration Flow (T046)', () => {
  test('should complete full registration workflow', async ({ page }) => {
    // Navigate to registration page
    await page.goto(`${FRONTEND_URL}/register`);
    await expect(page).toHaveTitle(/ContraVento/);

    // Fill registration form
    await page.fill('input[name="username"]', TEST_USER.username);
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.fill('input[name="confirmPassword"]', TEST_USER.password);
    await page.check('input[type="checkbox"]'); // Accept terms and conditions

    // Wait for Turnstile widget to load and auto-verify
    // Testing key 1x00000000000000000000AA should auto-pass
    // Give it generous time for the callback to execute
    await page.waitForTimeout(5000);

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for navigation - in testing mode redirects to /login, in production to /verify-email
    const finalUrl = await page.waitForURL(/\/(login|verify-email)/, { timeout: 10000 }).then(() => page.url());

    // Verify we ended up in the right place
    // Testing environment should redirect to /login (auto-verified)
    // Production should redirect to /verify-email
    expect(finalUrl).toMatch(/\/(login|verify-email)/);
  });

  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/register`);

    // Try to submit with empty fields
    await page.click('button[type="submit"]');

    // Should show field-specific errors
    await expect(page.locator('text=/nombre de usuario.*requerido/i')).toBeVisible();
    await expect(page.locator('text=/email.*requerido/i')).toBeVisible();
    await expect(page.locator('text=/contraseña.*requerida/i')).toBeVisible();
  });

  test('should prevent duplicate username registration', async ({ page }) => {
    // First, create a user via API
    const response = await page.request.post(`${API_URL}/auth/register`, {
      data: {
        username: TEST_USER.username,
        email: TEST_USER.email,
        password: TEST_USER.password,
        turnstile_token: 'dummy_token',
      },
    });

    expect(response.status()).toBe(201);

    // Now try to register with same username
    await page.goto(`${FRONTEND_URL}/register`);
    await page.fill('input[name="username"]', TEST_USER.username);
    await page.fill('input[name="email"]', `different_${TEST_USER.email}`);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.fill('input[name="confirmPassword"]', TEST_USER.password);
    await page.check('input[type="checkbox"]'); // Accept terms and conditions

    // Wait for Turnstile widget to load and auto-verify
    // Testing key should auto-pass, give generous time for callback
    await page.waitForTimeout(5000);

    await page.click('button[type="submit"]');

    // Should show error about duplicate username and stay on register page
    await expect(page.locator('.error-banner')).toBeVisible({ timeout: 10000 });
    await expect(page).toHaveURL(/\/register/);
  });
});

test.describe('Login Flow (T047)', () => {
  let registeredUser: typeof TEST_USER;

  test.beforeEach(async ({ page }) => {
    // Create a verified user for login tests
    registeredUser = {
      username: `loginuser_${Date.now()}`,
      email: `loginuser_${Date.now()}@example.com`,
      password: 'LoginTest123!',
    };

    // Register user via API
    const response = await page.request.post(`${API_URL}/auth/register`, {
      data: {
        username: registeredUser.username,
        email: registeredUser.email,
        password: registeredUser.password,
        turnstile_token: 'dummy_token',
      },
    });

    expect(response.status()).toBe(201);

    // Verify user via direct database update (for testing)
    // In production, user would click verification link
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/login`);

    // Fill login form
    await page.fill('input[name="login"]', registeredUser.username);
    await page.fill('input[name="password"]', registeredUser.password);

    // Submit login
    await page.click('button[type="submit"]');

    // Should redirect to home/dashboard
    await expect(page).toHaveURL(/\/(home|dashboard|trips)/, { timeout: 10000 });

    // Should show user menu with username
    await expect(page.locator('.username')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/login`);

    // Try login with wrong password
    await page.fill('input[name="login"]', registeredUser.username);
    await page.fill('input[name="password"]', 'WrongPassword123!');

    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('.error-banner')).toBeVisible();

    // Should stay on login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('should login with email instead of username', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/login`);

    // Login with email
    await page.fill('input[name="login"]', registeredUser.email);
    await page.fill('input[name="password"]', registeredUser.password);

    await page.click('button[type="submit"]');

    // Should successfully login
    await expect(page).toHaveURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
  });
});

test.describe('Logout Flow (T047)', () => {
  let authenticatedPage: Page;

  test.beforeEach(async ({ browser }) => {
    // Create authenticated session
    const context = await browser.newContext();
    authenticatedPage = await context.newPage();

    // Login user
    const testUser = {
      username: `logoutuser_${Date.now()}`,
      email: `logoutuser_${Date.now()}@example.com`,
      password: 'LogoutTest123!',
    };

    // Register and login via API
    await authenticatedPage.request.post(`${API_URL}/auth/register`, {
      data: {
        username: testUser.username,
        email: testUser.email,
        password: testUser.password,
        turnstile_token: 'dummy_token',
      },
    });

    await authenticatedPage.goto(`${FRONTEND_URL}/login`);
    await authenticatedPage.fill('input[name="login"]', testUser.username);
    await authenticatedPage.fill('input[name="password"]', testUser.password);
    await authenticatedPage.click('button[type="submit"]');

    // Wait for redirect
    await authenticatedPage.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });
  });

  test('should logout and clear session', async () => {
    // Click logout button (in user menu)
    await authenticatedPage.click('text=/cerrar sesión|logout/i');

    // Wait for navigation to complete (increased timeout)
    await authenticatedPage.waitForURL(/\/login/, { timeout: 10000 });

    // Verify we're on login page
    await expect(authenticatedPage).toHaveURL(/\/login/);

    // Should not be able to access protected pages
    await authenticatedPage.goto(`${FRONTEND_URL}/trips/new`);
    await expect(authenticatedPage).toHaveURL(/\/login/);
  });
});

test.describe('Session Persistence (T048)', () => {
  test('should maintain session across page refreshes', async ({ page }) => {
    // Create and login user
    const testUser = {
      username: `sessionuser_${Date.now()}`,
      email: `sessionuser_${Date.now()}@example.com`,
      password: 'SessionTest123!',
    };

    await page.request.post(`${API_URL}/auth/register`, {
      data: {
        username: testUser.username,
        email: testUser.email,
        password: testUser.password,
        turnstile_token: 'dummy_token',
      },
    });

    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[name="login"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/(home|dashboard|trips)/, { timeout: 10000 });

    // Refresh page
    await page.reload();

    // Should still be authenticated (HttpOnly cookie persists)
    await expect(page.locator('.username')).toBeVisible();

    // Should access protected pages without re-login
    await page.goto(`${FRONTEND_URL}/profile`);
    await expect(page).toHaveURL(/\/profile/);
  });

  test('should handle expired tokens gracefully', async ({ page }) => {
    // This test would require mocking token expiration
    // or waiting 15+ minutes (access token TTL)

    // For now, we'll test the refresh token flow by:
    // 1. Login
    // 2. Simulate expired access token (via API manipulation)
    // 3. Verify automatic token refresh

    // TODO: Implement token expiration testing
    test.skip();
  });
});

test.describe('Protected Routes (T048)', () => {
  test('should redirect unauthenticated users to login', async ({ page }) => {
    // Try to access protected routes without auth
    const protectedRoutes = [
      '/trips/new',
      '/profile',
      '/profile/edit',
      '/trips/some-trip-id/edit',
    ];

    for (const route of protectedRoutes) {
      await page.goto(`${FRONTEND_URL}${route}`);

      // Should redirect to login
      await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
    }
  });

  test('should allow access to public routes', async ({ page }) => {
    const publicRoutes = [
      { path: '/', expectedUrl: '/' },
      { path: '/login', expectedUrl: '/login' },
      { path: '/register', expectedUrl: '/register' },
      { path: '/trips/public', expectedUrl: '/trips/public' },
    ];

    for (const route of publicRoutes) {
      await page.goto(`${FRONTEND_URL}${route.path}`);

      // Should stay on the same route (not redirect)
      await expect(page).toHaveURL(new RegExp(route.expectedUrl.replace('/', '\\/')));
    }
  });
});
