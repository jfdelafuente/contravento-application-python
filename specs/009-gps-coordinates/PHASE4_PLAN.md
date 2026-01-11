# Phase 4: User Story 2 - Add GPS Coordinates When Creating Trips (Frontend UI)

**Branch**: `009-gps-coordinates-frontend`
**Goal**: Implement frontend UI for entering GPS coordinates during trip creation
**Status**: 🚧 Ready to Start

---

## Overview

Phase 4 implements **User Story 2** - enabling cyclists to add GPS coordinates (latitude/longitude) to trip locations through the trip creation form. This provides the data input interface for the visualization feature (US1).

**Key Features**:
- LocationInput component with coordinate fields
- Real-time validation with visual feedback
- Spanish error messages
- Add/remove multiple locations
- Review step shows coordinates before submission
- Optional coordinates (backwards compatible)

---

## Tasks Breakdown

### Frontend Tests (6 tasks) - TDD Approach

**⚠️ CRITICAL**: Write tests FIRST, ensure they FAIL before implementation

#### Unit Tests - LocationInput Component
- [ ] **T036**: Test LocationInput component rendering
- [ ] **T037**: Test coordinate validation (Zod schema)
- [ ] **T038**: Test onChange handlers

**File**: `frontend/tests/unit/LocationInput.test.tsx` (NEW)

#### Unit Tests - Validators
- [ ] **T039**: Test coordinate validators (Zod schema)

**File**: `frontend/tests/unit/tripValidators.test.ts` (EXTEND)

#### Integration Tests - TripForm
- [ ] **T040**: Test trip creation form with coordinates
- [ ] **T041**: Test form submission with coordinates

**File**: `frontend/tests/integration/TripForm.test.tsx` (EXTEND)

---

### Frontend Implementation (13 tasks)

#### Component Creation
- [ ] **T042**: Run frontend unit tests (verify FAIL)
- [ ] **T043**: Create LocationInput component
- [ ] **T044**: Create LocationInput.css styling
- [ ] **T045**: Update Step1BasicInfo to include location input section
- [ ] **T046**: Add location state management (useState)
- [ ] **T047**: Implement handleLocationChange handler
- [ ] **T048**: Implement handleAddLocation handler
- [ ] **T049**: Implement handleRemoveLocation handler
- [ ] **T050**: Update Step4Review to display coordinates
- [ ] **T051**: Update tripHelpers.ts formDataToApiPayload

#### Testing & Verification
- [ ] **T052**: Run frontend unit tests (verify PASS)
- [ ] **T053**: Run frontend integration tests (verify PASS)
- [ ] **T054**: Verify frontend test coverage ≥90%

---

## Component Design

### LocationInput Component

**File**: `frontend/src/components/trips/TripForm/LocationInput.tsx`

**Props**:
```typescript
interface LocationInputProps {
  location: LocationInputData;
  index: number;
  onChange: (index: number, field: string, value: string | number | null) => void;
  onRemove: (index: number) => void;
  errors?: LocationValidationErrors;
}

interface LocationInputData {
  name: string;
  latitude: number | null;
  longitude: number | null;
}
```

**Features**:
- Text input for location name (required)
- Number input for latitude (-90 to 90, 6 decimals)
- Number input for longitude (-180 to 180, 6 decimals)
- Remove location button
- Real-time validation with visual feedback (red border + error message)
- Spanish error messages
- Coordinates optional (can leave blank)

**Validation Rules**:
```typescript
// Zod schema in tripValidators.ts
const LocationInputSchema = z.object({
  name: z.string().min(1, 'El nombre es obligatorio'),
  latitude: z.number()
    .min(-90, 'Latitud debe estar entre -90 y 90 grados')
    .max(90, 'Latitud debe estar entre -90 y 90 grados')
    .nullable()
    .optional(),
  longitude: z.number()
    .min(-180, 'Longitud debe estar entre -180 y 180 grados')
    .max(180, 'Longitud debe estar entre -180 y 180 grados')
    .nullable()
    .optional(),
});
```

