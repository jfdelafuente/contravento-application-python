# Phase 0: Technical Research - Reverse Geocoding

**Feature**: 010-reverse-geocoding
**Date**: 2026-01-11
**Purpose**: Resolve technical unknowns and establish implementation approach

## Research Questions

### Q1: Which Reverse Geocoding API to Use?

**Decision**: Nominatim OpenStreetMap API

**Rationale**:
- **Free and Open Source**: No API key required, no usage fees
- **Global Coverage**: Complete worldwide address data from OpenStreetMap
- **Well-Documented**: Official Nominatim API documentation at nominatim.org
- **Rate Limit**: 1 request/second for free tier (acceptable for manual user interactions)
- **Response Quality**: Returns structured address components (road, city, country, postcode)
- **Language Support**: Supports Spanish language responses via `accept-language` header
- **No Vendor Lock-in**: Open source, can self-host if needed in future
- **Privacy**: No user tracking, no data retention policies to comply with

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Google Geocoding API | High accuracy, fast responses | Requires API key, costs $5/1000 requests after free tier | Cost prohibitive for scaling |
| Mapbox Geocoding | Good accuracy, modern API | Requires API key, $0.75/1000 requests | Cost and API key management |
| LocationIQ | Nominatim-based, better rate limits | Requires API key, commercial service | Adds dependency vs free Nominatim |
| Azure Maps | Enterprise-grade, Microsoft backing | Requires Azure account, complex pricing | Overkill for simple reverse geocoding |

**Implementation Notes**:
- Use official Nominatim endpoint: `https://nominatim.openstreetmap.org/reverse`
- Query parameters: `lat`, `lon`, `format=json`, `accept-language=es`
- Response structure: `{ display_name, address: { road, city, country, postcode }, lat, lon }`
- User-Agent header required: `ContraVento/1.0 (contact@contravento.com)`

---

### Q2: Frontend Map Click Handling Pattern

**Decision**: Use react-leaflet's `useMapEvents` hook with custom click handler

**Rationale**:
- **Built-in Support**: react-leaflet provides `useMapEvents()` hook for map interactions
- **Type Safety**: TypeScript definitions available for all event types
- **Event Bubbling Control**: Can prevent event propagation to markers
- **Already Installed**: react-leaflet@4.x already in package.json from Feature 009
- **Performance**: No additional library needed, minimal bundle size impact
- **Consistent API**: Aligns with existing TripMap component architecture

**Pattern**:
```typescript
import { useMapEvents } from 'react-leaflet';

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onMapClick, enabled }) => {
  useMapEvents({
    click(e: LeafletMouseEvent) {
      if (enabled) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null; // This component renders nothing
};
```

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Native Leaflet event listeners | Direct control, no React wrapper | Breaks React paradigm, harder to test | Not idiomatic React |
| Custom div overlay with onClick | Simple implementation | Breaks map interactions (zoom, pan) | UX regression |
| Third-party library (react-map-gl) | Feature-rich | Requires migration from react-leaflet | Too disruptive |

---

### Q3: Marker Dragging Implementation

**Decision**: Use Leaflet's built-in `draggable` marker option with `dragend` event

**Rationale**:
- **Native Feature**: Leaflet Marker supports `draggable` prop out of the box
- **Event Handling**: `dragend` event provides final position after drag completes
- **Performance**: Browser-native drag-and-drop, no additional libraries
- **Accessibility**: Works with keyboard navigation (arrow keys) when marker focused
- **Already Used**: Existing TripMap uses Leaflet Marker component

**Pattern**:
```typescript
<Marker
  position={[location.latitude!, location.longitude!]}
  draggable={isEditMode}
  eventHandlers={{
    dragend: (e: DragEndEvent) => {
      const marker = e.target;
      const position = marker.getLatLng();
      onMarkerDrag(location.location_id, position.lat, position.lng);
    },
  }}
/>
```

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| React-DnD library | Consistent drag API | Requires React context setup | Overkill for simple marker drag |
| Custom mouse event handlers | Full control | Complex touch/mouse logic | Reinventing the wheel |

---

### Q4: Geocoding Response Caching Strategy

**Decision**: Client-side cache with LRU eviction (max 100 entries, 100m radius)

**Rationale**:
- **Rate Limit Compliance**: Prevents duplicate API calls to Nominatim (1 req/sec limit)
- **Performance**: Instant response for nearby clicks (<100m from cached location)
- **Simple Implementation**: Use `Map<string, GeocodingResponse>` with key = `${lat.toFixed(3)},${lng.toFixed(3)}`
- **Privacy**: No server-side storage, cache cleared on page reload
- **User Experience**: Reduces loading time when user clicks near previous location

**Cache Key Strategy**:
- Round coordinates to 3 decimal places (~111m precision)
- Example: Click at (40.416775, -3.703790) → Cache key "40.417,-3.704"
- All clicks within 111m use same cache key

