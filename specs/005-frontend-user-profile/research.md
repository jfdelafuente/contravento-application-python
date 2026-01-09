# Technology Research & Decisions
**Feature**: Frontend de Autenticación y Perfiles de Usuario
**Created**: 2026-01-08
**Status**: COMPLETED

## Overview

This document records all technology decisions, alternatives considered, and rationale for the frontend authentication implementation. Each decision is mapped to specific functional requirements and success criteria from [spec.md](./spec.md).

---

## 1. React State Management Pattern

### Decision: **Context API** ✅

### Rationale

- **Scope-appropriate**: Authentication state is global but limited (user object, loading state, error state)
- **Zero dependencies**: No additional bundle size
- **TypeScript-friendly**: Excellent type inference with typed contexts
- **Sufficient performance**: Re-renders isolated to components consuming auth context
- **Team familiarity**: Standard React API, no learning curve

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Context API** | Zero deps, simple, built-in | Can cause unnecessary re-renders if not optimized | ✅ **SELECTED** |
| **Redux Toolkit** | Mature, DevTools, middleware ecosystem | Overkill for auth-only state, 15KB+ bundle | ❌ Too complex |
| **Zustand** | Lightweight (1KB), no Provider hell | Another dependency, team unfamiliarity | ❌ Unnecessary |
| **Jotai/Recoil** | Atomic state, modern patterns | Experimental, overkill for simple auth | ❌ Over-engineered |

### Implementation Pattern

```typescript
// src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/authService';

interface User {
  id: string;
  username: string;
  email: string;
  is_verified: boolean;
  profile?: {
    full_name?: string;
    photo_url?: string;
  };
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, rememberMe: boolean) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check auth status on mount (validates HttpOnly cookie)
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = async (email: string, password: string, rememberMe: boolean) => {
    const userData = await authService.login(email, password, rememberMe);
    setUser(userData);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const refreshUser = async () => {
    const currentUser = await authService.getCurrentUser();
    setUser(currentUser);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

### Success Criteria Mapping
- **SC-002**: Auth state persists across page reloads via HttpOnly cookie check
- **SC-019**: Login completes in <2s (no state management overhead)

---

## 2. Form Validation Library

### Decision: **React Hook Form** ✅

### Rationale

- **Performance**: Uncontrolled inputs minimize re-renders (critical for debounced validation)
- **TypeScript**: First-class TypeScript support with full type inference
- **Bundle size**: 8.5KB gzipped (vs Formik's 13KB)
- **Debounced validation**: Built-in support via `mode: 'onChange'` + custom async validators
- **Error handling**: Granular field-level errors align with FR-007, FR-008
- **Less boilerplate**: Simple API compared to Formik's `<Field>` components

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **React Hook Form** | Best performance, TypeScript, small bundle | Uncontrolled (less React-like) | ✅ **SELECTED** |
| **Formik** | Popular, controlled inputs | Heavier bundle, more re-renders | ❌ Performance concerns |
| **Custom Hooks** | Full control, zero deps | Reinventing wheel, maintenance burden | ❌ Not justified |

### Implementation Pattern

```typescript
// src/components/auth/RegisterForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useDebounce } from '../hooks/useDebounce';
import { authService } from '../services/authService';

