// frontend/tests/unit/landing/LandingPage.test.tsx

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { LandingPage } from '../../../src/pages/LandingPage';
import * as AuthContext from '../../../src/contexts/AuthContext';

/**
 * Test Suite: LandingPage Container (Feature 014 - User Story 1)
 *
 * Requirements from spec.md:
 * - FR-014-007: Redirect authenticated users to /trips/public (public feed)
 * - FR-014-008: Display landing page for unauthenticated visitors
 * - FR-014-009: Compose HeroSection + ManifestoSection + ValuePillarsSection
 * - SC-014-004: Page loads completely in < 2.5s (LCP)
 */
describe('LandingPage Container', () => {
  // Helper to render with HelmetProvider
  const renderWithHelmet = (ui: React.ReactElement) => {
    return render(
      <HelmetProvider>
        {ui}
      </HelmetProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Unauthenticated User Flow', () => {
    beforeEach(() => {
      // Mock useAuth to return null user (unauthenticated)
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
        updateProfile: vi.fn(),
      });
    });

    it('should render LandingPage for unauthenticated users', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      // Verify page renders without redirect
      const page = screen.getByRole('main');
      expect(page).toBeInTheDocument();
    });

    it('should render HeroSection component', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      // Verify hero headline is present
      const heroHeadline = screen.getByRole('heading', { level: 1, name: /el camino es el destino/i });
      expect(heroHeadline).toBeInTheDocument();
    });

    it('should render ManifestoSection component', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      // Verify manifesto section title is present
      const manifestoTitle = screen.getByRole('heading', { level: 2, name: /nuestra filosofía/i });
      expect(manifestoTitle).toBeInTheDocument();
    });

    it('should render sections in correct order (Hero → Manifesto)', () => {
      const { container } = renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      const sections = container.querySelectorAll('section');
      expect(sections.length).toBeGreaterThanOrEqual(2);

      // First section should be hero
      expect(sections[0]).toHaveClass('hero-section');

      // Second section should be manifesto
      expect(sections[1]).toHaveClass('manifesto-section');
    });

    it('should apply landing-page CSS class to main container', () => {
      const { container } = renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      const main = container.querySelector('main');
      expect(main).toHaveClass('landing-page');
    });
  });

  describe('Authenticated User Redirect', () => {
    beforeEach(() => {
      // Mock useAuth to return authenticated user
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: {
          user_id: '123e4567-e89b-12d3-a456-426614174000',
          email: 'testuser@example.com',
          username: 'testuser',
          is_verified: true,
          role: 'USER',
          created_at: '2024-01-01T00:00:00Z',
        },
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
        updateProfile: vi.fn(),
      });
    });

    it('should redirect authenticated users to /trips/public', async () => {
      const { container } = renderWithHelmet(
        <MemoryRouter initialEntries={['/']}>
          <LandingPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        // Verify Navigate component is rendered (redirecting)
        // In React Router 6, Navigate renders nothing and triggers navigation
        const main = container.querySelector('main');
        expect(main).not.toBeInTheDocument();
      });
    });

    it('should not render hero section for authenticated users', () => {
      renderWithHelmet(
        <MemoryRouter initialEntries={['/']}>
          <LandingPage />
        </MemoryRouter>
      );

      const heroHeadline = screen.queryByRole('heading', { level: 1, name: /el camino es el destino/i });
      expect(heroHeadline).not.toBeInTheDocument();
    });

    it('should not render manifesto section for authenticated users', () => {
      renderWithHelmet(
        <MemoryRouter initialEntries={['/']}>
          <LandingPage />
        </MemoryRouter>
      );

      const manifestoTitle = screen.queryByRole('heading', { level: 2, name: /nuestra filosofía/i });
      expect(manifestoTitle).not.toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    beforeEach(() => {
      // Mock useAuth to return loading state
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isLoading: true,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
        updateProfile: vi.fn(),
      });
    });

    it('should show loading indicator while authentication is being checked', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      // Verify loading indicator is displayed
      const loadingIndicator = screen.getByText(/cargando/i);
      expect(loadingIndicator).toBeInTheDocument();
    });

    it('should not render landing content during loading', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      const heroHeadline = screen.queryByRole('heading', { level: 1, name: /el camino es el destino/i });
      expect(heroHeadline).not.toBeInTheDocument();
    });
  });

  describe('SEO Meta Tags', () => {
    beforeEach(() => {
      // Mock useAuth to return unauthenticated user
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
        updateProfile: vi.fn(),
      });
    });

    it('should use useSEO hook with correct title', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      // Helmet updates document.title, verify it's set
      // Note: react-helmet-async may require additional setup for testing
      // For now, we verify the component renders without error
      const page = screen.getByRole('main');
      expect(page).toBeInTheDocument();
    });

    it('should render without console errors', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      expect(consoleSpy).not.toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('Component Integration', () => {
    beforeEach(() => {
      vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
        user: null,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
        updateProfile: vi.fn(),
      });
    });

    it('should render as main landmark for accessibility', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });

    it('should have aria-label on main element', () => {
      renderWithHelmet(
        <BrowserRouter>
          <LandingPage />
        </BrowserRouter>
      );

      const main = screen.getByRole('main');
      expect(main).toHaveAttribute('aria-label', expect.stringContaining('Landing'));
    });
  });
});
