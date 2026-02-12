// src/types/password.ts

export type PasswordStrength = 'weak' | 'medium' | 'strong';

export interface PasswordStrengthResult {
  /** Strength level (weak/medium/strong) */
  strength: PasswordStrength;

  /** Numeric score (0-4) */
  score: number;

  /** Feedback messages (e.g., "Incluye al menos una mayúscula") */
  feedback: string[];
}

export interface PasswordStrengthConfig {
  /** Minimum length required */
  minLength: number;

  /** Whether uppercase is required */
  requireUppercase: boolean;

  /** Whether lowercase is required */
  requireLowercase: boolean;

  /** Whether numbers are required */
  requireNumbers: boolean;

  /** Whether symbols are required (false per clarification Q2) */
  requireSymbols: boolean;
}

export interface PasswordCriteria {
  /** Has minimum length (≥8 chars) */
  hasMinLength: boolean;

  /** Contains uppercase letter */
  hasUppercase: boolean;

  /** Contains lowercase letter */
  hasLowercase: boolean;

  /** Contains number */
  hasNumber: boolean;

  /** Contains special character (allowed but not required) */
  hasSymbol: boolean;
}
