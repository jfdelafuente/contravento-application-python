# Feature Specification: Travel Diary Frontend

**Feature Branch**: `008-travel-diary-frontend`
**Created**: 2026-01-10
**Status**: Draft
**Input**: User description: "Travel Diary Frontend - List trips, create trips with multi-step form, trip details, upload photos with drag & drop, interactive tags system"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Trip List with Filters (Priority: P1)

As a cyclist, I want to browse my trips and other users' trips so I can discover routes and get inspiration for my next adventure.

**Why this priority**: This is the entry point to the travel diary feature. Users need to see what trips exist before they can create their own or view details. This delivers immediate value by showcasing the content.

**Independent Test**: Can be fully tested by logging in and viewing the trips page. Delivers value by allowing users to see all available trips, filter by tags, status, and search by keywords. Even without creating trips, users can explore existing content.

**Acceptance Scenarios**:

1. **Given** I'm logged in, **When** I navigate to "/trips", **Then** I see a grid of trip cards showing photo, title, distance, dates, and difficulty
2. **Given** I'm on the trips page, **When** I click a tag filter (e.g., "bikepacking"), **Then** only trips with that tag are displayed
3. **Given** I'm viewing trips, **When** I search for "Pirineos", **Then** only trips matching that keyword in title or description appear
4. **Given** I'm viewing my own trips, **When** I toggle "Show Drafts", **Then** my draft trips appear alongside published ones
5. **Given** I'm viewing another user's profile trips, **When** the page loads, **Then** I see only their published trips (no drafts)

---

### User Story 2 - View Trip Details (Priority: P1)

As a cyclist, I want to view complete trip details including photos, route information, and story so I can learn about the journey and plan similar adventures.

**Why this priority**: After discovering trips in the list, users need to see full details. This is the core value proposition of a travel diary - telling the story of cycling adventures with rich media.

**Independent Test**: Can be fully tested by clicking any trip card from the list. Delivers value by showing the complete trip narrative with photo gallery, map, stats, and user comments.

**Acceptance Scenarios**:

1. **Given** I click a trip card, **When** the trip detail page loads, **Then** I see hero image, title, dates, distance, difficulty badge, and full description
2. **Given** I'm viewing trip details, **When** I scroll to the gallery section, **Then** I see all trip photos in a responsive grid with lightbox viewing
3. **Given** I'm viewing trip details, **When** I check the tags section, **Then** I see all tags as clickable chips that filter trips
4. **Given** I'm the trip owner viewing my draft, **When** I see the trip status, **Then** I see "Draft" badge and "Publish" button
5. **Given** I'm viewing trip details, **When** I scroll to the map section, **Then** I see location markers (if provided) on an interactive map

---

### User Story 3 - Create Trip (Multi-Step Form) (Priority: P1)

As a cyclist, I want to create a new trip with a guided multi-step form so I can document my cycling adventures with all important details without feeling overwhelmed.

**Why this priority**: This is the core action that generates content. Without the ability to create trips, the platform has no value. Multi-step form reduces cognitive load and improves completion rate.

**Independent Test**: Can be fully tested by clicking "Create Trip" button. Delivers value by allowing users to document their adventures step by step, with validation and preview before publishing.

**Acceptance Scenarios**:

1. **Given** I click "Create Trip", **When** the form loads, **Then** I see Step 1/4 (Basic Info) with title, dates, distance, and difficulty fields
2. **Given** I complete Step 1, **When** I click "Next", **Then** I proceed to Step 2/4 (Story & Tags) with description editor and tag input
3. **Given** I'm adding tags in Step 2, **When** I type "bikepacking", **Then** I see autocomplete suggestions from existing tags
4. **Given** I complete Step 2, **When** I click "Next", **Then** I proceed to Step 3/4 (Photos) with drag-and-drop upload area
5. **Given** I'm in Step 3, **When** I drag images to the upload zone, **Then** files are validated (JPG/PNG, max 10MB), uploaded with progress bar, and thumbnails appear
6. **Given** I complete Step 3, **When** I click "Next", **Then** I proceed to Step 4/4 (Review & Publish) with summary of all entered data
7. **Given** I'm in Step 4, **When** I click "Save as Draft", **Then** trip is saved with status=DRAFT and I'm redirected to my trips page
8. **Given** I'm in Step 4, **When** I click "Publish", **Then** trip is validated (title, description ≥50 chars, dates valid) and published with status=PUBLISHED

