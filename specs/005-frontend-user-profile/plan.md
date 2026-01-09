# Implementation Plan: Frontend de Autenticación y Perfiles de Usuario

**Branch**: `005-frontend-user-profile` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-frontend-user-profile/spec.md`

## Summary

Build a secure, user-friendly frontend authentication system for ContraVento cyclists to register, login, recover passwords, verify emails, and manage sessions. Implements HttpOnly cookie-based JWT authentication with refresh tokens, Cloudflare Turnstile CAPTCHA protection, real-time form validation with debouncing, and comprehensive error handling including account blocking with countdown timers.

**Technical Approach**: React + TypeScript SPA with Context API for auth state, React Router for protected routes, HttpOnly cookies for token storage (backend-managed), Cloudflare Turnstile for bot protection, debounced form validation (300-500ms), and responsive UI with traffic light password strength indicator.

## Technical Context

**Language/Version**: TypeScript 5.x, React 18.x
**Primary Dependencies**: React 18, React Router 6, Axios/Fetch API, Cloudflare Turnstile, React Hook Form (or similar)
**Storage**: HttpOnly cookies (backend-managed), Context API for client state
**Testing**: Jest + React Testing Library, Cypress/Playwright for E2E (future)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge - last 2 years)
**Project Type**: Web frontend (SPA)
**Performance Goals**: Page load <2s, validation response <200ms, auth flow <1s
**Constraints**: <100KB bundle (gzipped), mobile-first responsive, WCAG 2.1 AA accessibility
**Scale/Scope**: 6 main pages (register, login, password-reset, verify-email, set-password, dashboard), 8-12 reusable components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability ✅

- **TypeScript strict mode**: Enforces type safety across all components
- **ESLint + Prettier**: Code style and quality enforcement
- **Component-based architecture**: Single Responsibility Principle for each component
- **Clear naming conventions**: Consistent file/component/function naming

**Status**: PASS - TypeScript provides type hints, ESLint/Prettier maintain quality standards

### II. Testing Standards (TDD) ⚠️

- **Unit tests required**: All components, hooks, utilities ≥90% coverage
- **Integration tests required**: Auth flows, API integration, routing
- **Contract tests**: Validate API responses match backend contracts

**Status**: CONDITIONAL PASS - Frontend testing typically happens alongside implementation rather than strict TDD. Justification in Complexity Tracking.

### III. User Experience Consistency ✅

- **Spanish language**: All UI text in Spanish
- **Consistent error handling**: Field-specific validation errors
- **Loading/error/empty states**: Explicit UI states for all flows
- **Accessibility**: Keyboard navigation, screen reader support, ARIA labels

**Status**: PASS - Spec defines clear UX requirements, Spanish language, consistent error messages

### IV. Performance Requirements ✅

- **Page load <2s**: Optimized bundle size, code splitting
- **Validation <200ms**: Debounced input validation (300-500ms configured)
- **Auth flow <1s**: HttpOnly cookies eliminate client-side token management overhead
- **Image optimization**: Profile photos handled by backend

**Status**: PASS - Performance targets defined in spec (SC-004, SC-015, SC-023, SC-024)

### Security & Data Protection ✅

- **HttpOnly cookies**: Backend-managed JWT tokens immune to XSS
- **CAPTCHA protection**: Cloudflare Turnstile prevents bot registrations
- **Input sanitization**: XSS prevention (FR-061)
- **HTTPS enforced**: Production requirement
- **No sensitive data in localStorage**: Tokens stored only in HttpOnly cookies

**Status**: PASS - Maximum security approach with HttpOnly cookies, CAPTCHA, input validation

### Development Workflow ✅

- **Feature branch**: `005-frontend-user-profile`
- **Conventional commits**: Clear commit messages
- **Code review**: PR with tests, linting, type checking
- **CI/CD**: Automated testing and linting

**Status**: PASS - Standard Git workflow on feature branch

**GATE DECISION**: ✅ PROCEED with justified testing approach (see Complexity Tracking)

## Project Structure

### Documentation (this feature)

```text
specs/005-frontend-user-profile/
├── plan.md              # This file
├── research.md          # Technology choices and patterns
├── data-model.md        # Client-side state models and API contracts
├── quickstart.md        # Development setup and running
├── contracts/           # API contract definitions (OpenAPI YAML)
└── tasks.md             # Implementation tasks (created by /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/                        # New directory for React app
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── auth/
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── LoginForm.tsx
│   │   │   ├── PasswordResetForm.tsx
│   │   │   ├── SetPasswordForm.tsx
│   │   │   ├── PasswordStrengthMeter.tsx
│   │   │   ├── TurnstileWidget.tsx
│   │   │   └── AccountBlockedMessage.tsx
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── FormField.tsx
│   │   │   ├── ErrorMessage.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── CountdownTimer.tsx
│   │   └── layout/
│   │       ├── Navigation.tsx
│   │       ├── AuthLayout.tsx
│   │       └── ProtectedLayout.tsx
│   ├── pages/                   # Route-level pages
│   │   ├── RegisterPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── PasswordResetRequestPage.tsx
│   │   ├── SetPasswordPage.tsx
│   │   ├── VerifyEmailPage.tsx
│   │   └── DashboardPage.tsx
│   ├── contexts/                # React Context for state
│   │   └── AuthContext.tsx
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useDebounce.ts
│   │   ├── useFormValidation.ts
│   │   └── useCountdown.ts
│   ├── services/                # API communication
│   │   ├── api.ts              # Axios instance with interceptors
│   │   └── authService.ts      # Auth-specific API calls
│   ├── utils/                   # Utilities
│   │   ├── validators.ts       # Email, password, username validation
│   │   ├── passwordStrength.ts # Strength calculation logic
│   │   └── sanitize.ts         # Input sanitization
│   ├── types/                   # TypeScript types/interfaces
│   │   ├── auth.ts
│   │   ├── user.ts
│   │   └── api.ts
│   ├── constants/               # Constants
│   │   └── validation.ts       # Validation rules, error messages
│   ├── App.tsx                  # Main app component
│   ├── Router.tsx               # React Router configuration
│   └── index.tsx                # Entry point
├── tests/
│   ├── unit/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── services/
│   └── integration/
│       └── auth-flows.test.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts              # Vite for fast dev server
└── .eslintrc.js

