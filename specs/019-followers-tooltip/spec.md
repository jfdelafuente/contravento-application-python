# Feature Specification: Dashboard Followers/Following Tooltips

**Feature Branch**: `019-followers-tooltip`
**Created**: 2026-02-12
**Status**: Draft
**Input**: User description: "Interactive tooltips showing followers/following user lists on hover in dashboard SocialStatsSection"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quick Follower Preview (Priority: P1)

As a cyclist viewing my dashboard, I want to see a preview of who follows me when I hover over the "Seguidores" card, so I can quickly discover my followers without navigating away from the dashboard.

**Why this priority**: This is the core value proposition - allowing users to quickly preview their social connections without disrupting their workflow. It's the primary use case for 80% of interactions with this feature.

**Independent Test**: Can be fully tested by hovering over the followers card, verifying the tooltip appears with 5-8 user avatars and usernames, and delivers immediate social discovery value without any navigation.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard page, **When** I hover over the "Seguidores" card for 500ms, **Then** a tooltip appears showing the first 5-8 followers with avatars and usernames
2. **Given** the followers tooltip is visible, **When** I move my mouse away from the card, **Then** the tooltip disappears after 200ms delay
3. **Given** I have 12 followers, **When** the tooltip displays showing 8 followers, **Then** I see "+ 4 más · Ver todos" link at the bottom
4. **Given** I have 3 followers, **When** the tooltip displays, **Then** all 3 followers are shown without "Ver todos" link
5. **Given** I hover over the followers card, **When** the data is loading, **Then** I see a loading spinner with "Cargando..." message

---

### User Story 2 - Quick Following Preview (Priority: P1)

As a cyclist viewing my dashboard, I want to see a preview of who I'm following when I hover over the "Siguiendo" card, so I can quickly check who I follow without navigating to a separate page.

**Why this priority**: Equal importance to US1 - users need quick access to both their followers AND following lists. This completes the social stats tooltip experience.

**Independent Test**: Can be fully tested by hovering over the following card, verifying the tooltip appears with 5-8 users being followed, and delivers immediate value without navigation.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard page, **When** I hover over the "Siguiendo" card for 500ms, **Then** a tooltip appears showing the first 5-8 users I'm following
2. **Given** the following tooltip is visible, **When** I move my mouse away, **Then** the tooltip disappears after 200ms delay
3. **Given** I'm following 15 users, **When** the tooltip displays showing 8 users, **Then** I see "+ 7 más · Ver todos" link
4. **Given** I'm following 0 users, **When** I hover over the card, **Then** I see "No sigues a nadie aún" message in the tooltip

---

### User Story 3 - Navigate to User Profiles (Priority: P2)

As a cyclist viewing the followers/following tooltip, I want to click on any username to visit their profile, so I can learn more about them or view their trips.

**Why this priority**: Enables the next action after discovery - navigating to a user's profile. This is a secondary action that depends on US1/US2 being implemented first.

**Independent Test**: Can be tested by hovering to show tooltip, clicking on any username, and verifying navigation to `/users/{username}` profile page.

**Acceptance Scenarios**:

1. **Given** the tooltip is visible with user list, **When** I click on a username, **Then** I navigate to that user's profile page at `/users/{username}`
2. **Given** I'm viewing the tooltip, **When** I hover over a username, **Then** the row highlights with background color change
3. **Given** the tooltip is visible, **When** I click outside the tooltip, **Then** the tooltip closes without navigation

---

### User Story 4 - View Complete List (Priority: P2)

As a cyclist viewing the tooltip preview, I want to click "Ver todos" to see the complete list of followers/following, so I can browse all my social connections when the preview isn't enough.

**Why this priority**: Provides progressive disclosure - users who need more than a quick preview can access the full list. Secondary to the primary quick-preview use case.

**Independent Test**: Can be tested by hovering to show tooltip with "+ X más · Ver todos" link, clicking it, and verifying navigation to full list page at `/users/{username}/followers` or `/users/{username}/following`.

**Acceptance Scenarios**:

1. **Given** the tooltip shows "+ 7 más · Ver todos" link, **When** I click it, **Then** I navigate to `/users/{username}/followers` page showing all followers
2. **Given** the following tooltip shows "+ 10 más · Ver todos", **When** I click it, **Then** I navigate to `/users/{username}/following` page showing all following

---

### User Story 5 - Mobile Touch Interaction (Priority: P3)

As a mobile user viewing the dashboard, I want to tap on the social stat cards to see my followers/following, since hover doesn't exist on touch devices.

**Why this priority**: Mobile UX is important but affects a smaller subset of users. Can be implemented after core hover functionality is working on desktop.

**Independent Test**: Can be tested independently on a mobile device by tapping the followers/following cards and verifying appropriate behavior (direct navigation or modal).

**Acceptance Scenarios**:

