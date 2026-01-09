// src/utils/typeGuards.ts

import type { User } from '../types/user';
import type { ApiError, AuthError } from '../types/errors';

/**
 * Type guard to check if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error
  );
}

/**
 * Type guard to check if error is an AuthError
 */
export function isAuthError(error: unknown): error is AuthError {
  return (
    isApiError(error) &&
    'code' in error &&
    typeof error.code === 'string'
  );
}

/**
 * Type guard to check if data is a User object
 */
export function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'username' in data &&
    'email' in data &&
    'is_verified' in data
  );
}

/**
 * Type guard to check if value is a non-null object
 */
export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Type guard to check if value is a non-empty string
 */
export function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}