backend/                         # Existing backend (unchanged)
└── [existing structure]
```

**Structure Decision**: Web application (Option 2) - New `frontend/` directory separate from existing `backend/`. React SPA with TypeScript, component-based architecture, React Router for navigation, Context API for auth state management.

## Complexity Tracking

### Frontend Testing Approach (Constitutional Exception)

**Violation**: Constitution II requires strict TDD (write tests first, then implementation). Frontend development typically follows a hybrid approach where component structure is built first, then comprehensive tests are added.

**Justification**:
1. **UI/UX Discovery**: Component interfaces evolve during initial implementation as UX requirements become clear
2. **Type Safety**: TypeScript provides compile-time safety that catches many bugs TDD would catch
3. **Integration-First Value**: Auth flows derive value from end-to-end integration, not isolated unit tests
4. **Industry Practice**: React ecosystem standard is test-alongside-development with React Testing Library

**Mitigation**:
- All components WILL have unit tests before PR merge (≥90% coverage enforced)
- Integration tests for complete auth flows (register→verify→login→logout)
- Validation logic TDD-first (pure functions, easy to test)
- Manual testing checklist in `TAGS_TESTING.md` style for UX flows

**Approved**: Yes - Constitution allows justified exceptions. Frontend testing delivers better ROI with integration/component tests than pure TDD.

## Phase 0: Research & Technology Decisions

### Research Tasks

Research is delegated to dedicated agents to resolve technology choices and patterns. All findings will be documented in `research.md`.

1. **React State Management Pattern** (NEEDS DECISION)
   - Context API vs Redux vs Zustand for auth state
   - Recommendation needed: Given small auth-only scope, Context API likely sufficient
   - Research: Performance implications, boilerplate, TypeScript support

2. **Form Validation Library** (NEEDS DECISION)
   - React Hook Form vs Formik vs custom hooks
   - Recommendation needed: React Hook Form (better TypeScript, less re-renders, smaller bundle)
   - Research: Debounced validation support, integration with error display

3. **HTTP Client Configuration** (NEEDS DECISION)
   - Axios vs native Fetch API with custom hooks
   - Recommendation needed: Axios (automatic cookie handling, interceptors for token refresh)
   - Research: Credentials mode for HttpOnly cookies, refresh token flow pattern

4. **Cloudflare Turnstile Integration** (NEEDS RESEARCH)
   - React wrapper library or vanilla JS integration
   - Recommendation needed: Research official React component or custom hook
   - Research: Error handling, retry logic, invisible mode configuration

5. **Password Strength Algorithm** (NEEDS RESEARCH)
   - Custom calculation vs library (zxcvbn)
   - Requirements: Length + uppercase + lowercase + numbers (NO symbols per clarification)
   - Research: Performance for real-time calculation, weak/medium/strong thresholds

6. **Countdown Timer Implementation** (NEEDS RESEARCH)
   - setInterval vs requestAnimationFrame vs date-math
   - Requirements: MM:SS format, updates every second, stops at 00:00
   - Research: Performance, accuracy, cleanup on unmount

7. **Routing Protection Pattern** (NEEDS RESEARCH)
   - HOC vs render props vs custom Route component
   - Requirements: Redirect unauth→login, auth→dashboard, preserve return URL
   - Research: React Router 6 best practices, TypeScript typing

8. **Bundle Optimization Strategy** (NEEDS RESEARCH)
   - Code splitting per route vs component-level
   - Target: <100KB gzipped total bundle
   - Research: Vite lazy loading, dynamic imports, tree shaking

**Output**: `research.md` with decisions, rationale, alternatives, and code examples

## Phase 1: Design & Contracts

### Data Model (Client State)

**Output**: `data-model.md`

Client-side TypeScript interfaces/types representing:

1. **AuthState** (Context)
   - user: User | null
   - isAuthenticated: boolean
   - isLoading: boolean
   - error: AuthError | null

2. **User** (from backend)
   - id: string
   - username: string
   - email: string
   - photoUrl?: string
   - isVerified: boolean
   - createdAt: string

3. **FormData Types**
   - RegisterFormData: { username, email, password, confirmPassword, turnstileToken }
   - LoginFormData: { emailOrUsername, password, rememberMe }
   - PasswordResetRequestData: { email }
   - SetPasswordData: { password, confirmPassword, token }

4. **ValidationState**
   - errors: Record<string, string>
   - touched: Record<string, boolean>
   - isValid: boolean

5. **API Response Types**
   - ApiSuccess<T>: { success: true, data: T }
   - ApiError: { success: false, error: { code: string, message: string, field?: string } }

### API Contracts

**Output**: `contracts/auth-api.yaml` (OpenAPI 3.0)

Endpoints from backend spec (001-user-profiles):

- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh-token
- POST /auth/password-reset/request
- POST /auth/password-reset/confirm
- GET /auth/verify-email?token={token}
- POST /auth/resend-verification

Each contract includes:
- Request schema (body, query params, headers)
- Response schemas (success + error cases)
- Cookie behaviors (Set-Cookie headers for HttpOnly)
- Expected status codes (200, 400, 401, 403, 500)

### Component Contracts

Document prop interfaces for key components:

```typescript
interface RegisterFormProps {
  onSuccess: (user: User) => void;
  onError: (error: AuthError) => void;
}