1. **Given** I'm on a touch device (no hover capability), **When** I tap the "Seguidores" card, **Then** I navigate directly to `/users/{username}/followers` page
2. **Given** I'm on a touch device, **When** I tap the "Siguiendo" card, **Then** I navigate directly to `/users/{username}/following` page

---

### User Story 6 - Keyboard Navigation (Priority: P3)

As a keyboard user, I want to focus on the social stat cards and trigger the tooltip with keyboard, so I can access the same functionality without a mouse.

**Why this priority**: Accessibility requirement for WCAG 2.1 AA compliance. Important but lower priority than core functionality since most users will use mouse/touch.

**Independent Test**: Can be tested independently using only keyboard (Tab to navigate, Enter/Space to activate) and verifying tooltip displays and is navigable.

**Acceptance Scenarios**:

1. **Given** I'm navigating with keyboard, **When** I Tab to the followers card and it receives focus, **Then** the tooltip appears after 500ms
2. **Given** the tooltip is visible, **When** I press Tab, **Then** focus moves to the first username link in the tooltip
3. **Given** the tooltip is visible, **When** I press Escape, **Then** the tooltip closes immediately
4. **Given** I'm focused on a username link in the tooltip, **When** I press Enter, **Then** I navigate to that user's profile

---

### Edge Cases

- What happens when a user has 0 followers? → Tooltip shows "No tienes seguidores aún" message
- What happens when a user has 0 following? → Tooltip shows "No sigues a nadie aún" message
- How does the system handle network errors while loading tooltip data? → Shows "Error al cargar usuarios" message with red border
- What happens if I hover quickly and move away before 500ms? → Tooltip never appears (hover delay prevents accidental tooltips)
- What happens if I move my mouse from the card into the tooltip? → Tooltip stays visible (200ms leave delay allows this transition)
- What happens if the tooltip would overflow the screen on small viewports? → Tooltip uses max-width and responsive sizing (200-280px)
- How does the system handle very long usernames in the tooltip? → Text-overflow ellipsis truncates with "..." after ~18 characters

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a tooltip when user hovers over the "Seguidores" card for 500ms or more
- **FR-002**: System MUST display a tooltip when user hovers over the "Siguiendo" card for 500ms or more
- **FR-003**: System MUST fetch follower/following data lazily (only when tooltip is triggered, not on page load)
- **FR-004**: System MUST display the first 5-8 users in the tooltip preview (limited preview for performance)
- **FR-005**: System MUST show each user in the tooltip with their avatar (profile photo or placeholder) and username
- **FR-006**: System MUST display a "Ver todos" link when total count exceeds the preview limit (e.g., "+ 7 más · Ver todos")
- **FR-007**: System MUST navigate to `/users/{username}` when a username is clicked in the tooltip
- **FR-008**: System MUST navigate to `/users/{username}/followers` when "Ver todos" is clicked in the followers tooltip
- **FR-009**: System MUST navigate to `/users/{username}/following` when "Ver todos" is clicked in the following tooltip
- **FR-010**: System MUST hide the tooltip 200ms after the mouse leaves both the card and the tooltip area
- **FR-011**: System MUST keep the tooltip visible when the mouse moves from the card into the tooltip (allowing interaction with links)
- **FR-012**: System MUST show a loading state ("Cargando..." with spinner) while fetching user data
- **FR-013**: System MUST show an error message ("Error al cargar usuarios") if the network request fails
- **FR-014**: System MUST display "No tienes seguidores aún" message when the user has 0 followers
- **FR-015**: System MUST display "No sigues a nadie aún" message when the user is following 0 users
- **FR-016**: System MUST use existing endpoints `/users/{username}/followers` and `/users/{username}/following` for data fetching
- **FR-017**: System MUST display placeholder avatar (first letter of username) when user has no profile photo
- **FR-018**: System MUST position the tooltip centered below the social stat card with 8px spacing
- **FR-019**: System MUST show an arrow pointing from tooltip to the card it originates from
- **FR-020**: System MUST truncate long usernames with ellipsis (...) when they exceed the tooltip width
- **FR-021**: System MUST apply fade-in animation (150ms) when tooltip appears
- **FR-022**: System MUST apply fade-out animation (150ms) when tooltip disappears
- **FR-023**: On touch devices (no hover capability), system MUST navigate directly to full list page when card is tapped (no tooltip)
- **FR-024**: System MUST support keyboard navigation: Tab to card, focus triggers tooltip, Tab through links, Escape closes
- **FR-025**: System MUST include ARIA attributes for screen reader accessibility (role="tooltip", aria-live="polite", aria-describedby)

### Key Entities *(include if feature involves data)*

- **FollowerPreview**: Represents a preview of the first 5-8 followers
  - Attributes: list of UserSummaryForFollow, total_count, has_more (boolean indicating if "Ver todos" should appear)

- **FollowingPreview**: Represents a preview of the first 5-8 users being followed
  - Attributes: list of UserSummaryForFollow, total_count, has_more