---

### Step1BasicInfo Updates

**File**: `frontend/src/components/trips/TripForm/Step1BasicInfo.tsx`

**New State**:
```typescript
const [locations, setLocations] = useState<LocationInputData[]>([
  { name: '', latitude: null, longitude: null }
]);
```

**New Handlers**:
```typescript
const handleLocationChange = (index: number, field: string, value: any) => {
  const newLocations = [...locations];
  newLocations[index] = { ...newLocations[index], [field]: value };
  setLocations(newLocations);
  onChange('locations', newLocations);
};

const handleAddLocation = () => {
  setLocations([...locations, { name: '', latitude: null, longitude: null }]);
};

const handleRemoveLocation = (index: number) => {
  setLocations(locations.filter((_, i) => i !== index));
};
```

**UI Section** (after Distance/Difficulty):
```tsx
<div className="form-section">
  <h3>Ubicaciones del Viaje</h3>
  <p className="section-hint">
    Añade las ubicaciones de tu ruta. Las coordenadas GPS son opcionales.
  </p>

  {locations.map((location, index) => (
    <LocationInput
      key={index}
      location={location}
      index={index}
      onChange={handleLocationChange}
      onRemove={handleRemoveLocation}
      errors={errors?.locations?.[index]}
    />
  ))}

  <button
    type="button"
    onClick={handleAddLocation}
    className="btn-secondary"
  >
    + Añadir Ubicación
  </button>
</div>
```

---

### Step4Review Updates

**File**: `frontend/src/components/trips/TripForm/Step4Review.tsx`

**New Section** (after Tags):
```tsx
<div className="review-section">
  <h4>Ubicaciones</h4>
  {formData.locations && formData.locations.length > 0 ? (
    <ul className="locations-list">
      {formData.locations.map((location, index) => (
        <li key={index}>
          <strong>{location.name}</strong>
          {location.latitude && location.longitude ? (
            <span className="coordinates">
              ({location.latitude.toFixed(6)}, {location.longitude.toFixed(6)})
            </span>
          ) : (
            <span className="no-coordinates">(Sin coordenadas GPS)</span>
          )}
        </li>
      ))}
    </ul>
  ) : (
    <p className="no-data">No se añadieron ubicaciones</p>
  )}
</div>
```

---

## Styling

### LocationInput.css

**File**: `frontend/src/components/trips/TripForm/LocationInput.css`

**Key Styles**:
```css
.location-input-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: #fafafa;
}

.location-input-container.has-error {
  border-color: #dc3545;
  background: #fff5f5;
}

.coordinates-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.coordinate-field input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.coordinate-field input.error {
  border-color: #dc3545;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 4px;
}

.remove-location-btn {
  background: transparent;
  color: #dc3545;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 4px 8px;
}

.remove-location-btn:hover {
  color: #a71d2a;
  text-decoration: underline;
}
```

---

## Testing Scenarios

### Unit Tests - LocationInput Component

**Test Suite 1: Rendering**
```typescript
describe('LocationInput', () => {
  test('renders all input fields', () => {
    render(<LocationInput location={mockLocation} ... />);
    expect(screen.getByLabelText('Nombre de ubicación')).toBeInTheDocument();
    expect(screen.getByLabelText('Latitud')).toBeInTheDocument();
    expect(screen.getByLabelText('Longitud')).toBeInTheDocument();
  });

  test('displays pre-filled values', () => {
    const location = { name: 'Madrid', latitude: 40.416775, longitude: -3.703790 };
    render(<LocationInput location={location} ... />);
    expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
    expect(screen.getByDisplayValue('40.416775')).toBeInTheDocument();
  });
});
```