const registerSchema = z.object({
  username: z.string()
    .min(3, 'El nombre de usuario debe tener al menos 3 caracteres')
    .max(30, 'El nombre de usuario no puede exceder 30 caracteres')
    .regex(/^[a-zA-Z0-9_]+$/, 'Solo letras, números y guiones bajos'),
  email: z.string().email('Formato de email inválido'),
  password: z.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .max(128, 'La contraseña no puede exceder 128 caracteres'),
  confirmPassword: z.string(),
  turnstileToken: z.string().min(1, 'Verificación CAPTCHA requerida'),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterForm = () => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    mode: 'onTouched', // Validate on blur, not on every keystroke
  });

  const password = watch('password');
  const email = watch('email');

  // Debounced async email validation (FR-003)
  const debouncedEmail = useDebounce(email, 500);
  useEffect(() => {
    if (debouncedEmail && !errors.email) {
      authService.checkEmailAvailability(debouncedEmail).then(available => {
        if (!available) {
          setError('email', {
            type: 'manual',
            message: 'Este email ya está registrado'
          });
        }
      });
    }
  }, [debouncedEmail]);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await authService.register(data);
      // Navigate to verification page
    } catch (error: any) {
      if (error.response?.data?.field) {
        setError(error.response.data.field, {
          message: error.response.data.message,
        });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('username')} />
      {errors.username && <span>{errors.username.message}</span>}

      <input type="email" {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}
      <PasswordStrengthMeter password={password} />

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Registrando...' : 'Crear cuenta'}
      </button>
    </form>
  );
};
```

### Dependencies

```json
{
  "react-hook-form": "^7.50.0",
  "@hookform/resolvers": "^3.3.4",
  "zod": "^3.22.4"
}
```

### Success Criteria Mapping
- **SC-003**: Form validation <300ms (uncontrolled inputs + debouncing)
- **SC-010**: Field-level error messages (React Hook Form error state)

---

## 3. HTTP Client Configuration

### Decision: **Axios with Interceptors** ✅

### Rationale

- **Automatic token refresh**: Response interceptor handles 401 errors and refreshes access token transparently
- **Request/response transformation**: Consistent error handling across all endpoints
- **CSRF protection**: Axios automatically includes CSRF tokens from cookies
- **TypeScript support**: Full type inference for request/response
- **Mature ecosystem**: Widely used, well-documented, stable API
- **Credentials handling**: `withCredentials: true` sends HttpOnly cookies automatically

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Axios** | Interceptors, mature, TypeScript support | 13KB bundle | ✅ **SELECTED** |
| **Native Fetch** | Zero deps, built-in | No interceptors, manual retry logic | ❌ Too much boilerplate |
| **ky** | Modern, retries, timeout | Less mature, unfamiliar | ❌ Not justified |
| **TanStack Query** | Caching, optimistic updates | Overkill for auth-only, 40KB+ | ❌ Over-engineered |

### Implementation Pattern

```typescript
// src/services/api.ts
import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true, // CRITICAL: Send HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // If 401 and not already retrying
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Call refresh endpoint (backend sets new access token cookie)
        await api.post('/auth/refresh-token');

        // Retry original request with new access token
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export { api };
```

```typescript
// src/services/authService.ts
import { api } from './api';

interface LoginResponse {
  user: User;
  message: string;
}

export const authService = {
  async login(email: string, password: string, rememberMe: boolean): Promise<User> {
    const { data } = await api.post<LoginResponse>('/auth/login', {
      email,
      password,
      remember_me: rememberMe,
    });
    return data.user;
  },

  async register(userData: RegisterData): Promise<void> {
    await api.post('/auth/register', userData);
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },

  async refreshToken(): Promise<void> {
    await api.post('/auth/refresh-token');
  },

  async checkEmailAvailability(email: string): Promise<boolean> {
    const { data } = await api.get(`/auth/check-email?email=${email}`);
    return data.available;
  },
};
```

### TypeScript Types

```typescript
// src/types/api.ts
declare module 'axios' {
  export interface AxiosRequestConfig {
    _retry?: boolean; // Track retry attempts
  }
}
```

### Success Criteria Mapping
- **SC-019**: Login request completes in <2s (Axios timeout: 5s default)
- **SC-020**: HttpOnly cookies sent automatically with `withCredentials: true`

---

## 4. Cloudflare Turnstile Integration

### Decision: **@marsidev/react-turnstile** ✅

### Rationale

- **Official-like wrapper**: Maintained React wrapper for Cloudflare Turnstile
- **TypeScript support**: Full type definitions included
- **Invisible mode**: Non-intrusive UX (auto-challenge when needed)
- **Zero user friction**: No puzzle solving for most users
- **Better privacy**: No Google tracking (vs reCAPTCHA)
- **Free tier**: 1M verifications/month (sufficient for MVP)

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **@marsidev/react-turnstile** | React hooks, TypeScript, maintained | Wrapper dependency (2KB) | ✅ **SELECTED** |
| **Manual integration** | No dependency | Manual script loading, cleanup | ❌ Reinventing wheel |
| **reCAPTCHA v3** | Mature, widely used | Google tracking, privacy concerns | ❌ Per spec choice |
| **hCaptcha** | Privacy-focused, accessible | Not specified in requirements | ❌ Not requested |

### Implementation Pattern

```typescript
// src/components/auth/TurnstileWidget.tsx
import { Turnstile, TurnstileInstance } from '@marsidev/react-turnstile';
import { useRef } from 'react';

interface TurnstileWidgetProps {
  onVerify: (token: string) => void;
  onError?: () => void;
}

