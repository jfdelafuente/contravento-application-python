# Plan: GPX Wizard Integration

**Feature**: Post-creation modal for GPX upload after trip creation
**Status**: Ready for implementation
**Priority**: High (UX Enhancement)
**Estimated Effort**: 0.5-1 day (4-8 hours)

---

## Overview

Implement a post-creation modal that prompts users to upload a GPX file immediately after creating a trip, improving discoverability without extending the existing 4-step wizard.

### Key Design Decision: Post-Creation Modal

**Chosen Approach**: Show modal after trip creation (Alternativa A from analysis)

**Rationale**:
1. ✅ **Minimal risk**: No changes to existing wizard flow
2. ✅ **Quick implementation**: 2-3 hours (vs 6-8h for new wizard step)
3. ✅ **Optional but visible**: High discoverability, zero friction to skip
4. ✅ **Consistent architecture**: Maintains separation (trip creation vs file uploads)
5. ✅ **Easy to test**: Independent component, isolated changes

**Trade-offs accepted**:
- ⚠️ Modal may feel slightly intrusive (mitigated by easy skip)
- ⚠️ Adds one extra interaction (open modal → click button)

---

## Architecture

### Component Hierarchy

```
TripCreatePage / TripFormWizard
  ├─ Step1BasicInfo
  ├─ Step2StoryTags
  ├─ Step3Photos
  ├─ Step4Review
  └─ PostCreationGPXModal ← NEW
       ├─ Initial State: Prompt UI (buttons)
       └─ Upload State: GPXUploader (reused)
```

### State Flow Diagram

```
User completes wizard
        ↓
handleSubmit() in useTripForm
        ↓
1. createTrip() → trip created
2. uploadPhotos() → photos uploaded
3. publishTrip() (if not draft)
4. setShowGPXModal(true) ← NEW (instead of navigate)
5. setCreatedTripId(trip.trip_id)
        ↓
PostCreationGPXModal renders
        ↓
        ├─ User clicks "Sí, subir ahora"
        │    ↓
        │  GPXUploader shown in modal
        │    ↓
        │  Upload succeeds → onClose() → navigate
        │
        ├─ User clicks "No, lo haré después"
        │    ↓
        │  onClose() → navigate
        │
        └─ User presses ESC / clicks overlay
             ↓
           onClose() → navigate
```

### Data Flow

```typescript
// 1. Trip creation (existing)
const trip = await createTrip(data);         // Backend: POST /trips
const tripId = trip.trip_id;                 // UUID returned

// 2. Photos upload (existing)
for (const photo of photos) {
  await uploadTripPhoto(tripId, photo);      // Backend: POST /trips/{id}/photos
}

// 3. Publish (existing)
if (!isDraft) {
  await publishTrip(tripId);                 // Backend: POST /trips/{id}/publish
}

// 4. Show GPX modal (NEW)
setShowGPXModal(true);
setCreatedTripId(tripId);

// 5. GPX upload (in modal, uses existing endpoint)
await uploadGPX(tripId, file);               // Backend: POST /trips/{id}/gpx

// 6. Navigate to detail page
navigate(`/trips/${tripId}`);
```

---

## Implementation Plan

### Phase 1: Create Modal Component (1-2 hours)

**File**: `frontend/src/components/trips/PostCreationGPXModal.tsx`

**Component Structure**:

```typescript
interface PostCreationGPXModalProps {
  tripId: string;
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

export const PostCreationGPXModal: React.FC<PostCreationGPXModalProps> = ({
  tripId,
  isOpen,
  onClose,
  onComplete,
}) => {
  const [uploadStarted, setUploadStarted] = useState(false);

  // Close modal on ESC key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Focus trap
  useEffect(() => {
    if (isOpen) {
      const modal = document.getElementById('gpx-modal');
      modal?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="presentation"
    >
      <div
        id="gpx-modal"
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="gpx-modal-title"
        tabIndex={-1}
      >
        {!uploadStarted ? (
          // Initial prompt state
          <>
            <h2 id="gpx-modal-title">¿Agregar ruta GPX?</h2>
            <p>
              Puedes subir un archivo GPX con la ruta de tu viaje para visualizarla
              en el mapa y obtener estadísticas de elevación.
            </p>

            <div className="modal-actions">
              <button
                onClick={() => setUploadStarted(true)}
                className="button-primary"
                aria-label="Subir archivo GPX ahora"
              >
                Sí, subir ahora
              </button>

              <button
                onClick={onClose}
                className="button-secondary"
                aria-label="Omitir subida de GPX y continuar"
              >
                No, lo haré después
              </button>
            </div>
          </>
        ) : (
          // Upload state
          <>
            <h2>Subir archivo GPX</h2>

            <GPXUploader
              tripId={tripId}
              onUploadComplete={() => {
                onComplete();
                onClose();
              }}
            />

            <button
              onClick={() => setUploadStarted(false)}
              className="button-text"
            >
              ← Volver
            </button>
          </>
        )}

        <button
          onClick={onClose}
          className="modal-close"
          aria-label="Cerrar modal"
        >
          ✕
        </button>
      </div>
    </div>
  );
};
```

