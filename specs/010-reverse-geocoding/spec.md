# Feature Specification: Reverse Geocoding

**Feature Branch**: `010-reverse-geocoding`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Geocoding Reverso: Click en mapa para seleccionar ubicaciones automáticamente con API de Nominatim"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Click Map to Add Location (Priority: P1)

When creating or editing a trip, users can click directly on the map to automatically add a location with GPS coordinates and a place name retrieved from the geocoding service. This eliminates the need to manually look up coordinates or type location names.

**Why this priority**: This is the core value proposition of the feature - enabling fast, accurate location selection through map interaction. It transforms the location input workflow from tedious manual entry to intuitive point-and-click.

**Independent Test**: Can be fully tested by opening the trip creation/edit form, clicking anywhere on the map, and verifying that a new location appears in the locations list with both coordinates and a suggested place name. Delivers immediate value by simplifying location entry.

**Acceptance Scenarios**:

1. **Given** user is creating a new trip with the map visible, **When** user clicks a point on the map (e.g., a park in Madrid), **Then** system displays a confirmation modal showing the suggested place name (e.g., "Parque del Retiro") and coordinates
2. **Given** user sees the confirmation modal with suggested place name, **When** user confirms the selection, **Then** the location is added to the trip's location list with the name and coordinates populated
3. **Given** user is editing an existing trip, **When** user clicks the map to add a new location, **Then** the new location is added to the existing locations list in sequence order
4. **Given** user clicks on a remote area with no named place nearby, **When** geocoding returns generic coordinates, **Then** system shows coordinates with a default name like "Ubicación sin nombre" and allows user to edit the name before confirming

---

### User Story 2 - Adjust Location by Dragging Marker (Priority: P2)

After adding a location via map click or manual entry, users can fine-tune the exact GPS coordinates by dragging the location marker on the map. This allows precise positioning without re-entering coordinates.

**Why this priority**: Complements P1 by enabling refinement of locations. Essential for accuracy but can be implemented after basic click-to-add functionality works.

**Independent Test**: Can be tested by creating a trip with at least one location that has GPS coordinates, entering edit mode, and dragging a marker to a new position. The location's coordinates should update to match the new marker position.

**Acceptance Scenarios**:

1. **Given** trip has locations with GPS coordinates displayed on map, **When** user enters "edit mode" for the map, **Then** all location markers become draggable
2. **Given** user is in map edit mode, **When** user drags a marker to a new position, **Then** the marker moves to the new position and the coordinates update in real-time
3. **Given** user drags a marker to a new position, **When** user releases the marker, **Then** system triggers reverse geocoding to suggest an updated place name based on new coordinates
4. **Given** user has dragged a marker and sees the new suggested name, **When** user confirms the change, **Then** the location's coordinates and name are updated in the locations list

---

### User Story 3 - Edit Location Name Before Saving (Priority: P3)

When the system suggests a place name from reverse geocoding, users can edit or customize the name before adding the location to their trip. This ensures users have control over how locations are labeled.

**Why this priority**: Provides user control and personalization, but the feature is still usable without this capability (users can accept suggested names or edit later).

**Independent Test**: Can be tested by clicking the map to trigger a location suggestion, editing the suggested name in the confirmation modal, and verifying the custom name is saved instead of the suggested one.

**Acceptance Scenarios**:

1. **Given** user clicks the map and sees a confirmation modal with suggested place name "Mirador de San Nicolás", **When** user edits the name to "Mirador favorito del Albaicín", **Then** the edited name is displayed in the preview
2. **Given** user has edited the suggested place name, **When** user confirms the location, **Then** the custom name is saved to the trip's locations list (not the suggested name)
3. **Given** suggested place name is very long or generic (e.g., "Calle de Alcalá, 123, Madrid, Comunidad de Madrid, España"), **When** user sees the confirmation modal, **Then** system displays the full name but allows easy editing with a clear input field
4. **Given** reverse geocoding fails to return a place name, **When** user sees the confirmation modal, **Then** the name field is pre-filled with "Ubicación sin nombre" and the user can provide a custom name

---

### Edge Cases

- **What happens when reverse geocoding API is unavailable or times out?**
  - System should fall back to displaying coordinates only with a default name like "Ubicación (lat, lng)"
  - User can still add the location and edit the name manually
  - Show a warning message: "No se pudo obtener el nombre del lugar. Verifica tu conexión."

