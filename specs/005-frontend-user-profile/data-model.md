# Frontend Data Model: Autenticación y Perfiles de Usuario
**Feature**: 005-frontend-user-profile
**Created**: 2026-01-08
**Status**: APPROVED

## Overview

This document defines all TypeScript interfaces, types, and data structures for the frontend authentication system. These types ensure type safety across components, services, and state management.

---

## Table of Contents

1. [User & Profile Types](#user--profile-types)
2. [Authentication State Types](#authentication-state-types)
3. [Form Data Types](#form-data-types)
4. [Validation Types](#validation-types)
5. [API Request/Response Types](#api-requestresponse-types)
6. [Error Types](#error-types)
7. [CAPTCHA Types](#captcha-types)
8. [Password Strength Types](#password-strength-types)

---

## 1. User & Profile Types

### User Entity

Represents the authenticated user with profile information.

```typescript
// src/types/user.ts

export interface User {
  /** Unique user identifier (UUID from backend) */
  id: string;

  /** Unique username (3-30 alphanumeric + underscore) */
  username: string;

  /** User email address */
  email: string;

  /** Email verification status (per FR-008) */
  is_verified: boolean;

  /** Account creation timestamp */
  created_at: string; // ISO 8601

  /** Optional profile data */
  profile?: UserProfile;

  /** Optional statistics */
  stats?: UserStats;
}

export interface UserProfile {
  /** Full name (optional) */
  full_name?: string;

  /** Profile photo URL */
  photo_url?: string;

  /** Short biography (max 500 chars) */
  bio?: string;

  /** User location */
  location?: string;

  /** Social media links */
  social_links?: {
    instagram?: string;
    strava?: string;
    website?: string;
  };
}

export interface UserStats {
  /** Total trips published */
  trip_count: number;

  /** Total distance cycled (km) */
  total_distance_km: number;

  /** Number of followers */
  followers_count: number;

  /** Number of users following */
  following_count: number;
}
```

---

## 2. Authentication State Types

### AuthContext State

Global authentication state managed by Context API.

```typescript
// src/types/auth.ts

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
```

### Session Metadata

Information about the current session.

```typescript
export interface SessionMetadata {
  /** Access token expiration (client-side tracking) */
  access_token_expires_at?: number; // Unix timestamp

  /** Whether "Remember Me" is active */
  remember_me: boolean;

  /** Last activity timestamp for idle detection */
  last_activity_at: number; // Unix timestamp
}
```

---

## 3. Form Data Types

### Registration Form

```typescript
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
```

### Login Form

```typescript
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
```

### Password Reset Forms

```typescript
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
```

---

## 4. Validation Types

### Field Validation State

Real-time validation state for form fields (per FR-003, FR-012).

```typescript
// src/types/validation.ts

export type ValidationStatus = 'idle' | 'validating' | 'valid' | 'invalid';

export interface FieldValidationState {
  /** Current validation status */
  status: ValidationStatus;

  /** Error message (if invalid) */
  message?: string;

  /** Success message (if valid and explicitly shown) */
  successMessage?: string;

  /** Whether field has been touched/blurred */
  touched: boolean;

  /** Whether field is currently being validated (async) */
  isValidating: boolean;
}

export interface FormValidationState {
  /** Map of field names to validation state */
  fields: Record<string, FieldValidationState>;

  /** Overall form validity */
  isValid: boolean;

  /** Whether form has been submitted */
  isSubmitted: boolean;
}
```

### Email Availability Check

```typescript
export interface EmailAvailabilityResponse {
  available: boolean;
  message?: string;
}

export interface UsernameAvailabilityResponse {
  available: boolean;
  message?: string;
}
```

---

## 5. API Request/Response Types

### Standard API Response Wrapper

All API responses follow this structure (per Constitution III).

```typescript
// src/types/api.ts

export interface ApiResponse<T = any> {
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
```

### Authentication Endpoints

```typescript
// POST /auth/register
export interface RegisterResponse {
  message: string;
  user: {
    id: string;
    username: string;
    email: string;
    is_verified: false;
  };
}

// POST /auth/login
export interface LoginResponse {
  message: string;
  user: User;
  // Note: Tokens are HttpOnly cookies, not in response body
}

// POST /auth/logout
export interface LogoutResponse {
  message: string;
}

// POST /auth/refresh-token
export interface RefreshTokenResponse {
  message: string;
  // New access token set via HttpOnly cookie
}

// GET /auth/me
export type CurrentUserResponse = User;

// POST /auth/verify-email
export interface VerifyEmailResponse {
  message: string;
  user: User;
}

// POST /auth/resend-verification
export interface ResendVerificationResponse {
  message: string;
  email_sent_to: string;
}

// POST /auth/forgot-password
export interface ForgotPasswordResponse {
  message: string;
  email_sent_to: string;
}

// POST /auth/reset-password
export interface ResetPasswordResponse {
  message: string;
}
```

### Account Blocking Response

```typescript
export interface AccountBlockedResponse {
  error: {
    code: 'ACCOUNT_BLOCKED';
    message: string;
    blocked_until: string; // ISO 8601 timestamp
    attempts_remaining: 0;
    retry_after_seconds: number;
  };
}
```

---

## 6. Error Types

### Authentication Errors

```typescript
// src/types/errors.ts

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
  details?: Record<string, any>;
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
```

### Error Mapping Utility

```typescript
/**
 * Maps backend error codes to user-friendly Spanish messages
 */
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
```

---

## 7. CAPTCHA Types

### Cloudflare Turnstile

```typescript
// src/types/turnstile.ts

export interface TurnstileOptions {
  /** Turnstile site key */
  siteKey: string;

  /** Theme (light/dark/auto) */
  theme?: 'light' | 'dark' | 'auto';

  /** Widget size */
  size?: 'normal' | 'compact';

  /** Action name (for analytics) */
  action?: string;

  /** Appearance mode */
  appearance?: 'always' | 'execute' | 'interaction-only';

  /** Language code */
  language?: string;
}

export interface TurnstileCallbacks {
  /** Called when verification succeeds */
  onSuccess: (token: string) => void;

  /** Called when verification fails */
  onError?: (error: string) => void;

  /** Called when token expires */
  onExpire?: () => void;

  /** Called when challenge loads */
  onLoad?: () => void;
}

export interface TurnstileWidgetProps extends TurnstileOptions, TurnstileCallbacks {
  /** Optional ref to Turnstile instance */
  ref?: React.Ref<TurnstileInstance>;
}

export interface TurnstileInstance {
  /** Reset the widget */
  reset: () => void;

  /** Remove the widget */
  remove: () => void;

  /** Get current token */
  getResponse: () => string | undefined;
}
```

---

## 8. Password Strength Types

### Password Strength Calculation

```typescript
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
```

---

## 9. Component Prop Types

### Common Component Props

```typescript
// src/types/components.ts

export interface BaseFormProps {
  /** Form submission handler */
  onSubmit: (data: any) => Promise<void>;

  /** Loading state */
  isLoading?: boolean;

  /** Error message */
  error?: string | null;

  /** Success message */
  successMessage?: string | null;
}

export interface PasswordInputProps {
  /** Input value */
  value: string;

  /** Change handler */
  onChange: (value: string) => void;

  /** Error message */
  error?: string;

  /** Whether to show strength meter */
  showStrengthMeter?: boolean;

  /** Whether field is disabled */
  disabled?: boolean;

  /** Placeholder text */
  placeholder?: string;

  /** Input name */
  name?: string;
}

export interface AccountBlockedMessageProps {
  /** ISO timestamp when block expires */
  blockedUntil: string;

  /** Callback when block expires */
  onUnblock: () => void;

  /** Number of failed attempts */
  attemptCount?: number;
}
```

---

## 10. Utility Types

### Debounce Hook

```typescript
// src/types/hooks.ts

export interface UseDebounceOptions {
  /** Delay in milliseconds (default: 500) */
  delay?: number;

  /** Leading edge trigger */
  leading?: boolean;

  /** Trailing edge trigger */
  trailing?: boolean;
}

export type DebouncedFunction<T extends (...args: any[]) => any> = {
  (...args: Parameters<T>): void;
  cancel: () => void;
  flush: () => void;
};
```

### Countdown Hook

```typescript
export interface UseCountdownOptions {
  /** Initial seconds */
  initialSeconds: number;

  /** Callback when countdown completes */
  onComplete?: () => void;

  /** Auto-start on mount */
  autoStart?: boolean;
}

export interface UseCountdownReturn {
  /** Seconds remaining */
  secondsRemaining: number;

  /** Formatted time (MM:SS) */
  formattedTime: string;

  /** Whether countdown is running */
  isRunning: boolean;

  /** Start countdown */
  start: () => void;

  /** Pause countdown */
  pause: () => void;

  /** Reset to initial value */
  reset: () => void;
}
```

### Auth Hook

```typescript
export interface UseAuthReturn extends AuthContextType {
  /** Check if user has verified email */
  isEmailVerified: boolean;

  /** Check if session is expired (client-side heuristic) */
  isSessionExpired: boolean;

  /** Manually trigger token refresh */
  refreshToken: () => Promise<void>;
}
```

---

## 11. Route Types

### Protected Route Props

```typescript
// src/types/routing.ts

export interface ProtectedRouteProps {
  /** Child components to render if authenticated */
  children: React.ReactNode;

  /** Whether email verification is required (default: true) */
  requireVerified?: boolean;

  /** Redirect path if not authenticated (default: /login) */
  redirectTo?: string;

  /** Loading component while checking auth */
  loadingComponent?: React.ReactNode;
}

export interface LocationState {
  /** Previous location for post-login redirect */
  from?: {
    pathname: string;
    search?: string;
  };
}
```

---

## 12. Environment Variables

### Vite Environment Types

```typescript
// src/types/env.d.ts

/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend API base URL */
  readonly VITE_API_URL: string;

  /** Cloudflare Turnstile site key */
  readonly VITE_TURNSTILE_SITE_KEY: string;

  /** Environment (development/staging/production) */
  readonly VITE_ENV: 'development' | 'staging' | 'production';

  /** Enable debug logging */
  readonly VITE_DEBUG?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

---

## 13. Axios Configuration Types

### Extended Axios Config

```typescript
// src/types/axios.d.ts

import 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    /** Track retry attempts for refresh token logic */
    _retry?: boolean;

    /** Skip automatic token refresh for this request */
    _skipAuthRefresh?: boolean;
  }
}
```

---

## Type Relationships Diagram

```
User
 ├── UserProfile (optional)
 └── UserStats (optional)

AuthContextType
 ├── user: User | null
 ├── isLoading: boolean
 ├── isAuthenticated: boolean
 └── methods: login, register, logout, etc.

RegisterFormData
 ├── username: string
 ├── email: string
 ├── password: string
 ├── confirmPassword: string
 ├── turnstileToken: string
 └── acceptTerms: boolean

ApiResponse<T>
 ├── success: boolean
 ├── data?: T
 ├── error?: ApiError
 └── meta?: ApiResponseMetadata

PasswordStrengthResult
 ├── strength: 'weak' | 'medium' | 'strong'
 ├── score: number (0-4)
 └── feedback: string[]
```

---

## Implementation Notes

### Type Safety Guidelines

1. **No `any` types**: Use `unknown` for truly unknown data, then narrow with type guards
2. **Strict null checks**: All types assume `strictNullChecks: true` in tsconfig.json
3. **Discriminated unions**: Use for error handling and loading states
4. **Readonly where applicable**: Mark props and config objects as `readonly`
5. **Branded types**: Consider for sensitive data (tokens, IDs) to prevent mixing

### Example Type Guard

```typescript
// src/utils/typeGuards.ts

export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error
  );
}

export function isAuthError(error: unknown): error is AuthError {
  return (
    isApiError(error) &&
    'code' in error &&
    typeof error.code === 'string' &&
    error.code in AUTH_ERROR_MESSAGES
  );
}

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
```

---

## Success Criteria Mapping

- **FR-001, FR-002**: User, UserProfile types support registration and profile data
- **FR-003, FR-007**: FieldValidationState supports real-time validation
- **FR-013**: PasswordStrengthResult supports strength meter
- **FR-014**: TurnstileOptions and callbacks for CAPTCHA integration
- **FR-020**: LoginFormData with `rememberMe` field
- **FR-028**: AccountBlockedResponse with `blocked_until` timestamp
- **SC-010**: ApiError with field-specific validation errors
- **SC-020**: Types assume HttpOnly cookies (no token in localStorage)

---

**Document Status**: ✅ COMPLETE
**TypeScript Version**: 5.3+
**Reviewed By**: Implementation Planning Agent
**Approved**: 2026-01-08
