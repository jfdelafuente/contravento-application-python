/**
 * DifficultyBadge Component Unit Tests
 *
 * Tests for trip difficulty badge display component.
 * Tests difficulty levels, color coding, and accessibility.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 5 (US3)
 * Task: T055
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { DifficultyBadge } from '../../src/components/trips/DifficultyBadge';
import type { TripDifficulty } from '../../src/services/gpxWizardService';

describe('DifficultyBadge (T055)', () => {
  describe('Difficulty Display', () => {
    it('should display "Fácil" for easy difficulty', () => {
      render(<DifficultyBadge difficulty="easy" />);

      expect(screen.getByText('Fácil')).toBeInTheDocument();
    });

    it('should display "Moderada" for moderate difficulty', () => {
      render(<DifficultyBadge difficulty="moderate" />);

      expect(screen.getByText('Moderada')).toBeInTheDocument();
    });

    it('should display "Difícil" for difficult difficulty', () => {
      render(<DifficultyBadge difficulty="difficult" />);

      expect(screen.getByText('Difícil')).toBeInTheDocument();
    });

    it('should display "Muy Difícil" for very_difficult difficulty', () => {
      render(<DifficultyBadge difficulty="very_difficult" />);

      expect(screen.getByText('Muy Difícil')).toBeInTheDocument();
    });
  });

  describe('Color Coding', () => {
    it('should apply green color for easy difficulty', () => {
      render(<DifficultyBadge difficulty="easy" />);

      const badge = screen.getByText('Fácil').closest('.difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge--easy');
    });

    it('should apply orange color for moderate difficulty', () => {
      render(<DifficultyBadge difficulty="moderate" />);

      const badge = screen.getByText('Moderada').closest('.difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge--moderate');
    });

    it('should apply red color for difficult difficulty', () => {
      render(<DifficultyBadge difficulty="difficult" />);

      const badge = screen.getByText('Difícil').closest('.difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge--difficult');
    });

    it('should apply purple color for very_difficult difficulty', () => {
      render(<DifficultyBadge difficulty="very_difficult" />);

      const badge = screen.getByText('Muy Difícil').closest('.difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge--very-difficult');
    });
  });

  describe('Accessibility', () => {
    it('should have semantic span element', () => {
      render(<DifficultyBadge difficulty="moderate" />);

      const badge = screen.getByText('Moderada');
      expect(badge.tagName).toBe('SPAN');
    });

    it('should have aria-label describing difficulty level', () => {
      render(<DifficultyBadge difficulty="difficult" />);

      const badge = screen.getByLabelText('Dificultad: Difícil');
      expect(badge).toBeInTheDocument();
    });

    it('should include difficulty level in accessible name', () => {
      render(<DifficultyBadge difficulty="easy" />);

      const badge = screen.getByLabelText('Dificultad: Fácil');
      expect(badge).toBeInTheDocument();
    });
  });

  describe('Component Structure', () => {
    it('should render with correct CSS class', () => {
      render(<DifficultyBadge difficulty="moderate" />);

      const badge = screen.getByText('Moderada').closest('.difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge');
    });

    it('should have both base and modifier classes', () => {
      render(<DifficultyBadge difficulty="easy" />);

      const badge = screen.getByText('Fácil').closest('.difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge');
      expect(badge).toHaveClass('difficulty-badge--easy');
    });

    it('should render as inline element (not block)', () => {
      const { container } = render(<DifficultyBadge difficulty="moderate" />);

      const badge = container.querySelector('.difficulty-badge');
      expect(badge?.tagName).toBe('SPAN');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string gracefully', () => {
      // @ts-expect-error Testing edge case with invalid type
      render(<DifficultyBadge difficulty="" />);

      // Should render without crashing
      const badge = document.querySelector('.difficulty-badge');
      expect(badge).toBeInTheDocument();
    });

    it('should handle unknown difficulty value', () => {
      // @ts-expect-error Testing edge case with invalid type
      render(<DifficultyBadge difficulty="unknown" />);

      // Should render without crashing (fallback to gray)
      const badge = document.querySelector('.difficulty-badge');
      expect(badge).toBeInTheDocument();
    });

    it('should handle null difficulty gracefully', () => {
      // @ts-expect-error Testing edge case with invalid type
      render(<DifficultyBadge difficulty={null} />);

      // Should render without crashing
      const badge = document.querySelector('.difficulty-badge');
      expect(badge).toBeInTheDocument();
    });
  });

  describe('Visual Styling', () => {
    it('should apply consistent styling across all difficulty levels', () => {
      const difficulties: TripDifficulty[] = ['easy', 'moderate', 'difficult', 'very_difficult'];

      difficulties.forEach((difficulty) => {
        const { container, unmount } = render(<DifficultyBadge difficulty={difficulty} />);

        const badge = container.querySelector('.difficulty-badge');
        expect(badge).toHaveClass('difficulty-badge');
        expect(badge).toHaveClass(`difficulty-badge--${difficulty}`);

        unmount();
      });
    });
  });

  describe('Props Validation', () => {
    it('should accept valid TripDifficulty values', () => {
      const difficulties: TripDifficulty[] = ['easy', 'moderate', 'difficult', 'very_difficult'];

      difficulties.forEach((difficulty) => {
        const { unmount } = render(<DifficultyBadge difficulty={difficulty} />);

        // Should render without errors
        expect(screen.getByRole('generic')).toBeInTheDocument();

        unmount();
      });
    });

    it('should not accept invalid difficulty values (TypeScript check)', () => {
      // This test verifies TypeScript type safety at compile time
      // @ts-expect-error - Testing that TypeScript prevents invalid values
      const invalidDifficulty: TripDifficulty = 'invalid';

      // TypeScript should catch this error during development
      expect(invalidDifficulty).toBeDefined();
    });
  });

  describe('Reusability', () => {
    it('should render multiple badges independently', () => {
      const { container } = render(
        <>
          <DifficultyBadge difficulty="easy" />
          <DifficultyBadge difficulty="difficult" />
        </>
      );

      const badges = container.querySelectorAll('.difficulty-badge');
      expect(badges).toHaveLength(2);

      expect(screen.getByText('Fácil')).toBeInTheDocument();
      expect(screen.getByText('Difícil')).toBeInTheDocument();
    });

    it('should maintain independent state when multiple instances rendered', () => {
      render(
        <>
          <DifficultyBadge difficulty="easy" />
          <DifficultyBadge difficulty="moderate" />
          <DifficultyBadge difficulty="difficult" />
        </>
      );

      // Each badge should have its own modifier class
      const easyBadge = screen.getByText('Fácil').closest('.difficulty-badge');
      const moderateBadge = screen.getByText('Moderada').closest('.difficulty-badge');
      const difficultBadge = screen.getByText('Difícil').closest('.difficulty-badge');

      expect(easyBadge).toHaveClass('difficulty-badge--easy');
      expect(moderateBadge).toHaveClass('difficulty-badge--moderate');
      expect(difficultBadge).toHaveClass('difficulty-badge--difficult');
    });
  });
});