- **What happens when user clicks the map in a location with no nearby places (e.g., ocean, desert)?**
  - Geocoding API may return very generic results (e.g., "Atlantic Ocean", "Desierto del Sahara")
  - System should accept these but clearly indicate they are low-confidence results
  - User should be prompted to edit the name to something more meaningful for their trip

- **What happens when user clicks the map rapidly multiple times?**
  - System should debounce/throttle map clicks to prevent multiple simultaneous geocoding requests
  - Show a loading indicator on the first click and disable further clicks until the confirmation modal appears
  - Rate-limit geocoding API calls to respect Nominatim's 1 request/second limit

- **What happens when user drags a marker to an invalid location (e.g., outside valid lat/lng bounds)?**
  - System should constrain marker position to valid geographic coordinates (-90 to 90 lat, -180 to 180 lng)
  - If user somehow drags to invalid coordinates, show validation error and reset marker to last valid position

- **What happens when editing a trip with 20+ locations and map has many overlapping markers?**
  - System should provide zoom controls and marker clustering to prevent UI clutter
  - In edit mode, highlight the currently selected marker to make it easily identifiable
  - Consider showing a numbered list alongside the map to select locations without clicking crowded markers

- **What happens when reverse geocoding returns a place name in a different language than Spanish?**
  - Accept the returned name as-is (Nominatim returns names in the local language of the place)
  - User can edit the name to Spanish if desired
  - Document that place names will be in the native language of the location (e.g., "Paris" not "París", "München" not "Múnich")

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to click on the map to trigger location selection during trip creation or editing
- **FR-002**: System MUST send the clicked coordinates (latitude, longitude) to a reverse geocoding service to retrieve a suggested place name
- **FR-003**: System MUST display a confirmation modal showing the suggested place name and coordinates before adding the location to the trip
- **FR-004**: System MUST allow users to edit the suggested place name in the confirmation modal before confirming
- **FR-005**: System MUST add the confirmed location (with coordinates and name) to the trip's locations list in sequence order
- **FR-006**: System MUST enable drag-and-drop editing of location markers when in "map edit mode"
- **FR-007**: System MUST update location coordinates when a marker is dragged to a new position
- **FR-008**: System MUST trigger reverse geocoding when a marker is dragged to suggest an updated place name
- **FR-009**: System MUST handle reverse geocoding failures gracefully by allowing users to add locations with coordinates only and a default/custom name
- **FR-010**: System MUST respect the Nominatim OpenStreetMap API usage policy of maximum 1 request per second
- **FR-011**: System MUST cache reverse geocoding results to avoid duplicate API calls for the same coordinates (within 100m radius)
- **FR-012**: System MUST provide visual feedback (loading indicator) while waiting for geocoding API response
- **FR-013**: System MUST validate that clicked/dragged coordinates are within valid geographic bounds (latitude: -90 to 90, longitude: -180 to 180)
- **FR-014**: System MUST maintain the existing manual coordinate entry option as an alternative to map clicking
- **FR-015**: System MUST persist updated locations (from map clicks or marker drags) when the trip is saved

### Key Entities

- **Location Selection**: Represents a temporary state when user has clicked the map but not yet confirmed the location. Contains suggested place name, coordinates, and confirmation status.
- **Reverse Geocoding Request**: Represents an API call to retrieve place name from coordinates. Contains request timestamp (for rate limiting), coordinates, response data, and cache key.
- **Map Edit Mode**: Represents the state of the map component when markers are draggable. Controls whether locations can be repositioned via drag-and-drop.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a location to their trip in under 10 seconds using map click (vs. 30+ seconds with manual coordinate lookup)
- **SC-002**: 90% of location additions use map click instead of manual coordinate entry (measured after 2 weeks of feature availability)
- **SC-003**: Reverse geocoding API responds within 2 seconds for 95% of requests
- **SC-004**: System successfully retrieves a place name for at least 85% of map clicks (remaining 15% may be remote areas with no named places)
- **SC-005**: Marker drag operations update coordinates smoothly with no perceived lag (< 100ms response time)
- **SC-006**: Zero violations of Nominatim API rate limit (1 request/second) under normal usage
- **SC-007**: Users report improved satisfaction with location entry workflow (measured via post-release survey or user feedback)
- **SC-008**: Support tickets related to "how to add GPS coordinates" decrease by at least 50% after feature release
