# Tasks: User Profiles & Authentication

**Input**: Design documents from `/specs/001-user-profiles/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: This feature follows TDD (Test-Driven Development) per constitution requirement. Tests are written FIRST before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This project uses **Web application** structure:
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/` (future work, not in this feature)
- See plan.md lines 145-234 for complete structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (backend/src/, backend/tests/, backend/migrations/)
- [x] T002 Initialize Poetry project with pyproject.toml and install core dependencies (FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic 2.0+)
- [x] T003 [P] Install development dependencies (pytest, pytest-asyncio, pytest-cov, black, ruff, mypy)
- [x] T004 [P] Install auth dependencies (python-jose, passlib[bcrypt], python-multipart, aiofiles)
- [x] T005 [P] Install database drivers (aiosqlite for dev/test, asyncpg for production)
- [x] T006 [P] Install HTTP client for tests (httpx with async support)
- [x] T007 Create .env.example with all configuration variables per quickstart.md
- [x] T008 Create .env.test with SQLite in-memory configuration
- [x] T009 [P] Configure black formatter (line length 100) in pyproject.toml
- [x] T010 [P] Configure ruff linter in pyproject.toml
- [x] T011 [P] Configure mypy type checker in pyproject.toml
- [x] T012 Create .gitignore for Python project (venv/, __pycache__/, .env, *.db, storage/)
- [x] T013 Create backend/storage/profile_photos/ directory structure

**Checkpoint**: Project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Database Infrastructure

- [x] T014 Create backend/src/config.py with environment variable loading and validation
- [x] T015 Create backend/src/database.py with async SQLAlchemy engine setup (dual SQLite/PostgreSQL support)
- [x] T016 Add SQLite foreign key pragma handler to database.py per data-model.md
- [x] T017 Initialize Alembic in backend/src/migrations/ with env.py configured for async
- [x] T018 Configure Alembic to detect dialect (SQLite vs PostgreSQL) for migrations

### Core Utilities (Needed by All User Stories)

- [x] T019 [P] Create backend/src/utils/__init__.py
- [x] T020 [P] Implement backend/src/utils/security.py (password hashing with bcrypt 12 rounds, JWT encode/decode)
- [x] T021 [P] Implement backend/src/utils/validators.py (custom Pydantic validators for username, email)
- [x] T022 [P] Implement backend/src/utils/email.py (async email sending with templates, SMTP configuration)
- [x] T023 [P] Implement backend/src/utils/file_storage.py (photo upload, Pillow resize to 400x400, storage path management)

### FastAPI Application Setup

- [x] T024 Create backend/src/main.py with FastAPI app initialization
- [x] T025 Add CORS middleware to main.py with configuration from .env
- [x] T026 Add error handling middleware with standardized JSON response format (success, data, error)
- [x] T027 Add timezone-aware UTC timestamp handling to responses
- [x] T028 Create backend/src/api/__init__.py and include router setup in main.py
- [x] T029 Create backend/src/api/deps.py with dependency injection functions (get_db, get_current_user placeholder)

### Test Infrastructure

- [x] T030 Create backend/tests/conftest.py with SQLite in-memory database fixture
- [x] T031 Add async test client fixture to conftest.py (httpx.AsyncClient)
- [x] T032 Add test database cleanup/rollback fixture to conftest.py
- [x] T033 Add Faker fixture for generating test data to conftest.py
- [x] T034 Create backend/tests/contract/__init__.py
- [x] T035 Create backend/tests/integration/__init__.py
- [x] T036 Create backend/tests/unit/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Registro y Autenticación de Usuario (Priority: P1) 🎯 MVP

**Goal**: Users can register with email/username/password, verify email, login securely with JWT tokens, logout, and reset forgotten passwords

**Independent Test**: Register new user → verify email → logout → login with credentials → access protected endpoint

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Contract Tests (Validate OpenAPI Schema)

- [x] T037 [P] [US1] Contract test for POST /auth/register in backend/tests/contract/test_auth_contracts.py
- [x] T038 [P] [US1] Contract test for POST /auth/verify-email in backend/tests/contract/test_auth_contracts.py
- [x] T039 [P] [US1] Contract test for POST /auth/resend-verification in backend/tests/contract/test_auth_contracts.py
- [x] T040 [P] [US1] Contract test for POST /auth/login in backend/tests/contract/test_auth_contracts.py
- [x] T041 [P] [US1] Contract test for POST /auth/refresh in backend/tests/contract/test_auth_contracts.py
- [x] T042 [P] [US1] Contract test for POST /auth/logout in backend/tests/contract/test_auth_contracts.py
- [x] T043 [P] [US1] Contract test for POST /auth/password-reset/request in backend/tests/contract/test_auth_contracts.py
- [x] T044 [P] [US1] Contract test for POST /auth/password-reset/confirm in backend/tests/contract/test_auth_contracts.py
- [x] T045 [P] [US1] Contract test for GET /auth/me in backend/tests/contract/test_auth_contracts.py

#### Integration Tests (Full User Journeys)

