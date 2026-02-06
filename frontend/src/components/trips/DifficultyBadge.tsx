/**
 * DifficultyBadge Component - Trip Difficulty Display
 *
 * Displays trip difficulty level with color coding.
 * Used in wizard Step 2 to show auto-calculated difficulty.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 5 (US3)
 * Task: T056
 *
 * @example
 * ```typescript
 * <DifficultyBadge difficulty="moderate" />
 * // Renders: Orange badge with "Moderada"
 * ```
 */

import React from 'react';
import { formatDifficulty, type TripDifficulty } from '../../services/gpxWizardService';
import './DifficultyBadge.css';

/**
 * Props for DifficultyBadge component
 */
export interface DifficultyBadgeProps {
  /** Trip difficulty level (easy, moderate, difficult, very_difficult) */
  difficulty: TripDifficulty;
}

/**
 * Trip Difficulty Badge Component
 *
 * Displays difficulty level with color-coded badge:
 * - Easy: Green (#10b981)
 * - Moderate: Orange (#f59e0b)
 * - Difficult: Red (#ef4444)
 * - Very Difficult: Purple (#9333ea)
 *
 * Read-only display component (difficulty is calculated from GPX telemetry).
 *
 * @param props - Component props
 */
export const DifficultyBadge: React.FC<DifficultyBadgeProps> = ({ difficulty }) => {
  // Get Spanish label for difficulty
  const label = formatDifficulty(difficulty);

  // Generate CSS class modifier for color coding
  const modifierClass = `difficulty-badge--${difficulty}`;

  return (
    <span
      className={`difficulty-badge ${modifierClass}`}
      aria-label={`Dificultad: ${label}`}
      role="generic"
    >
      {label}
    </span>
  );
};