**Eviction Policy**:
- LRU (Least Recently Used) with max 100 entries
- When cache full, remove oldest unused entry
- Cache survives component re-renders (useRef or React Context)

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Server-side cache (Redis) | Shared across users | Infrastructure cost, deployment complexity | Overkill for user-specific workflow |
| IndexedDB cache | Persists across sessions | Async API, quota limits | Not needed for session-only usage |
| No caching | Simplest | Violates rate limit, slow UX | Unacceptable UX and API abuse |

---

### Q5: Confirmation Modal Pattern

**Decision**: Controlled modal component with confirmation/edit/cancel actions

**Rationale**:
- **User Control**: Allows editing suggested name before accepting
- **Error Recovery**: User can cancel if geocoding returns wrong result
- **Consistent UX**: Matches existing ContraVento modal patterns (e.g., delete confirmation in TripDetailPage)
- **Accessibility**: Modal can trap focus, announce via ARIA live region
- **Validation**: Can validate user input before confirming location

**Modal Structure**:
```typescript
interface LocationConfirmModalProps {
  isOpen: boolean;
  suggestedName: string;
  coordinates: { lat: number; lng: number };
  onConfirm: (name: string, lat: number, lng: number) => void;
  onCancel: () => void;
}

// User can:
// 1. See suggested name from geocoding
// 2. Edit name in text input
// 3. Confirm → adds location to trip
// 4. Cancel → closes modal, discards location
```

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Inline editing (no modal) | Faster workflow | Harder to cancel, cluttered UI | UX regression |
| Toast notification only | Non-blocking | No editing capability | Fails FR-004 |
| Two-step flow (add → edit) | Simpler code | Extra click required | Slower UX |

---

### Q6: Edit Mode Toggle Mechanism

**Decision**: Prop-based edit mode with explicit "Edit Locations" button

**Rationale**:
- **Clear Intent**: User explicitly enters edit mode, preventing accidental drags
- **State Management**: Simple boolean prop `isEditMode` passed to TripMap
- **Visual Feedback**: Edit mode shows "Save" and "Cancel" buttons, different cursor
- **Testability**: Easy to test edit vs view mode in isolation
- **Consistent Pattern**: Matches existing TripEditPage workflow

**UI Flow**:
1. User opens trip edit form (TripEditPage)
2. TripMap initially in view mode (draggable=false)
3. User clicks "Edit Locations on Map" button
4. Map enters edit mode (draggable=true, cursor: move)
5. User drags markers or clicks map to add locations
6. User clicks "Save" → updates trip.locations
7. User clicks "Cancel" → reverts to original locations

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Always-draggable markers | Simpler code | Accidental drags, confusing UX | Poor UX |
| Keyboard modifier (Ctrl+click) | Power-user friendly | Discoverability issues | Accessibility concern |
| Context menu (right-click) | Familiar pattern | Inconsistent across browsers | UX inconsistency |

---

### Q7: Rate Limiting Implementation

**Decision**: Debounced API calls with 1-second delay + request queue

**Rationale**:
- **Nominatim Compliance**: 1 request/second maximum (free tier)
- **User Experience**: Prevents rapid-clicking from triggering multiple requests
- **Simple Implementation**: Use lodash.debounce or custom debounce function
- **Queue Management**: If requests queued, show loading indicator and process sequentially

**Debounce Strategy**:
```typescript
const debouncedGeocode = useMemo(
  () => debounce(async (lat: number, lng: number) => {
    // Check cache first
    // If miss, call Nominatim API
    // Update cache
  }, 1000),
  []
);
```

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Throttle (1 req/sec) | Guaranteed rate limit | Ignores user's last click if rapid | Poor UX for final click |
| No rate limiting | Simplest code | Violates Nominatim ToS, risks IP ban | Unacceptable risk |
| Backend rate limiting only | Centralized control | Network latency for rejected requests | Wastes bandwidth |

---

### Q8: Error Handling Strategy

**Decision**: Graceful degradation with fallback to coordinate-only location

**Rationale**:
- **User Progress**: Never block user from adding location, even if geocoding fails
- **Clear Messaging**: Show Spanish error message explaining failure
- **Default Name**: Use "Ubicación (lat, lng)" as fallback name
- **Retry Option**: Allow user to manually edit name and retry if desired
- **Logging**: Log errors to console for debugging, don't expose to user

**Error Scenarios**:

| Error | Handling | User Experience |
|-------|----------|-----------------|
| Network timeout | Show fallback name after 5s | "No se pudo obtener el nombre. Edita el nombre manualmente." |
| Rate limit exceeded | Queue request, retry after 1s | Loading indicator, eventual success or timeout |
| Invalid coordinates (ocean) | Accept generic result | "Océano Atlántico" or "Ubicación sin nombre" |
| API error (500) | Fallback to coordinates | "Error al conectar con el servicio de mapas" |
| Malformed response | Fallback to coordinates | Logs error, user sees default name |

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Block UI until success | Enforces valid names | Poor UX, blocks workflow | Unacceptable blocking |
| Silent failure | Simplest code | User confused why name is blank | Poor UX |
| Retry with exponential backoff | Maximizes success rate | Complex code, long wait times | Over-engineered |

---

## Technology Stack Summary

### Frontend (React/TypeScript)