**Test Suite 2: Validation**
```typescript
describe('LocationInput - Validation', () => {
  test('shows error for invalid latitude', () => {
    const location = { name: 'Test', latitude: 100, longitude: 0 };
    render(<LocationInput location={location} errors={mockErrors} ... />);
    expect(screen.getByText('Latitud debe estar entre -90 y 90 grados')).toBeInTheDocument();
  });

  test('shows error for invalid longitude', () => {
    const location = { name: 'Test', latitude: 0, longitude: 200 };
    render(<LocationInput location={location} errors={mockErrors} ... />);
    expect(screen.getByText('Longitud debe estar entre -180 y 180 grados')).toBeInTheDocument();
  });
});
```

**Test Suite 3: User Interaction**
```typescript
describe('LocationInput - User Interaction', () => {
  test('calls onChange when name changes', () => {
    const onChange = jest.fn();
    render(<LocationInput onChange={onChange} ... />);

    const nameInput = screen.getByLabelText('Nombre de ubicación');
    fireEvent.change(nameInput, { target: { value: 'Barcelona' } });

    expect(onChange).toHaveBeenCalledWith(0, 'name', 'Barcelona');
  });

  test('calls onRemove when remove button clicked', () => {
    const onRemove = jest.fn();
    render(<LocationInput index={2} onRemove={onRemove} ... />);

    const removeBtn = screen.getByText('Eliminar ubicación');
    fireEvent.click(removeBtn);

    expect(onRemove).toHaveBeenCalledWith(2);
  });
});
```

---

### Integration Tests - TripForm

**Test Suite 4: Trip Creation with GPS**
```typescript
describe('TripForm - GPS Coordinates', () => {
  test('creates trip with GPS coordinates', async () => {
    render(<TripFormWizard />);

    // Step 1: Fill basic info
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Ruta Test GPS' } });
    fireEvent.change(screen.getByLabelText('Distancia (km)'), { target: { value: '50' } });

    // Add location with coordinates
    fireEvent.change(screen.getByLabelText('Nombre de ubicación'), { target: { value: 'Madrid' } });
    fireEvent.change(screen.getByLabelText('Latitud'), { target: { value: '40.416775' } });
    fireEvent.change(screen.getByLabelText('Longitud'), { target: { value: '-3.703790' } });

    // Submit form
    fireEvent.click(screen.getByText('Siguiente'));
    fireEvent.click(screen.getByText('Siguiente'));
    fireEvent.click(screen.getByText('Publicar Viaje'));

    // Verify API call
    await waitFor(() => {
      expect(mockTripService.createTrip).toHaveBeenCalledWith({
        locations: [{ name: 'Madrid', latitude: 40.416775, longitude: -3.703790 }],
        ...
      });
    });
  });

  test('creates trip without GPS coordinates (backwards compatible)', async () => {
    // Same test but leave latitude/longitude empty
    // Verify API call includes location with null coordinates
  });
});
```

---

## Manual Testing Checklist

Once implementation is complete, verify:

### Happy Path
- [ ] Navigate to `/trips/create`
- [ ] Fill trip details (title, dates, distance, difficulty)
- [ ] Click "Añadir Ubicación"
- [ ] Enter location name: "Jaca"
- [ ] Enter latitude: `42.570084`
- [ ] Enter longitude: `-0.549941`
- [ ] Add second location: "Somport" (lat: `42.791667`, lng: `-0.526944`)
- [ ] Proceed to Step 4 (Review)
- [ ] Verify coordinates displayed correctly
- [ ] Submit form
- [ ] Verify trip created in backend
- [ ] View trip detail page
- [ ] Verify map displays with 2 markers and route line

### Validation Tests
- [ ] Enter invalid latitude `100` → Error: "Latitud debe estar entre -90 y 90 grados"
- [ ] Enter invalid longitude `200` → Error: "Longitud debe estar entre -180 y 180 grados"
- [ ] Enter empty location name → Error: "El nombre es obligatorio"
- [ ] Enter coordinates with >6 decimals → Verify rounded to 6

