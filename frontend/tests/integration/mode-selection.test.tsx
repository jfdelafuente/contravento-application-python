/**
 * Mode Selection Integration Tests
 *
 * End-to-end tests for trip creation mode selection flow (User Story 1).
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 3 (US1)
 * Task: T029
 *
 * Test Scenarios:
 * - User navigates to /trips/new → modal displays
 * - User selects "Con GPS" → navigates to /trips/new/gpx
 * - User selects "Sin GPS" → navigates to /trips/new/manual
 * - User presses ESC → navigates back to /trips
 * - User clicks overlay → navigates back to /trips
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../../src/App';

// Mock AuthContext to simulate authenticated user
vi.mock('../../src/contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    user: {
      user_id: 'test-user-123',
      username: 'testuser',
      email: 'test@example.com',
    },
    isAuthenticated: true,
    isLoading: false,
  }),
}));

// Mock page CSS imports
vi.mock('../../src/pages/TripCreateModePage.css', () => ({}));
vi.mock('../../src/pages/TripCreatePage.css', () => ({}));

describe('Mode Selection Integration Tests (T029)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('User Story 1: Mode Selection Flow', () => {
    it('should display mode selection modal when navigating to /trips/new', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        const heading = screen.getByRole('heading', {
          name: /¿cómo quieres crear tu viaje\?/i,
        });
        expect(heading).toBeInTheDocument();
      });

      // Verify both options are present
      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });

      expect(gpsButton).toBeInTheDocument();
      expect(manualButton).toBeInTheDocument();
    });

    it('should navigate to GPS wizard when "Con GPS" clicked', async () => {
      const { container } = render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /¿cómo quieres crear tu viaje\?/i })).toBeInTheDocument();
      });

      // Click "Con GPS" button
      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      fireEvent.click(gpsButton);

      // Wait for navigation to /trips/new/gpx
      await waitFor(() => {
        // GPXTripCreatePage placeholder should render
        expect(screen.getByText(/gps trip creation wizard/i)).toBeInTheDocument();
        expect(screen.getByText(/placeholder for phase 4/i)).toBeInTheDocument();
      });
    });

    it('should navigate to manual form when "Sin GPS" clicked', async () => {
      const { container } = render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /¿cómo quieres crear tu viaje\?/i })).toBeInTheDocument();
      });

      // Click "Sin GPS" button
      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });
      fireEvent.click(manualButton);

      // Wait for navigation to /trips/new/manual
      // TripCreatePage should render (mocked in this test, but verified by route)
      await waitFor(
        () => {
          // Modal should be gone
          const modal = screen.queryByRole('dialog');
          expect(modal).not.toBeInTheDocument();
        },
        { timeout: 2000 }
      );
    });
  });

  describe('Modal Dismissal', () => {
    it('should navigate back when ESC key pressed', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(modal).toBeInTheDocument();
      });

      // Press ESC key
      const modal = screen.getByRole('dialog');
      fireEvent.keyDown(modal, { key: 'Escape', code: 'Escape' });

      // Wait for navigation away from modal
      await waitFor(
        () => {
          // Modal should be dismissed (navigated away)
          const modalAfterDismiss = screen.queryByRole('dialog');
          expect(modalAfterDismiss).not.toBeInTheDocument();
        },
        { timeout: 2000 }
      );
    });

    it('should navigate back when overlay clicked', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(modal).toBeInTheDocument();
      });

      // Click overlay (parent of modal)
      const modal = screen.getByRole('dialog');
      const overlay = modal.parentElement;
      expect(overlay).toBeInTheDocument();

      fireEvent.click(overlay!);

      // Wait for navigation away from modal
      await waitFor(
        () => {
          const modalAfterDismiss = screen.queryByRole('dialog');
          expect(modalAfterDismiss).not.toBeInTheDocument();
        },
        { timeout: 2000 }
      );
    });

    it('should NOT dismiss when modal content clicked', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(modal).toBeInTheDocument();
      });

      // Click modal content (not overlay)
      const modal = screen.getByRole('dialog');
      fireEvent.click(modal);

      // Modal should still be visible
      await waitFor(() => {
        const modalAfterClick = screen.getByRole('dialog');
        expect(modalAfterClick).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should support keyboard navigation between options', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /¿cómo quieres crear tu viaje\?/i })).toBeInTheDocument();
      });

      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });

      // Tab to first button
      gpsButton.focus();
      expect(gpsButton).toHaveFocus();

      // Tab to second button
      manualButton.focus();
      expect(manualButton).toHaveFocus();

      // Enter key should trigger navigation
      fireEvent.keyDown(manualButton, { key: 'Enter', code: 'Enter' });

      await waitFor(
        () => {
          // Should navigate (modal dismissed)
          const modal = screen.queryByRole('dialog');
          expect(modal).not.toBeInTheDocument();
        },
        { timeout: 2000 }
      );
    });

    it('should have proper ARIA attributes', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for modal to render
      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(modal).toBeInTheDocument();
      });

      const modal = screen.getByRole('dialog');

      // Check ARIA attributes
      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby');
    });
  });
});