export const TurnstileWidget = ({ onVerify, onError }: TurnstileWidgetProps) => {
  const turnstileRef = useRef<TurnstileInstance>(null);

  return (
    <Turnstile
      ref={turnstileRef}
      siteKey={import.meta.env.VITE_TURNSTILE_SITE_KEY}
      onSuccess={onVerify}
      onError={() => {
        console.error('Turnstile verification failed');
        onError?.();
      }}
      options={{
        theme: 'light',
        size: 'normal',
        action: 'register', // Different actions for register/login
        appearance: 'always', // or 'interaction-only' for invisible
      }}
    />
  );
};
```

```typescript
// Usage in RegisterForm
import { TurnstileWidget } from './TurnstileWidget';

export const RegisterForm = () => {
  const [turnstileToken, setTurnstileToken] = useState('');

  const handleTurnstileVerify = (token: string) => {
    setTurnstileToken(token);
    // React Hook Form will validate this is not empty
  };

  return (
    <form>
      {/* Other fields */}
      <TurnstileWidget onVerify={handleTurnstileVerify} />
      <button type="submit" disabled={!turnstileToken}>
        Crear cuenta
      </button>
    </form>
  );
};
```

### Environment Variables

```env
# .env.local
VITE_TURNSTILE_SITE_KEY=your_site_key_here
```

### Backend Integration

The backend must verify the token on registration:

```python
# backend/src/api/auth.py (for reference)
import httpx

async def verify_turnstile(token: str, client_ip: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            json={
                'secret': settings.TURNSTILE_SECRET_KEY,
                'response': token,
                'remoteip': client_ip,
            }
        )
        data = response.json()
        return data.get('success', False)
```

### Dependencies

```json
{
  "@marsidev/react-turnstile": "^0.7.0"
}
```

### Success Criteria Mapping
- **FR-014**: CAPTCHA integration for registration
- **SC-006**: Bot prevention with Cloudflare Turnstile

---

## 5. Password Strength Algorithm

### Decision: **Custom Implementation (No Library)** ✅

### Rationale

- **Spec-aligned**: Exact criteria defined in FR-013 (length, uppercase, lowercase, numbers)
- **Symbols excluded**: Per clarification Q2, symbols allowed but NOT considered in strength
- **Lightweight**: ~20 lines of code vs 5KB+ library
- **Visual feedback**: Red/Yellow/Green traffic light system (per clarification Q4)
- **No external dependencies**: Reduces bundle size

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Custom implementation** | Spec-aligned, zero deps | Maintenance responsibility | ✅ **SELECTED** |
| **zxcvbn** | Industry-standard, entropy-based | 400KB bundle, overkill | ❌ Too heavy |
| **check-password-strength** | Lightweight (5KB), configurable | Not aligned with spec criteria | ❌ Misaligned |

### Implementation Pattern

```typescript
// src/utils/passwordStrength.ts
export type PasswordStrength = 'weak' | 'medium' | 'strong';

export interface PasswordStrengthResult {
  strength: PasswordStrength;
  score: number; // 0-4
  feedback: string[];
}

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
    strength = 'weak';
  } else if (score === 3) {
    strength = 'medium';
  } else {
    strength = 'strong'; // score === 4
  }

  return { strength, score, feedback };
};
```

```typescript
// src/components/auth/PasswordStrengthMeter.tsx
import { useMemo } from 'react';
import { calculatePasswordStrength, PasswordStrength } from '../../utils/passwordStrength';
import './PasswordStrengthMeter.css';

interface PasswordStrengthMeterProps {
  password: string;
}

const STRENGTH_CONFIG: Record<PasswordStrength, { label: string; color: string }> = {
  weak: { label: 'Débil', color: '#ef4444' }, // Red
  medium: { label: 'Media', color: '#eab308' }, // Yellow
  strong: { label: 'Fuerte', color: '#22c55e' }, // Green
};