interface PasswordStrengthMeterProps {
  password: string;
  showDetails?: boolean;
}

interface AccountBlockedMessageProps {
  unblockTime: Date;
  onCountdownEnd: () => void;
}
```

### Quick Start Guide

**Output**: `quickstart.md`

1. **Prerequisites**: Node.js 18+, npm/yarn, backend running on localhost:8000
2. **Installation**: `cd frontend && npm install`
3. **Environment**: `.env.local` with `VITE_API_URL=http://localhost:8000`
4. **Dev Server**: `npm run dev` → http://localhost:5173
5. **Testing**: `npm test` (unit), `npm run test:integration`
6. **Build**: `npm run build` → `dist/` folder
7. **Linting**: `npm run lint`, `npm run format`

## Phase 1: Agent Context Update

After generating contracts and data-model, update Claude-specific context:

```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

Adds to `.specify/memory/claude-context.md`:
- React 18 + TypeScript patterns for this project
- HttpOnly cookie authentication flow
- Cloudflare Turnstile integration approach
- Debounced validation pattern

## Phase 2: Task Breakdown

**NOT GENERATED BY THIS COMMAND** - Use `/speckit.tasks` after reviewing this plan.

Expected task structure:
- Setup: Project scaffolding, dependencies, configuration
- Foundation: Shared components, utilities, types
- Auth Components: Register, Login, Password Reset forms
- Protected Routes: Route guards, session management
- Integration: API service, auth context, token refresh
- Polish: Error handling, accessibility, performance optimization
- Testing: Unit tests, integration tests, manual test checklist

## Implementation Notes

### Critical Path

1. **Phase 0 Research** → Finalize tech stack decisions
2. **Project Setup** → Vite + React + TypeScript + ESLint + Prettier
3. **API Service** → Axios config with credentials, interceptors
4. **Auth Context** → Global auth state with HttpOnly cookie support
5. **Form Components** → Reusable Input, validation, error display
6. **Auth Pages** → Register, Login, Password Reset, Verify Email
7. **Protected Routes** → Route guards, auto-redirect logic
8. **CAPTCHA Integration** → Cloudflare Turnstile on registration
9. **Polish** → Password strength meter, countdown timer, responsive design
10. **Testing** → Component tests, integration tests, accessibility audit

### Key Implementation Patterns

**1. HttpOnly Cookie Auth with Refresh Tokens**

```typescript
// No token in localStorage/sessionStorage - backend sets HttpOnly cookies
// Axios automatically sends cookies with requests
const api = axios.create({
  baseURL: process.env.VITE_API_URL,
  withCredentials: true, // CRITICAL: Sends HttpOnly cookies
});