---

### User Story 4 - Upload and Manage Trip Photos (Priority: P2)

As a cyclist, I want to upload multiple photos to my trip with drag-and-drop so I can visually tell the story of my journey without tedious clicking.

**Why this priority**: Photos are essential to travel stories, but this can be done after trip creation. Users can create text-only trips initially and add photos later. This is separated for better UX.

**Independent Test**: Can be fully tested by editing an existing trip and navigating to the photos section. Delivers value by allowing bulk photo uploads with preview, reordering, and deletion.

**Acceptance Scenarios**:

1. **Given** I'm editing a trip, **When** I navigate to the photos step, **Then** I see existing photos (if any) and a drop zone for new uploads
2. **Given** I drag 5 images to the drop zone, **When** I release, **Then** all images are validated, uploaded in parallel with individual progress bars
3. **Given** photos are uploaded, **When** upload completes, **Then** thumbnails appear in the gallery with reorder handles
4. **Given** I want to reorder photos, **When** I drag a photo to a new position, **Then** the order updates and is saved automatically
5. **Given** I want to delete a photo, **When** I click the delete icon, **Then** I see confirmation dialog and photo is removed after confirmation
6. **Given** I upload an invalid file (e.g., .txt), **When** validation runs, **Then** I see error message "Only JPG and PNG images allowed (max 10MB)"

---

### User Story 5 - Edit Existing Trip (Priority: P2)

As a cyclist, I want to edit my trip details after creation so I can correct mistakes, add more information, or update my story as I complete the journey.

**Why this priority**: Editing is important for quality control but not required for initial MVP. Users can create trips first and edit later if needed.

**Independent Test**: Can be fully tested by clicking "Edit" on any owned trip. Delivers value by allowing modifications to all trip fields with the same multi-step form used for creation.

**Acceptance Scenarios**:

1. **Given** I'm viewing my trip, **When** I click "Edit", **Then** the multi-step form loads pre-filled with current trip data
2. **Given** I'm editing a published trip, **When** I modify the description in Step 2, **Then** changes are saved and trip remains published
3. **Given** I'm editing a draft trip, **When** I complete all steps and click "Publish", **Then** trip is validated and published
4. **Given** I'm editing trip dates, **When** I set end_date before start_date, **Then** validation error prevents saving: "End date must be after start date"

---

### User Story 6 - Delete Trip (Priority: P3)

As a cyclist, I want to delete trips I no longer want to keep so I can manage my travel diary and remove content I'm not proud of or that's outdated.

**Why this priority**: Deletion is a maintenance feature that's rarely used. Can be deferred to later iterations without impacting core functionality.

**Independent Test**: Can be fully tested by clicking "Delete" on any owned trip. Delivers value by allowing users to remove unwanted content permanently.

**Acceptance Scenarios**:

1. **Given** I'm viewing my trip, **When** I click "Delete", **Then** I see confirmation dialog with warning about permanent deletion
2. **Given** I confirm deletion, **When** the action completes, **Then** trip and all photos are deleted and I'm redirected to my trips list
3. **Given** I'm viewing my stats dashboard, **When** I delete a published trip, **Then** my stats are automatically recalculated (trip count, km, photos)

---

### Edge Cases

- What happens when a user tries to publish a trip without a title or with description <50 characters?
  → Validation error message appears: "Title is required" and "Description must be at least 50 characters"

- How does the system handle photo upload failures (network error, timeout)?
  → Individual file shows error state with retry button. Other uploads continue unaffected.

- What happens when a user tries to create tags with special characters or very long names?
  → Tags are normalized (lowercase, trim whitespace). Max 30 characters enforced. Special chars allowed except: <>{}[]

- How does the system handle browsing trips when no trips exist?
  → Empty state with illustration and "Create your first trip" call-to-action button