export const PasswordStrengthMeter = ({ password }: PasswordStrengthMeterProps) => {
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
```

```css
/* src/components/auth/PasswordStrengthMeter.css */
.password-strength-meter {
  margin-top: 0.5rem;
}

.strength-bar {
  height: 6px;
  background-color: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-info {
  margin-top: 0.25rem;
  font-size: 0.875rem;
}

.strength-feedback {
  margin-top: 0.5rem;
  padding-left: 1.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}
```

### Success Criteria Mapping
- **FR-013**: Password strength indicator (length, uppercase, lowercase, numbers)
- **SC-004**: Real-time visual feedback (red/yellow/green)

---

## 6. Countdown Timer Implementation

### Decision: **Custom React Hook** ✅

### Rationale

- **Spec requirement**: Account block shows "MM:SS" countdown (per clarification Q8)
- **Simple logic**: setInterval + state management (~30 lines)
- **No library needed**: Libraries like `react-countdown` are overkill (15KB) for simple timer
- **Cleanup handling**: useEffect cleanup prevents memory leaks
- **Reusable**: Can be used for email verification resend countdown

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Custom hook** | Lightweight, full control | Manual implementation | ✅ **SELECTED** |
| **react-countdown** | Feature-rich, tested | 15KB bundle, overkill | ❌ Too heavy |
| **use-countdown** | Smaller (3KB) | Still unnecessary dependency | ❌ Not justified |

### Implementation Pattern

```typescript
// src/hooks/useCountdown.ts
import { useState, useEffect, useCallback } from 'react';

interface UseCountdownOptions {
  initialSeconds: number;
  onComplete?: () => void;
}

interface UseCountdownReturn {
  secondsRemaining: number;
  formattedTime: string; // MM:SS format
  isRunning: boolean;
  start: () => void;
  pause: () => void;
  reset: () => void;
}

export const useCountdown = ({
  initialSeconds,
  onComplete
}: UseCountdownOptions): UseCountdownReturn => {
  const [secondsRemaining, setSecondsRemaining] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isRunning || secondsRemaining <= 0) return;

    const interval = setInterval(() => {
      setSecondsRemaining(prev => {
        if (prev <= 1) {
          setIsRunning(false);
          onComplete?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, secondsRemaining, onComplete]);

  const start = useCallback(() => {
    if (secondsRemaining > 0) {
      setIsRunning(true);
    }
  }, [secondsRemaining]);

  const pause = useCallback(() => {
    setIsRunning(false);
  }, []);

  const reset = useCallback(() => {
    setSecondsRemaining(initialSeconds);
    setIsRunning(false);
  }, [initialSeconds]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return {
    secondsRemaining,
    formattedTime: formatTime(secondsRemaining),
    isRunning,
    start,
    pause,
    reset,
  };
};
```

```typescript
// src/components/auth/AccountBlockedMessage.tsx
import { useEffect } from 'react';
import { useCountdown } from '../../hooks/useCountdown';

interface AccountBlockedMessageProps {
  blockedUntil: string; // ISO timestamp from backend
  onUnblock: () => void;
}

export const AccountBlockedMessage = ({ blockedUntil, onUnblock }: AccountBlockedMessageProps) => {
  const blockedUntilDate = new Date(blockedUntil);
  const initialSeconds = Math.max(0, Math.floor((blockedUntilDate.getTime() - Date.now()) / 1000));

  const { formattedTime, start, secondsRemaining } = useCountdown({
    initialSeconds,
    onComplete: onUnblock,
  });

  useEffect(() => {
    start(); // Auto-start countdown on mount
  }, [start]);

  if (secondsRemaining === 0) return null;

  return (
    <div className="account-blocked-alert" role="alert">
      <h3>Cuenta bloqueada temporalmente</h3>
      <p>
        Has superado el número máximo de intentos de inicio de sesión.
      </p>
      <p className="countdown">
        Tiempo restante: <strong>{formattedTime}</strong>
      </p>
      <p className="help-text">
        Por tu seguridad, inténtalo de nuevo cuando expire el tiempo o
        <a href="/reset-password"> recupera tu contraseña</a>.
      </p>
    </div>
  );
};
```

### Success Criteria Mapping
- **FR-028**: Account block countdown in MM:SS format
- **SC-008**: Clear blocking message with time remaining

---

## 7. Routing Protection Pattern

### Decision: **React Router 6 + Custom ProtectedRoute Component** ✅

### Rationale

- **React Router 6**: Industry standard, tree-shaking, TypeScript support
- **Declarative protection**: `<ProtectedRoute>` wrapper makes intent clear
- **Loading states**: Handles auth check in progress (prevents flash of login screen)
- **Redirect preservation**: Saves intended destination for post-login redirect
- **Email verification enforcement**: Redirects unverified users per clarification Q3

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **React Router 6 + wrapper** | Declarative, standard pattern | Manual implementation | ✅ **SELECTED** |
| **TanStack Router** | Type-safe, modern | Beta, migration cost | ❌ Too new |
| **Route guards (manual)** | Full control | Imperative, error-prone | ❌ Less maintainable |

### Implementation Pattern

```typescript
// src/components/routing/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireVerified?: boolean; // Enforce email verification
}

export const ProtectedRoute = ({
  children,
  requireVerified = true
}: ProtectedRouteProps) => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking auth
  if (isLoading) {
    return <div className="loading-spinner">Cargando...</div>;
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Authenticated but email not verified (per clarification Q3: complete block)
  if (requireVerified && !user?.is_verified) {
    return <Navigate to="/verify-email" replace />;
  }

  // Authenticated and verified - render protected content
  return <>{children}</>;
};
```

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/routing/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { DashboardPage } from './pages/DashboardPage';

export const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};
```

### Post-Login Redirect Pattern

```typescript
// src/pages/LoginPage.tsx
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const onSubmit = async (data: LoginFormData) => {
    await login(data.email, data.password, data.rememberMe);

    // Redirect to intended destination or default to dashboard
    const from = (location.state as any)?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
  };

  // ...
};
```

### Dependencies

```json
{
  "react-router-dom": "^6.21.0"
}
```

### Success Criteria Mapping
- **FR-038**: Unverified users redirected to verification page
- **SC-012**: Protected routes enforce authentication

---

## 8. Bundle Optimization Strategy

### Decision: **Vite + Code Splitting + Lazy Loading** ✅

### Rationale

- **Vite**: Faster dev server (esbuild), optimized production builds (Rollup)
- **Automatic code splitting**: Route-based lazy loading reduces initial bundle
- **Tree-shaking**: Dead code elimination in production
- **Asset optimization**: Auto-minification, image optimization
- **Target bundle**: <200KB initial (auth forms only), <500KB total with all routes

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Vite** | Fastest dev, modern, simple config | Newer ecosystem | ✅ **SELECTED** |
| **Create React App** | Mature, zero config | Slow dev, Webpack bloat | ❌ Outdated |
| **Next.js** | SSR, API routes, optimization | Overkill for SPA, backend separate | ❌ Over-engineered |

### Implementation Pattern

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2020',
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'form-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
        },
      },
    },
    chunkSizeWarningLimit: 500, // Warn if chunk > 500KB
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

```typescript
// src/App.tsx - Lazy load routes
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Eager load critical routes (login/register)
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

// Lazy load non-critical routes
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));

export const App = () => {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Cargando...</div>}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};
```

### Bundle Analysis Commands

```json
{
  "scripts": {
    "build": "vite build",
    "analyze": "vite-bundle-visualizer"
  },
  "devDependencies": {
    "vite-bundle-visualizer": "^0.11.0"
  }
}
```

### Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Initial JS bundle | <200KB | Code splitting, lazy routes |
| Total bundle (all routes) | <500KB | Tree-shaking, minification |
| First Contentful Paint | <1.5s | Inline critical CSS, font preload |
| Time to Interactive | <3s | Defer non-critical JS |
| Lighthouse score | ≥90 | Accessibility, performance, SEO |

### Success Criteria Mapping
- **SC-001**: Registration form loads in <1.5s (optimized bundle)
- **SC-019**: Login request completes in <2s (network + bundle time)

---

## Summary of Decisions

| Category | Decision | Bundle Impact | Rationale |
|----------|----------|---------------|-----------|
| **State Management** | Context API | 0KB | Sufficient for auth-only state |
| **Form Validation** | React Hook Form + Zod | ~12KB | Best performance, TypeScript, debouncing |
| **HTTP Client** | Axios | ~13KB | Automatic token refresh, interceptors |
| **CAPTCHA** | Cloudflare Turnstile | ~2KB | Privacy-focused, invisible, per spec |
| **Password Strength** | Custom implementation | <1KB | Spec-aligned, zero deps |
| **Countdown Timer** | Custom hook | <1KB | Simple logic, no library needed |
| **Routing** | React Router 6 | ~10KB | Industry standard, type-safe |
| **Build Tool** | Vite | 0KB (dev tool) | Fastest dev, optimized builds |
| **Total Dependencies** | — | **~38KB** | Well under 200KB target |

---

## Next Steps

1. ✅ **Phase 0 Complete**: All technology decisions finalized
2. **Phase 1**: Generate design artifacts
   - `data-model.md`: TypeScript interfaces for auth state, user, forms, API responses
   - `contracts/auth-api.yaml`: OpenAPI 3.0 spec for all auth endpoints
   - `quickstart.md`: Development environment setup guide
3. **Phase 2**: Update agent context with React patterns
4. **Phase 3**: Generate `tasks.md` with implementation checklist

---

**Document Status**: ✅ COMPLETE
**Reviewed By**: Implementation Planning Agent
**Approved**: 2026-01-08
