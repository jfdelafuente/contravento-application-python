/**
 * TripCreateModePage Unit Tests
 *
 * Tests for mode selection modal (User Story 1):
 * - T021: Component tests for TripCreateModePage
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 3
 *
 * Test Coverage:
 * - Modal renders with two mode options
 * - "Con GPS" button navigates to /trips/new/gpx
 * - "Sin GPS" button navigates to /trips/new/manual
 * - ESC key closes modal and navigates back
 * - Overlay click closes modal and navigates back
 * - Accessibility: ARIA labels, keyboard navigation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { BrowserRouter } from 'react-router-dom';
import { TripCreateModePage } from '../../src/pages/TripCreateModePage';

// Mock navigate function
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock TripCreateModePage CSS
vi.mock('../../src/pages/TripCreateModePage.css', () => ({}));

// Wrapper component for router context
const RouterWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('TripCreateModePage - Mode Selection (T021)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Modal Rendering', () => {
    it('should render modal overlay with heading', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      // Check modal overlay
      const modalOverlay = screen.getByRole('dialog');
      expect(modalOverlay).toBeInTheDocument();
      expect(modalOverlay).toHaveAttribute('aria-modal', 'true');

      // Check heading
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
      expect(heading).toHaveTextContent(/¿cómo quieres crear tu viaje\?/i);
    });

    it('should render two mode selection options', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      // Check "Con GPS" option
      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      expect(gpsButton).toBeInTheDocument();

      // Check "Sin GPS" option
      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });
      expect(manualButton).toBeInTheDocument();
    });

    it('should display descriptive text for each mode', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      // GPS mode description
      expect(screen.getByText(/sube un archivo gpx/i)).toBeInTheDocument();

      // Manual mode description
      expect(screen.getByText(/ingresa manualmente/i)).toBeInTheDocument();
    });
  });

  describe('Navigation - GPS Mode (AS1.2)', () => {
    it('should navigate to /trips/new/gpx when "Con GPS" clicked', async () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      fireEvent.click(gpsButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/trips/new/gpx');
        expect(mockNavigate).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Navigation - Manual Mode (AS1.3)', () => {
    it('should navigate to /trips/new/manual when "Sin GPS" clicked', async () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });
      fireEvent.click(manualButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/trips/new/manual');
        expect(mockNavigate).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Modal Dismissal (AS1.4)', () => {
    it('should navigate back when ESC key pressed', async () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const modal = screen.getByRole('dialog');
      fireEvent.keyDown(modal, { key: 'Escape', code: 'Escape' });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/trips');
        expect(mockNavigate).toHaveBeenCalledTimes(1);
      });
    });

    it('should navigate back when overlay clicked', async () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const modalOverlay = screen.getByRole('dialog').parentElement;
      expect(modalOverlay).toBeInTheDocument();

      // Click overlay (not modal content)
      fireEvent.click(modalOverlay!);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/trips');
        expect(mockNavigate).toHaveBeenCalledTimes(1);
      });
    });

    it('should NOT dismiss when modal content clicked', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const modalContent = screen.getByRole('dialog');
      fireEvent.click(modalContent);

      // Should not navigate
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility (WCAG 2.1 AA)', () => {
    it('should have proper ARIA attributes on modal', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby');
    });

    it('should have descriptive button labels', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });

      expect(gpsButton).toHaveAccessibleName();
      expect(manualButton).toHaveAccessibleName();
    });

    it('should support keyboard navigation', async () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

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

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/trips/new/manual');
      });
    });
  });

  describe('Modal Display Order (AS1.1)', () => {
    it('should display "Con GPS" option first (left/top position)', () => {
      render(
        <RouterWrapper>
          <TripCreateModePage />
        </RouterWrapper>
      );

      const buttons = screen.getAllByRole('button');
      const gpsButton = screen.getByRole('button', { name: /crear viaje con gps/i });
      const manualButton = screen.getByRole('button', { name: /crear viaje sin gps/i });

      // GPS button should appear before manual button in DOM
      const gpsIndex = buttons.indexOf(gpsButton);
      const manualIndex = buttons.indexOf(manualButton);

      expect(gpsIndex).toBeLessThan(manualIndex);
    });
  });
});
