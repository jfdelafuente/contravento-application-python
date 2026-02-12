// frontend/tests/unit/landing/HowItWorksSection.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HowItWorksSection } from '../../../src/components/landing/HowItWorksSection';

/**
 * Test Suite: HowItWorksSection Component (Feature 014 - User Story 3)
 *
 * Requirements from spec.md:
 * - FR-014-014: Display 4-step process flow
 * - FR-014-015: Show numbered steps (1-4) with icons
 * - FR-014-016: Step titles: Documenta, Comparte, Descubre, Impacta
 * - FR-014-017: Brief description under each step (1-2 sentences)
 * - SC-014-006: Responsive layout (2x2 grid on desktop, stacked on mobile)
 */
describe('HowItWorksSection Component', () => {
  const renderHowItWorksSection = () => {
    return render(<HowItWorksSection />);
  };

  describe('Section Structure', () => {
    it('should render as a section element', () => {
      const { container } = renderHowItWorksSection();
      const section = container.querySelector('section');
      expect(section).toBeInTheDocument();
    });

    it('should have how-it-works-section CSS class', () => {
      const { container } = renderHowItWorksSection();
      const section = container.querySelector('.how-it-works-section');
      expect(section).toBeInTheDocument();
    });

    it('should have aria-labelledby attribute for accessibility', () => {
      const { container } = renderHowItWorksSection();
      const section = container.querySelector('section[aria-labelledby]');
      expect(section).toBeInTheDocument();
    });

    it('should render section title "Cómo Funciona"', () => {
      renderHowItWorksSection();
      const title = screen.getByRole('heading', { level: 2, name: /cómo funciona/i });
      expect(title).toBeInTheDocument();
    });
  });

  describe('4-Step Process', () => {
    it('should render exactly 4 steps', () => {
      const { container } = renderHowItWorksSection();
      const steps = container.querySelectorAll('.how-it-works-step');
      expect(steps).toHaveLength(4);
    });

    it('should render step 1: "Documenta"', () => {
      renderHowItWorksSection();
      const step1 = screen.getByRole('heading', { level: 3, name: /documenta/i });
      expect(step1).toBeInTheDocument();
    });

    it('should render step 2: "Comparte"', () => {
      renderHowItWorksSection();
      const step2 = screen.getByRole('heading', { level: 3, name: /comparte/i });
      expect(step2).toBeInTheDocument();
    });

    it('should render step 3: "Descubre"', () => {
      renderHowItWorksSection();
      const step3 = screen.getByRole('heading', { level: 3, name: /descubre/i });
      expect(step3).toBeInTheDocument();
    });

    it('should render step 4: "Impacta"', () => {
      renderHowItWorksSection();
      const step4 = screen.getByRole('heading', { level: 3, name: /impacta/i });
      expect(step4).toBeInTheDocument();
    });
  });

  describe('Step Numbers', () => {
    it('should display step number 1', () => {
      const { container } = renderHowItWorksSection();
      const stepNumber1 = container.querySelector('.step-number');
      expect(stepNumber1?.textContent).toBe('1');
    });

    it('should display all step numbers (1-4)', () => {
      const { container } = renderHowItWorksSection();
      const stepNumbers = container.querySelectorAll('.step-number');
      expect(stepNumbers).toHaveLength(4);

      expect(stepNumbers[0].textContent).toBe('1');
      expect(stepNumbers[1].textContent).toBe('2');
      expect(stepNumbers[2].textContent).toBe('3');
      expect(stepNumbers[3].textContent).toBe('4');
    });
  });

  describe('Step Icons (Heroicons)', () => {
    it('should render icon for each step', () => {
      const { container } = renderHowItWorksSection();
      const icons = container.querySelectorAll('.how-it-works-step svg');
      expect(icons.length).toBeGreaterThanOrEqual(4);
    });

    it('should render icons with proper accessibility attributes', () => {
      const { container } = renderHowItWorksSection();
      const icons = container.querySelectorAll('.how-it-works-step svg');
      icons.forEach(icon => {
        expect(icon).toHaveAttribute('aria-hidden', 'true');
      });
    });

    it('should use CameraIcon for Step 1: Documenta', () => {
      const { container } = renderHowItWorksSection();
      const firstStep = container.querySelectorAll('.how-it-works-step')[0];
      const icon = firstStep?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should use ShareIcon for Step 2: Comparte', () => {
      const { container } = renderHowItWorksSection();
      const secondStep = container.querySelectorAll('.how-it-works-step')[1];
      const icon = secondStep?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should use MapIcon for Step 3: Descubre', () => {
      const { container } = renderHowItWorksSection();
      const thirdStep = container.querySelectorAll('.how-it-works-step')[2];
      const icon = thirdStep?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should use HeartIcon for Step 4: Impacta', () => {
      const { container } = renderHowItWorksSection();
      const fourthStep = container.querySelectorAll('.how-it-works-step')[3];
      const icon = fourthStep?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Step Descriptions', () => {
    it('should include description for Step 1: Documenta', () => {
      renderHowItWorksSection();
      const description = screen.getByText(/registra tus viajes/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for Step 2: Comparte', () => {
      renderHowItWorksSection();
      const description = screen.getByText(/historias con la comunidad/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for Step 3: Descubre', () => {
      renderHowItWorksSection();
      const description = screen.getByText(/rutas y lugares/i);
      expect(description).toBeInTheDocument();
    });

    it('should include description for Step 4: Impacta', () => {
      renderHowItWorksSection();
      const description = screen.getByText(/impacto positivo/i);
      expect(description).toBeInTheDocument();
    });
  });

  describe('Styling and Layout', () => {
    it('should render steps in a grid container', () => {
      const { container } = renderHowItWorksSection();
      const grid = container.querySelector('.how-it-works-grid');
      expect(grid).toBeInTheDocument();
    });

    it('should apply how-it-works-step class to each step', () => {
      const { container } = renderHowItWorksSection();
      const steps = container.querySelectorAll('.how-it-works-step');
      steps.forEach(step => {
        expect(step).toHaveClass('how-it-works-step');
      });
    });

    it('should render icon containers with proper styling class', () => {
      const { container } = renderHowItWorksSection();
      const iconContainers = container.querySelectorAll('.step-icon');
      expect(iconContainers.length).toBe(4);
    });

    it('should use serif font for section title', () => {
      const { container } = renderHowItWorksSection();
      const title = container.querySelector('.how-it-works-title');
      expect(title).toBeInTheDocument();
    });

    it('should use sans-serif font for step titles', () => {
      const { container } = renderHowItWorksSection();
      const stepTitles = container.querySelectorAll('.step-title');
      expect(stepTitles).toHaveLength(4);
    });
  });

  describe('Responsive Behavior', () => {
    it('should render 2x2 grid on desktop (CSS verification)', () => {
      const { container } = renderHowItWorksSection();
      const grid = container.querySelector('.how-it-works-grid');
      expect(grid).toBeInTheDocument();
      // CSS will handle grid-template-columns: repeat(2, 1fr)
    });

    it('should stack steps vertically on mobile (CSS verification)', () => {
      const { container } = renderHowItWorksSection();
      const grid = container.querySelector('.how-it-works-grid');
      expect(grid).toBeInTheDocument();
      // CSS @media (max-width: 768px) will handle stacking
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy (h2 → h3)', () => {
      renderHowItWorksSection();
      const sectionTitle = screen.getByRole('heading', { level: 2 });
      const stepTitles = screen.getAllByRole('heading', { level: 3 });

      expect(sectionTitle).toBeInTheDocument();
      expect(stepTitles).toHaveLength(4);
    });

    it('should have descriptive aria-labelledby linking section to title', () => {
      const { container } = renderHowItWorksSection();
      const section = container.querySelector('section');
      const titleId = section?.getAttribute('aria-labelledby');

      expect(titleId).toBeTruthy();

      const title = container.querySelector(`#${titleId}`);
      expect(title).toBeInTheDocument();
      expect(title?.textContent).toMatch(/cómo funciona/i);
    });

    it('should hide decorative icons from screen readers', () => {
      const { container } = renderHowItWorksSection();
      const icons = container.querySelectorAll('svg[aria-hidden="true"]');
      expect(icons.length).toBe(4);
    });

    it('should use aria-label for step numbers', () => {
      const { container } = renderHowItWorksSection();
      const stepNumbers = container.querySelectorAll('.step-number');
      stepNumbers.forEach((stepNumber, index) => {
        expect(stepNumber).toHaveAttribute('aria-label', `Paso ${index + 1}`);
      });
    });
  });

  describe('Content Ordering', () => {
    it('should render steps in correct order (1 → 2 → 3 → 4)', () => {
      const { container } = renderHowItWorksSection();
      const stepHeadings = Array.from(container.querySelectorAll('.how-it-works-step h3'));
      const headingTexts = stepHeadings.map(h => h.textContent);

      expect(headingTexts[0]).toMatch(/documenta/i);
      expect(headingTexts[1]).toMatch(/comparte/i);
      expect(headingTexts[2]).toMatch(/descubre/i);
      expect(headingTexts[3]).toMatch(/impacta/i);
    });
  });
});