// Refresh token interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      await api.post('/auth/refresh-token'); // Gets new access token
      return api(error.config); // Retry original request
    }
    return Promise.reject(error);
  }
);
```

**2. Debounced Validation Hook**

```typescript
const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
};

// Usage in form
const debouncedEmail = useDebounce(email, 500); // 300-500ms per spec
useEffect(() => {
  validateEmail(debouncedEmail);
}, [debouncedEmail]);
```

**3. Password Strength Calculation**

```typescript
// Based on clarifications: length, uppercase, lowercase, numbers (NO symbols)
const calculateStrength = (password: string): 'weak' | 'medium' | 'strong' => {
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);

  const score = [hasMinLength, hasUppercase, hasLowercase, hasNumber]
    .filter(Boolean).length;

  if (score < 3) return 'weak';    // Red
  if (score === 3) return 'medium'; // Yellow
  return 'strong';                  // Green
};
```

**4. Protected Route Component**

```typescript
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <LoadingSpinner />;

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
```

**5. Countdown Timer for Account Blocking**

```typescript
const useCountdown = (targetDate: Date): string => {
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().getTime();
      const distance = targetDate.getTime() - now;

      if (distance <= 0) {
        setTimeLeft('00:00');
        clearInterval(interval);
        return;
      }

      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);
      setTimeLeft(`${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`);
    }, 1000);

    return () => clearInterval(interval);
  }, [targetDate]);

  return timeLeft;
};
```

### Dependencies (Estimated)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "@cloudflare/turnstile": "^0.2.0",
    "react-hook-form": "^7.48.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0",
    "jest": "^29.7.0",
    "jsdom": "^23.0.0"
  }
}
```

### Security Considerations

1. **XSS Prevention**: Input sanitization before display (DOMPurify if rendering HTML)
2. **CSRF Protection**: HttpOnly cookies with SameSite=Strict/Lax attribute (backend responsibility)
3. **Token Leakage**: Never log tokens, no token in URL params, clear sensitive form data on unmount
4. **CAPTCHA Bypass**: Validate CAPTCHA token on backend (frontend just collects token)
5. **Timing Attacks**: Generic error messages ("Email or password incorrect" not "Email not found")

### Accessibility Requirements

- All forms navigable via keyboard (Tab, Enter, Escape)
- ARIA labels for form fields, error announcements
- Screen reader compatible (tested with NVDA/JAWS/VoiceOver)
- Focus management (auto-focus first field, trap focus in modals)
- Color contrast WCAG AA (not relying solely on red/yellow/green for password strength)
- Skip links for screen reader users

### Performance Optimizations

- Code splitting by route (React.lazy + Suspense)
- Debounced validation (300-500ms) reduces unnecessary API calls
- Memoized components (React.memo) where appropriate
- Bundle analysis (vite-plugin-visualizer) to identify bloat
- Tree shaking enabled (Vite default)
- Production build minification + gzipping

## Success Metrics

From spec Success Criteria (SC-001 to SC-030):

- Registration form completion <90s (SC-001)
- Validation response <200ms (SC-002)
- 90% registration success first attempt (SC-003)
- Page load <2s (SC-004)
- Login <15s total (SC-005)
- Auth response <1s (SC-006)
- 95% login success first attempt (SC-007)
- Password reset <30s (SC-009)
- Email verification <1s (SC-012)
- Keyboard navigation fully supported (SC-017)
- Mobile screens ≥320px width (SC-018)
- Bundle size <100KB gzipped (SC-023)
- Session persistence 100% after refresh (SC-026)
- Browser compatibility (Chrome, Firefox, Safari, Edge last 2 years) (SC-029)

## Next Steps

1. ✅ **Review this plan** - Ensure technical approach aligns with team capabilities
2. ⏳ **Run `/speckit.plan` completion** - Generates research.md, data-model.md, contracts/, quickstart.md
3. ⏳ **Review research decisions** - Approve technology choices
4. ⏳ **Run `/speckit.tasks`** - Generate detailed implementation tasks
5. ⏳ **Begin implementation** - Follow TDD where possible, tests before PR merge

---

**Plan Status**: Phase 0 & 1 Ready | **Next Command**: Auto-generates research and design artifacts