- [x] T046 [US1] Integration test for registration → email verification → login flow in backend/tests/integration/test_auth_flow.py
- [x] T047 [US1] Integration test for forgot password → reset → login flow in backend/tests/integration/test_auth_flow.py
- [x] T048 [US1] Integration test for token refresh mechanism in backend/tests/integration/test_auth_flow.py
- [x] T049 [US1] Integration test for rate limiting (5 failed login attempts) in backend/tests/integration/test_auth_flow.py

#### Unit Tests (Business Logic)

- [x] T050 [P] [US1] Unit test for password hashing and verification in backend/tests/unit/test_security_utils.py
- [x] T051 [P] [US1] Unit test for JWT token creation and validation in backend/tests/unit/test_security_utils.py
- [x] T052 [P] [US1] Unit test for username/email validators in backend/tests/unit/test_validators.py
- [x] T053 [P] [US1] Unit test for password strength validator in backend/tests/unit/test_validators.py
- [x] T054 [US1] Unit tests for AuthService.register() in backend/tests/unit/test_auth_service.py
- [x] T055 [US1] Unit tests for AuthService.verify_email() in backend/tests/unit/test_auth_service.py
- [x] T056 [US1] Unit tests for AuthService.login() in backend/tests/unit/test_auth_service.py
- [x] T057 [US1] Unit tests for AuthService.refresh_token() in backend/tests/unit/test_auth_service.py
- [x] T058 [US1] Unit tests for AuthService.logout() in backend/tests/unit/test_auth_service.py
- [x] T059 [US1] Unit tests for AuthService.request_password_reset() in backend/tests/unit/test_auth_service.py
- [x] T060 [US1] Unit tests for AuthService.confirm_password_reset() in backend/tests/unit/test_auth_service.py

### Implementation for User Story 1

#### Data Models (Database Schema)

- [x] T061 [P] [US1] Create User model in backend/src/models/user.py (id, username, email, hashed_password, is_active, is_verified)
- [x] T062 [P] [US1] Create UserProfile model in backend/src/models/user.py (1-to-1 with User, initialized empty on registration)
- [x] T063 [P] [US1] Create PasswordReset model in backend/src/models/auth.py (user_id, token_hash, expires_at, token_type, used_at)
- [x] T064 [US1] Create Alembic migration 001_initial_auth_schema.py for User, UserProfile, PasswordReset tables

#### Pydantic Schemas (Validation)

- [x] T065 [P] [US1] Create RegisterRequest schema in backend/src/schemas/auth.py
- [x] T066 [P] [US1] Create RegisterResponse schema in backend/src/schemas/auth.py
- [x] T067 [P] [US1] Create LoginRequest schema in backend/src/schemas/auth.py
- [x] T068 [P] [US1] Create LoginResponse schema with TokenResponse in backend/src/schemas/auth.py
- [x] T069 [P] [US1] Create UserResponse schema in backend/src/schemas/user.py
- [x] T070 [P] [US1] Create PasswordResetRequest schema in backend/src/schemas/auth.py
- [x] T071 [P] [US1] Create PasswordResetConfirm schema in backend/src/schemas/auth.py

#### Business Logic (Service Layer)

- [x] T072 [US1] Implement AuthService.register() in backend/src/services/auth_service.py (create user, send verification email)
- [x] T073 [US1] Implement AuthService.verify_email() in backend/src/services/auth_service.py (validate token, mark verified)
- [x] T074 [US1] Implement AuthService.resend_verification() in backend/src/services/auth_service.py (rate limit: 3/hour)
- [x] T075 [US1] Implement AuthService.login() in backend/src/services/auth_service.py (validate credentials, create JWT tokens, check rate limit)
- [x] T076 [US1] Implement AuthService.refresh_token() in backend/src/services/auth_service.py (validate refresh token, issue new tokens)
- [x] T077 [US1] Implement AuthService.logout() in backend/src/services/auth_service.py (invalidate refresh token)
- [x] T078 [US1] Implement AuthService.request_password_reset() in backend/src/services/auth_service.py (create token, send email)
- [x] T079 [US1] Implement AuthService.confirm_password_reset() in backend/src/services/auth_service.py (validate token, update password)
- [x] T080 [US1] Add rate limiting logic for failed login attempts (5 attempts, 15min lockout) to AuthService

#### API Endpoints (FastAPI Routes)

- [x] T081 [US1] Implement POST /auth/register endpoint in backend/src/api/auth.py (FR-001, FR-002, FR-003, FR-004, FR-005)
- [x] T082 [US1] Implement POST /auth/verify-email endpoint in backend/src/api/auth.py (FR-005)
- [x] T083 [US1] Implement POST /auth/resend-verification endpoint in backend/src/api/auth.py (FR-005)
- [x] T084 [US1] Implement POST /auth/login endpoint in backend/src/api/auth.py (FR-006, FR-009)
- [x] T085 [US1] Implement POST /auth/refresh endpoint in backend/src/api/auth.py (FR-010)
- [x] T086 [US1] Implement POST /auth/logout endpoint in backend/src/api/auth.py (FR-007)
- [x] T087 [US1] Implement POST /auth/password-reset/request endpoint in backend/src/api/auth.py (FR-008)
- [x] T088 [US1] Implement POST /auth/password-reset/confirm endpoint in backend/src/api/auth.py (FR-008)
- [x] T089 [US1] Implement GET /auth/me endpoint in backend/src/api/auth.py (get current user info)
- [x] T090 [US1] Update backend/src/api/deps.py with get_current_user() dependency (JWT validation)

