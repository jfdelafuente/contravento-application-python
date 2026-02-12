# Research: GPS Coordinates for Trip Locations

**Feature**: 009-gps-coordinates
**Date**: 2026-01-11
**Purpose**: Technology decisions and best practices for coordinate validation, input UX, and backwards compatibility

## Research Questions

This research addresses technical unknowns identified in the Technical Context section of the implementation plan.

### 1. Coordinate Validation Patterns

**Question**: Should we use Pydantic validators or custom validation functions for coordinate range validation?

**Research Findings**:

**Option A: Pydantic Field Validators** (RECOMMENDED)
- Use `Field()` with `ge` (greater or equal) and `le` (less or equal) constraints
- Built-in error messages in English (can customize with `description`)
- Example:
  ```python
  from pydantic import BaseModel, Field

  class LocationInput(BaseModel):
      name: str = Field(..., min_length=1, max_length=200)
      latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitud en grados decimales")
      longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitud en grados decimales")
  ```

**Option B: Custom `@field_validator`**
- More control over error messages (Spanish language support)
- Can validate decimal precision (6 decimal places)
- Example:
  ```python
  from pydantic import BaseModel, field_validator

  @field_validator('latitude')
  @classmethod
  def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
      if v is None:
          return v
      if not -90 <= v <= 90:
          raise ValueError('Latitud debe estar entre -90 y 90 grados')
      return round(v, 6)  # Enforce 6 decimal precision
  ```

**Decision**: **Hybrid Approach**
- Use Pydantic `Field()` constraints for basic range validation (fast, declarative)
- Add custom `@field_validator` for decimal precision enforcement and Spanish error messages
- Rationale: Combines performance of built-in validation with UX requirement for Spanish messages

**Alternatives Considered**:
- Pure custom validators: More code, slower performance
- No validation (rely on database constraints): Poor UX, no field-specific error messages

---

### 2. Frontend Coordinate Input UX

**Question**: How should users input GPS coordinates in the trip creation/edit forms?

**Research Findings**:

**Option A: Separate Numeric Input Fields** (RECOMMENDED per spec clarification)
- Two separate `<input type="number">` fields (Latitude, Longitude)
- Labels: "Latitud (opcional)" and "Longitud (opcional)"
- `step="0.000001"` for 6 decimal precision
- Placeholder examples: "40.416775" (Madrid latitude), "-3.703790" (Madrid longitude)
- Client-side validation: `min="-90" max="90"` (latitude), `min="-180" max="180"` (longitude)
- Visual feedback: Green checkmark for valid, red error message for invalid
- Example:
  ```tsx
  <div className="coordinate-inputs">
    <label>
      Latitud (opcional)
      <input
        type="number"
        step="0.000001"
        min="-90"
        max="90"
        placeholder="40.416775"
      />
    </label>
    <label>
      Longitud (opcional)
      <input
        type="number"
        step="0.000001"
        min="-180"
        max="180"
        placeholder="-3.703790"
      />
    </label>
  </div>
  ```

**Option B: Combined Text Input with Parsing**
- Single text input: "40.416775, -3.703790"
- Parse comma-separated values
- More compact UI but requires parsing logic and validation

**Option C: Map Picker**
- Interactive map where user clicks to select coordinates
- Best UX but requires additional library (leaflet click handlers)
- Out of scope for Phase 1 (manual entry only per spec)

**Decision**: **Option A - Separate Numeric Fields**
- Matches spec clarification Q1: "Separate numeric input fields - one for latitude, one for longitude"
- Clear validation boundaries (browser enforces numeric input)
- No parsing ambiguity (e.g., "40.5, -3.7" vs "40,5 -3,7")
- Accessible (screen readers can distinguish fields)

**Alternatives Considered**:
- Combined input: Requires custom parsing, error-prone with localization (comma vs period decimals)
- Map picker: Better UX but adds complexity, deferred to future phase

---

### 3. Map Error Handling Strategies

**Question**: How should the system handle map loading failures or timeouts (FR-015)?

**Research Findings**:

**Option A: Error State with Retry Button + Fallback** (RECOMMENDED per spec clarification)
- Display error message: "No se pudo cargar el mapa. Verifica tu conexión a internet."
- Retry button: "Reintentar"
- Fallback: Show location list in text format below error message
- Example:
  ```tsx
  {mapLoadError && (
    <div className="trip-map__error">
      <p className="trip-map__error-message">
        No se pudo cargar el mapa. Verifica tu conexión a internet.
      </p>
      <button onClick={retryMapLoad} className="trip-map__retry-button">
        Reintentar
      </button>
      <div className="trip-map__fallback">
        <h4>Ubicaciones del viaje:</h4>
        <ul>
          {locations.map((loc, i) => (
            <li key={loc.location_id}>
              {i + 1}. {loc.name}
              {loc.latitude && loc.longitude && (
                <span> ({loc.latitude}, {loc.longitude})</span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )}
  ```

