# Tasks: Frontend de Autenticación y Perfiles de Usuario

**Input**: Design documents from `/specs/005-frontend-user-profile/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/auth-api.yaml

**Tests**: Tests are NOT included in this feature per the Constitution exception for frontend development. Testing will follow test-alongside-development approach with ≥90% coverage enforced before PR merge.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `frontend/src/` for all React components, hooks, services
- Paths use the structure defined in plan.md and quickstart.md

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize frontend project with Vite + React + TypeScript

- [x] T001 Create frontend directory structure as defined in quickstart.md
- [x] T002 Initialize Vite project with React + TypeScript template in frontend/
- [x] T003 [P] Install core dependencies: react-router-dom, axios, @marsidev/react-turnstile, react-hook-form, @hookform/resolvers, zod
- [x] T004 [P] Configure Vite config with port 3000, proxy to backend, and build optimization in frontend/vite.config.ts
- [x] T005 [P] Create .env.example with VITE_API_URL and VITE_TURNSTILE_SITE_KEY in frontend/
- [x] T006 [P] Create .env.local with local development values in frontend/ (gitignored)
- [x] T007 [P] Update frontend/.gitignore to exclude .env.local and build artifacts
- [x] T008 [P] Configure TypeScript strict mode and path aliases in frontend/tsconfig.json

**Checkpoint**: Project structure ready, dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Create all TypeScript type definitions from data-model.md in frontend/src/types/user.ts
- [x] T010 [P] Create auth types from data-model.md in frontend/src/types/auth.ts
- [x] T011 [P] Create form types from data-model.md in frontend/src/types/forms.ts
- [x] T012 [P] Create API types from data-model.md in frontend/src/types/api.ts
- [x] T013 [P] Create error types from data-model.md in frontend/src/types/errors.ts
- [x] T014 [P] Create validation types from data-model.md in frontend/src/types/validation.ts
- [x] T015 [P] Create password strength types from data-model.md in frontend/src/types/password.ts
- [x] T016 [P] Create Turnstile types from data-model.md in frontend/src/types/turnstile.ts
- [x] T017 [P] Create environment types in frontend/src/types/env.d.ts
- [x] T018 Implement Axios client with interceptors and refresh token logic in frontend/src/services/api.ts
- [x] T019 Implement authService with all API calls (login, register, logout, etc.) in frontend/src/services/authService.ts
- [x] T020 [P] Implement password strength calculation utility from research.md in frontend/src/utils/passwordStrength.ts
- [x] T021 [P] Implement useDebounce hook from research.md in frontend/src/hooks/useDebounce.ts
- [x] T022 [P] Implement useCountdown hook from research.md in frontend/src/hooks/useCountdown.ts
- [x] T023 [P] Implement type guard utilities in frontend/src/utils/typeGuards.ts
- [x] T024 [P] Implement field validators in frontend/src/utils/validators.ts
- [x] T025 Create AuthContext with user state, loading state, and auth methods in frontend/src/contexts/AuthContext.tsx
- [x] T026 Create ProtectedRoute component with email verification enforcement in frontend/src/components/routing/ProtectedRoute.tsx
- [x] T027 [P] Create global CSS styles in frontend/src/styles/global.css
- [x] T028 Update App.tsx to include AuthProvider and React Router setup with all routes in frontend/src/App.tsx
- [x] T029 Update main.tsx to render App with global styles in frontend/src/main.tsx

**Checkpoint**: Foundation ready - all shared utilities, types, services, and context are complete. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Registro de Nuevo Usuario (Priority: P1) 🎯 MVP

**Goal**: Enable new cyclists to create an account with real-time validation, password strength meter, and CAPTCHA protection

**Independent Test**:
1. Navigate to /register
2. Fill form with valid data
3. See real-time validation as you type
4. See password strength change from red → yellow → green
5. Complete CAPTCHA
6. Submit form
7. See success message and verification email sent notice

### Implementation for User Story 1

- [x] T030 [P] [US1] Create PasswordStrengthMeter component with red/yellow/green visual indicator in frontend/src/components/auth/PasswordStrengthMeter.tsx
- [x] T031 [P] [US1] Create TurnstileWidget component wrapping @marsidev/react-turnstile in frontend/src/components/auth/TurnstileWidget.tsx
- [x] T032 [US1] Create RegisterForm component with React Hook Form + Zod validation in frontend/src/components/auth/RegisterForm.tsx
- [x] T033 [US1] Implement debounced email availability check in RegisterForm component
- [x] T034 [US1] Implement debounced username availability check in RegisterForm component
- [x] T035 [US1] Integrate PasswordStrengthMeter into RegisterForm password field
- [x] T036 [US1] Integrate TurnstileWidget into RegisterForm
- [x] T037 [US1] Create RegisterPage component that renders RegisterForm in frontend/src/pages/RegisterPage.tsx
- [x] T038 [US1] Add /register route to App.tsx router configuration
- [x] T039 [US1] Add error handling and success messaging to RegisterPage
- [x] T040 [US1] Add loading states during form submission

**Checkpoint**: User Story 1 complete - users can register with full validation, password strength feedback, and CAPTCHA protection

---

## Phase 4: User Story 2 - Inicio de Sesión (Priority: P1)

**Goal**: Enable registered cyclists to authenticate and access their dashboard with "Remember Me" functionality and account blocking protection

**Independent Test**:
1. Navigate to /login
2. Enter valid credentials
3. Check "Remember Me" checkbox
4. Submit form
5. Redirected to /dashboard
6. Close browser and reopen - still authenticated
7. Test with invalid credentials 5 times - see account blocked message with countdown

### Implementation for User Story 2

- [x] T041 [P] [US2] Create AccountBlockedMessage component with countdown timer in frontend/src/components/auth/AccountBlockedMessage.tsx
- [x] T042 [US2] Create LoginForm component with email/password fields and Remember Me checkbox in frontend/src/components/auth/LoginForm.tsx
- [x] T043 [US2] Implement form validation with React Hook Form + Zod in LoginForm
- [x] T044 [US2] Integrate useCountdown hook for account blocking countdown in AccountBlockedMessage
- [x] T045 [US2] Handle 403 ACCOUNT_BLOCKED error response and display AccountBlockedMessage
- [x] T046 [US2] Handle 403 EMAIL_NOT_VERIFIED error and redirect to verification page
- [x] T047 [US2] Create LoginPage component that renders LoginForm in frontend/src/pages/LoginPage.tsx
- [x] T048 [US2] Implement post-login redirect to intended destination or /dashboard
- [x] T049 [US2] Add /login route to App.tsx router configuration
- [x] T050 [US2] Create basic DashboardPage placeholder in frontend/src/pages/DashboardPage.tsx
- [x] T051 [US2] Add /dashboard as protected route in App.tsx
- [x] T052 [US2] Add error handling for invalid credentials
- [x] T053 [US2] Add loading states during login

**Checkpoint**: User Story 2 complete - users can login with Remember Me, account blocking works with countdown, and protected routes enforce authentication

---

## Phase 5: User Story 3 - Recuperación de Contraseña (Priority: P2)

**Goal**: Enable cyclists to reset forgotten passwords via email link with secure token validation

**Independent Test**:
1. Navigate to /forgot-password
2. Enter email address
3. Complete CAPTCHA
4. Submit - see success message
5. Check email for reset link
6. Click link → navigate to /reset-password?token=xxx
7. Enter new password (see strength meter)
8. Submit - see success message
9. Login with new password

### Implementation for User Story 3

- [x] T054 [P] [US3] Create ForgotPasswordForm component with email field and CAPTCHA in frontend/src/components/auth/ForgotPasswordForm.tsx
- [x] T055 [P] [US3] Create ResetPasswordForm component with new password fields in frontend/src/components/auth/ResetPasswordForm.tsx
- [x] T056 [US3] Integrate TurnstileWidget into ForgotPasswordForm
- [x] T057 [US3] Integrate PasswordStrengthMeter into ResetPasswordForm
- [x] T058 [US3] Create ForgotPasswordPage that renders ForgotPasswordForm in frontend/src/pages/ForgotPasswordPage.tsx
- [x] T059 [US3] Create ResetPasswordPage that extracts token from URL and renders ResetPasswordForm in frontend/src/pages/ResetPasswordPage.tsx
- [x] T060 [US3] Add /forgot-password route to App.tsx
- [x] T061 [US3] Add /reset-password route to App.tsx
- [x] T062 [US3] Handle TOKEN_EXPIRED and INVALID_TOKEN errors in ResetPasswordPage
- [x] T063 [US3] Add success messaging and redirect to /login after password reset
- [x] T064 [US3] Add link to /forgot-password from LoginPage

**Checkpoint**: User Story 3 complete - users can request password reset, receive email, and set new password with full validation

---

## Phase 6: User Story 4 - Verificación de Email (Priority: P2)

**Goal**: Enable new users to verify their email address via link sent during registration

**Independent Test**:
1. Register new account (see US1)
2. Check email for verification link
3. Click link → navigate to /verify-email?token=xxx
4. See success message
5. Redirected to /login
6. Login successfully (no longer blocked by email verification)

### Implementation for User Story 4

- [x] T065 [US4] Create VerifyEmailPage that extracts token from URL and calls verify endpoint in frontend/src/pages/VerifyEmailPage.tsx
- [x] T066 [US4] Add /verify-email route to App.tsx
- [x] T067 [US4] Handle TOKEN_EXPIRED error and show "resend verification" button
- [x] T068 [US4] Handle INVALID_TOKEN error with clear messaging
- [x] T069 [US4] Implement resend verification email functionality using authService
- [x] T070 [US4] Add success animation or visual feedback on successful verification
- [x] T071 [US4] Add automatic redirect to /login after 3 seconds on success
- [x] T072 [US4] Add rate limiting feedback for resend verification (max 1 per 5 minutes)

**Checkpoint**: User Story 4 complete - users can verify email via link, resend verification if expired, and access platform after verification

---

## Phase 7: User Story 5 - Cierre de Sesión (Priority: P2)

**Goal**: Enable authenticated users to securely logout and invalidate their session

**Independent Test**:
1. Login to platform (see US2)
2. Navigate to dashboard
3. Click logout button in user menu
4. See loading indicator briefly
5. Redirected to /login
6. Try navigating to /dashboard - redirected back to /login (session invalidated)

### Implementation for User Story 5

- [x] T073 [P] [US5] Create UserMenu component with logout button in frontend/src/components/auth/UserMenu.tsx
- [x] T074 [US5] Implement logout handler that calls authService.logout()
- [x] T075 [US5] Update AuthContext to clear user state on logout
- [x] T076 [US5] Add UserMenu to DashboardPage navigation bar
- [x] T077 [US5] Add loading state during logout operation
- [x] T078 [US5] Add confirmation dialog for logout action (optional - can skip for MVP)
- [x] T079 [US5] Ensure all protected routes redirect to /login after logout
- [x] T080 [US5] Clear any client-side cached data on logout

**Checkpoint**: User Story 5 complete - users can logout securely, session is invalidated on backend, and routes are protected

---

## Phase 8: User Story 6 - Navegación y Persistencia de Sesión (Priority: P3)

**Goal**: Maintain consistent authentication state across page navigation with automatic token refresh and user info display

**Independent Test**:
1. Login to platform (see US2) with Remember Me checked
2. Navigate to /dashboard
3. See user info in navigation bar (username, photo if available)
4. Refresh page - still authenticated
5. Navigate to /profile - still authenticated
6. Wait 16 minutes (access token expires) - automatic refresh on next request
7. Close browser and reopen - still authenticated (refresh token valid)

### Implementation for User Story 6

- [x] T081 [P] [US6] Create ProfilePage placeholder component in frontend/src/pages/ProfilePage.tsx
- [x] T082 [US6] Add /profile protected route to App.tsx
- [x] T083 [US6] Update UserMenu to display user info (username, photo) from AuthContext
- [x] T084 [US6] Implement automatic auth check on app mount in AuthContext
- [x] T085 [US6] Test automatic token refresh on 401 response (already in api.ts interceptor)
- [x] T086 [US6] Add loading spinner while auth check is in progress
- [x] T087 [US6] Handle session expiration gracefully (refresh token expired)
- [x] T088 [US6] Add navigation links to UserMenu (Dashboard, Profile, Logout)
- [x] T089 [US6] Ensure ProtectedRoute shows loading state during auth check
- [x] T090 [US6] Test navigation between protected routes maintains state

**Checkpoint**: User Story 6 complete - authentication persists across navigation, page refreshes, and browser sessions (with Remember Me)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and optimizations that affect multiple user stories

- [ ] T091 [P] Add accessibility attributes (ARIA labels, roles) to all form components
- [ ] T092 [P] Add proper focus management and keyboard navigation to forms
- [ ] T093 [P] Optimize bundle size - verify <200KB initial load via `npm run build` + analysis
- [ ] T094 [P] Add error boundary for graceful error handling in frontend/src/components/ErrorBoundary.tsx
- [ ] T095 [P] Implement lazy loading for non-critical routes (Dashboard, Profile pages)
- [ ] T096 [P] Add loading skeletons for better UX during data fetching
- [ ] T097 [P] Create reusable Button component with loading states in frontend/src/components/common/Button.tsx
- [ ] T098 [P] Create reusable Input component with validation styles in frontend/src/components/common/Input.tsx
- [ ] T099 [P] Add Spanish translations for all user-facing text (ensure consistency)
- [ ] T100 [P] Add meta tags for SEO in index.html
- [ ] T101 [P] Configure CSP headers for security in production
- [ ] T102 [P] Add unit tests for critical utilities (passwordStrength, validators) - target ≥90% coverage
- [ ] T103 [P] Add component tests for forms using @testing-library/react
- [ ] T104 Code cleanup and refactoring - remove console.logs, unused imports
- [ ] T105 Performance audit - ensure Lighthouse score ≥90
- [ ] T106 Security audit - verify no tokens in localStorage, HTTPS enforced, etc.
- [ ] T107 Run quickstart.md validation - verify all setup steps work
- [ ] T108 Create README.md in frontend/ with setup, dev commands, and architecture overview

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1+US2 → US3+US4+US5 → US6)
- **Polish (Phase 9)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Depends on US1 for email verification redirect
- **User Story 3 (P2)**: Can start after Foundational - Independent (uses TurnstileWidget from US1)
- **User Story 4 (P2)**: Can start after Foundational - Integrates with US1 registration flow
- **User Story 5 (P2)**: Can start after US2 (needs authenticated state)
- **User Story 6 (P3)**: Can start after US2+US5 (needs login + logout + navigation)

### Within Each User Story

- Components before pages
- Pages before route configuration
- Core implementation before integration
- Error handling after happy path
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: Tasks T003, T004, T005, T006, T007, T008 can run in parallel
- **Phase 2 (Foundational)**: All type definition tasks (T009-T017) can run in parallel
- **Phase 2 (Foundational)**: Utility tasks (T020-T024) can run in parallel after types
- **Phase 2 (Foundational)**: Component tasks (T026-T027) can run in parallel
- **Phase 3 (US1)**: PasswordStrengthMeter (T030) and TurnstileWidget (T031) can run in parallel
- **Phase 4 (US2)**: AccountBlockedMessage (T041) can be built in parallel with LoginForm (T042)
- **Phase 5 (US3)**: ForgotPasswordForm (T054) and ResetPasswordForm (T055) can run in parallel
- **Phase 7 (US5)**: UserMenu (T073) is independent component
- **Phase 8 (US6)**: ProfilePage (T081) is independent
- **Phase 9 (Polish)**: Most tasks marked [P] can run in parallel (T091-T108)

---

## Parallel Example: User Story 1 (Registration)

```bash
# Launch component development in parallel:
Task T030: "Create PasswordStrengthMeter component in frontend/src/components/auth/PasswordStrengthMeter.tsx"
Task T031: "Create TurnstileWidget component in frontend/src/components/auth/TurnstileWidget.tsx"