#### Email Templates

- [x] T091 [P] [US1] Create email verification template (Spanish) in backend/src/utils/email.py
- [x] T092 [P] [US1] Create password reset template (Spanish) in backend/src/utils/email.py

#### Integration & Error Handling

- [x] T093 [US1] Add validation for duplicate email/username with Spanish error messages in AuthService
- [x] T094 [US1] Add validation for weak passwords with Spanish error messages in AuthService
- [x] T095 [US1] Add handling for expired tokens with Spanish error messages in AuthService
- [x] T096 [US1] Add handling for invalid credentials with Spanish error messages in AuthService
- [x] T097 [US1] Add logging for authentication events (registration, login, failed attempts) in AuthService

**Checkpoint**: User Story 1 should be fully functional - users can register, verify email, login, and reset passwords independently

---

## Phase 4: User Story 2 - Gestión de Perfil Básico (Priority: P2)

**Goal**: Authenticated users can edit their profile (bio, location, cycling type), upload/change profile photo, and view public profiles

**Independent Test**: Create account → login → edit profile fields → upload photo → view public profile → verify changes visible

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

#### Contract Tests

- [X] T098 [P] [US2] Contract test for GET /users/{username}/profile in backend/tests/contract/test_profile_contracts.py
- [X] T099 [P] [US2] Contract test for PUT /users/{username}/profile in backend/tests/contract/test_profile_contracts.py
- [X] T100 [P] [US2] Contract test for POST /users/{username}/profile/photo in backend/tests/contract/test_profile_contracts.py
- [X] T101 [P] [US2] Contract test for DELETE /users/{username}/profile/photo in backend/tests/contract/test_profile_contracts.py
- [X] T102 [P] [US2] Contract test for PUT /users/{username}/profile/privacy in backend/tests/contract/test_profile_contracts.py

#### Integration Tests

- [X] T103 [US2] Integration test for profile update workflow in backend/tests/integration/test_profile_management.py
- [X] T104 [US2] Integration test for photo upload with resize in backend/tests/integration/test_photo_upload.py
- [X] T105 [US2] Integration test for privacy settings (show_email, show_location) in backend/tests/integration/test_profile_management.py
- [X] T106 [US2] Integration test for public profile view respecting privacy in backend/tests/integration/test_profile_management.py

#### Unit Tests

- [X] T107 [P] [US2] Unit test for photo resize to 400x400 in backend/tests/unit/test_file_storage.py
- [X] T108 [P] [US2] Unit test for photo MIME type validation in backend/tests/unit/test_file_storage.py
- [X] T109 [P] [US2] Unit test for photo size limit (5MB) validation in backend/tests/unit/test_file_storage.py
- [X] T110 [US2] Unit tests for ProfileService.get_profile() in backend/tests/unit/test_profile_service.py
- [X] T111 [US2] Unit tests for ProfileService.update_profile() in backend/tests/unit/test_profile_service.py
- [X] T112 [US2] Unit tests for ProfileService.upload_photo() in backend/tests/unit/test_profile_service.py
- [X] T113 [US2] Unit tests for ProfileService.delete_photo() in backend/tests/unit/test_profile_service.py
- [X] T114 [US2] Unit tests for ProfileService.update_privacy() in backend/tests/unit/test_profile_service.py

### Implementation for User Story 2

#### Pydantic Schemas

- [X] T115 [P] [US2] Create ProfileResponse schema in backend/src/schemas/profile.py
- [X] T116 [P] [US2] Create ProfileUpdateRequest schema in backend/src/schemas/profile.py (bio max 500 chars, cycling_type enum)
- [X] T117 [P] [US2] Create PrivacySettings schema in backend/src/schemas/profile.py

#### Business Logic

- [X] T118 [US2] Implement ProfileService.get_profile() in backend/src/services/profile_service.py (respects privacy settings)
- [X] T119 [US2] Implement ProfileService.update_profile() in backend/src/services/profile_service.py (FR-011, FR-014, FR-015)
- [X] T120 [US2] Implement ProfileService.upload_photo() in backend/src/services/profile_service.py (FR-012, FR-013, async Pillow resize)
- [X] T121 [US2] Implement ProfileService.delete_photo() in backend/src/services/profile_service.py (FR-016)
- [X] T122 [US2] Implement ProfileService.update_privacy() in backend/src/services/profile_service.py (FR-018)

#### API Endpoints

- [X] T123 [US2] Implement GET /users/{username}/profile endpoint in backend/src/api/profile.py (FR-016, public access)
- [X] T124 [US2] Implement PUT /users/{username}/profile endpoint in backend/src/api/profile.py (FR-011, authenticated, owner only)
- [X] T125 [US2] Implement POST /users/{username}/profile/photo endpoint in backend/src/api/profile.py (FR-012, multipart/form-data)
- [X] T126 [US2] Implement DELETE /users/{username}/profile/photo endpoint in backend/src/api/profile.py (FR-016)
- [X] T127 [US2] Implement PUT /users/{username}/profile/privacy endpoint in backend/src/api/profile.py (FR-018)

