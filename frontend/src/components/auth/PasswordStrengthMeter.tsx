// src/components/auth/PasswordStrengthMeter.tsx

import React, { useMemo } from 'react';
import { calculatePasswordStrength } from '../../utils/passwordStrength';
import type { PasswordStrength } from '../../types/password';
import './PasswordStrengthMeter.css';

interface PasswordStrengthMeterProps {
  password: string;
}

const STRENGTH_CONFIG: Record<PasswordStrength, { label: string; color: string }> = {
  weak: { label: 'Débil', color: '#ef4444' }, // Red
  medium: { label: 'Media', color: '#eab308' }, // Yellow
  strong: { label: 'Fuerte', color: '#22c55e' }, // Green
};

/**
 * Password strength meter with red/yellow/green visual indicator
 *
 * Based on ContraVento criteria:
 * - Length ≥8 characters
 * - Uppercase letter
 * - Lowercase letter
 * - Number
 * - Symbols allowed but not required
 */
export const PasswordStrengthMeter: React.FC<PasswordStrengthMeterProps> = ({ password }) => {
  const result = useMemo(() => calculatePasswordStrength(password), [password]);

  if (!password) return null;

  const { label, color } = STRENGTH_CONFIG[result.strength];
  const widthPercentage = (result.score / 4) * 100;

  return (
    <div className="password-strength-meter">
      <div className="strength-bar">
        <div
          className="strength-fill"
          style={{
            width: `${widthPercentage}%`,
            backgroundColor: color,
            transition: 'all 0.3s ease',
          }}
        />
      </div>
      <div className="strength-info">
        <span className="strength-label" style={{ color }}>
          Seguridad: <strong>{label}</strong>
        </span>
      </div>
      {result.feedback.length > 0 && (
        <ul className="strength-feedback">
          {result.feedback.map((tip, i) => (
            <li key={i}>{tip}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