**CSS** (create `frontend/src/components/trips/PostCreationGPXModal.css`):

```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease-out;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  animation: slideUp 0.2s ease-out;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions button {
  flex: 1;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 44px; /* Touch target */
}

.button-primary {
  background: #8b5cf6;
  color: white;
  border: none;
}

.button-primary:hover {
  background: #7c3aed;
}

.button-secondary {
  background: white;
  color: #666;
  border: 2px solid #e0e0e0;
}

.button-secondary:hover {
  border-color: #bbb;
  background: #f9f9f9;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .modal-content {
    width: 95vw;
    padding: 1.5rem;
    border-radius: 16px 16px 0 0;
    align-self: flex-end;
    max-height: 90vh;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-actions button {
    width: 100%;
  }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

### Phase 2: Modify Trip Form Hook (1 hour)

**File**: `frontend/src/hooks/useTripForm.ts`

**Changes**:

```typescript
export const useTripForm = ({ tripId, isEditMode }: Options) => {
  const navigate = useNavigate();

  // Existing state
  const [isSubmitting, setIsSubmitting] = useState(false);

  // NEW: GPX modal state
  const [showGPXModal, setShowGPXModal] = useState(false);
  const [createdTripId, setCreatedTripId] = useState<string | null>(null);

  const methods = useForm<TripCreateInput>({
    resolver: zodResolver(tripFormSchema),
  });

  const handleSubmit = async (
    data: TripCreateInput,
    isDraft: boolean,
    photos: PhotoFile[]
  ) => {
    setIsSubmitting(true);

    try {
      // 1. Create trip
      const trip = isEditMode && tripId
        ? await updateTrip(tripId, data)
        : await createTrip(data);

      // 2. Upload photos
      for (const photo of photos) {
        await uploadTripPhoto(trip.trip_id, photo.file);
      }

      // 3. Publish if needed
      if (!isDraft && !isEditMode) {
        await publishTrip(trip.trip_id);
      }

      toast.success(
        isEditMode ? 'Viaje actualizado correctamente' : 'Viaje creado correctamente'
      );

      // 4. Show GPX modal INSTEAD of immediate navigation (NEW)
      if (!isEditMode) {
        setCreatedTripId(trip.trip_id);
        setShowGPXModal(true);
      } else {
        // Editing: navigate directly (no modal)
        navigate(`/trips/${trip.trip_id}`);
      }
    } catch (error: any) {
      // Error handling
      if (error.response?.status === 409) {
        toast.error('El viaje fue modificado por otra sesión...');
      } else {
        toast.error(
          error.response?.data?.error?.message || 'Error al procesar el viaje'
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // NEW: Handle modal close
  const handleGPXModalClose = () => {
    setShowGPXModal(false);
    if (createdTripId) {
      navigate(`/trips/${createdTripId}`);
    }
  };

  // NEW: Handle upload completion
  const handleGPXUploadComplete = () => {
    toast.success('Archivo GPX procesado correctamente');
    // Modal will close via onClose callback
  };

  return {
    methods,
    handleSubmit,
    isSubmitting,
    // NEW: Modal state
    showGPXModal,
    createdTripId,
    handleGPXModalClose,
    handleGPXUploadComplete,
  };
};
```

---

### Phase 3: Integrate Modal into Wizard (30 minutes)

**File**: `frontend/src/pages/TripCreatePage.tsx` or wherever TripFormWizard is used

**Changes**:

```typescript
import { PostCreationGPXModal } from '../components/trips/PostCreationGPXModal';

export const TripCreatePage: React.FC = () => {
  const {
    methods,
    handleSubmit,
    isSubmitting,
    showGPXModal,        // NEW
    createdTripId,       // NEW
    handleGPXModalClose, // NEW
    handleGPXUploadComplete, // NEW
  } = useTripForm({ isEditMode: false });

  return (
    <div className="trip-create-page">
      <TripFormWizard
        methods={methods}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
      />

      {/* NEW: GPX Modal */}
      {createdTripId && (
        <PostCreationGPXModal
          tripId={createdTripId}
          isOpen={showGPXModal}
          onClose={handleGPXModalClose}
          onComplete={handleGPXUploadComplete}
        />
      )}
    </div>
  );
};
```

---

### Phase 4: TypeScript Types (15 minutes)

**File**: `frontend/src/types/trip.ts` (if needed)

```typescript
export interface PostCreationGPXModalProps {
  /** ID of the just-created trip */
  tripId: string;

  /** Controls modal visibility */
  isOpen: boolean;

  /** Callback when modal closes (skip or after upload) */
  onClose: () => void;

  /** Callback when GPX upload completes successfully */
  onComplete: () => void;
}
```

---

### Phase 5: Testing (1-2 hours)

#### Unit Tests

**File**: `frontend/tests/unit/PostCreationGPXModal.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { PostCreationGPXModal } from '@/components/trips/PostCreationGPXModal';

describe('PostCreationGPXModal', () => {
  const mockOnClose = jest.fn();
  const mockOnComplete = jest.fn();
  const mockTripId = 'trip-123';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders nothing when isOpen is false', () => {
    const { container } = render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={false}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    expect(container).toBeEmptyDOMElement();
  });

  it('renders prompt state initially', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('¿Agregar ruta GPX?')).toBeInTheDocument();
    expect(screen.getByText('Sí, subir ahora')).toBeInTheDocument();
    expect(screen.getByText('No, lo haré después')).toBeInTheDocument();
  });

  it('shows GPXUploader when "Sí, subir ahora" clicked', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    fireEvent.click(screen.getByText('Sí, subir ahora'));

    // GPXUploader should be visible (check for its distinctive elements)
    expect(screen.getByText('Subir archivo GPX')).toBeInTheDocument();
  });

  it('calls onClose when "No, lo haré después" clicked', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    fireEvent.click(screen.getByText('No, lo haré después'));

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay clicked', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    const overlay = screen.getByRole('presentation');
    fireEvent.click(overlay);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when ESC key pressed', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    fireEvent.keyDown(window, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('does not close when modal content clicked', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    const modalContent = screen.getByRole('dialog');
    fireEvent.click(modalContent);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('has correct ARIA attributes', () => {
    render(
      <PostCreationGPXModal
        tripId={mockTripId}
        isOpen={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
      />
    );

    const dialog = screen.getByRole('dialog');

    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'gpx-modal-title');
  });
});
```

#### Manual Test Cases

**Test Case 1: Successful GPX Upload via Modal**
```
1. Navigate to /trips/create
2. Complete 4-step wizard
3. Click "Guardar Borrador" or "Publicar"
4. ✅ Verify modal appears with "¿Agregar ruta GPX?"
5. Click "Sí, subir ahora"
6. ✅ Verify GPXUploader appears in modal
7. Drag-drop valid GPX file (e.g., short_route.gpx)
8. ✅ Verify upload progress shown
9. ✅ Verify success toast: "Archivo GPX procesado correctamente"
10. ✅ Verify modal closes automatically
11. ✅ Verify navigated to /trips/{trip_id}
12. ✅ Verify GPX data visible on TripDetailPage
```

**Test Case 2: Skip GPX Upload**
```
1. Navigate to /trips/create
2. Complete 4-step wizard
3. Click "Publicar"
4. ✅ Verify modal appears
5. Click "No, lo haré después"
6. ✅ Verify modal closes immediately
7. ✅ Verify navigated to /trips/{trip_id}
8. ✅ Verify GPXUploader still available on detail page
9. ✅ Verify trip created successfully (without GPX)
```

**Test Case 3: GPX Upload Error Handling**
```
1. Navigate to /trips/create
2. Complete wizard → modal appears
3. Click "Sí, subir ahora"
4. Upload invalid file (e.g., 15MB file, exceeds 10MB limit)
5. ✅ Verify error toast with Spanish message
6. ✅ Verify modal stays open (allows retry)
7. Click "No, lo haré después"
8. ✅ Verify navigated to detail page
9. ✅ Verify trip exists (not deleted)
10. ✅ Verify can upload GPX from detail page
```

**Test Case 4: ESC Key and Overlay Click**
```
1. Complete wizard → modal appears
2. Press ESC key
3. ✅ Verify modal closes
4. ✅ Verify navigated to detail page