#### File Handling

- [X] T128 [US2] Add background task for async photo processing in backend/src/services/profile_service.py
- [X] T129 [US2] Add cleanup for old profile photos when new one uploaded in backend/src/services/profile_service.py
- [X] T130 [US2] Add validation for photo formats (JPG, PNG, WebP) in backend/src/utils/file_storage.py

#### Authorization

- [X] T131 [US2] Add authorization check (owner only) for profile updates in backend/src/api/profile.py
- [X] T132 [US2] Add 403 Forbidden response for non-owners in backend/src/api/profile.py

#### Error Handling

- [X] T133 [US2] Add validation for bio length (500 chars) with Spanish error in ProfileService
- [X] T134 [US2] Add validation for invalid cycling_type with Spanish error in ProfileService
- [X] T135 [US2] Add handling for file too large (>5MB) with Spanish error in ProfileService
- [X] T136 [US2] Add handling for invalid file format with Spanish error in ProfileService

**Checkpoint**: User Story 2 complete - users can customize profiles and upload photos independently

---

## Phase 5: User Story 3 - Estadísticas y Logros del Ciclista (Priority: P3)

**Goal**: Automatically calculate and display user statistics (km, trips, countries visited) and award achievement badges based on milestones

**Independent Test**: Create account → simulate trip publish events → verify stats update → check achievements awarded → view stats on profile

### Tests for User Story 3 (TDD - Write FIRST) ⚠️

#### Contract Tests

- [X] T137 [P] [US3] Contract test for GET /users/{username}/stats in backend/tests/contract/test_stats_contracts.py
- [X] T138 [P] [US3] Contract test for GET /users/{username}/achievements in backend/tests/contract/test_stats_contracts.py
- [X] T139 [P] [US3] Contract test for GET /achievements in backend/tests/contract/test_stats_contracts.py

#### Integration Tests

- [X] T140 [US3] Integration test for stats calculation on trip publish in backend/tests/integration/test_stats_calculation.py
- [X] T141 [US3] Integration test for stats update on trip edit in backend/tests/integration/test_stats_calculation.py
- [X] T142 [US3] Integration test for stats update on trip delete in backend/tests/integration/test_stats_calculation.py
- [X] T143 [US3] Integration test for achievement award on milestone in backend/tests/integration/test_stats_calculation.py
- [X] T144 [US3] Integration test for multiple achievements in single event in backend/tests/integration/test_stats_calculation.py

#### Unit Tests

- [X] T145 [P] [US3] Unit tests for StatsService.get_user_stats() in backend/tests/unit/test_stats_service.py
- [X] T146 [P] [US3] Unit tests for StatsService.update_stats_on_trip_publish() in backend/tests/unit/test_stats_service.py
- [X] T147 [P] [US3] Unit tests for StatsService.update_stats_on_trip_delete() in backend/tests/unit/test_stats_service.py
- [X] T148 [P] [US3] Unit tests for StatsService.check_achievements() in backend/tests/unit/test_stats_service.py
- [X] T149 [P] [US3] Unit tests for StatsService.award_achievement() in backend/tests/unit/test_stats_service.py
- [X] T150 [US3] Unit tests for achievement criteria validation in backend/tests/unit/test_stats_service.py

### Implementation for User Story 3

#### Data Models

- [X] T151 [P] [US3] Create UserStats model in backend/src/models/stats.py (total_trips, total_km, countries_visited, total_photos, last_trip_date)
- [X] T152 [P] [US3] Create Achievement model in backend/src/models/stats.py (code, name, description, badge_icon, requirement_type, requirement_value)
- [X] T153 [P] [US3] Create UserAchievement model in backend/src/models/stats.py (user_id, achievement_id, awarded_at)
- [X] T154 [US3] Create Alembic migration 003_stats_and_achievements.py for UserStats, Achievement, UserAchievement tables

#### Pydantic Schemas

- [X] T155 [P] [US3] Create StatsResponse schema in backend/src/schemas/stats.py
- [X] T156 [P] [US3] Create AchievementResponse schema in backend/src/schemas/stats.py
- [X] T157 [P] [US3] Create AchievementDefinition schema in backend/src/schemas/stats.py
- [X] T158 [P] [US3] Create UserAchievementResponse schema in backend/src/schemas/stats.py

#### Business Logic

- [X] T159 [US3] Implement StatsService.get_user_stats() in backend/src/services/stats_service.py (FR-019, FR-020, FR-021)
- [X] T160 [US3] Implement StatsService.get_user_achievements() in backend/src/services/stats_service.py (FR-024)
- [X] T161 [US3] Implement StatsService.update_stats_on_trip_publish() in backend/src/services/stats_service.py (FR-022, event-driven)
- [X] T162 [US3] Implement StatsService.update_stats_on_trip_edit() in backend/src/services/stats_service.py (FR-022)
- [X] T163 [US3] Implement StatsService.update_stats_on_trip_delete() in backend/src/services/stats_service.py (FR-022)
- [X] T164 [US3] Implement StatsService.check_achievements() in backend/src/services/stats_service.py (FR-024, check all criteria)
- [X] T165 [US3] Implement StatsService.award_achievement() in backend/src/services/stats_service.py (FR-024, idempotent)