| Technology | Version | Purpose | Already Installed? |
|-----------|---------|---------|-------------------|
| react-leaflet | 4.x | Map interaction hooks | ✅ Yes (Feature 009) |
| Leaflet.js | 1.9.x | Core mapping library | ✅ Yes (Feature 009) |
| axios | 1.x | HTTP client for geocoding API | ✅ Yes (existing) |
| lodash.debounce | 4.x | Rate limiting implementation | ❌ **New dependency** |

**New Frontend Files**:
- `frontend/src/components/trips/LocationConfirmModal.tsx` - Confirmation modal
- `frontend/src/components/trips/MapClickHandler.tsx` - Click event handler component
- `frontend/src/hooks/useReverseGeocode.ts` - Geocoding logic hook
- `frontend/src/services/geocodingService.ts` - Nominatim API client
- `frontend/src/utils/geocodingCache.ts` - LRU cache implementation

### Backend (Python/FastAPI)

| Technology | Version | Purpose | Already Installed? |
|-----------|---------|---------|-------------------|
| httpx | 0.24.x | Async HTTP client for Nominatim | ✅ Yes (existing) |
| cachetools | 5.x | Server-side cache (optional) | ❌ **Optional** |

**New Backend Files**:
- `backend/src/services/geocoding_service.py` - Reverse geocoding service (optional backend wrapper)
- `backend/src/api/geocoding.py` - Geocoding API endpoints (optional, direct frontend→Nominatim preferred)

**Decision**: Implement geocoding **frontend-only** initially
- **Rationale**: Nominatim supports CORS, direct frontend calls reduce latency
- **Future**: Add backend proxy if rate limiting or caching needed across users

---

## Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Geocoding API response | <2s p95 | Browser DevTools Network tab |
| Map click → modal open | <500ms | User perception, no loading spinner needed |
| Marker drag → coordinate update | <100ms | Real-time, no perceptible lag |
| Cache hit rate | >70% | Log cache hits/misses in console |
| Rate limit violations | 0 | Monitor Nominatim responses for 429 errors |

---

## Security & Privacy Considerations

### Data Privacy
- **No PII Sent**: Only lat/lng coordinates sent to Nominatim (no user email, name, etc.)
- **No Tracking**: Nominatim doesn't track users or require authentication
- **Client-Side Cache**: Cache stored in browser memory, cleared on page reload
- **GDPR Compliance**: No personal data persisted server-side

### API Security
- **User-Agent Header**: Include `ContraVento/1.0 (contact@contravento.com)` as required by Nominatim
- **Rate Limiting**: Enforce 1 req/sec client-side to comply with ToS
- **No API Key**: Nominatim doesn't require API key, no secret to protect
- **HTTPS Only**: Nominatim endpoint uses HTTPS, prevents MITM attacks

### Input Validation
- **Coordinate Bounds**: Validate lat (-90 to 90) and lng (-180 to 180) before API call
- **Cache Key Sanitization**: Round coordinates to prevent cache pollution
- **User Input Sanitization**: Escape location name before saving to database (existing trip validation)

---

## Testing Strategy

### Unit Tests
- `useReverseGeocode` hook: Mock axios, test cache hits/misses
- `geocodingService`: Test API response parsing, error handling
- `geocodingCache`: Test LRU eviction, cache key generation
- `MapClickHandler`: Test click event handling, coordinate extraction

### Integration Tests
- Frontend → Nominatim API: Real API calls (rate-limited, max 5 tests)
- Map click → modal open → location added: Full user workflow
- Marker drag → geocode → name update: Drag-and-drop workflow
- Error handling: Network errors, malformed responses

### End-to-End Tests (Manual)
- Create trip with map-clicked locations
- Edit trip, drag markers to new positions
- Test on slow network (3G throttling)
- Test with ad blockers (ensure Nominatim not blocked)

---

## Migration & Rollout Plan

### Phase 1: Frontend-Only (Initial Release)
1. Add `lodash.debounce` to frontend package.json
2. Implement geocoding service (client-side)
3. Add LocationConfirmModal component
4. Add MapClickHandler to TripMap (behind feature flag if needed)
5. Update TripEditPage to support edit mode toggle
6. Deploy to staging for user testing

### Phase 2: Optimization (Future)
1. Add backend proxy endpoint if rate limiting issues
2. Implement server-side cache (Redis) if needed
3. Add geocoding analytics (track success/failure rates)
4. Consider self-hosted Nominatim instance for higher rate limits

### Rollback Plan
- Feature flag: `ENABLE_REVERSE_GEOCODING` in frontend environment
- If issues detected, disable flag to revert to manual coordinate entry
- No database changes, backward compatible

---

## Open Questions (Resolved)

All technical unknowns have been researched and decided. No open questions remain.

---

## Next Steps

Proceed to **Phase 1: Design & Contracts**:
1. Generate `data-model.md` - Define geocoding cache and location entities
2. Generate `contracts/` - API contracts for geocoding (if backend proxy added)
3. Generate `quickstart.md` - Developer guide for implementing reverse geocoding
4. Update `CLAUDE.md` - Add Nominatim API and geocoding patterns

**Phase 0 Complete** ✅