5. Create another trip → modal appears
6. Click overlay background (outside modal content)
7. ✅ Verify modal closes
8. ✅ Verify navigated to detail page
```

**Test Case 5: Mobile Responsiveness**
```
1. Open browser DevTools
2. Switch to mobile viewport (375px width)
3. Complete wizard → modal appears
4. ✅ Verify modal bottom-aligned
5. ✅ Verify buttons full-width and stacked
6. ✅ Verify touch targets ≥44px
7. Click "Sí, subir ahora"
8. ✅ Verify GPXUploader usable on mobile
```

---

### Phase 6: Documentation (30 minutes)

**Update CLAUDE.md**:

Add section to "Travel Diary Frontend (Feature 008)":

```markdown
### Post-Creation GPX Upload Modal (Feature 015)

The GPX upload modal appears automatically after trip creation to improve discoverability.

**Pattern: Post-Creation Action Modal**

```typescript
// useTripForm.ts - Show modal instead of immediate navigation
const handleSubmit = async (data, isDraft, photos) => {
  const trip = await createTrip(data);
  await uploadPhotos(trip.trip_id, photos);

  // NEW: Show modal instead of navigate
  setCreatedTripId(trip.trip_id);
  setShowGPXModal(true);
};

const handleGPXModalClose = () => {
  setShowGPXModal(false);
  navigate(`/trips/${createdTripId}`);
};
```