**Option B: Silent Failure with Empty State**
- Don't show error, just hide map
- Poor UX: user doesn't know if map is loading or broken

**Option C: Toast Notification Only**
- Show temporary error toast
- User can't retry, no fallback

**Decision**: **Option A - Error State with Retry + Fallback**
- Matches spec clarification Q3 and FR-015
- Graceful degradation (location data still accessible in text format)
- User can retry without refreshing entire page
- Clear feedback (not silent failure)

**Alternatives Considered**:
- Silent failure: Poor UX, user confusion
- Toast only: No retry mechanism, data inaccessible

---

### 4. Backwards Compatibility Approach

**Question**: How do we ensure existing trips without GPS coordinates continue to work normally?

**Research Findings**:

**Option A: Nullable Coordinates with Graceful Degradation** (RECOMMENDED)
- Backend: `latitude: Optional[float]` and `longitude: Optional[float]` in schema
- Database: Columns already nullable (`latitude Float NULL`, `longitude Float NULL`)
- Frontend: Filter out locations with `null` coordinates before map rendering
  ```typescript
  const validLocations = locations.filter(
    loc => loc.latitude !== null && loc.longitude !== null
  );
  if (validLocations.length === 0) {
    return <EmptyState message="No hay coordenadas GPS para mostrar el mapa" />;
  }
  ```
- TripMap component already implements this pattern (line 43-45)

**Option B: Default Coordinates (e.g., 0, 0)**
- Use (0, 0) as sentinel value for "no coordinates"
- Bad UX: Would show locations in Atlantic Ocean off Africa coast

**Option C: Separate "has_coordinates" Boolean Flag**
- Add extra column to track coordinate presence
- Redundant (can check `latitude IS NOT NULL`)

**Decision**: **Option A - Nullable Coordinates**
- Already implemented in existing code (TripMap component)
- No migration needed (columns already nullable)
- Backward compatible: Existing trips have `NULL` coordinates, continue to work without maps
- Forward compatible: New trips can have coordinates, maps display automatically
- Clean semantics: `null` means "no data", not "invalid data"

**Alternatives Considered**:
- Default coordinates: Misleading map display
- Boolean flag: Unnecessary complexity, redundant with NULL check

---

## Technology Stack Confirmation

### Backend
- **Validation**: Pydantic `Field()` + custom `@field_validator` for Spanish error messages
- **Storage**: Existing SQLAlchemy TripLocation model (no changes needed)
- **Testing**: pytest with parametrized tests for coordinate edge cases

### Frontend
- **Input**: Two separate `<input type="number">` fields with `step="0.000001"`
- **Validation**: Zod schema with custom refinements for coordinate ranges
- **Error Handling**: React error boundary + retry mechanism for map failures
- **Map Display**: Existing TripMap component (no changes needed)
- **Testing**: Vitest + React Testing Library for coordinate input component

---

## Performance Considerations

### Validation Performance
- Pydantic `Field()` validation: <0.1ms per coordinate (native Python float comparison)
- Custom validator for decimal precision: ~0.05ms (single `round()` call)
- **Total overhead per location**: <0.2ms (negligible for 50 max locations = 10ms total)

### Frontend Rendering
- Coordinate input: Controlled components with `onChange` debouncing (300ms)
- Map rendering: Lazy-loaded component (already optimized, no changes)
- Validation: Client-side numeric validation (instant feedback, no network calls)

### Database
- No new indexes needed (coordinates not queried for filtering/sorting)
- No migrations needed (columns already exist)
- Query performance: Same as current (coordinates loaded via existing relationship)

---

## Security Considerations

### Input Validation
- Server-side validation REQUIRED (never trust client)
- Numeric type coercion in Pydantic (rejects strings like "40.5; DROP TABLE trips;")
- Range validation prevents out-of-bounds values (no negative latitudes >90)

### Data Sensitivity
- GPS coordinates are public trip data (not personal location tracking)
- Published trips already public, coordinates don't increase sensitivity
- Draft trips restricted to owner (existing authorization logic applies)

---

## Best Practices Applied

1. **Validation**: Defense in depth (client-side + server-side validation)
2. **UX**: Progressive enhancement (maps optional, trips work without coordinates)
3. **Accessibility**: Semantic HTML (`<label>` for inputs, ARIA attributes for error messages)
4. **i18n**: All user-facing text in Spanish (error messages, labels, placeholders)
5. **Testing**: TDD workflow (write validation tests before implementation)
6. **Performance**: Minimize overhead (in-memory validation, no extra queries)
7. **Security**: Server-side validation, numeric type safety, no injection risks

---

## References

- [Pydantic Field Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [HTML5 Number Input](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/number)
- [WGS84 Coordinate System](https://en.wikipedia.org/wiki/World_Geodetic_System)
- [Leaflet.js Error Handling](https://leafletjs.com/reference.html#map-event)
- ContraVento Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Phase 0 Status**: ✅ COMPLETE

All technology decisions finalized. Ready to proceed to Phase 1 (Design & Contracts).