#### API Endpoints

- [X] T166 [US3] Implement GET /users/{username}/stats endpoint in backend/src/api/stats.py (public access)
- [X] T167 [US3] Implement GET /users/{username}/achievements endpoint in backend/src/api/stats.py (public access)
- [X] T168 [US3] Implement GET /achievements endpoint in backend/src/api/stats.py (list all available achievements)

#### Database Seeding

- [X] T169 [US3] Create script to seed 9 predefined achievements in backend/scripts/seed_achievements.py per data-model.md (FIRST_TRIP, CENTURY, VOYAGER, EXPLORER, PHOTOGRAPHER, GLOBETROTTER, MARATHONER, INFLUENCER, PROLIFIC)
- [X] T170 [US3] Add achievement seeding to Alembic migration or separate data migration

#### Stats Calculation Logic

- [X] T171 [US3] Implement total_kilometers calculation from trip GPX data in StatsService
- [X] T172 [US3] Implement unique countries extraction from trip locations in StatsService
- [X] T173 [US3] Implement total_photos count from trip photo attachments in StatsService
- [X] T174 [US3] Add background task for stats recalculation (daily reconciliation) in StatsService

#### Achievement Criteria

- [X] T175 [P] [US3] Implement distance milestone checks (100km, 1000km, 5000km) in StatsService.check_achievements()
- [X] T176 [P] [US3] Implement trip count milestone checks (1, 10, 25) in StatsService.check_achievements()
- [X] T177 [P] [US3] Implement countries visited milestone checks (5, 10) in StatsService.check_achievements()
- [X] T178 [P] [US3] Implement photos milestone checks (50) in StatsService.check_achievements()

#### Display Logic

- [X] T179 [US3] Add zero-state message for users with no trips (Spanish) in StatsResponse
- [X] T180 [US3] Add stats display to ProfileResponse in backend/src/schemas/profile.py

**Checkpoint**: User Story 3 complete - stats auto-calculate and achievements award automatically

---

## Phase 6: User Story 4 - Conexiones Sociales (Seguir/Seguidores) (Priority: P4)

**Goal**: Users can follow/unfollow other users, view follower/following lists, and see social connection counts on profiles

**Independent Test**: Create 2 accounts → user A follows user B → verify follower/following lists update → user A unfollows → verify lists update

### Tests for User Story 4 (TDD - Write FIRST) ⚠️

#### Contract Tests

- [X] T181 [P] [US4] Contract test for POST /users/{username}/follow in backend/tests/contract/test_social_contracts.py
- [X] T182 [P] [US4] Contract test for DELETE /users/{username}/follow in backend/tests/contract/test_social_contracts.py
- [X] T183 [P] [US4] Contract test for GET /users/{username}/followers in backend/tests/contract/test_social_contracts.py
- [X] T184 [P] [US4] Contract test for GET /users/{username}/following in backend/tests/contract/test_social_contracts.py
- [X] T185 [P] [US4] Contract test for GET /users/{username}/follow-status in backend/tests/contract/test_social_contracts.py

#### Integration Tests

- [X] T186 [US4] Integration test for full follow workflow (follow → verify lists → unfollow) in backend/tests/integration/test_follow_workflow.py
- [X] T187 [US4] Integration test for follower/following counter updates in backend/tests/integration/test_follow_workflow.py
- [X] T188 [US4] Integration test for pagination of followers list (50+ users) in backend/tests/integration/test_follow_workflow.py
- [X] T189 [US4] Integration test for self-follow prevention in backend/tests/integration/test_follow_workflow.py
- [X] T190 [US4] Integration test for unauthenticated follow redirect in backend/tests/integration/test_follow_workflow.py

#### Unit Tests

- [X] T191 [P] [US4] Unit tests for SocialService.follow_user() in backend/tests/unit/test_social_service.py
- [X] T192 [P] [US4] Unit tests for SocialService.unfollow_user() in backend/tests/unit/test_social_service.py
- [X] T193 [P] [US4] Unit tests for SocialService.get_followers() in backend/tests/unit/test_social_service.py
- [X] T194 [P] [US4] Unit tests for SocialService.get_following() in backend/tests/unit/test_social_service.py
- [X] T195 [P] [US4] Unit tests for SocialService.get_follow_status() in backend/tests/unit/test_social_service.py
- [X] T196 [US4] Unit tests for duplicate follow prevention in backend/tests/unit/test_social_service.py
- [X] T197 [US4] Unit tests for counter update on follow/unfollow in backend/tests/unit/test_social_service.py

### Implementation for User Story 4

#### Data Models

