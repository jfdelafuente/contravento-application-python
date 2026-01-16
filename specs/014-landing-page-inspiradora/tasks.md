# Tasks: Landing Page Inspiradora

**Input**: Design documents from `/specs/014-landing-page-inspiradora/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), quickstart.md (complete)

**Tests**: TDD approach enforced - tests MUST be written FIRST before implementation for all components and hooks (≥90% coverage required per constitution).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `frontend/src/`, `frontend/tests/`
- **Backend**: No changes required (frontend-only feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install react-helmet-async dependency in frontend/package.json
- [X] T002 [P] Create landing components directory structure in frontend/src/components/landing/
- [X] T003 [P] Create landing tests directory structure in frontend/tests/unit/landing/
- [X] T004 [P] Create landing images directory in frontend/src/assets/images/landing/
- [X] T005 Add landing page color custom properties to frontend/src/styles/theme.css
- [X] T006 Wrap App with HelmetProvider in frontend/src/main.tsx
- [X] T007 [P] Create placeholder legal pages: TermsOfServicePage.tsx and PrivacyPolicyPage.tsx in frontend/src/pages/
- [X] T008 Add legal page routes to frontend/src/App.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create useSEO custom hook in frontend/src/hooks/useSEO.ts
- [X] T010 Source or create placeholder hero images (hero.jpg, hero.webp, hero-mobile.jpg, hero-mobile.webp) in frontend/src/assets/images/landing/
- [X] T011 Optimize hero images for performance (WebP conversion, compression to < 200KB)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Visitante Descubre la Filosofía ContraVento (Priority: P1) 🎯 MVP

**Goal**: Visitor lands on root URL and sees cinematic hero with "El camino es el destino" headline and 4-pillar manifesto, understanding ContraVento's core philosophy without needing to navigate elsewhere.

**Independent Test**: Navigate to http://localhost:5173/, verify hero image loads with headline, scroll to manifesto section and verify 4 pillars are visible in order. Test on mobile (< 768px), tablet (768-1024px), and desktop (> 1024px).

### Tests for User Story 1 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Unit test for HeroSection component in frontend/tests/unit/landing/HeroSection.test.tsx
- [X] T013 [P] [US1] Unit test for ManifestoSection component in frontend/tests/unit/landing/ManifestoSection.test.tsx
- [X] T014 [P] [US1] Unit test for LandingPage authenticated redirect in frontend/tests/unit/landing/LandingPage.test.tsx

### Implementation for User Story 1

- [X] T015 [P] [US1] Create HeroSection component in frontend/src/components/landing/HeroSection.tsx
- [X] T016 [P] [US1] Create HeroSection styles in frontend/src/components/landing/HeroSection.css
- [X] T017 [P] [US1] Create ManifestoSection component in frontend/src/components/landing/ManifestoSection.tsx
- [X] T018 [P] [US1] Create ManifestoSection styles in frontend/src/components/landing/ManifestoSection.css
- [X] T019 [US1] Create LandingPage container component in frontend/src/pages/LandingPage.tsx (composing HeroSection + ManifestoSection + authenticated redirect logic)
- [X] T020 [US1] Create LandingPage styles in frontend/src/pages/LandingPage.css
- [X] T021 [US1] Update App.tsx to change root route from PublicFeedPage to LandingPage in frontend/src/App.tsx (line 44)
- [X] T022 [US1] Add /trips/public route for PublicFeedPage in frontend/src/App.tsx (after root route)
- [X] T023 [US1] Verify all T012-T014 tests pass after implementation

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Visitor can see hero + manifesto, authenticated users redirect to dashboard.

---

## Phase 4: User Story 2 - Visitante Comprende los Valores Diferenciadores (Priority: P2)

**Goal**: Visitor scrolls to "Pilares de Valor" section and sees 3-column grid (Territorio, Comunidad, Ética) with icons and concise descriptions, understanding how ContraVento's philosophy translates to concrete actions.

**Independent Test**: Navigate to http://localhost:5173/, scroll to Value Pillars section, verify 3 columns on desktop, stacked layout on mobile, hover effects work. Icons from Heroicons should render correctly.

### Tests for User Story 2 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T024 [P] [US2] Unit test for ValuePillarsSection component in frontend/tests/unit/landing/ValuePillarsSection.test.tsx

### Implementation for User Story 2

- [X] T025 [P] [US2] Create ValuePillarsSection component in frontend/src/components/landing/ValuePillarsSection.tsx (import Heroicons: ShoppingBagIcon, UsersIcon, SparklesIcon)
- [X] T026 [P] [US2] Create ValuePillarsSection styles in frontend/src/components/landing/ValuePillarsSection.css (CSS Grid 3 columns, responsive stacking)
- [X] T027 [US2] Integrate ValuePillarsSection into LandingPage container in frontend/src/pages/LandingPage.tsx (add between ManifestoSection and placeholder for next section)
- [X] T028 [US2] Verify T024 test passes after implementation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Visitor sees hero → manifesto → value pillars.

---

## Phase 5: User Story 3 - Visitante Entiende Cómo Funciona la Plataforma (Priority: P2)

**Goal**: Visitor scrolls to "Cómo Funciona" section and sees 4-step numbered flow (Documenta, Comparte, Descubre, Impacta) with icons and descriptions, understanding the practical cycle of using ContraVento.

**Independent Test**: Navigate to http://localhost:5173/, scroll to How It Works section, verify 4 steps numbered 1-4 with icons (CameraIcon, ShareIcon, MapIcon, HeartIcon), horizontal flow on desktop, vertical stack on mobile.

### Tests for User Story 3 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T029 [P] [US3] Unit test for HowItWorksSection component in frontend/tests/unit/landing/HowItWorksSection.test.tsx

### Implementation for User Story 3

- [X] T030 [P] [US3] Create HowItWorksSection component in frontend/src/components/landing/HowItWorksSection.tsx (import Heroicons: CameraIcon, ShareIcon, MapIcon, HeartIcon)
- [X] T031 [P] [US3] Create HowItWorksSection styles in frontend/src/components/landing/HowItWorksSection.css (Flexbox horizontal layout, responsive stacking)
- [X] T032 [US3] Integrate HowItWorksSection into LandingPage container in frontend/src/pages/LandingPage.tsx (add after ValuePillarsSection)
- [X] T033 [US3] Verify T029 test passes after implementation

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Visitor sees complete journey: hero → manifesto → values → how it works.

---

## Phase 6: User Story 4 - Visitante Se Registra en la Plataforma (Priority: P1)

**Goal**: Visitor clicks CTA button "Formar parte del viaje" (visible in hero section and final CTA section) and is redirected to /register page to complete registration.

**Independent Test**: Navigate to http://localhost:5173/, click "Formar parte del viaje" button in hero, verify redirect to /register. Scroll to bottom, verify final CTA section with same button and login link. Click from either location, verify redirect works.

### Tests for User Story 4 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T034 [P] [US4] Unit test for CTASection component in frontend/tests/unit/landing/CTASection.test.tsx
- [X] T035 [P] [US4] E2E test for visitor CTA click journey in frontend/tests/e2e/landing.spec.ts

### Implementation for User Story 4

- [X] T036 [P] [US4] Create CTASection component in frontend/src/components/landing/CTASection.tsx (CTA button + login link)
- [X] T037 [P] [US4] Create CTASection styles in frontend/src/components/landing/CTASection.css (centered, large terracota button)
- [X] T038 [US4] Integrate CTASection into LandingPage container in frontend/src/pages/LandingPage.tsx (add after HowItWorksSection)
- [X] T039 [US4] Verify T034 and T035 tests pass after implementation

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently. Visitor can navigate full landing page and click CTA to register.

---

## Phase 7: User Story 5 - Visitante Accede a Información Adicional (Footer) (Priority: P3)

**Goal**: Visitor scrolls to footer and sees ContraVento branding, social media links (Instagram, Facebook), legal links (Terms, Privacy), and contact email.

**Independent Test**: Navigate to http://localhost:5173/, scroll to bottom, verify footer displays branding, social links open in new tab, legal links navigate to placeholder pages, contact email is clickable mailto link.

### Tests for User Story 5 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T040 [P] [US5] Unit test for Footer component in frontend/tests/unit/landing/Footer.test.tsx

### Implementation for User Story 5

- [X] T041 [P] [US5] Create Footer component in frontend/src/components/landing/Footer.tsx (branding, social links, legal links, contact)
- [X] T042 [P] [US5] Create Footer styles in frontend/src/components/landing/Footer.css (4-column grid desktop, stacked mobile)
- [X] T043 [US5] Integrate Footer into LandingPage container in frontend/src/pages/LandingPage.tsx (add at bottom after CTASection)
- [X] T044 [US5] Verify T040 test passes after implementation

**Checkpoint**: All user stories should now be independently functional. Complete landing page with hero → manifesto → values → how it works → CTA → footer.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, performance optimization, accessibility, and final validation

### Responsive Design & Accessibility

- [ ] T045 [P] Test and refine mobile styles (< 768px) across all sections
- [ ] T046 [P] Test and refine tablet styles (768-1024px) across all sections
- [ ] T047 [P] Verify WCAG AA contrast ratios for all text (terracota CTA: 4.8:1, verde bosque: 15.2:1, gris carbón: 9.7:1)
- [ ] T048 [P] Add ARIA labels and semantic HTML across all components
- [ ] T049 [P] Verify keyboard navigation (Tab, Enter) works for all interactive elements
- [ ] T050 [P] Add alt text to all images (hero image, icons if using img tags)

### Performance Optimization

- [ ] T051 Run Lighthouse audit and verify Core Web Vitals (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] T052 Analyze bundle size and verify < 500KB initial load
- [ ] T053 [P] Implement lazy loading for below-the-fold images
- [ ] T054 [P] Preload critical fonts (Playfair Display) in index.html
- [ ] T055 Verify hero image loads with WebP format and JPG fallback

### Cross-Browser & Device Testing

- [ ] T056 [P] Test on Chrome (latest 2 versions)
- [ ] T057 [P] Test on Firefox (latest 2 versions)
- [ ] T058 [P] Test on Safari macOS (latest 2 versions)
- [ ] T059 [P] Test on Edge (latest 2 versions)
- [ ] T060 [P] Test on Safari iOS (latest version, real device)
- [ ] T061 [P] Test on Chrome Android (latest version, real device)

### E2E Testing

- [ ] T062 [P] E2E test for authenticated user auto-redirect in frontend/tests/e2e/landing.spec.ts
- [ ] T063 [P] E2E test for mobile responsive behavior in frontend/tests/e2e/landing.spec.ts

### SEO & Meta Tags

- [X] T064 Verify SEO meta tags present in page source (title, description, og:image, og:type, twitter:card)
- [ ] T065 Test Open Graph preview using Facebook Sharing Debugger
- [X] T066 Verify semantic HTML structure (h1 → h2 → h3 hierarchy)

### Final Validation

- [X] T067 Run all unit tests and verify ≥90% coverage (172/172 landing page tests passing, 100% coverage)
- [ ] T068 Run all E2E tests and verify passing
- [ ] T069 Execute quickstart.md integration scenarios
- [ ] T070 Verify PublicFeedPage still works at /trips/public route
- [X] T071 Update NEXT_STEPS.md or CHANGELOG.md with feature completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US4 (P1) → US2 (P2) → US3 (P2) → US5 (P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Hero + Manifesto)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Value Pillars)**: Can start after Foundational (Phase 2) - Integrates into LandingPage after US1, but independently testable
- **User Story 3 (P2 - How It Works)**: Can start after Foundational (Phase 2) - Integrates into LandingPage after US2, but independently testable
- **User Story 4 (P1 - CTA & Registration)**: Can start after Foundational (Phase 2) - Integrates into LandingPage after US3, but independently testable (CTA just redirects to existing /register)
- **User Story 5 (P3 - Footer)**: Can start after Foundational (Phase 2) - Integrates into LandingPage at bottom, completely independent

### Within Each User Story (TDD Workflow)

1. Tests MUST be written and FAIL before implementation
2. Component implementation
3. CSS styling
4. Integration into LandingPage container
5. Verify tests pass
6. Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (T001-T008)**:
- T002, T003, T004 can run in parallel (different directories)
- T005, T007 can run in parallel (different files)

**Foundational Phase (T009-T011)**:
- All tasks can run in parallel

**User Story 1 (T012-T023)**:
- Tests T012, T013, T014 can run in parallel (TDD - write first)
- Components T015+T016, T017+T018 can run in parallel (Hero and Manifesto are independent)
- T019, T020, T021, T022 are sequential (container composition and routing)

**User Story 2 (T024-T028)**:
- T024 test written first
- T025, T026 can run in parallel (component + styles)
- T027, T028 are sequential (integration + test verification)

**User Story 3 (T029-T033)**:
- T029 test written first
- T030, T031 can run in parallel (component + styles)
- T032, T033 are sequential (integration + test verification)

**User Story 4 (T034-T039)**:
- T034, T035 tests can run in parallel (unit + E2E)
- T036, T037 can run in parallel (component + styles)
- T038, T039 are sequential (integration + test verification)

**User Story 5 (T040-T044)**:
- T040 test written first
- T041, T042 can run in parallel (component + styles)
- T043, T044 are sequential (integration + test verification)

**Polish Phase (T045-T071)**:
- T045, T046, T047, T048, T049, T050 can run in parallel (different aspects)
- T053, T054, T055 can run in parallel (different optimizations)
- T056, T057, T058, T059, T060, T061 can run in parallel (cross-browser testing)
- T062, T063 can run in parallel (different E2E scenarios)

**Multiple User Stories in Parallel** (if team capacity allows):
- After Foundational phase completes, different developers can work on US1, US2, US3, US4, US5 simultaneously
- Each story integrates into LandingPage container sequentially but can be developed in parallel branches

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task: "Unit test for HeroSection component in frontend/tests/unit/landing/HeroSection.test.tsx"
Task: "Unit test for ManifestoSection component in frontend/tests/unit/landing/ManifestoSection.test.tsx"
Task: "Unit test for LandingPage authenticated redirect in frontend/tests/unit/landing/LandingPage.test.tsx"

# After tests written and failing, launch component development in parallel:
Task: "Create HeroSection component in frontend/src/components/landing/HeroSection.tsx"
Task: "Create HeroSection styles in frontend/src/components/landing/HeroSection.css"
Task: "Create ManifestoSection component in frontend/src/components/landing/ManifestoSection.tsx"
Task: "Create ManifestoSection styles in frontend/src/components/landing/ManifestoSection.css"

# Sequential integration:
Task: "Create LandingPage container component in frontend/src/pages/LandingPage.tsx"
Task: "Update App.tsx to change root route"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 4 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T011) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T012-T023) - Hero + Manifesto
4. Complete Phase 6: User Story 4 (T034-T039) - CTA for registration
5. **STOP and VALIDATE**: Test that visitor can see hero/manifesto and click CTA to register
6. Deploy/demo if ready

This gives you the absolute minimum viable landing page: visitors see the core philosophy (hero + manifesto) and can register (CTA).

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Hero + Manifesto visible)
3. Add User Story 4 → Test independently → Deploy/Demo (CTA functional - MVP complete!)
4. Add User Story 2 → Test independently → Deploy/Demo (Value Pillars add depth)
5. Add User Story 3 → Test independently → Deploy/Demo (How It Works explains cycle)
6. Add User Story 5 → Test independently → Deploy/Demo (Footer completes page)
7. Complete Phase 8: Polish → Final deployment
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T011)
2. Once Foundational is done, split into parallel work:
   - **Developer A**: User Story 1 (T012-T023) - Hero + Manifesto
   - **Developer B**: User Story 2 (T024-T028) - Value Pillars
   - **Developer C**: User Story 3 (T029-T033) - How It Works
   - **Developer D**: User Story 4 (T034-T039) - CTA
   - **Developer E**: User Story 5 (T040-T044) - Footer
3. Each developer integrates their section into LandingPage container sequentially
4. Team completes Phase 8: Polish together (T045-T071)

---

## Notes

- **[P] tasks** = different files, no dependencies, safe to run in parallel
- **[Story] label** maps task to specific user story for traceability
- **TDD enforced**: All tests (T012-T014, T024, T029, T034-T035, T040, T062-T063) MUST be written FIRST and FAIL before implementation
- **Coverage requirement**: ≥90% unit test coverage across all components (constitutional mandate)
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Red → Green → Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Hero image**: Placeholder from Unsplash acceptable for development, replace with official ContraVento image before production
- **Legal pages**: Placeholders created in T007, update with real content post-launch (non-blocking)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Total Tasks**: 71
**Task Count per User Story**:
- Setup (Phase 1): 8 tasks
- Foundational (Phase 2): 3 tasks
- User Story 1 (P1): 12 tasks
- User Story 2 (P2): 5 tasks
- User Story 3 (P2): 5 tasks
- User Story 4 (P1): 6 tasks
- User Story 5 (P3): 5 tasks
- Polish (Phase 8): 27 tasks

**Parallel Opportunities Identified**: 45 tasks marked [P]

**Independent Test Criteria**:
- US1: Navigate to /, see hero + manifesto, test responsive
- US2: Scroll to Value Pillars, see 3 columns, test responsive + hover
- US3: Scroll to How It Works, see 4 steps, test responsive
- US4: Click CTA, redirect to /register
- US5: Scroll to footer, see links, test external link behavior

**Suggested MVP Scope**: User Story 1 (Hero + Manifesto) + User Story 4 (CTA) = 18 tasks (T001-T011, T012-T023, T034-T039)

**Format Validation**: ✅ ALL tasks follow the checklist format (checkbox + ID + optional [P] + optional [Story] + description with file path)

---

**Tasks Generation Status**: ✅ COMPLETE
**Ready for Implementation**: YES
**Next Step**: Begin Phase 1 (Setup) by installing react-helmet-async dependency
