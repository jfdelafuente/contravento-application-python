// src/types/forms.ts

export interface RegisterFormData {
  /** Username (3-30 chars, alphanumeric + underscore) */
  username: string;

  /** Email address */
  email: string;

  /** Password (8-128 chars) */
  password: string;

  /** Password confirmation */
  confirmPassword: string;

  /** Cloudflare Turnstile token (per FR-014) */
  turnstileToken: string;

  /** Terms of service acceptance */
  acceptTerms: boolean;
}

export interface RegisterRequestPayload {
  username: string;
  email: string;
  password: string;
  turnstile_token: string;
}

export interface LoginFormData {
  /** Email address */
  email: string;

  /** Password */
  password: string;

  /** Remember Me checkbox (affects token duration) */
  rememberMe: boolean;

  /** Optional Turnstile token (if rate limited) */
  turnstileToken?: string;
}

export interface LoginRequestPayload {
  email: string;
  password: string;
  remember_me: boolean;
  turnstile_token?: string;
}

export interface ForgotPasswordFormData {
  /** Email address for password reset */
  email: string;

  /** Turnstile token for bot protection */
  turnstileToken: string;
}

export interface ResetPasswordFormData {
  /** New password */
  newPassword: string;

  /** New password confirmation */
  confirmPassword: string;

  /** Reset token from email link */
  token: string;
}
