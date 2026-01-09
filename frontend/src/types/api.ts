// src/types/api.ts

import { User } from './user';

export interface ApiResponse<T = unknown> {
  /** Success status */
  success: boolean;

  /** Response data (if successful) */
  data?: T;

  /** Error details (if failed) */
  error?: ApiError;

  /** Optional metadata */
  meta?: ApiResponseMetadata;
}

export interface ApiResponseMetadata {
  /** Request timestamp */
  timestamp?: string;

  /** Request ID for debugging */
  request_id?: string;
}

export interface ApiError {
  /** Error code */
  code: string;

  /** User-friendly message (Spanish) */
  message: string;

  /** Field name (for validation errors) */
  field?: string;

  /** Validation errors for multiple fields */
  validation_errors?: FieldError[];
}

export interface FieldError {
  field: string;
  message: string;
}

// Authentication endpoint responses

export interface RegisterResponse {
  message: string;
  user: {
    id: string;
    username: string;
    email: string;
    is_verified: false;
  };
}

export interface LoginResponse {
  message: string;
  user: User;
}

export interface LogoutResponse {
  message: string;
}

export interface RefreshTokenResponse {
  message: string;
}

export type CurrentUserResponse = User;

export interface VerifyEmailResponse {
  message: string;
  user: User;
}

export interface ResendVerificationResponse {
  message: string;
  email_sent_to: string;
}

export interface ForgotPasswordResponse {
  message: string;
  email_sent_to: string;
}

export interface ResetPasswordResponse {
  message: string;
}

export interface AccountBlockedResponse {
  error: {
    code: 'ACCOUNT_BLOCKED';
    message: string;
    blocked_until: string; // ISO 8601 timestamp
    attempts_remaining: 0;
    retry_after_seconds: number;
  };
}

export interface EmailAvailabilityResponse {
  available: boolean;
  message?: string;
}

export interface UsernameAvailabilityResponse {
  available: boolean;
  message?: string;
}