- [X] T198 [US4] Create Follow model in backend/src/models/social.py (follower_id, following_id, created_at, unique constraint, CHECK no self-follow)
- [X] T199 [US4] Add followers_count and following_count to UserProfile model in backend/src/models/user.py (denormalized counters)
- [X] T200 [US4] Create Alembic migration 004_social_features.py for Follow table and UserProfile counter columns

#### Pydantic Schemas

- [X] T201 [P] [US4] Create FollowResponse schema in backend/src/schemas/social.py
- [X] T202 [P] [US4] Create UserSummary schema for follower/following lists in backend/src/schemas/social.py
- [X] T203 [P] [US4] Create FollowersListResponse schema with pagination in backend/src/schemas/social.py
- [X] T204 [P] [US4] Create FollowingListResponse schema with pagination in backend/src/schemas/social.py
- [X] T205 [P] [US4] Create FollowStatusResponse schema in backend/src/schemas/social.py

#### Business Logic

- [X] T206 [US4] Implement SocialService.follow_user() in backend/src/services/social_service.py (FR-025, FR-027, transactional counter update)
- [X] T207 [US4] Implement SocialService.unfollow_user() in backend/src/services/social_service.py (FR-026, FR-031, transactional counter update)
- [X] T208 [US4] Implement SocialService.get_followers() in backend/src/services/social_service.py (FR-028, FR-030, paginated, max 50)
- [X] T209 [US4] Implement SocialService.get_following() in backend/src/services/social_service.py (FR-029, FR-030, paginated, max 50)
- [X] T210 [US4] Implement SocialService.get_follow_status() in backend/src/services/social_service.py (check if current user follows target)

#### API Endpoints

- [X] T211 [US4] Implement POST /users/{username}/follow endpoint in backend/src/api/social.py (FR-025, authenticated only)
- [X] T212 [US4] Implement DELETE /users/{username}/follow endpoint in backend/src/api/social.py (FR-026, authenticated only)
- [X] T213 [US4] Implement GET /users/{username}/followers endpoint in backend/src/api/social.py (FR-028, public, paginated)
- [X] T214 [US4] Implement GET /users/{username}/following endpoint in backend/src/api/social.py (FR-029, public, paginated)
- [X] T215 [US4] Implement GET /users/{username}/follow-status endpoint in backend/src/api/social.py (authenticated only)

#### Database Optimization

- [X] T216 [US4] Add indexes on Follow (follower_id, following_id) per data-model.md in migration
- [X] T217 [US4] Add index on Follow (created_at) for sorting in migration

#### Validation & Error Handling

- [X] T218 [US4] Add validation for self-follow prevention with Spanish error in SocialService
- [X] T219 [US4] Add validation for duplicate follow with Spanish error in SocialService
- [X] T220 [US4] Add validation for unfollow non-existent relationship with Spanish error in SocialService
- [X] T221 [US4] Add 401 redirect for unauthenticated follow attempts in backend/src/api/social.py

#### Counter Consistency

- [X] T222 [US4] Add transactional update for followers_count and following_count in SocialService.follow_user()
- [X] T223 [US4] Add transactional update for followers_count and following_count in SocialService.unfollow_user()
- [ ] T224 [US4] Add background task for periodic counter reconciliation in backend/scripts/ (optional, future)

**Checkpoint**: User Story 4 complete - social connections fully functional with accurate counts

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

### Performance Optimization

- [X] T225 [P] Add database indexes verification per data-model.md (email, username, foreign keys)
- [X] T226 [P] Add query optimization with eager loading for profile+stats+achievements
- [X] T227 [P] Optimize photo processing to run in background task (if not already async)
- [X] T228 Run performance tests with Locust per quickstart.md (100+ concurrent registrations, <500ms auth, <200ms profiles)

### Security Hardening

- [X] T229 [P] Audit password hashing to confirm bcrypt 12 rounds in production config
- [X] T230 [P] Audit JWT token expiration (15min access, 30-day refresh) in config
- [X] T231 [P] Verify all endpoints validate authentication/authorization correctly
- [X] T232 [P] Add CSRF protection if using cookies (not needed for JWT in headers)
- [X] T233 Scan for SQL injection vulnerabilities (verify only ORM used, no raw SQL)
- [X] T234 Scan for XSS vulnerabilities in bio and other user inputs

### Documentation

- [X] T235 [P] Add API documentation with examples to each endpoint (FastAPI auto-docs enhancement)
- [X] T236 [P] Create README.md in backend/ with quickstart instructions
- [X] T237 [P] Document environment variables in .env.example with descriptions
- [X] T238 Add architecture diagram to docs/ showing layers (models → services → api)

### Code Quality

- [X] T239 Run black formatter on all Python files
- [X] T240 Run ruff linter and fix all issues
- [X] T241 Run mypy type checker and fix all type errors
- [X] T242 Review and remove any commented-out code or TODOs
- [X] T243 Ensure all functions have Google-style docstrings
- [X] T244 Verify no magic numbers (all constants in config.py)

### Testing & Coverage

- [X] T245 Run full test suite: pytest backend/tests/ --cov=backend/src --cov-report=html
- [X] T246 Verify ≥90% test coverage across all modules (constitution requirement)
- [X] T247 Add additional edge case tests if coverage gaps found
- [X] T248 Test all error messages are in Spanish per constitution