- What happens when a user navigates away from the create/edit form with unsaved changes?
  → Browser prompt: "You have unsaved changes. Are you sure you want to leave?"

- How does the system handle viewing a deleted trip (user follows old link)?
  → 404 error page with message: "This trip no longer exists" and button to browse all trips

- What happens when photo upload exceeds 10MB limit?
  → File is rejected before upload with error: "Image too large (max 10MB). Try compressing it first."

## Requirements *(mandatory)*

### Functional Requirements

#### Trip Listing & Filtering

- **FR-001**: System MUST display trips in a paginated grid layout with 12 trips per page
- **FR-002**: System MUST show trip cards with thumbnail photo, title, distance, date range, and difficulty badge
- **FR-003**: System MUST support filtering trips by tags (clickable tag chips)
- **FR-004**: System MUST support searching trips by keyword (searches title and description)
- **FR-005**: System MUST allow users to toggle visibility of their draft trips on their own profile
- **FR-006**: System MUST only show published trips when viewing other users' profiles
- **FR-007**: System MUST support sorting trips by date (newest first as default) or distance

#### Trip Details View

- **FR-008**: System MUST display full trip information including title, description, dates, distance, difficulty, location, and tags
- **FR-009**: System MUST render trip description with proper HTML formatting (sanitized by backend)
- **FR-010**: System MUST display trip photos in a responsive gallery grid (3 columns desktop, 2 tablet, 1 mobile)
- **FR-011**: System MUST provide lightbox viewing for trip photos with prev/next navigation
- **FR-012**: System MUST show trip status badge ("Draft" or "Published") for owner-viewed trips
- **FR-013**: System MUST display tags as clickable chips that link to tag-filtered trip list
- **FR-014**: System MUST show trip location on interactive map (if location data provided)
- **FR-015**: System MUST display "Edit" and "Delete" buttons only to trip owners
- **FR-016**: System MUST show "Publish" button for draft trips (owner only)

#### Trip Creation (Multi-Step Form)

- **FR-017**: System MUST provide a 4-step wizard for trip creation: (1) Basic Info, (2) Story & Tags, (3) Photos, (4) Review
- **FR-018**: System MUST validate required fields in Step 1: title (required), start_date (required), end_date (optional), distance_km (optional), difficulty (required)
- **FR-019**: System MUST validate description minimum length of 50 characters in Step 2 for publishing (drafts can have shorter descriptions)
- **FR-020**: System MUST provide tag autocomplete suggestions based on existing tags in the system
- **FR-021**: System MUST allow users to add up to 10 tags per trip
- **FR-022**: System MUST normalize tags to lowercase and trim whitespace
- **FR-023**: System MUST provide drag-and-drop photo upload area in Step 3 with multi-file support
- **FR-024**: System MUST validate photo file types (JPG, PNG only) and size (max 10MB per file) before upload
- **FR-025**: System MUST show upload progress for each photo with percentage indicator
- **FR-026**: System MUST support uploading up to 20 photos per trip
- **FR-027**: System MUST display review summary in Step 4 with all entered data
- **FR-028**: System MUST provide "Save as Draft" option that saves trip without validation
- **FR-029**: System MUST provide "Publish" option that validates all required fields and publishes trip
- **FR-030**: System MUST allow navigation back to previous steps to edit data
- **FR-031**: System MUST persist form data across step navigation (no data loss)

#### Trip Editing

- **FR-032**: System MUST pre-fill edit form with existing trip data
- **FR-033**: System MUST use the same 4-step wizard interface for editing as for creation
- **FR-034**: System MUST allow editing all trip fields except trip ID and owner
- **FR-035**: System MUST preserve trip status (draft/published) when editing unless explicitly changed
- **FR-036**: System MUST show unsaved changes warning when navigating away from edit form

#### Photo Management

- **FR-037**: System MUST allow reordering photos via drag-and-drop with visual feedback
- **FR-038**: System MUST persist photo order changes immediately to backend
- **FR-039**: System MUST allow deleting individual photos with confirmation dialog
- **FR-040**: System MUST update gallery display immediately after photo deletion
- **FR-041**: System MUST handle upload failures gracefully with retry option for each failed file