# Then integrate into form:
Task T032: "Create RegisterForm component"
Task T033: "Implement debounced email check"
Task T034: "Implement debounced username check"
```

---

## Parallel Example: User Story 2 (Login)

```bash
# Launch components in parallel:
Task T041: "Create AccountBlockedMessage component in frontend/src/components/auth/AccountBlockedMessage.tsx"
Task T042: "Create LoginForm component in frontend/src/components/auth/LoginForm.tsx"

# Then integrate:
Task T044: "Integrate useCountdown hook"
Task T045: "Handle ACCOUNT_BLOCKED error"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T029) - CRITICAL
3. Complete Phase 3: User Story 1 - Registration (T030-T040)
4. Complete Phase 4: User Story 2 - Login (T041-T053)
5. **STOP and VALIDATE**: Test registration + login flow end-to-end
6. Deploy/demo MVP

**MVP Deliverable**: Users can register accounts and login - core authentication working

### Incremental Delivery

1. **Foundation** (Phases 1-2) → All shared infrastructure ready
2. **MVP** (Phases 3-4: US1+US2) → Registration + Login → Deploy/Demo ✅
3. **Password Recovery** (Phase 5: US3) → Forgot password flow → Deploy/Demo
4. **Email Verification** (Phase 6: US4) → Email verification → Deploy/Demo
5. **Session Management** (Phases 7-8: US5+US6) → Logout + navigation → Deploy/Demo
6. **Polish** (Phase 9) → Performance + accessibility → Final Deploy

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Registration) - Phase 3
   - Developer B: User Story 2 (Login) - Phase 4
   - Developer C: User Story 3 (Password Recovery) - Phase 5
