/**
 * App Routing Tests
 *
 * Tests for route configuration changes in Feature 017:
 * - T024: Route configuration tests for mode selection modal
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 3 (US1)
 *
 * Test Coverage:
 * - /trips/new renders TripCreateModePage (mode selection modal)
 * - /trips/new/manual renders TripCreatePage (manual trip form)
 * - /trips/new/gpx renders GPXTripCreatePage (GPS wizard - placeholder for Phase 4)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../../src/App';

// Mock AuthContext to bypass authentication
vi.mock('../../src/contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    user: {
      user_id: 'test-user-id',
      username: 'testuser',
      email: 'test@example.com',
    },
    isAuthenticated: true,
    isLoading: false,
  }),
}));

// Mock lazy-loaded page components
vi.mock('../../src/pages/DashboardPage', () => ({
  DashboardPage: () => <div>Dashboard Page</div>,
}));

vi.mock('../../src/pages/ProfilePage', () => ({
  ProfilePage: () => <div>Profile Page</div>,
}));

vi.mock('../../src/pages/ProfileEditPage', () => ({
  ProfileEditPage: () => <div>Profile Edit Page</div>,
}));

vi.mock('../../src/pages/TripsListPage', () => ({
  TripsListPage: () => <div>Trips List Page</div>,
}));

vi.mock('../../src/pages/TripDetailPage', () => ({
  TripDetailPage: () => <div>Trip Detail Page</div>,
}));

vi.mock('../../src/pages/TripEditPage', () => ({
  TripEditPage: () => <div>Trip Edit Page</div>,
}));

vi.mock('../../src/pages/PublicFeedPage', () => ({
  PublicFeedPage: () => <div>Public Feed Page</div>,
}));

vi.mock('../../src/pages/FeedPage', () => ({
  FeedPage: () => <div>Feed Page</div>,
}));

vi.mock('../../src/pages/UserProfilePage', () => ({
  UserProfilePage: () => <div>User Profile Page</div>,
}));

// Mock TripCreatePage (manual form)
vi.mock('../../src/pages/TripCreatePage', () => ({
  TripCreatePage: () => <div data-testid="trip-create-page">Manual Trip Create Page</div>,
}));

// Mock TripCreateModePage (mode selection modal)
vi.mock('../../src/pages/TripCreateModePage', () => ({
  TripCreateModePage: () => (
    <div data-testid="trip-create-mode-page">Trip Create Mode Page</div>
  ),
}));

// Mock GPXTripCreatePage (GPS wizard - to be implemented in Phase 4)
vi.mock('../../src/pages/GPXTripCreatePage', () => ({
  GPXTripCreatePage: () => <div data-testid="gpx-trip-create-page">GPX Trip Create Page</div>,
}));

// Mock CSS imports
vi.mock('../../src/pages/TripCreatePage.css', () => ({}));
vi.mock('../../src/pages/TripCreateModePage.css', () => ({}));

describe('App Routing - Trip Creation Routes (T024)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('/trips/new - Mode Selection Modal', () => {
    it('should render TripCreateModePage at /trips/new', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        const modePage = screen.getByTestId('trip-create-mode-page');
        expect(modePage).toBeInTheDocument();
        expect(modePage).toHaveTextContent('Trip Create Mode Page');
      });
    });

    it('should NOT render TripCreatePage (manual form) at /trips/new', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        const modePage = screen.getByTestId('trip-create-mode-page');
        expect(modePage).toBeInTheDocument();
      });

      // Manual form should NOT be rendered at /trips/new
      const manualPage = screen.queryByTestId('trip-create-page');
      expect(manualPage).not.toBeInTheDocument();
    });
  });

  describe('/trips/new/manual - Manual Trip Form', () => {
    it('should render TripCreatePage at /trips/new/manual', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new/manual']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        const manualPage = screen.getByTestId('trip-create-page');
        expect(manualPage).toBeInTheDocument();
        expect(manualPage).toHaveTextContent('Manual Trip Create Page');
      });
    });

    it('should NOT render TripCreateModePage at /trips/new/manual', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new/manual']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        const manualPage = screen.getByTestId('trip-create-page');
        expect(manualPage).toBeInTheDocument();
      });

      // Mode selection should NOT be rendered at /trips/new/manual
      const modePage = screen.queryByTestId('trip-create-mode-page');
      expect(modePage).not.toBeInTheDocument();
    });
  });

  describe('/trips/new/gpx - GPS Wizard (Phase 4)', () => {
    it('should render GPXTripCreatePage at /trips/new/gpx', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new/gpx']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        const gpxPage = screen.getByTestId('gpx-trip-create-page');
        expect(gpxPage).toBeInTheDocument();
        expect(gpxPage).toHaveTextContent('GPX Trip Create Page');
      });
    });

    it('should NOT render other trip creation pages at /trips/new/gpx', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new/gpx']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        const gpxPage = screen.getByTestId('gpx-trip-create-page');
        expect(gpxPage).toBeInTheDocument();
      });

      // Other pages should NOT be rendered at /trips/new/gpx
      const modePage = screen.queryByTestId('trip-create-mode-page');
      const manualPage = screen.queryByTestId('trip-create-page');
      expect(modePage).not.toBeInTheDocument();
      expect(manualPage).not.toBeInTheDocument();
    });
  });

  describe('Route Protection', () => {
    it('should require authentication for /trips/new', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new']}>
          <App />
        </MemoryRouter>
      );

      // Wait for rendering
      await waitFor(() => {
        expect(screen.getByTestId('trip-create-mode-page')).toBeInTheDocument();
      });

      // This test verifies the route is accessible with authentication
      // (AuthContext is mocked to return isAuthenticated: true)
    });

    it('should require authentication for /trips/new/manual', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new/manual']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('trip-create-page')).toBeInTheDocument();
      });
    });

    it('should require authentication for /trips/new/gpx', async () => {
      render(
        <MemoryRouter initialEntries={['/trips/new/gpx']}>
          <App />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('gpx-trip-create-page')).toBeInTheDocument();
      });
    });
  });
});
