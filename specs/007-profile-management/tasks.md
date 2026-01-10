# Tasks: Profile Management

**Input**: Design documents from `/specs/007-profile-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Manual testing only (unit tests deferred per constitution justification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below use `frontend/src/` for React components

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install frontend dependencies: `react-hook-form`, `zod`, `@hookform/resolvers` via npm in frontend/
- [x] T002 [P] Install image cropping library: `react-easy-crop` via npm in frontend/
- [x] T003 [P] Install toast notifications: `react-hot-toast` via npm in frontend/
- [x] T004 [P] Create profile component directory structure in frontend/src/components/profile/
- [x] T005 [P] Create profile hooks directory in frontend/src/hooks/
- [x] T006 [P] Create profile types file in frontend/src/types/profile.ts
- [x] T007 [P] Add ProfileEditPage route to React Router in frontend/src/App.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Define TypeScript interfaces in frontend/src/types/profile.ts (UserProfile, ProfileUpdateRequest, PrivacySettingsUpdate, PasswordChangeRequest, PhotoUploadResponse)
- [x] T009 [P] Create Zod validation schemas in frontend/src/utils/validators.ts (profileEditSchema, passwordChangeSchema, photoUploadSchema)
- [x] T010 [P] Create profileService in frontend/src/services/profileService.ts with updateProfile() and updatePrivacy() functions
- [x] T011 [P] Create photoService in frontend/src/services/photoService.ts with uploadPhoto() function
- [x] T012 [P] Create file helper utilities in frontend/src/utils/fileHelpers.ts (MIME check, size validation)
- [x] T013 Create useUnsavedChanges hook in frontend/src/hooks/useUnsavedChanges.ts for navigation warnings
- [x] T014 Create ProfileEditPage container in frontend/src/pages/ProfileEditPage.tsx with routing and navigation
- [x] T015 [P] Add rustic styling for ProfileEditPage in frontend/src/pages/ProfileEditPage.css

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Edit Basic Profile Information (Priority: P1) 🎯 MVP

**Goal**: Enable users to update bio, location, and cycling type with real-time validation and character counting

**Independent Test**: Log in, navigate to /profile/edit, update bio (200 chars), select location "Barcelona, España", select cycling type "Mountain Biking", save, verify updates display on /profile page. Test unsaved changes warning by navigating away before saving.

### Implementation for User Story 1

- [x] T016 [P] [US1] Create BasicInfoSection component in frontend/src/components/profile/BasicInfoSection.tsx
- [x] T017 [P] [US1] Add bio textarea with real-time character counter (500 max) in BasicInfoSection
- [x] T018 [P] [US1] Add location input field (free text) in BasicInfoSection
- [x] T019 [P] [US1] Add cycling type dropdown (bikepacking, road, mountain, touring, gravel) in BasicInfoSection
- [x] T020 [P] [US1] Add rustic styling for BasicInfoSection in frontend/src/components/profile/BasicInfoSection.css
- [x] T021 [US1] Create useProfileEdit hook in frontend/src/hooks/useProfileEdit.ts with React Hook Form integration
- [x] T022 [US1] Integrate BasicInfoSection into ProfileEditPage with form state management
- [x] T023 [US1] Add Zod validation for bio (max 500 chars), location, and cycling type
- [x] T024 [US1] Implement save button with loading state in ProfileEditPage
- [x] T025 [US1] Add success toast notification on successful profile update
- [x] T026 [US1] Add error handling with Spanish field-specific messages
- [x] T027 [US1] Integrate useUnsavedChanges hook to warn on navigation with unsaved changes
- [ ] T028 [US1] Test acceptance scenarios 1-4 from spec.md for User Story 1

**Checkpoint**: At this point, User Story 1 should be fully functional - users can edit bio/location/cycling type, see validation, save changes, and get warned about unsaved changes.

---

## Phase 4: User Story 2 - Upload and Manage Profile Photo (Priority: P1)

**Goal**: Enable users to upload profile photos (JPG/PNG, max 5MB), crop them with interactive tool, and see immediate updates with progress indication

**Independent Test**: Navigate to /profile/edit, click "Cambiar foto", select JPG under 5MB, use crop interface to select area, save, verify circular photo displays on profile. Test file validation by uploading 10MB file or wrong format.

### Implementation for User Story 2

- [x] T029 [P] [US2] Create PhotoUploadSection component in frontend/src/components/profile/PhotoUploadSection.tsx
- [x] T030 [P] [US2] Add file input with validation (JPG/PNG, max 5MB) in PhotoUploadSection
- [x] T031 [P] [US2] Add current photo preview (200x200px circular) in PhotoUploadSection
- [x] T032 [P] [US2] Add "Cambiar foto" and "Eliminar foto" buttons in PhotoUploadSection
- [x] T033 [P] [US2] Add rustic styling for PhotoUploadSection in frontend/src/components/profile/PhotoUploadSection.css
- [x] T034 [P] [US2] Create PhotoCropModal component in frontend/src/components/profile/PhotoCropModal.tsx with react-easy-crop integration
- [x] T035 [P] [US2] Add crop controls (zoom, rotation) and save/cancel buttons in PhotoCropModal
- [x] T036 [P] [US2] Add rustic modal styling for PhotoCropModal in frontend/src/components/profile/PhotoCropModal.css
- [x] T037 [US2] Create usePhotoUpload hook in frontend/src/hooks/usePhotoUpload.ts with upload progress state
- [x] T038 [US2] Implement photo upload with Axios onUploadProgress callback in photoService.ts
- [x] T039 [US2] Add linear progress bar component during photo upload in PhotoUploadSection
- [x] T040 [US2] Integrate PhotoUploadSection into ProfileEditPage
- [x] T041 [US2] Add file validation with Spanish error messages (size, format)
- [x] T042 [US2] Implement photo preview update after successful upload
- [x] T043 [US2] Add success/error toast notifications for photo operations
- [x] T044 [US2] Implement lazy loading for PhotoCropModal to reduce initial bundle size
- [ ] T045 [US2] Test acceptance scenarios 1-4 from spec.md for User Story 2

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can edit profile info and upload/crop photos.

---

## Phase 5: User Story 3 - Change Password (Priority: P2)

**Goal**: Enable users to change their password with current password verification, real-time strength indicator, and validation feedback

**Independent Test**: Navigate to /profile/edit, enter current password, enter new password (8+ chars, mixed case, number), see strength indicator update, save, verify success message and confirmation email. Test with incorrect current password to see error.

### Implementation for User Story 3

- [x] T046 [P] [US3] Create PasswordChangeSection component in frontend/src/components/profile/PasswordChangeSection.tsx
- [x] T047 [P] [US3] Add current password input field in PasswordChangeSection
- [x] T048 [P] [US3] Add new password input field with visibility toggle in PasswordChangeSection
- [x] T049 [P] [US3] Create password strength indicator component (custom regex-based)
- [x] T050 [P] [US3] Add rustic styling for PasswordChangeSection in frontend/src/components/profile/PasswordChangeSection.css
- [x] T051 [US3] Create usePasswordChange hook in frontend/src/hooks/usePasswordChange.ts
- [x] T052 [US3] Implement password strength calculation (length, uppercase, lowercase, number checks)
- [x] T053 [US3] Add visual password strength bar with color coding (red/yellow/green)
- [x] T054 [US3] Add Zod validation for password requirements (min 8 chars, mixed case, number)
- [x] T055 [US3] Integrate PasswordChangeSection into ProfileEditPage
- [x] T056 [US3] Create changePassword() function in profileService.ts calling PUT /api/profile/me/password
- [x] T057 [US3] Add real-time validation feedback showing which requirements are not met
- [x] T058 [US3] Implement separate save button for password change (independent from profile save)
- [x] T059 [US3] Add success toast with confirmation email message
- [x] T060 [US3] Add error handling for incorrect current password
- [ ] T061 [US3] Test acceptance scenarios 1-4 from spec.md for User Story 3

**Checkpoint**: All P1 and P2 user stories should now be independently functional - profile editing, photo upload, and password change all work.

---

## Phase 6: User Story 4 - Configure Account Privacy Settings (Priority: P3)

**Goal**: Enable users to control profile visibility (public/private) and trip visibility (public/followers/private) with immediate effect

**Independent Test**: Navigate to /profile/edit, toggle "Private Profile" to ON, save, verify profile invisible to non-followers from logged-out view. Select "Followers Only" for trip visibility, save, verify only followers can see trips.

### Implementation for User Story 4

- [x] T062 [P] [US4] Create PrivacySettingsSection component in frontend/src/components/profile/PrivacySettingsSection.tsx
- [x] T063 [P] [US4] Add profile visibility toggle switch (Public/Private) in PrivacySettingsSection
- [x] T064 [P] [US4] Add trip visibility selector (Public/Followers Only/Private) in PrivacySettingsSection
- [x] T065 [P] [US4] Add rustic toggle switch styling in frontend/src/components/profile/PrivacySettingsSection.css
- [x] T066 [US4] Integrate PrivacySettingsSection into ProfileEditPage
- [x] T067 [US4] Add privacy settings to ProfileUpdateRequest type in profile.ts
- [x] T068 [US4] Implement updatePrivacy() function in profileService.ts calling PUT /api/profile/me
- [x] T069 [US4] Add immediate save on toggle change (or deferred with main form save)
- [x] T070 [US4] Add success toast notification for privacy changes
- [x] T071 [US4] Add explanatory text for each privacy option (what it does)
- [ ] T072 [US4] Test acceptance scenarios 1-4 from spec.md for User Story 4

**Checkpoint**: All user stories should now be independently functional - complete profile management feature ready.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T073 [P] Add responsive testing for all sections (mobile: <640px, tablet: 640-1023px, desktop: ≥1024px)
- [ ] T074 [P] Verify all text is in Spanish across all components
- [ ] T075 [P] Add ARIA labels for accessibility (screen readers, keyboard navigation)
- [ ] T076 [P] Add focus states for all interactive elements (buttons, inputs, toggles)
- [ ] T077 [P] Verify color contrast meets WCAG AA standards
- [ ] T078 [P] Test all components with keyboard-only navigation
- [ ] T079 [P] Add loading skeleton for ProfileEditPage initial render
- [x] T080 Create manual testing checklist in specs/007-profile-management/MANUAL_TESTING.md
- [ ] T081 Test edge cases: 10MB+ photo, concurrent edits, session expiry during edit
- [ ] T082 Test performance: form validation <500ms, photo upload <30s, password change <10s
- [ ] T083 Verify all success criteria from spec.md are met (SC-001 through SC-012)
- [x] T084 Code cleanup: Remove console.logs, unused imports, commented code
- [ ] T085 Add TSDoc comments for all public component props and hook signatures
- [ ] T086 Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] T087 Final integration test: Complete all 4 user stories in sequence without errors
- [ ] T088 Create commit with comprehensive message documenting all features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**Key Insight**: All 4 user stories are INDEPENDENT after Foundational phase completes. They can be developed and tested in parallel by different team members.

### Within Each User Story

- Components before integration into ProfileEditPage
- Hooks before component integration
- Services before hooks
- Validation schemas before form integration
- Styling in parallel with component creation
- Testing after story implementation complete

### Parallel Opportunities

- **Setup phase**: All tasks T001-T007 can run in parallel
- **Foundational phase**: Tasks T009-T012 can run in parallel (different files)
- **After Foundational**: All 4 user stories can start in parallel:
  - Developer A: User Story 1 (T016-T028)
  - Developer B: User Story 2 (T029-T045)
  - Developer C: User Story 3 (T046-T061)
  - Developer D: User Story 4 (T062-T072)
- **Polish phase**: Tasks T073-T079 can run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# Launch all component and styling tasks for User Story 1 together:
Task T016: "Create BasicInfoSection component in frontend/src/components/profile/BasicInfoSection.tsx"
Task T017: "Add bio textarea with real-time character counter (500 max) in BasicInfoSection"
Task T018: "Add location input field (free text) in BasicInfoSection"
Task T019: "Add cycling type dropdown (bikepacking, road, mountain, touring, gravel) in BasicInfoSection"
Task T020: "Add rustic styling for BasicInfoSection in frontend/src/components/profile/BasicInfoSection.css"

# Then create hook:
Task T021: "Create useProfileEdit hook in frontend/src/hooks/useProfileEdit.ts with React Hook Form integration"

# Then integrate:
Task T022: "Integrate BasicInfoSection into ProfileEditPage with form state management"
```