3. **Next Sprint**:
   - Developer A: User Story 4 (Email Verification) - Phase 6
   - Developer B: User Story 5 (Logout) - Phase 7
   - Developer C: User Story 6 (Navigation) - Phase 8
4. **Final Sprint**: All developers on Polish (Phase 9)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **No test tasks**: Frontend follows test-alongside-development per Constitution exception
- **Coverage target**: ≥90% enforced before PR merge
- **File paths**: All paths are exact locations in frontend/src/
- **Each user story**: Independently completable and testable
- **Commit strategy**: Commit after each task or logical group of [P] tasks
- **Validation checkpoints**: Stop at each user story checkpoint to test independently
- **Backend dependency**: Backend API must be running (local-dev or Docker) for integration testing
- **Cloudflare Turnstile**: Requires valid site key in .env.local (use test key for development)
- **HttpOnly cookies**: Ensure backend CORS_ORIGINS includes http://localhost:3000

---

## Success Criteria Validation

### Performance (from spec.md SC-001 to SC-003)
- [ ] Registration form loads in <1.5s
- [ ] Login request completes in <2s
- [ ] Form validation responds in <300ms

### User Experience (from spec.md SC-004 to SC-010)
- [ ] Password strength shows red/yellow/green real-time
- [ ] CAPTCHA widget loads and functions correctly
- [ ] Account blocking shows MM:SS countdown timer
- [ ] All forms show clear Spanish error messages
- [ ] Field-level validation errors display correctly

### Security (from spec.md SC-020)
- [ ] HttpOnly cookies used for tokens (no localStorage)
- [ ] Access token expires in 15 minutes
- [ ] Refresh token lasts 30 days with Remember Me
- [ ] Session-only refresh token without Remember Me
- [ ] Unverified users blocked from login

### Functionality (from spec.md FR-001 to FR-065)
- [ ] All 65 functional requirements testable via user stories
- [ ] Each user story maps to specific FRs in spec.md
- [ ] Independent testing possible for each story

---

**Total Tasks**: 108
**Parallelizable Tasks**: 45 (marked with [P])
**User Stories**: 6 (organized as independent phases)
**Estimated MVP**: Phases 1-4 (Tasks T001-T053) = ~53 tasks
**Suggested First Milestone**: Complete MVP (US1+US2) then validate

**Document Status**: ✅ COMPLETE
**Ready for Implementation**: YES
**Generated**: 2026-01-08