### Deployment Preparation

- [X] T249 Create Dockerfile for backend per plan.md
- [X] T250 Create docker-compose.yml with PostgreSQL + Redis per plan.md
- [X] T251 Test backend with PostgreSQL (not just SQLite)
- [X] T252 Create .env.prod template with production settings
- [X] T253 Verify all migrations work with PostgreSQL

### Final Validation

- [X] T254 Run quickstart.md validation end-to-end (setup → register → login → profile → stats → follow)
- [X] T255 Verify all 32 functional requirements (FR-001 to FR-032) are implemented
- [X] T256 Verify all 25 success criteria (SC-001 to SC-025) are met
- [X] T257 Verify all 4 user stories are independently testable
- [X] T258 Create release notes / changelog

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) + User Story 1 (needs User model) - Can start once US1 models exist
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Independent of US1/US2, but integrates with User
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) + User Story 1 (needs User model) - Independent otherwise
- **Polish (Phase 7)**: Depends on all 4 user stories being complete

### User Story Dependencies

**Critical Path**:
1. Setup (Phase 1) → Foundational (Phase 2) → MUST complete before any user story
2. User Story 1 (P1) → Creates User/UserProfile models needed by US2 and US4
3. User Stories 2, 3, 4 → Can proceed in parallel after US1 models exist

**Optimal Execution Order**:
- **Sequential**: Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7 (Polish)
- **Parallel** (after Phase 2): Once US1 models are created (T061-T064), US2/US3/US4 can proceed in parallel with separate developers

### Within Each User Story

**TDD Workflow (CRITICAL)**:
1. Write ALL tests for the user story FIRST (contract → integration → unit)
2. Verify ALL tests FAIL (Red)
3. Create models (Green - make tests pass)
4. Implement services (Green)
5. Implement API endpoints (Green)
6. Verify ALL tests now PASS
7. Refactor if needed
8. Verify tests still pass after refactoring

**Dependency Order within Story**:
- Tests before implementation (TDD)
- Models before services (services use models)
- Services before endpoints (endpoints use services)
- Core implementation before integration
- Validation/error handling after core logic

### Parallel Opportunities

**Phase 1 (Setup)**: T003-T006, T009-T011 can run in parallel (different config files)

**Phase 2 (Foundational)**: T019-T023 (all utils), T034-T036 (test dirs) can run in parallel

**Phase 3 (US1 Tests)**: T037-T045 (contract tests), T050-T053 (validator tests) can run in parallel

**Phase 3 (US1 Models)**: T061-T063 (User, UserProfile, PasswordReset) can run in parallel before T064

**Phase 3 (US1 Schemas)**: T065-T071 can all run in parallel

**Phase 3 (US1 Emails)**: T091-T092 can run in parallel

**Phase 4 (US2 Tests)**: T098-T102 (contract tests), T107-T109 (file storage tests) can run in parallel

**Phase 4 (US2 Schemas)**: T115-T117 can run in parallel

**Phase 5 (US3 Tests)**: T137-T139 (contract tests), T145-T150 (unit tests) can run in parallel

**Phase 5 (US3 Models)**: T151-T153 can run in parallel before T154

**Phase 5 (US3 Schemas)**: T155-T158 can run in parallel

**Phase 5 (US3 Achievement Criteria)**: T175-T178 can run in parallel

**Phase 6 (US4 Tests)**: T181-T185 (contract tests), T191-T197 (unit tests) can run in parallel

**Phase 6 (US4 Schemas)**: T201-T205 can run in parallel

**Phase 7 (Polish)**: T225-T228 (performance), T229-T234 (security), T235-T238 (docs), T239-T244 (code quality) groups can run in parallel

---

## Parallel Example: User Story 1 (Authentication)

```bash
# Launch all contract tests for User Story 1 together:
Task: "Contract test for POST /auth/register in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/verify-email in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/resend-verification in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/login in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/refresh in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/logout in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/password-reset/request in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for POST /auth/password-reset/confirm in backend/tests/contract/test_auth_contracts.py"
Task: "Contract test for GET /auth/me in backend/tests/contract/test_auth_contracts.py"

# Launch all models for User Story 1 together:
Task: "Create User model in backend/src/models/user.py"
Task: "Create UserProfile model in backend/src/models/user.py"
Task: "Create PasswordReset model in backend/src/models/auth.py"

# Launch all Pydantic schemas for User Story 1 together:
Task: "Create RegisterRequest schema in backend/src/schemas/auth.py"
Task: "Create RegisterResponse schema in backend/src/schemas/auth.py"
Task: "Create LoginRequest schema in backend/src/schemas/auth.py"
Task: "Create LoginResponse schema with TokenResponse in backend/src/schemas/auth.py"
Task: "Create UserResponse schema in backend/src/schemas/user.py"
Task: "Create PasswordResetRequest schema in backend/src/schemas/auth.py"
Task: "Create PasswordResetConfirm schema in backend/src/schemas/auth.py"
```

---

## Parallel Example: User Story 3 (Stats & Achievements)