- **UserSummaryForFollow**: Represents a single user in the tooltip list (existing type from followService.ts)
  - Attributes: user_id, username, profile_photo_url (nullable)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can preview their followers/following within 1 second of hovering over the card (includes 500ms hover delay + <500ms API response)
- **SC-002**: Tooltip appears and disappears smoothly with no visual jank or layout shifts
- **SC-003**: 90% of users discover the tooltip feature organically through hover without explicit instructions
- **SC-004**: Users can navigate to a user profile from the tooltip in 2 clicks or less (hover → click username)
- **SC-005**: Tooltip preview reduces full-list page navigation by 60% (users get value from preview alone)
- **SC-006**: Feature works correctly on desktop browsers (Chrome, Firefox, Safari, Edge) with hover support
- **SC-007**: Feature gracefully degrades on mobile devices by providing direct navigation instead of tooltips
- **SC-008**: Keyboard users can access all tooltip functionality using only keyboard (Tab, Enter, Escape)
- **SC-009**: Screen readers announce tooltip content and loading/error states appropriately
- **SC-010**: Tooltip loading state appears within 100ms of hover trigger to provide immediate feedback
- **SC-011**: Accidental tooltip triggers are reduced to <5% through 500ms hover delay
- **SC-012**: Users can move their mouse from card to tooltip without it closing (200ms leave delay)
- **SC-013**: Feature does not increase dashboard initial page load time (lazy loading on hover only)
- **SC-014**: Tooltip handles edge cases (0 followers, network errors, long usernames) without breaking layout
- **SC-015**: Feature accessibility passes WCAG 2.1 AA automated tests (axe-core or similar)

## Assumptions

1. **Existing Endpoints**: We assume the endpoints `/users/{username}/followers` and `/users/{username}/following` already exist and return the required UserSummaryForFollow data structure with user_id, username, and profile_photo_url fields.

2. **User Authentication**: We assume the user is authenticated when viewing the dashboard and their username is available via the useAuth() hook.

3. **Photo URLs**: We assume profile_photo_url is either a valid absolute URL or null (no photo), and we'll display a placeholder avatar (first letter) when null.

4. **Preview Limit**: We assume showing 5-8 users in the tooltip is sufficient for a "quick preview" based on industry standards (Instagram, Twitter, LinkedIn show similar counts).

5. **Hover Delay**: We assume 500ms hover delay is optimal to prevent accidental tooltip triggers based on UX research (standard for tooltips).

6. **Mobile Detection**: We assume we can detect touch devices using `window.matchMedia('(hover: none)')` to provide appropriate mobile fallback behavior.

7. **Navigation Routes**: We assume the routes `/users/{username}`, `/users/{username}/followers`, and `/users/{username}/following` already exist in the React Router configuration.

8. **Styling System**: We assume the application uses CSS custom properties (--surface-elevated, --border-emphasis, --accent-amber, etc.) and spacing variables (--space-2, --space-3, etc.) that we can reuse for the tooltip styling.

9. **Internationalization**: We assume all user-facing text will be in Spanish (primary language of ContraVento application) as per the project's existing convention.

10. **Performance**: We assume fetching 5-8 users from the existing endpoints will return in under 500ms on average, allowing the total tooltip display time (hover delay + API call) to be under 1 second.

## Dependencies

- **Frontend**: Existing followService.ts with getFollowers() and getFollowing() functions
- **Frontend**: Existing useAuth() hook providing current user's username
- **Frontend**: Existing React Router configuration with routes for user profiles and follower/following lists
- **Frontend**: Existing CSS design system with custom properties for colors, spacing, and borders
- **Backend**: Existing API endpoints `/users/{username}/followers` and `/users/{username}/following` that return FollowersListResponse and FollowingListResponse respectively

## Out of Scope

- **Full Follower/Following Pages**: This feature only implements the tooltip preview. The full list pages (`/users/{username}/followers` and `/users/{username}/following`) are assumed to exist or will be implemented separately.

- **Follow/Unfollow Actions in Tooltip**: Users cannot follow/unfollow directly from the tooltip. They must navigate to user profiles to perform these actions.

- **Search/Filter in Tooltip**: The tooltip displays a simple chronological list. No search or filtering capabilities are included.

- **Real-Time Updates**: The tooltip data is fetched on hover and cached. It does not update in real-time if someone follows/unfollows the user while the tooltip is visible.

- **Infinite Scroll in Tooltip**: The tooltip displays a fixed preview (5-8 users max). There is no infinite scroll or pagination within the tooltip itself.

- **Customizable Preview Count**: The number of users shown (5-8) is hardcoded and not user-configurable.

- **Hover-to-Follow on Avatars**: Hovering over user avatars in the tooltip does not trigger any additional actions or nested tooltips.

- **Backend Changes**: This is a frontend-only feature. No changes to backend API endpoints, database schema, or business logic are required.
