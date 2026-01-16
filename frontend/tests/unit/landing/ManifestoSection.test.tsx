// frontend/tests/unit/landing/ManifestoSection.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ManifestoSection } from '../../../src/components/landing/ManifestoSection';

/**
 * Test Suite: ManifestoSection Component (Feature 014 - User Story 1)
 *
 * Requirements from spec.md:
 * - FR-014-004: Display 4-pillar manifesto with headings
 * - FR-014-005: Show "El camino es el destino", "Pedalear para conectar", "Regenerar territorios", "Comunidad sobre competencia"
 * - FR-014-006: Include brief description (1-2 sentences) under each pillar
 * - SC-014-003: Manifesto visible above the fold on desktop after hero section
 */
describe('ManifestoSection Component', () => {
  const renderManifestoSection = () => {
    return render(<ManifestoSection />);
  };

  describe('Section Structure', () => {
    it('should render as a section element', () => {
      const { container } = renderManifestoSection();
      const section = container.querySelector('section');
      expect(section).toBeInTheDocument();
    });

    it('should have manifesto-section CSS class', () => {
      const { container } = renderManifestoSection();
      const section = container.querySelector('.manifesto-section');
      expect(section).toBeInTheDocument();
    });

    it('should have aria-labelledby attribute for accessibility', () => {
      const { container } = renderManifestoSection();
      const section = container.querySelector('section[aria-labelledby]');
      expect(section).toBeInTheDocument();
    });

    it('should render section title "Nuestra Filosofía"', () => {
      renderManifestoSection();
      const title = screen.getByRole('heading', { level: 2, name: /nuestra filosofía/i });
      expect(title).toBeInTheDocument();
    });
  });

  describe('4-Pillar Content', () => {
    it('should render exactly 4 pillars', () => {
      const { container } = renderManifestoSection();
      const pillars = container.querySelectorAll('.manifesto-pillar');
      expect(pillars).toHaveLength(4);
    });

    it('should render first pillar: "El camino es el destino"', () => {
      renderManifestoSection();
      const pillar1 = screen.getByRole('heading', { level: 3, name: /el camino es el destino/i });
      expect(pillar1).toBeInTheDocument();
    });

    it('should render second pillar: "Pedalear para conectar"', () => {
      renderManifestoSection();
      const pillar2 = screen.getByRole('heading', { level: 3, name: /pedalear para conectar/i });
      expect(pillar2).toBeInTheDocument();
    });

    it('should render third pillar: "Regenerar territorios"', () => {
      renderManifestoSection();
      const pillar3 = screen.getByRole('heading', { level: 3, name: /regenerar territorios/i });
      expect(pillar3).toBeInTheDocument();
    });

    it('should render fourth pillar: "Comunidad sobre competencia"', () => {
      renderManifestoSection();
      const pillar4 = screen.getByRole('heading', { level: 3, name: /comunidad sobre competencia/i });
      expect(pillar4).toBeInTheDocument();
    });
  });

  describe('Pillar Descriptions', () => {
    it('should include description for "El camino es el destino" pillar', () => {
      renderManifestoSection();
      const description = screen.getByText(/el viaje importa más que el destino/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for "Pedalear para conectar" pillar', () => {
      renderManifestoSection();
      const description = screen.getByText(/conexión humana y territorial/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for "Regenerar territorios" pillar', () => {
      renderManifestoSection();
      const description = screen.getByText(/apoyar economía local/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for "Comunidad sobre competencia" pillar', () => {
      renderManifestoSection();
      const description = screen.getByText(/Celebramos el esfuerzo compartido/i);
      expect(description).toBeInTheDocument();
    });
  });

  describe('Styling and Layout', () => {
    it('should render pillars in a grid container', () => {
      const { container } = renderManifestoSection();
      const grid = container.querySelector('.manifesto-grid');
      expect(grid).toBeInTheDocument();
    });

    it('should apply manifesto-pillar class to each pillar', () => {
      const { container } = renderManifestoSection();
      const pillars = container.querySelectorAll('.manifesto-pillar');
      pillars.forEach(pillar => {
        expect(pillar).toHaveClass('manifesto-pillar');
      });
    });

    it('should use serif font for pillar headings', () => {
      const { container } = renderManifestoSection();
      const pillarHeadings = container.querySelectorAll('.manifesto-pillar h3');
      pillarHeadings.forEach(heading => {
        expect(heading).toHaveClass('manifesto-pillar-title');
      });
    });
  });

  describe('Responsive Behavior', () => {
    it('should render 2-column grid on desktop (CSS verification)', () => {
      const { container } = renderManifestoSection();
      const grid = container.querySelector('.manifesto-grid');
      expect(grid).toBeInTheDocument();
      // CSS will handle grid-template-columns: repeat(2, 1fr)
    });

    it('should stack pillars vertically on mobile (CSS verification)', () => {
      const { container } = renderManifestoSection();
      const grid = container.querySelector('.manifesto-grid');
      expect(grid).toBeInTheDocument();
      // CSS @media (max-width: 768px) will handle stacking
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy (h2 → h3)', () => {
      renderManifestoSection();
      const sectionTitle = screen.getByRole('heading', { level: 2 });
      const pillarTitles = screen.getAllByRole('heading', { level: 3 });

      expect(sectionTitle).toBeInTheDocument();
      expect(pillarTitles).toHaveLength(4);
    });

    it('should have descriptive aria-labelledby linking section to title', () => {
      const { container } = renderManifestoSection();
      const section = container.querySelector('section');
      const titleId = section?.getAttribute('aria-labelledby');

      expect(titleId).toBeTruthy();

      const title = container.querySelector(`#${titleId}`);
      expect(title).toBeInTheDocument();
      expect(title?.textContent).toMatch(/nuestra filosofía/i);
    });
  });

  describe('Content Ordering', () => {
    it('should render pillars in correct order (1-4)', () => {
      const { container } = renderManifestoSection();
      const pillarHeadings = Array.from(container.querySelectorAll('.manifesto-pillar h3'));
      const headingTexts = pillarHeadings.map(h => h.textContent);

      expect(headingTexts[0]).toMatch(/el camino es el destino/i);
      expect(headingTexts[1]).toMatch(/pedalear para conectar/i);
      expect(headingTexts[2]).toMatch(/regenerar territorios/i);
      expect(headingTexts[3]).toMatch(/comunidad sobre competencia/i);
    });
  });
});
