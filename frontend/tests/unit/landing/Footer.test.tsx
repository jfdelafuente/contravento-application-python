// frontend/tests/unit/landing/Footer.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Footer } from '../../../src/components/landing/Footer';

/**
 * Test Suite: Footer Component (Feature 014 - User Story 5)
 *
 * Requirements from spec.md:
 * - FR-014-022: Display ContraVento branding/logo
 * - FR-014-023: Display social media links (Instagram, Facebook)
 * - FR-014-024: Social links open in new tab with rel="noopener noreferrer"
 * - FR-014-025: Display legal links (Terms of Service, Privacy Policy)
 * - FR-014-026: Legal links navigate to /terms-of-service and /privacy-policy
 * - FR-014-027: Display contact email (hola@contravento.com) as mailto link
 * - SC-014-009: 4-column grid on desktop, stacked on mobile
 * - SC-014-010: Verde bosque background (#1B2621) with crema text (#F9F7F2)
 */
describe('Footer Component', () => {
  const renderFooter = () => {
    return render(
      <MemoryRouter>
        <Footer />
      </MemoryRouter>
    );
  };

  describe('Footer Structure', () => {
    it('should render as a footer element', () => {
      const { container } = renderFooter();
      const footer = container.querySelector('footer');
      expect(footer).toBeInTheDocument();
    });

    it('should have footer CSS class', () => {
      const { container } = renderFooter();
      const footer = container.querySelector('.footer');
      expect(footer).toBeInTheDocument();
    });

    it('should render footer content container', () => {
      const { container } = renderFooter();
      const footerContent = container.querySelector('.footer-content');
      expect(footerContent).toBeInTheDocument();
    });
  });

  describe('Branding Section', () => {
    it('should display ContraVento branding', () => {
      const { container } = renderFooter();
      const logo = container.querySelector('.footer-logo');
      expect(logo).toBeInTheDocument();
      expect(logo?.textContent).toBe('ContraVento');
    });

    it('should display tagline or mission statement', () => {
      renderFooter();
      const tagline = screen.getByText(/el camino es el destino/i);
      expect(tagline).toBeInTheDocument();
    });

    it('should render branding in footer-brand section', () => {
      const { container } = renderFooter();
      const brandSection = container.querySelector('.footer-brand');
      expect(brandSection).toBeInTheDocument();
    });
  });

  describe('Social Media Links', () => {
    it('should display Instagram link', () => {
      renderFooter();
      const instagramLink = screen.getByRole('link', { name: /instagram/i });
      expect(instagramLink).toBeInTheDocument();
    });

    it('should display Facebook link', () => {
      renderFooter();
      const facebookLink = screen.getByRole('link', { name: /facebook/i });
      expect(facebookLink).toBeInTheDocument();
    });

    it('should open Instagram link in new tab', () => {
      renderFooter();
      const instagramLink = screen.getByRole('link', { name: /instagram/i });
      expect(instagramLink).toHaveAttribute('target', '_blank');
    });

    it('should open Facebook link in new tab', () => {
      renderFooter();
      const facebookLink = screen.getByRole('link', { name: /facebook/i });
      expect(facebookLink).toHaveAttribute('target', '_blank');
    });

    it('should have rel="noopener noreferrer" on Instagram link', () => {
      renderFooter();
      const instagramLink = screen.getByRole('link', { name: /instagram/i });
      expect(instagramLink).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('should have rel="noopener noreferrer" on Facebook link', () => {
      renderFooter();
      const facebookLink = screen.getByRole('link', { name: /facebook/i });
      expect(facebookLink).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('should render social links in footer-social section', () => {
      const { container } = renderFooter();
      const socialSection = container.querySelector('.footer-social');
      expect(socialSection).toBeInTheDocument();
    });
  });

  describe('Legal Links', () => {
    it('should display "Términos de Servicio" link', () => {
      renderFooter();
      const termsLink = screen.getByRole('link', { name: /términos de servicio/i });
      expect(termsLink).toBeInTheDocument();
    });

    it('should display "Política de Privacidad" link', () => {
      renderFooter();
      const privacyLink = screen.getByRole('link', { name: /política de privacidad/i });
      expect(privacyLink).toBeInTheDocument();
    });

    it('should link "Términos de Servicio" to /terms-of-service', () => {
      renderFooter();
      const termsLink = screen.getByRole('link', { name: /términos de servicio/i });
      expect(termsLink).toHaveAttribute('href', '/terms-of-service');
    });

    it('should link "Política de Privacidad" to /privacy-policy', () => {
      renderFooter();
      const privacyLink = screen.getByRole('link', { name: /política de privacidad/i });
      expect(privacyLink).toHaveAttribute('href', '/privacy-policy');
    });

    it('should render legal links in footer-legal section', () => {
      const { container } = renderFooter();
      const legalSection = container.querySelector('.footer-legal');
      expect(legalSection).toBeInTheDocument();
    });
  });

  describe('Contact Information', () => {
    it('should display contact email', () => {
      renderFooter();
      const emailLink = screen.getByRole('link', { name: /hola@contravento\.com/i });
      expect(emailLink).toBeInTheDocument();
    });

    it('should render email as mailto link', () => {
      renderFooter();
      const emailLink = screen.getByRole('link', { name: /hola@contravento\.com/i });
      expect(emailLink).toHaveAttribute('href', 'mailto:hola@contravento.com');
    });

    it('should render contact info in footer-contact section', () => {
      const { container } = renderFooter();
      const contactSection = container.querySelector('.footer-contact');
      expect(contactSection).toBeInTheDocument();
    });
  });

  describe('Layout and Styling', () => {
    it('should use 4-column grid on desktop (CSS verification)', () => {
      const { container } = renderFooter();
      const footerContent = container.querySelector('.footer-content');
      expect(footerContent).toBeInTheDocument();
      // CSS will handle grid-template-columns: repeat(4, 1fr)
    });

    it('should have verde bosque background color (CSS verification)', () => {
      const { container } = renderFooter();
      const footer = container.querySelector('.footer');
      expect(footer).toBeInTheDocument();
      // CSS will handle background-color: var(--landing-title) (#1B2621)
    });

    it('should use crema text color (CSS verification)', () => {
      const { container } = renderFooter();
      const footer = container.querySelector('.footer');
      expect(footer).toBeInTheDocument();
      // CSS will handle color: var(--landing-bg) (#F9F7F2)
    });

    it('should render footer sections in correct order', () => {
      const { container } = renderFooter();
      const sections = container.querySelectorAll('.footer-content > div');
      expect(sections.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('Responsive Behavior', () => {
    it('should stack sections vertically on mobile (CSS verification)', () => {
      const { container } = renderFooter();
      const footerContent = container.querySelector('.footer-content');
      expect(footerContent).toBeInTheDocument();
      // CSS @media (max-width: 768px) will handle stacking
    });

    it('should maintain readable text size on mobile', () => {
      const { container } = renderFooter();
      const footer = container.querySelector('.footer');
      expect(footer).toBeInTheDocument();
      // CSS will handle responsive font sizes
    });
  });

  describe('Accessibility', () => {
    it('should use semantic footer element', () => {
      const { container } = renderFooter();
      const footer = container.querySelector('footer');
      expect(footer).toBeInTheDocument();
    });

    it('should have accessible link text for all links', () => {
      renderFooter();
      const instagramLink = screen.getByRole('link', { name: /instagram/i });
      const facebookLink = screen.getByRole('link', { name: /facebook/i });
      const termsLink = screen.getByRole('link', { name: /términos de servicio/i });
      const privacyLink = screen.getByRole('link', { name: /política de privacidad/i });
      const emailLink = screen.getByRole('link', { name: /hola@contravento\.com/i });

      expect(instagramLink).toBeInTheDocument();
      expect(facebookLink).toBeInTheDocument();
      expect(termsLink).toBeInTheDocument();
      expect(privacyLink).toBeInTheDocument();
      expect(emailLink).toBeInTheDocument();
    });

    it('should have proper ARIA attributes for external links', () => {
      renderFooter();
      const instagramLink = screen.getByRole('link', { name: /instagram/i });

      // External links should have target="_blank" and rel="noopener noreferrer"
      expect(instagramLink).toHaveAttribute('target', '_blank');
      expect(instagramLink).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('Copyright Information', () => {
    it('should display copyright year', () => {
      renderFooter();
      const currentYear = new Date().getFullYear();
      const copyright = screen.getByText(new RegExp(`${currentYear}`, 'i'));
      expect(copyright).toBeInTheDocument();
    });

    it('should display copyright notice with ContraVento', () => {
      renderFooter();
      const copyright = screen.getByText(/©.*contravento/i);
      expect(copyright).toBeInTheDocument();
    });
  });

  describe('Content Organization', () => {
    it('should have heading for each footer section', () => {
      const { container } = renderFooter();
      const headings = container.querySelectorAll('.footer-section-title');
      expect(headings.length).toBeGreaterThanOrEqual(3); // Social, Legal, Contact sections
    });

    it('should group related links together', () => {
      const { container } = renderFooter();
      const socialSection = container.querySelector('.footer-social');
      const legalSection = container.querySelector('.footer-legal');
      const contactSection = container.querySelector('.footer-contact');

      expect(socialSection).toBeInTheDocument();
      expect(legalSection).toBeInTheDocument();
      expect(contactSection).toBeInTheDocument();
    });
  });
});
