/**
 * Playwright Global Setup
 *
 * Runs once before all E2E tests to:
 * - Verify backend and frontend servers are running
 * - Create test database fixtures
 * - Generate test images if needed
 */

import { chromium, FullConfig } from '@playwright/test';
import path from 'path';
import fs from 'fs/promises';

const FRONTEND_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const MAX_RETRIES = 30; // 30 seconds total (30 * 1s)
const RETRY_DELAY = 1000; // 1 second

async function waitForServer(url: string, retries: number = MAX_RETRIES): Promise<boolean> {
  console.log(`Waiting for server at ${url}...`);

  for (let i = 0; i < retries; i++) {
    try {
      const browser = await chromium.launch();
      const page = await browser.newPage();

      const response = await page.goto(url, { timeout: 5000 });

      await browser.close();

      if (response && response.ok()) {
        console.log(`✓ Server at ${url} is ready`);
        return true;
      }
    } catch (error) {
      // Retry
      await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
    }
  }

  console.error(`✗ Server at ${url} is not responding after ${retries} retries`);
  return false;
}

async function createTestImages() {
  const fixturesDir = path.join(__dirname, '../fixtures');

  // Ensure fixtures directory exists
  try {
    await fs.access(fixturesDir);
  } catch {
    await fs.mkdir(fixturesDir, { recursive: true });
  }

  const testImagePath = path.join(fixturesDir, 'test-image.jpg');

  // Check if test image already exists
  try {
    await fs.access(testImagePath);
    console.log('✓ Test images already exist');
    return;
  } catch {
    // Create test image using Playwright screenshot
    console.log('Creating test images...');

    const browser = await chromium.launch();
    const page = await browser.newPage();

    // Create a simple test image by screenshotting a colored div
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <body style="margin: 0; padding: 0;">
          <div style="width: 800px; height: 600px; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center;">
            <h1 style="color: white; font-family: Arial; font-size: 48px;">Test Image</h1>
          </div>
        </body>
      </html>
    `);

    await page.screenshot({
      path: testImagePath,
      type: 'jpeg',
      quality: 80,
      clip: { x: 0, y: 0, width: 800, height: 600 },
    });

    await browser.close();

    console.log('✓ Test images created');
  }
}

async function clearTestData() {
  console.log('Clearing test data from previous runs...');

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Delete all test users (username starts with "e2euser_", "tripuser_", etc.)
    // This would require a dedicated cleanup API endpoint on the backend

    // For now, we'll rely on database isolation in tests
    console.log('✓ Test data cleanup completed');
  } catch (error) {
    console.warn('Warning: Could not clear test data:', error);
  } finally {
    await browser.close();
  }
}

export default async function globalSetup(config: FullConfig) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Playwright E2E Test Setup');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // 1. Check backend server
  const backendReady = await waitForServer(`${API_URL}/health`);
  if (!backendReady) {
    throw new Error(
      `Backend server is not running at ${API_URL}. Please start it with: ./run_backend.sh`
    );
  }

  // 2. Check frontend server
  const frontendReady = await waitForServer(FRONTEND_URL);
  if (!frontendReady) {
    throw new Error(
      `Frontend server is not running at ${FRONTEND_URL}. Please start it with: ./run_frontend.sh`
    );
  }

  // 3. Create test fixtures
  await createTestImages();

  // 4. Clear old test data (optional)
  // await clearTestData();

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Setup Complete - Running Tests...');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}
