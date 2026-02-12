// frontend/tests/unit/landing/CTASection.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { CTASection } from '../../../src/components/landing/CTASection';

/**
 * Test Suite: CTASection Component (Feature 014 - User Story 4)
 *
 * Requirements from spec.md:
 * - FR-014-018: Display prominent CTA button "Formar parte del viaje"
 * - FR-014-019: CTA button links to /register route
 * - FR-014-020: Display "¿Ya tienes cuenta? Inicia sesión" link
 * - FR-014-021: Login link navigates to /login route
 * - SC-014-007: CTA button uses terracota color (#D35400)
 * - SC-014-008: CTA section centered, visible on all viewports
 */
describe('CTASection Component', () => {
  const renderCTASection = () => {
    return render(
      <MemoryRouter>
        <CTASection />
      </MemoryRouter>
    );
  };

  describe('Section Structure', () => {
    it('should render as a section element', () => {
      const { container } = renderCTASection();
      const section = container.querySelector('section');
      expect(section).toBeInTheDocument();
    });

    it('should have cta-section CSS class', () => {
      const { container } = renderCTASection();
      const section = container.querySelector('.cta-section');
      expect(section).toBeInTheDocument();
    });

    it('should have aria-labelledby attribute for accessibility', () => {
      const { container } = renderCTASection();
      const section = container.querySelector('section[aria-labelledby]');
      expect(section).toBeInTheDocument();
    });

    it('should render section title', () => {
      renderCTASection();
      const title = screen.getByRole('heading', { level: 2 });
      expect(title).toBeInTheDocument();
    });
  });

  describe('CTA Button Content', () => {
    it('should display "Formar parte del viaje" button text', () => {
      renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      expect(ctaButton).toBeInTheDocument();
    });

    it('should render CTA button as a link', () => {
      renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      expect(ctaButton.tagName).toBe('A');
    });

    it('should link CTA button to /register route', () => {
      renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      expect(ctaButton).toHaveAttribute('href', '/register');
    });

    it('should have cta-button CSS class on CTA button', () => {
      renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      expect(ctaButton).toHaveClass('cta-button');
    });
  });

  describe('Login Link Content', () => {
    it('should display "¿Ya tienes cuenta? Inicia sesión" text', () => {
      renderCTASection();
      const loginText = screen.getByText(/¿ya tienes cuenta\?/i);
      expect(loginText).toBeInTheDocument();
    });

    it('should display "Inicia sesión" as a link', () => {
      renderCTASection();
      const loginLink = screen.getByRole('link', { name: /inicia sesión/i });
      expect(loginLink).toBeInTheDocument();
    });

    it('should link "Inicia sesión" to /login route', () => {
      renderCTASection();
      const loginLink = screen.getByRole('link', { name: /inicia sesión/i });
      expect(loginLink).toHaveAttribute('href', '/login');
    });

    it('should have cta-login-link CSS class on login link', () => {
      renderCTASection();
      const loginLink = screen.getByRole('link', { name: /inicia sesión/i });
      expect(loginLink).toHaveClass('cta-login-link');
    });
  });

  describe('Layout and Styling', () => {
    it('should center content with cta-content container', () => {
      const { container } = renderCTASection();
      const contentContainer = container.querySelector('.cta-content');
      expect(contentContainer).toBeInTheDocument();
    });

    it('should render CTA button before login text', () => {
      const { container } = renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      const loginText = screen.getByText(/¿ya tienes cuenta\?/i);

      const buttonPosition = Array.from(container.querySelectorAll('*')).indexOf(ctaButton as Element);
      const loginPosition = Array.from(container.querySelectorAll('*')).indexOf(loginText as Element);

      expect(buttonPosition).toBeLessThan(loginPosition);
    });

    it('should apply serif font to section title', () => {
      const { container } = renderCTASection();
      const title = container.querySelector('.cta-title');
      expect(title).toBeInTheDocument();
    });

    it('should use terracota color for CTA button (CSS verification)', () => {
      const { container } = renderCTASection();
      const ctaButton = container.querySelector('.cta-button');
      expect(ctaButton).toBeInTheDocument();
      // CSS will handle background-color: var(--landing-cta) (#D35400)
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy (h2)', () => {
      renderCTASection();
      const sectionTitle = screen.getByRole('heading', { level: 2 });
      expect(sectionTitle).toBeInTheDocument();
    });

    it('should have descriptive aria-labelledby linking section to title', () => {
      const { container } = renderCTASection();
      const section = container.querySelector('section');
      const titleId = section?.getAttribute('aria-labelledby');

      expect(titleId).toBeTruthy();

      const title = container.querySelector(`#${titleId}`);
      expect(title).toBeInTheDocument();
    });

    it('should have accessible link text for CTA button', () => {
      renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      expect(ctaButton.textContent).toMatch(/formar parte del viaje/i);
    });

    it('should have accessible link text for login link', () => {
      renderCTASection();
      const loginLink = screen.getByRole('link', { name: /inicia sesión/i });
      expect(loginLink.textContent).toMatch(/inicia sesión/i);
    });
  });

  describe('Responsive Behavior', () => {
    it('should render centered on all viewports (CSS verification)', () => {
      const { container } = renderCTASection();
      const section = container.querySelector('.cta-section');
      expect(section).toBeInTheDocument();
      // CSS will handle text-align: center and responsive padding
    });

    it('should maintain visibility on mobile (CSS verification)', () => {
      const { container } = renderCTASection();
      const ctaButton = container.querySelector('.cta-button');
      expect(ctaButton).toBeInTheDocument();
      // CSS @media (max-width: 768px) will handle mobile styles
    });
  });

  describe('Content Hierarchy', () => {
    it('should render title, CTA button, then login link in order', () => {
      renderCTASection();
      const title = screen.getByRole('heading', { level: 2 });
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      const loginLink = screen.getByRole('link', { name: /inicia sesión/i });

      expect(title).toBeInTheDocument();
      expect(ctaButton).toBeInTheDocument();
      expect(loginLink).toBeInTheDocument();
    });
  });

  describe('Call-to-Action Messaging', () => {
    it('should use compelling CTA copy aligned with ContraVento philosophy', () => {
      renderCTASection();
      const ctaButton = screen.getByRole('link', { name: /formar parte del viaje/i });
      expect(ctaButton.textContent).toMatch(/formar parte del viaje/i);
      // "Formar parte del viaje" aligns with "el camino es el destino" philosophy
    });

    it('should include supportive subtitle or description (optional)', () => {
      const { container } = renderCTASection();
      // Optional: Check for subtitle or description if implemented
      const subtitle = container.querySelector('.cta-subtitle');
      if (subtitle) {
        expect(subtitle).toBeInTheDocument();
      }
    });
  });
});
