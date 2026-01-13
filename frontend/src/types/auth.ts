// src/types/auth.ts

import { User } from './user';

export interface AuthContextType {
  /** Current authenticated user (null if not authenticated) */
  user: User | null;

  /** Loading state during initial auth check */
  isLoading: boolean;

  /** Computed authentication status */
  isAuthenticated: boolean;

  /** Login function */
  login: (email: string, password: string, rememberMe: boolean) => Promise<void>;

  /** Register function */
  register: (data: RegisterFormData) => Promise<void>;

  /** Logout function */
  logout: () => Promise<void>;

  /** Refresh user data */
  refreshUser: () => Promise<void>;

  /** Update user data */
  updateUser: (userData: Partial<User>) => void;

  /** Request password reset */
  requestPasswordReset: (email: string) => Promise<void>;

  /** Reset password with token */
  resetPassword: (token: string, newPassword: string) => Promise<void>;

  /** Resend verification email */
  resendVerificationEmail: () => Promise<void>;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: AuthError | null;
}

export interface SessionMetadata {
  /** Access token expiration (client-side tracking) */
  access_token_expires_at?: number; // Unix timestamp

  /** Whether "Remember Me" is active */
  remember_me: boolean;

  /** Last activity timestamp for idle detection */
  last_activity_at: number; // Unix timestamp
}

export type AuthErrorCode =
  | 'INVALID_CREDENTIALS'
  | 'EMAIL_NOT_VERIFIED'
  | 'ACCOUNT_BLOCKED'
  | 'INVALID_TOKEN'
  | 'TOKEN_EXPIRED'
  | 'EMAIL_ALREADY_EXISTS'
  | 'USERNAME_TAKEN'
  | 'WEAK_PASSWORD'
  | 'CAPTCHA_FAILED'
  | 'NETWORK_ERROR'
  | 'UNKNOWN_ERROR';

export interface AuthError {
  /** Error code for programmatic handling */
  code: AuthErrorCode;

  /** User-friendly Spanish error message */
  message: string;

  /** Optional field name (for validation errors) */
  field?: string;

  /** Optional additional details */
  details?: Record<string, unknown>;
}

export const AUTH_ERROR_MESSAGES: Record<AuthErrorCode, string> = {
  INVALID_CREDENTIALS: 'Email o contraseña incorrectos',
  EMAIL_NOT_VERIFIED: 'Debes verificar tu email antes de iniciar sesión',
  ACCOUNT_BLOCKED: 'Cuenta bloqueada temporalmente. Inténtalo más tarde.',
  INVALID_TOKEN: 'El enlace de verificación no es válido',
  TOKEN_EXPIRED: 'El enlace de verificación ha expirado',
  EMAIL_ALREADY_EXISTS: 'Este email ya está registrado',
  USERNAME_TAKEN: 'Este nombre de usuario no está disponible',
  WEAK_PASSWORD: 'La contraseña no cumple los requisitos de seguridad',
  CAPTCHA_FAILED: 'Verificación CAPTCHA fallida. Inténtalo de nuevo.',
  NETWORK_ERROR: 'Error de conexión. Verifica tu internet.',
  UNKNOWN_ERROR: 'Ha ocurrido un error inesperado. Inténtalo de nuevo.',
};

// Import RegisterFormData from forms.ts (will be created next)
export type { RegisterFormData } from './forms';