---

## Parallel Example: User Story 2

```bash
# Launch all component and styling tasks for User Story 2 together:
Task T029: "Create PhotoUploadSection component in frontend/src/components/profile/PhotoUploadSection.tsx"
Task T030: "Add file input with validation (JPG/PNG, max 5MB) in PhotoUploadSection"
Task T031: "Add current photo preview (200x200px circular) in PhotoUploadSection"
Task T032: "Add 'Cambiar foto' and 'Eliminar foto' buttons in PhotoUploadSection"
Task T033: "Add rustic styling for PhotoUploadSection in frontend/src/components/profile/PhotoUploadSection.css"
Task T034: "Create PhotoCropModal component in frontend/src/components/profile/PhotoCropModal.tsx with react-easy-crop integration"
Task T035: "Add crop controls (zoom, rotation) and save/cancel buttons in PhotoCropModal"
Task T036: "Add rustic modal styling for PhotoCropModal in frontend/src/components/profile/PhotoCropModal.css"

# Then create hook and service:
Task T037: "Create usePhotoUpload hook in frontend/src/hooks/usePhotoUpload.ts with upload progress state"
Task T038: "Implement photo upload with Axios onUploadProgress callback in photoService.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

Both User Stories 1 and 2 are Priority P1, representing the core profile management experience:

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 - Edit Basic Profile (T016-T028)
4. Complete Phase 4: User Story 2 - Upload Profile Photo (T029-T045)
5. **STOP and VALIDATE**: Test both stories independently and together
6. Deploy/demo if ready

**MVP Deliverables**:
- Users can edit bio (500 char max), location, cycling type
- Users can upload and crop profile photos (JPG/PNG, 5MB max)
- Real-time validation with Spanish error messages
- Unsaved changes warnings
- Progress indicators for photo uploads
- Circular profile photo display (200x200px)

### Incremental Delivery

1. Complete Setup + Foundational (T001-T015) → Foundation ready
2. Add User Story 1 (T016-T028) → Test independently → Partial MVP
3. Add User Story 2 (T029-T045) → Test independently → Full MVP (Deploy/Demo!)
4. Add User Story 3 (T046-T061) → Test independently → Enhanced version
5. Add User Story 4 (T062-T072) → Test independently → Complete feature
6. Add Polish (T073-T088) → Production ready

### Parallel Team Strategy

With 2-4 developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - **Developer A**: User Story 1 - Basic Info (T016-T028)
   - **Developer B**: User Story 2 - Photo Upload (T029-T045)
   - **Developer C**: User Story 3 - Password Change (T046-T061)
   - **Developer D**: User Story 4 - Privacy Settings (T062-T072)
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (T073-T088)

**Time Estimate** (single developer, sequential):
- Setup + Foundational: 2-3 hours
- User Story 1: 3-4 hours
- User Story 2: 4-5 hours (cropping complexity)
- User Story 3: 2-3 hours
- User Story 4: 1-2 hours
- Polish: 2-3 hours
- **Total**: 14-20 hours (~2-3 days)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Backend APIs already exist - no backend changes needed
- Manual testing only (unit tests deferred per constitution)
- Commit after each user story completion (Phase 3, 4, 5, 6)
- Stop at any checkpoint to validate story independently
- All text must be in Spanish (error messages, labels, placeholders)
- Follow rustic design system (earth tones, Playfair Display, gradients)
- Ensure responsive design (mobile-first, breakpoints at 640px, 1024px)
- All components must be accessible (ARIA labels, keyboard navigation, WCAG AA contrast)

---

**Total Tasks**: 88
**User Story 1 Tasks**: 13 (T016-T028)
**User Story 2 Tasks**: 17 (T029-T045)
**User Story 3 Tasks**: 16 (T046-T061)
**User Story 4 Tasks**: 11 (T062-T072)
**MVP Tasks** (US1 + US2): 30 tasks (T016-T045)
**Parallel Opportunities**: 40+ tasks marked [P]

**MVP Scope Recommendation**: Complete User Stories 1 and 2 (both P1) for initial deployment - this delivers core profile editing and photo upload capabilities.