#### Trip Deletion

- **FR-042**: System MUST require confirmation before deleting a trip
- **FR-043**: System MUST delete all associated photos when trip is deleted
- **FR-044**: System MUST redirect user to trips list after successful deletion
- **FR-045**: System MUST recalculate user stats (via backend) when a published trip is deleted

### Key Entities

- **Trip**: A documented cycling journey with title, description, dates, distance, difficulty, status (draft/published), location, and associated photos and tags
- **TripPhoto**: An image attached to a trip with URL, order, file size, dimensions, and optional caption
- **Tag**: A reusable categorization label (e.g., "bikepacking", "mountain", "coast") with normalized name for matching
- **TripLocation**: Optional geographic information for a trip including latitude, longitude, address, and country

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can browse trip list and click into trip details in under 5 seconds
- **SC-002**: Users can complete trip creation form (all 4 steps) in under 8 minutes for average trip (5 photos, 200-word description)
- **SC-003**: Photo upload completes in under 30 seconds for 5 photos (5MB total) on standard broadband
- **SC-004**: Trip list page loads and displays 12 trips in under 2 seconds
- **SC-005**: Tag filtering updates trip list in under 500ms
- **SC-006**: Multi-step form preserves data across navigation with 100% accuracy (no data loss)
- **SC-007**: Photo drag-and-drop upload accepts all valid files (JPG/PNG under 10MB) and rejects invalid files with clear error messages
- **SC-008**: Users can successfully publish trips on first attempt 90% of the time (validation errors caught before final step)
- **SC-009**: Trip gallery lightbox opens and navigates between photos in under 300ms per transition
- **SC-010**: Mobile users can complete all trip creation steps with touch interactions (no desktop-only features)
- **SC-011**: Users can discover trips via tag filters, finding relevant content in 2-3 clicks maximum
- **SC-012**: Photo reordering via drag-and-drop completes with visual feedback in under 200ms per move

## Assumptions

- Backend API endpoints from Feature 002 (Travel Diary Backend) are fully functional and tested
- User authentication is handled by existing auth system (Feature 005)
- Backend handles all photo processing (resize, thumbnail generation, EXIF handling)
- Backend enforces all business rules (photo limits, tag limits, content sanitization)
- Map functionality will use a free tier mapping service (e.g., OpenStreetMap with Leaflet)
- Users have modern browsers with HTML5 drag-and-drop support
- Photo uploads use multipart/form-data with progress tracking
- Backend returns absolute URLs for uploaded photos (no client-side path construction needed)
- Responsive design breakpoints: mobile <640px, tablet 640-1023px, desktop ≥1024px

## Dependencies

- Feature 002: Travel Diary Backend (all API endpoints must be available)
- Feature 005: Frontend User Authentication (auth tokens, protected routes)
- Feature 001: User Profiles Backend (user data for trip owner display)
- React Image Crop library (or similar) for future photo editing features
- Drag-and-drop library (e.g., react-dropzone) for file uploads
- Lightbox library (e.g., react-image-lightbox) for photo viewing
- Form validation library (Zod, already used in Feature 007)
- Map library (e.g., react-leaflet with OpenStreetMap)

## Out of Scope

- **Real-time collaboration**: Multiple users editing the same trip simultaneously
- **Social features**: Comments, likes, sharing trips (deferred to Feature 009)
- **GPS route tracking**: Importing .gpx files and displaying elevation profiles (deferred to Feature 003 frontend)
- **Advanced photo editing**: Filters, cropping, rotation within the app (users must edit photos before upload)
- **Offline mode**: Creating trips without internet connection
- **Trip analytics**: Views count, popular trips dashboard
- **Export functionality**: Downloading trip as PDF or sharing to social media
- **Trip templates**: Pre-filled forms for common trip types
- **Multi-language support**: All UI text will be in Spanish initially
- **Accessibility features**: Screen reader optimization, keyboard-only navigation (will be added in later polish phase)
