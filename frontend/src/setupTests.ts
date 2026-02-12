/**
 * Test Setup File
 *
 * Global test configuration and mocks for Vitest + React Testing Library
 */

import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Cleanup after each test case
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia for responsive design tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock Fullscreen API with getter/setter for tests
let _fullscreenElement: Element | null = null;

Object.defineProperty(document, 'fullscreenElement', {
  get: () => _fullscreenElement,
  configurable: true,
});

// Helper to set fullscreen element in tests
(globalThis as any).setFullscreenElement = (element: Element | null) => {
  _fullscreenElement = element;
};

Object.defineProperty(document, 'exitFullscreen', {
  writable: true,
  configurable: true,
  value: vi.fn().mockImplementation(() => {
    _fullscreenElement = null;
    document.dispatchEvent(new Event('fullscreenchange'));
    return Promise.resolve();
  }),
});

Object.defineProperty(HTMLElement.prototype, 'requestFullscreen', {
  writable: true,
  configurable: true,
  value: vi.fn().mockImplementation(function(this: HTMLElement) {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    _fullscreenElement = this;
    document.dispatchEvent(new Event('fullscreenchange'));
    return Promise.resolve();
  }),
});

// Mock IntersectionObserver
globalThis.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;

// Mock ResizeObserver
globalThis.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any;
