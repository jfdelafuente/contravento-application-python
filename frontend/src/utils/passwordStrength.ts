// src/utils/passwordStrength.ts

import type { PasswordStrength, PasswordStrengthResult } from '../types/password';

/**
 * Calculate password strength based on ContraVento criteria:
 * - Length ≥8 characters
 * - Contains uppercase letter
 * - Contains lowercase letter
 * - Contains number
 * - Special characters allowed but NOT considered in strength
 */
export const calculatePasswordStrength = (password: string): PasswordStrengthResult => {
  const feedback: string[] = [];
  let score = 0;

  // Criterion 1: Minimum length
  const hasMinLength = password.length >= 8;
  if (hasMinLength) {
    score++;
  } else {
    feedback.push('Mínimo 8 caracteres');
  }

  // Criterion 2: Uppercase letter
  const hasUppercase = /[A-Z]/.test(password);
  if (hasUppercase) {
    score++;
  } else {
    feedback.push('Incluye al menos una mayúscula');
  }

  // Criterion 3: Lowercase letter
  const hasLowercase = /[a-z]/.test(password);
  if (hasLowercase) {
    score++;
  } else {
    feedback.push('Incluye al menos una minúscula');
  }

  // Criterion 4: Number
  const hasNumber = /\d/.test(password);
  if (hasNumber) {
    score++;
  } else {
    feedback.push('Incluye al menos un número');
  }

  // Map score to strength level
  let strength: PasswordStrength;
  if (score < 3) {
    strength = 'weak';    // Red
  } else if (score === 3) {
    strength = 'medium';  // Yellow
  } else {
    strength = 'strong';  // Green (score === 4)
  }

  return { strength, score, feedback };
};
