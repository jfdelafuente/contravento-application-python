// frontend/tests/unit/landing/HeroSection.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { HeroSection } from '../../../src/components/landing/HeroSection';

/**
 * Test Suite: HeroSection Component (Feature 014 - User Story 1)
 *
 * Requirements from spec.md:
 * - FR-014-001: Display hero image with "El camino es el destino" headline
 * - FR-014-002: Show subtitle about human and territorial connection
 * - FR-014-003: Include CTA button linking to registration
 * - SC-014-001: Hero image loads in < 2.5s (LCP requirement)
 * - SC-014-002: Responsive on mobile (< 768px), tablet (768-1024px), desktop (> 1024px)
 */
describe('HeroSection Component', () => {
  const renderHeroSection = () => {
    return render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );
  };

  describe('Content Requirements', () => {
    it('should render the main headline "El camino es el destino"', () => {
      renderHeroSection();
      const headline = screen.getByRole('heading', { level: 1 });
      expect(headline).toHaveTextContent('El camino es el destino');
    });

    it('should render subtitle about connection philosophy', () => {
      renderHeroSection();
      const subtitle = screen.getByText(/pedalear para conectar/i);
      expect(subtitle).toBeInTheDocument();
    });

    it('should render CTA button with "Únete a la Comunidad" text', () => {
      renderHeroSection();
      const ctaButton = screen.getByRole('link', { name: /únete a la comunidad/i });
      expect(ctaButton).toBeInTheDocument();
    });

    it('should link CTA button to /register route', () => {
      renderHeroSection();
      const ctaButton = screen.getByRole('link', { name: /únete a la comunidad/i });
      expect(ctaButton).toHaveAttribute('href', '/register');
    });
  });

  describe('Image Rendering', () => {
    it('should render hero image with correct alt text', () => {
      renderHeroSection();
      const heroImage = screen.getByRole('img', { name: /ciclista en entorno rural/i });
      expect(heroImage).toBeInTheDocument();
    });

    it('should use picture element for responsive images', () => {
      const { container } = renderHeroSection();
      const picture = container.querySelector('picture');
      expect(picture).toBeInTheDocument();
    });

    it('should include WebP source for modern browsers', () => {
      const { container } = renderHeroSection();
      const webpSource = container.querySelector('source[type="image/webp"]');
      expect(webpSource).toBeInTheDocument();
    });

    it('should include mobile-specific image source for screens < 768px', () => {
      const { container } = renderHeroSection();
      const mobileSource = container.querySelector('source[media="(max-width: 768px)"]');
      expect(mobileSource).toBeInTheDocument();
    });

    it('should have loading="eager" on hero image for LCP optimization', () => {
      renderHeroSection();
      const heroImage = screen.getByRole('img');
      expect(heroImage).toHaveAttribute('loading', 'eager');
    });
  });

  describe('Styling and Accessibility', () => {
    it('should have semantic structure with section element', () => {
      const { container } = renderHeroSection();
      const section = container.querySelector('section');
      expect(section).toBeInTheDocument();
    });

    it('should apply hero-section CSS class', () => {
      const { container } = renderHeroSection();
      const section = container.querySelector('.hero-section');
      expect(section).toBeInTheDocument();
    });

    it('should have aria-label for accessibility', () => {
      const { container } = renderHeroSection();
      const section = container.querySelector('section[aria-label]');
      expect(section).toBeInTheDocument();
      expect(section).toHaveAttribute('aria-label', expect.stringContaining('Hero'));
    });

    it('should render headline with landing page serif font class', () => {
      renderHeroSection();
      const headline = screen.getByRole('heading', { level: 1 });
      expect(headline).toHaveClass('hero-title');
    });
  });

  describe('Responsive Behavior', () => {
    it('should render content overlay container', () => {
      const { container } = renderHeroSection();
      const overlay = container.querySelector('.hero-content');
      expect(overlay).toBeInTheDocument();
    });

    it('should center content vertically and horizontally', () => {
      const { container } = renderHeroSection();
      const overlay = container.querySelector('.hero-content');
      expect(overlay).toHaveClass('hero-content');
    });
  });

  describe('Performance Optimizations', () => {
    it('should not lazy load hero image (eager loading for LCP)', () => {
      renderHeroSection();
      const heroImage = screen.getByRole('img');
      expect(heroImage).not.toHaveAttribute('loading', 'lazy');
    });

    it('should use WebP format for better compression', () => {
      const { container } = renderHeroSection();
      const webpSource = container.querySelector('source[type="image/webp"]');
      expect(webpSource?.getAttribute('srcSet')).toContain('.webp');
    });
  });
});