**Modal state flow**:
1. User completes wizard → trip created
2. Modal appears with two options
3. User uploads GPX → modal closes → navigate
4. User skips GPX → modal closes → navigate

**Component reuse**: Uses existing GPXUploader component without modifications.
```

---

## Backend Changes

**Required**: ✅ **NONE**

This feature is frontend-only. It uses existing backend endpoints:
- `POST /trips` - Create trip
- `POST /trips/{trip_id}/photos` - Upload photos
- `POST /trips/{trip_id}/publish` - Publish trip
- `POST /trips/{trip_id}/gpx` - Upload GPX (existing)

---

## Deployment Strategy

### Local Development
```bash
# Frontend dev server with hot reload
cd frontend
npm run dev

# Test trip creation flow:
# 1. Navigate to http://localhost:5173/trips/create
# 2. Complete wizard
# 3. Verify modal appears
```

### Staging
```bash
# Build frontend with staging config
npm run build:staging

# Deploy to staging environment
./deploy.sh staging
```

### Production
```bash
# Build frontend with production config
npm run build:prod

# Deploy to production
./deploy.sh prod
```

**Rollback plan**: If modal causes issues, can be disabled via feature flag without reverting deployment.

---

## Verification Checklist

Before merging to develop:

- [ ] PostCreationGPXModal component renders correctly
- [ ] Modal appears after trip creation (not during wizard)
- [ ] "Sí, subir ahora" shows GPXUploader
- [ ] "No, lo haré después" closes and navigates
- [ ] ESC key closes modal
- [ ] Overlay click closes modal
- [ ] GPX upload success closes modal and navigates
- [ ] GPX upload error keeps modal open
- [ ] Trip is created successfully regardless of GPX outcome
- [ ] TypeScript: Zero errors
- [ ] Unit tests: ≥90% coverage
- [ ] Manual tests: All 5 test cases pass
- [ ] Mobile: Works on 375px viewport
- [ ] Accessibility: ARIA attributes correct, keyboard navigation works
- [ ] Code review: Approved by reviewer
- [ ] Documentation: CLAUDE.md updated

---

## Timeline

**Estimated effort**: 0.5-1 day (4-8 hours)

**Breakdown**:
- Phase 1: Modal component (1-2h)
- Phase 2: Hook modification (1h)
- Phase 3: Integration (0.5h)
- Phase 4: Types (0.25h)
- Phase 5: Testing (1-2h)
- Phase 6: Documentation (0.5h)

**Total**: 4.25-6.25 hours (round up to 1 day with buffer)

---

## Success Metrics

**Implementation Success**:
- ✅ All acceptance criteria met (4 user stories)
- ✅ All verification checklist items complete
- ✅ Code review approved
- ✅ Merged to develop without issues

**User Impact (measure after 1 week)**:
- Target: ≥30% of trips created with GPX via modal
- Target: ≥80% completion rate (users who start upload complete it)
- Target: <5% error rate on modal uploads
- Target: Positive user feedback (qualitative)
