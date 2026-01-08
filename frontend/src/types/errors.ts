// src/types/errors.ts

// Re-export auth error types
export type {
  AuthError,
  AuthErrorCode,
} from './auth';

export { AUTH_ERROR_MESSAGES } from './auth';

// Re-export API error types
export type {
  ApiError,
  FieldError,
} from './api';
