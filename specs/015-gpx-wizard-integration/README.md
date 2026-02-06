# Feature 015: GPX Wizard Integration

**Quick Start Guide for Developers**

---

## 🎯 What is this feature?

A post-creation modal that appears immediately after creating a trip, prompting users to upload a GPX file without navigating away. Improves discoverability of GPX upload functionality.

## 📊 Current vs Proposed Flow

### Current Flow (2 steps, fragmented)
```
1. User completes 4-step wizard → Trip created
2. Navigate to TripDetailPage → Find GPXUploader → Upload GPX
```

### New Flow (integrated)
```
1. User completes 4-step wizard → Trip created
2. Modal appears: "¿Agregar ruta GPX?"
   - Option A: "Sí, subir ahora" → Upload in modal → Navigate to detail page
   - Option B: "No, lo haré después" → Navigate to detail page
```

---

## 🚀 Quick Implementation Overview

### Frontend Changes (3 new files + 2 modifications)

**New Files**:
1. `frontend/src/components/trips/PostCreationGPXModal.tsx` - Modal component
2. `frontend/src/components/trips/PostCreationGPXModal.css` - Styling
3. `frontend/tests/unit/PostCreationGPXModal.test.tsx` - Unit tests

**Modified Files**:
1. `frontend/src/hooks/useTripForm.ts` - Add modal state, show modal instead of direct navigation
2. `frontend/src/pages/TripCreatePage.tsx` - Render modal after wizard

**Backend Changes**: ✅ **NONE** (reuses existing endpoints)

---

## 📐 Architecture

### Component Structure
```
TripCreatePage
  └─ TripFormWizard (existing)
  └─ PostCreationGPXModal (new)
       ├─ Prompt State: "¿Agregar ruta GPX?" + buttons
       └─ Upload State: <GPXUploader /> (reused, no changes)
```

### State Flow
```typescript
// useTripForm.ts
const [showGPXModal, setShowGPXModal] = useState(false);
const [createdTripId, setCreatedTripId] = useState<string | null>(null);

// After successful trip creation
setCreatedTripId(trip.trip_id);
setShowGPXModal(true);  // Shows modal instead of navigate()

// Modal close handler
const handleGPXModalClose = () => {
  setShowGPXModal(false);
  navigate(`/trips/${createdTripId}`);
};
```

---

## ✅ Key Features

1. **Non-intrusive**: Easy 1-click skip ("No, lo haré después")
2. **Component Reuse**: Uses existing `GPXUploader` (zero modifications)
3. **Accessibility**: Full ARIA support, keyboard navigation, screen reader compatible
4. **Mobile-Optimized**: Bottom-aligned modal, touch-friendly buttons (≥44px)
5. **Error Handling**: Upload errors don't block trip creation
6. **No Backend Changes**: Uses existing `POST /trips/{trip_id}/gpx` endpoint

---

## 🧪 Testing Strategy

### Unit Tests (8 tests)
```bash
npm test PostCreationGPXModal.test.tsx
```

**Coverage**:
- Modal visibility (isOpen true/false)
- Button click handlers
- ESC key handler
- Overlay click handler
- ARIA attributes

### Manual Tests (6 scenarios)
1. Successful GPX upload via modal
2. Skip GPX upload
3. GPX upload error handling
4. ESC key and overlay click
5. Mobile responsiveness (375px viewport)
6. Edit mode (modal should NOT appear)

---

## 📚 Documentation

- **Specification**: [spec.md](./spec.md) - User stories, requirements, success criteria
- **Implementation Plan**: [plan.md](./plan.md) - Technical design, component structure
- **Tasks**: [tasks.md](./tasks.md) - Step-by-step implementation tasks (50 tasks)
- **Analysis**: [../003-gps-routes/GPX_WIZARD_INTEGRATION_ANALYSIS.md](../003-gps-routes/GPX_WIZARD_INTEGRATION_ANALYSIS.md) - Alternative approaches considered

---

## ⏱️ Estimated Effort

**Total**: 0.5-1 day (4-8 hours)

**Breakdown**:
- Component development: 3 hours
- State management: 1 hour
- Integration: 30 min
- Testing: 1.5 hours
- Documentation: 30 min
- PR & review: 30 min