```bash
# Launch all models together:
Task: "Create UserStats model in backend/src/models/stats.py"
Task: "Create Achievement model in backend/src/models/stats.py"
Task: "Create UserAchievement model in backend/src/models/stats.py"

# Launch all achievement criteria checks together:
Task: "Implement distance milestone checks (100km, 1000km, 5000km) in StatsService.check_achievements()"
Task: "Implement trip count milestone checks (1, 10, 25) in StatsService.check_achievements()"
Task: "Implement countries visited milestone checks (5, 10) in StatsService.check_achievements()"
Task: "Implement photos milestone checks (50) in StatsService.check_achievements()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Get authentication working ASAP for demo/testing

1. Complete Phase 1: Setup (T001-T013) ✅
2. Complete Phase 2: Foundational (T014-T036) ✅ CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T037-T097) ✅
4. **STOP and VALIDATE**:
   - Run all US1 tests (should be ≥90% coverage for auth module)
   - Manual test: Register → Verify Email → Login → Logout → Password Reset
   - Verify all FR-001 to FR-010 work
5. Deploy to staging/demo if ready

**Estimated Tasks**: 97 tasks for MVP
**Value Delivered**: Secure user authentication, the foundation for all other features

### Incremental Delivery (Full Feature)

**Recommended Order**:

1. **Sprint 1**: Setup + Foundational → Foundation ready (T001-T036, ~3-5 days)
2. **Sprint 2**: User Story 1 (Authentication) → Test independently → Deploy/Demo (T037-T097, ~5-7 days) ✅ MVP!
3. **Sprint 3**: User Story 2 (Profile Management) → Test independently → Deploy/Demo (T098-T136, ~4-5 days)
4. **Sprint 4**: User Story 3 (Stats & Achievements) → Test independently → Deploy/Demo (T137-T180, ~4-5 days)
5. **Sprint 5**: User Story 4 (Social Connections) → Test independently → Deploy/Demo (T181-T224, ~4-5 days)
6. **Sprint 6**: Polish & Final Validation → Production ready (T225-T258, ~3-4 days)

**Total Estimated**: 258 tasks, 6 sprints (~23-31 days with 1 developer)

**Value at Each Sprint**:
- Sprint 1: Infrastructure ready for development
- Sprint 2: Users can create accounts and login ✅ Usable product!
- Sprint 3: Users can customize profiles and upload photos
- Sprint 4: Users see their cycling achievements and stats
- Sprint 5: Users can build their social network
- Sprint 6: Production-ready, secure, performant

### Parallel Team Strategy

With 4 developers after Foundation completes:

1. **Week 1**: Entire team completes Setup + Foundational together (T001-T036)
2. **Week 2**: Once Foundational done:
   - Developer A: User Story 1 (T037-T097) - Authentication
   - Wait for Dev A to complete models (T061-T064) before others start
3. **Week 3**: After US1 models exist:
   - Developer A: Continue User Story 1 services/endpoints
   - Developer B: User Story 2 (T098-T136) - Profile Management
   - Developer C: User Story 3 (T137-T180) - Stats & Achievements
   - Developer D: User Story 4 (T181-T224) - Social Connections
4. **Week 4**:
   - All developers: Polish & Cross-Cutting (T225-T258) together
   - Integration testing across all stories
   - Production deployment

**Total Estimated**: 258 tasks, 4 weeks with 4 developers

---

## Task Summary

**Total Tasks**: 258

**By Phase**:
- Phase 1 (Setup): 13 tasks
- Phase 2 (Foundational): 23 tasks
- Phase 3 (US1 - Authentication): 61 tasks
- Phase 4 (US2 - Profile Management): 39 tasks
- Phase 5 (US3 - Stats & Achievements): 44 tasks
- Phase 6 (US4 - Social Connections): 44 tasks
- Phase 7 (Polish): 34 tasks

**By Type**:
- Setup/Infrastructure: 36 tasks
- Tests (TDD): 86 tasks (33% - reflects TDD focus)
- Models/Schemas: 36 tasks
- Services (Business Logic): 32 tasks
- API Endpoints: 24 tasks
- Validation/Error Handling: 20 tasks
- Polish/Quality: 24 tasks

**Parallel Opportunities**: 78 tasks marked [P] can run concurrently (30% parallelizable)

**Independent Test Criteria Met**:
- ✅ User Story 1: Register → Verify → Login → Logout → Reset Password
- ✅ User Story 2: Login → Edit Profile → Upload Photo → View Public Profile
- ✅ User Story 3: Login → Simulate Trip → View Stats → Check Achievements
- ✅ User Story 4: Create 2 Users → Follow → View Lists → Unfollow

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 97 tasks

**Coverage Target**: ≥90% per constitution requirement II (verified in T245-T246)

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story for traceability and independent delivery
- **TDD is MANDATORY** per constitution: Write tests FIRST, ensure they FAIL, then implement
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All error messages MUST be in Spanish per constitution III
- All code MUST follow PEP 8 with black (line length 100) and ruff linter per constitution I
- All functions MUST have type hints and Google-style docstrings per constitution I
- Test coverage MUST be ≥90% per constitution II

**Format Validation**: ✅ All 258 tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