### Backwards Compatibility
- [ ] Create trip with location name only (no coordinates)
- [ ] Verify trip saved successfully
- [ ] View trip detail page → No map shown
- [ ] Mixed locations: Some with GPS, some without
- [ ] Verify only locations with GPS show on map

### Edge Cases
- [ ] Add 5 locations, remove 3rd location → Verify indices update correctly
- [ ] Enter latitude `0`, longitude `0` (valid) → No error
- [ ] Enter latitude `-90`, longitude `180` (valid edge) → No error
- [ ] Enter decimal separator `,` instead of `.` → Verify handling

---

## Dependencies

### Frontend Dependencies (Need Installation)

```bash
cd frontend

# Testing libraries
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest

# Leaflet types (if not already installed)
npm install --save-dev @types/leaflet
```

---

## Success Criteria

### Functionality
- ✅ Users can add GPS coordinates during trip creation
- ✅ Coordinates are optional (backwards compatible)
- ✅ Real-time validation with Spanish error messages
- ✅ Add/remove multiple locations
- ✅ Review step shows coordinates before submission
- ✅ Map displays on trip detail page after creation

### Code Quality
- ✅ Frontend test coverage ≥90%
- ✅ All ESLint/TypeScript checks pass
- ✅ Component follows React best practices (hooks, separation of concerns)
- ✅ CSS follows BEM naming convention
- ✅ Accessible (keyboard navigation, ARIA labels)

### Performance
- ✅ Form validation is instant (<50ms)
- ✅ No unnecessary re-renders (React.memo where needed)
- ✅ Coordinate precision calculated client-side (no backend calls for validation)

---

## Checkpoints

### Checkpoint 1: Tests Written (Red Phase)
- ✅ 6 frontend tests created (unit + integration)
- ✅ All tests FAIL (component not yet implemented)

### Checkpoint 2: Component Implemented (Green Phase)
- ✅ LocationInput component created
- ✅ Step1BasicInfo updated with location management
- ✅ Step4Review updated to show coordinates
- ✅ All tests PASS

### Checkpoint 3: Manual Testing Complete
- ✅ All manual test scenarios verified
- ✅ Edge cases handled correctly
- ✅ Backwards compatibility confirmed

### Checkpoint 4: Ready for Merge
- ✅ Code reviewed (self or peer)
- ✅ Test coverage ≥90%
- ✅ No linter warnings
- ✅ Documentation updated

---

## Commands

### Development

```bash
cd frontend

# Start development server
npm run dev

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test LocationInput.test.tsx

# Run tests with coverage
npm test -- --coverage

# Lint code
npm run lint

# Type check
npm run type-check
```

### Testing

```bash
# Run all tests
npm test

# Run unit tests only
npm test -- --testPathPattern=unit

# Run integration tests only
npm test -- --testPathPattern=integration

# Generate coverage report
npm test -- --coverage --coverageReporters=html
open coverage/index.html
```

---

## Next Steps After Phase 4

Once Phase 4 is complete:

1. **Commit and push** frontend changes to `009-gps-coordinates-frontend` branch
2. **Run manual tests** following checklist above
3. **Create PR** to merge into `develop`
4. **Move to Phase 5**: User Story 3 - Edit GPS Coordinates for Existing Trips

---

## Related Files

**Specification**:
- [spec.md](spec.md) - Feature specification
- [plan.md](plan.md) - Implementation plan
- [tasks.md](tasks.md) - Detailed task breakdown

**Testing**:
- [TESTING.md](../../TESTING.md) - Root testing guide
- [scripts/testing/gps/README.md](../../scripts/testing/gps/README.md) - GPS testing scripts

**Implementation**:
- Phase 1-2: Backend validation (merged to develop)
- Phase 3: TDD tests (branch: 009-gps-coordinates-tests)
- **Phase 4: Frontend UI (this document)** (branch: 009-gps-coordinates-frontend)

---

**Created**: 2026-01-11
**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