---

## 🎨 UI Preview (Conceptual)

### Prompt State
```
┌────────────────────────────────────┐
│  ¿Agregar ruta GPX?              X │
│                                    │
│  Puedes subir un archivo GPX con   │
│  la ruta de tu viaje para          │
│  visualizarla en el mapa y obtener │
│  estadísticas de elevación.        │
│                                    │
│  ┌─────────────────────────────┐  │
│  │  Sí, subir ahora            │  │
│  └─────────────────────────────┘  │
│                                    │
│  ┌─────────────────────────────┐  │
│  │  No, lo haré después        │  │
│  └─────────────────────────────┘  │
└────────────────────────────────────┘
```

### Upload State
```
┌────────────────────────────────────┐
│  Subir archivo GPX               X │
│                                    │
│  ┌────────────────────────────┐   │
│  │                            │   │
│  │   [GPXUploader Component]  │   │
│  │   (drag-drop area)         │   │
│  │                            │   │
│  └────────────────────────────┘   │
│                                    │
│  ← Volver                          │
└────────────────────────────────────┘
```

---

## 🚦 Getting Started

### 1. Prerequisites
```bash
# Ensure Features 003 and 008 are complete
git log --oneline --all | grep "003-gps-routes"
git log --oneline --all | grep "008-travel-diary-frontend"
```

### 2. Create Branch
```bash
git checkout develop
git pull origin develop
git checkout -b 015-gpx-wizard-integration
```

### 3. Follow Tasks
See [tasks.md](./tasks.md) for step-by-step implementation guide (50 tasks).

### 4. Run Tests
```bash
# Unit tests
npm test PostCreationGPXModal.test.tsx

# Type check
npm run type-check

# Lint
npm run lint
```

### 5. Manual Testing
```bash
# Start dev server
npm run dev

# Navigate to: http://localhost:5173/trips/create
# Complete wizard → Verify modal appears
```

---

## 📖 Related Features

- **Feature 003**: GPS Routes Interactive (provides GPXUploader component)
- **Feature 008**: Travel Diary Frontend (provides TripFormWizard)
- **Feature 004**: Celery + Redis (future: improves large file processing)

---

## ❓ FAQ

**Q: Why not add GPX upload as a step in the wizard?**
A: Would extend wizard from 4 to 5 steps, risking user abandonment. Modal approach keeps wizard short while improving GPX discoverability.

**Q: What if the GPX upload fails?**
A: Modal shows error message in Spanish, allows retry or skip. Trip is NOT deleted (upload is optional).

**Q: Does this change the backend?**
A: No. Uses existing `POST /trips/{trip_id}/gpx` endpoint. Frontend-only change.

**Q: Can users still upload GPX later?**
A: Yes. GPXUploader remains available on TripDetailPage. Modal just improves discoverability.

**Q: Is the modal mobile-friendly?**
A: Yes. Bottom-aligned on mobile, touch targets ≥44px, full-width buttons.

**Q: How do I disable the modal for debugging?**
A: In `useTripForm.ts`, comment out `setShowGPXModal(true)` and uncomment `navigate(...)` (temporary workaround).

---

## 📊 Success Metrics

**After 1 week in production**:
- Target: ≥30% of trips created with GPX via modal
- Target: ≥80% upload completion rate
- Target: <5% error rate
- Target: Positive user feedback (qualitative surveys)

---

## 🤝 Contributing

1. Read [spec.md](./spec.md) for requirements
2. Follow [tasks.md](./tasks.md) for implementation steps
3. Write tests FIRST (TDD approach)
4. Test on mobile (375px viewport)
5. Verify accessibility (keyboard nav, screen reader)
6. Update [CLAUDE.md](../../CLAUDE.md) with new patterns

---

## 📝 Status

**Current**: ⏸️ **NOT STARTED** - Ready for implementation
**Branch**: `015-gpx-wizard-integration` (to be created)
**Target**: develop
**Priority**: High (UX Enhancement)
**Estimated Effort**: 0.5-1 day

---

**Last Updated**: 2026-01-28
**Author**: Claude Code (via specification-driven development)
