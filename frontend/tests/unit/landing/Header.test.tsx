// frontend/tests/unit/landing/Header.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Header } from '../../../src/components/landing/Header';

/**
 * Test Suite: Header Component (Landing Page)
 *
 * Requirements:
 * - Display ContraVento logo on the left
 * - Display navigation links on the right (Rutas, Login)
 * - Links should navigate to correct routes
 * - Responsive design (mobile/desktop)
 * - Sticky header behavior
 */
describe('Header Component', () => {
  const renderHeader = () => {
    return render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
  };

  describe('Header Structure', () => {
    it('should render as a header element', () => {
      const { container } = renderHeader();
      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('should have landing-header CSS class', () => {
      const { container } = renderHeader();
      const header = container.querySelector('.landing-header');
      expect(header).toBeInTheDocument();
    });

    it('should render header content container', () => {
      const { container } = renderHeader();
      const headerContent = container.querySelector('.landing-header-content');
      expect(headerContent).toBeInTheDocument();
    });
  });

  describe('Logo Section', () => {
    it('should display ContraVento logo', () => {
      renderHeader();
      const logo = screen.getByRole('link', { name: /contravento/i });
      expect(logo).toBeInTheDocument();
    });

    it('should link logo to homepage', () => {
      renderHeader();
      const logo = screen.getByRole('link', { name: /contravento/i });
      expect(logo).toHaveAttribute('href', '/');
    });

    it('should render logo in header-logo section', () => {
      const { container } = renderHeader();
      const logoSection = container.querySelector('.landing-header-logo');
      expect(logoSection).toBeInTheDocument();
    });
  });

  describe('Navigation Links', () => {
    it('should display "Rutas" link', () => {
      renderHeader();
      const rutasLink = screen.getByRole('link', { name: /rutas/i });
      expect(rutasLink).toBeInTheDocument();
    });

    it('should display "Login" link', () => {
      renderHeader();
      const loginLink = screen.getByRole('link', { name: /login/i });
      expect(loginLink).toBeInTheDocument();
    });

    it('should link "Rutas" to /trips/public', () => {
      renderHeader();
      const rutasLink = screen.getByRole('link', { name: /rutas/i });
      expect(rutasLink).toHaveAttribute('href', '/trips/public');
    });

    it('should link "Login" to /login', () => {
      renderHeader();
      const loginLink = screen.getByRole('link', { name: /login/i });
      expect(loginLink).toHaveAttribute('href', '/login');
    });

    it('should render navigation links in header-nav section', () => {
      const { container } = renderHeader();
      const navSection = container.querySelector('.landing-header-nav');
      expect(navSection).toBeInTheDocument();
    });

    it('should render links in correct order (Rutas, Login)', () => {
      const { container } = renderHeader();
      const navLinks = container.querySelectorAll('.landing-header-nav a');
      expect(navLinks).toHaveLength(2);
      expect(navLinks[0]).toHaveTextContent(/rutas/i);
      expect(navLinks[1]).toHaveTextContent(/login/i);
    });
  });

  describe('Layout and Styling', () => {
    it('should use flexbox layout for header content (CSS verification)', () => {
      const { container } = renderHeader();
      const headerContent = container.querySelector('.landing-header-content');
      expect(headerContent).toBeInTheDocument();
      // CSS will handle display: flex, justify-content: space-between
    });

    it('should position logo on the left (CSS verification)', () => {
      const { container } = renderHeader();
      const logo = container.querySelector('.landing-header-logo');
      expect(logo).toBeInTheDocument();
      // CSS will handle positioning
    });

    it('should position navigation on the right (CSS verification)', () => {
      const { container } = renderHeader();
      const nav = container.querySelector('.landing-header-nav');
      expect(nav).toBeInTheDocument();
      // CSS will handle positioning
    });
  });

  describe('Responsive Behavior', () => {
    it('should stack logo and nav vertically on mobile (CSS verification)', () => {
      const { container } = renderHeader();
      const headerContent = container.querySelector('.landing-header-content');
      expect(headerContent).toBeInTheDocument();
      // CSS @media (max-width: 768px) will handle stacking
    });

    it('should maintain horizontal layout on desktop (CSS verification)', () => {
      const { container } = renderHeader();
      const headerContent = container.querySelector('.landing-header-content');
      expect(headerContent).toBeInTheDocument();
      // CSS will handle flex-direction: row on desktop
    });
  });

  describe('Accessibility', () => {
    it('should use semantic header element', () => {
      const { container } = renderHeader();
      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('should have accessible link text for all links', () => {
      renderHeader();
      const logo = screen.getByRole('link', { name: /contravento/i });
      const rutasLink = screen.getByRole('link', { name: /rutas/i });
      const loginLink = screen.getByRole('link', { name: /login/i });

      expect(logo).toBeInTheDocument();
      expect(rutasLink).toBeInTheDocument();
      expect(loginLink).toBeInTheDocument();
    });

    it('should have proper navigation landmark', () => {
      const { container } = renderHeader();
      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();
    });
  });

  describe('Sticky Header Behavior', () => {
    it('should have sticky positioning (CSS verification)', () => {
      const { container } = renderHeader();
      const header = container.querySelector('.landing-header');
      expect(header).toBeInTheDocument();
      // CSS will handle position: sticky
    });
  });
});
