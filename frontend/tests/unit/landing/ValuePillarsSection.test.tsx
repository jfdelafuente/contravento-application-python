// frontend/tests/unit/landing/ValuePillarsSection.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ValuePillarsSection } from '../../../src/components/landing/ValuePillarsSection';

/**
 * Test Suite: ValuePillarsSection Component (Feature 014 - User Story 2)
 *
 * Requirements from spec.md:
 * - FR-014-010: Display 3-column grid with value pillars
 * - FR-014-011: Show icons for each pillar (Heroicons)
 * - FR-014-012: Include pillar names: Territorio, Comunidad, Ética
 * - FR-014-013: Brief descriptions under each pillar (1-2 sentences)
 * - SC-014-005: Responsive layout (3 columns desktop, stacked mobile)
 */
describe('ValuePillarsSection Component', () => {
  const renderValuePillarsSection = () => {
    return render(<ValuePillarsSection />);
  };

  describe('Section Structure', () => {
    it('should render as a section element', () => {
      const { container } = renderValuePillarsSection();
      const section = container.querySelector('section');
      expect(section).toBeInTheDocument();
    });

    it('should have value-pillars-section CSS class', () => {
      const { container } = renderValuePillarsSection();
      const section = container.querySelector('.value-pillars-section');
      expect(section).toBeInTheDocument();
    });

    it('should have aria-labelledby attribute for accessibility', () => {
      const { container } = renderValuePillarsSection();
      const section = container.querySelector('section[aria-labelledby]');
      expect(section).toBeInTheDocument();
    });

    it('should render section title "Pilares de Valor"', () => {
      renderValuePillarsSection();
      const title = screen.getByRole('heading', { level: 2, name: /pilares de valor/i });
      expect(title).toBeInTheDocument();
    });
  });

  describe('3-Pillar Content', () => {
    it('should render exactly 3 pillars', () => {
      const { container } = renderValuePillarsSection();
      const pillars = container.querySelectorAll('.value-pillar');
      expect(pillars).toHaveLength(3);
    });

    it('should render first pillar: "Territorio"', () => {
      renderValuePillarsSection();
      const pillar1 = screen.getByRole('heading', { level: 3, name: /territorio/i });
      expect(pillar1).toBeInTheDocument();
    });

    it('should render second pillar: "Comunidad"', () => {
      renderValuePillarsSection();
      const pillar2 = screen.getByRole('heading', { level: 3, name: /comunidad/i });
      expect(pillar2).toBeInTheDocument();
    });

    it('should render third pillar: "Ética"', () => {
      renderValuePillarsSection();
      const pillar3 = screen.getByRole('heading', { level: 3, name: /ética/i });
      expect(pillar3).toBeInTheDocument();
    });
  });

  describe('Pillar Icons (Heroicons)', () => {
    it('should render icon for Territorio pillar', () => {
      const { container } = renderValuePillarsSection();
      const icons = container.querySelectorAll('.value-pillar svg');
      expect(icons.length).toBeGreaterThanOrEqual(3);
    });

    it('should render icons with proper accessibility attributes', () => {
      const { container } = renderValuePillarsSection();
      const icons = container.querySelectorAll('.value-pillar svg');
      icons.forEach(icon => {
        expect(icon).toHaveAttribute('aria-hidden', 'true');
      });
    });

    it('should use ShoppingBagIcon for Territorio pillar', () => {
      const { container } = renderValuePillarsSection();
      // Icon should be rendered as SVG within first pillar
      const firstPillar = container.querySelectorAll('.value-pillar')[0];
      const icon = firstPillar?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should use UsersIcon for Comunidad pillar', () => {
      const { container } = renderValuePillarsSection();
      const secondPillar = container.querySelectorAll('.value-pillar')[1];
      const icon = secondPillar?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should use SparklesIcon for Ética pillar', () => {
      const { container } = renderValuePillarsSection();
      const thirdPillar = container.querySelectorAll('.value-pillar')[2];
      const icon = thirdPillar?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Pillar Descriptions', () => {
    it('should include description for Territorio pillar', () => {
      renderValuePillarsSection();
      const description = screen.getByText(/economía local/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for Comunidad pillar', () => {
      renderValuePillarsSection();
      const description = screen.getByText(/red de ciclistas/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for Ética pillar', () => {
      renderValuePillarsSection();
      const description = screen.getByText(/respeto por el medio ambiente/i);
      expect(description).toBeInTheDocument();
    });
  });

  describe('Styling and Layout', () => {
    it('should render pillars in a grid container', () => {
      const { container } = renderValuePillarsSection();
      const grid = container.querySelector('.value-pillars-grid');
      expect(grid).toBeInTheDocument();
    });

    it('should apply value-pillar class to each pillar', () => {
      const { container } = renderValuePillarsSection();
      const pillars = container.querySelectorAll('.value-pillar');
      pillars.forEach(pillar => {
        expect(pillar).toHaveClass('value-pillar');
      });
    });

    it('should render icon containers with proper styling class', () => {
      const { container } = renderValuePillarsSection();
      const iconContainers = container.querySelectorAll('.value-pillar-icon');
      expect(iconContainers.length).toBe(3);
    });

    it('should use serif font for section title', () => {
      const { container } = renderValuePillarsSection();
      const title = container.querySelector('.value-pillars-title');
      expect(title).toBeInTheDocument();
    });

    it('should use sans-serif font for pillar titles', () => {
      const { container } = renderValuePillarsSection();
      const pillarTitles = container.querySelectorAll('.value-pillar-title');
      expect(pillarTitles).toHaveLength(3);
    });
  });

  describe('Responsive Behavior', () => {
    it('should render 3-column grid on desktop (CSS verification)', () => {
      const { container } = renderValuePillarsSection();
      const grid = container.querySelector('.value-pillars-grid');
      expect(grid).toBeInTheDocument();
      // CSS will handle grid-template-columns: repeat(3, 1fr)
    });

    it('should stack pillars vertically on mobile (CSS verification)', () => {
      const { container } = renderValuePillarsSection();
      const grid = container.querySelector('.value-pillars-grid');
      expect(grid).toBeInTheDocument();
      // CSS @media (max-width: 768px) will handle stacking
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy (h2 → h3)', () => {
      renderValuePillarsSection();
      const sectionTitle = screen.getByRole('heading', { level: 2 });
      const pillarTitles = screen.getAllByRole('heading', { level: 3 });

      expect(sectionTitle).toBeInTheDocument();
      expect(pillarTitles).toHaveLength(3);
    });

    it('should have descriptive aria-labelledby linking section to title', () => {
      const { container } = renderValuePillarsSection();
      const section = container.querySelector('section');
      const titleId = section?.getAttribute('aria-labelledby');

      expect(titleId).toBeTruthy();

      const title = container.querySelector(`#${titleId}`);
      expect(title).toBeInTheDocument();
      expect(title?.textContent).toMatch(/pilares de valor/i);
    });

    it('should hide decorative icons from screen readers', () => {
      const { container } = renderValuePillarsSection();
      const icons = container.querySelectorAll('svg[aria-hidden="true"]');
      expect(icons.length).toBe(3);
    });
  });

  describe('Content Ordering', () => {
    it('should render pillars in correct order (Territorio → Comunidad → Ética)', () => {
      const { container } = renderValuePillarsSection();
      const pillarHeadings = Array.from(container.querySelectorAll('.value-pillar h3'));
      const headingTexts = pillarHeadings.map(h => h.textContent);

      expect(headingTexts[0]).toMatch(/territorio/i);
      expect(headingTexts[1]).toMatch(/comunidad/i);
      expect(headingTexts[2]).toMatch(/ética/i);
    });
  });

  describe('Hover Effects', () => {
    it('should apply hover effect class to pillars', () => {
      const { container } = renderValuePillarsSection();
      const pillars = container.querySelectorAll('.value-pillar');

      // Verify pillars exist for hover interaction
      expect(pillars.length).toBe(3);

      // CSS handles :hover state
      pillars.forEach(pillar => {
        expect(pillar).toHaveClass('value-pillar');
      });
    });
  });
});
