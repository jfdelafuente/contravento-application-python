# Implementation Plan: Reverse Geocoding

**Branch**: `010-reverse-geocoding` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)

## Summary

Enable users to click on a map to automatically select trip locations with GPS coordinates and place names retrieved via reverse geocoding (Nominatim OpenStreetMap API). Users can also drag markers to adjust coordinates, with automatic reverse geocoding triggered on drag completion.

**Primary Requirement**: FR-001 (Allow map clicks) + FR-002 (Reverse geocode to place names)

**Technical Approach**: Frontend-only implementation using react-leaflet hooks, Nominatim API, and client-side LRU caching.

---

## Technical Context

**Language/Version**: TypeScript 5 (frontend), Python 3.12 (backend - no changes)
**Primary Dependencies**: react-leaflet 4.x, Leaflet.js 1.9.x, lodash.debounce 4.x (NEW), axios 1.x
**Storage**: No new backend storage (uses existing TripLocation model)
**Testing**: Vitest (frontend unit/integration)
**Target Platform**: Web browsers (desktop + mobile)
**Project Type**: Web application (frontend-only)
**Performance Goals**: <2s p95 geocoding, <100ms marker drag, >70% cache hit rate
**Constraints**: 1 req/sec Nominatim rate limit, no API key required
**Scale/Scope**: ~2000 LOC (services, hooks, components, tests)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **ALL GATES PASSED** - No violations, ready for implementation

See full constitution check in complete plan.md for detailed gate-by-gate analysis.

---

## Project Structure

### Documentation (this feature)

```text
specs/010-reverse-geocoding/
├── plan.md              # This file
├── research.md          # ✅ Phase 0 output
├── data-model.md        # ✅ Phase 1 output
├── quickstart.md        # ✅ Phase 1 output
├── contracts/           # ✅ Phase 1 output
│   └── README.md
└── tasks.md             # ⏳ Phase 2 output (/speckit.tasks)
```

### Source Code (frontend-only changes)

```text
frontend/
├── src/
│   ├── components/trips/
│   │   ├── TripMap.tsx                    # MODIFIED
│   │   ├── MapClickHandler.tsx            # NEW
│   │   ├── LocationConfirmModal.tsx       # NEW
│   │   └── LocationConfirmModal.css       # NEW
│   ├── hooks/
│   │   └── useReverseGeocode.ts           # NEW
│   ├── services/
│   │   └── geocodingService.ts            # NEW
│   ├── types/
│   │   └── geocoding.ts                   # NEW
│   ├── utils/
│   │   └── geocodingCache.ts              # NEW
│   └── pages/
│       └── TripEditPage.tsx               # MODIFIED
└── tests/
    ├── unit/
    │   ├── geocodingService.test.ts       # NEW
    │   ├── geocodingCache.test.ts         # NEW
    │   └── useReverseGeocode.test.ts      # NEW
    └── integration/
        └── TripForm.geocoding.test.tsx    # NEW
```

---

## Phase 0: Research (Complete ✅)

See [research.md](./research.md) for full technical decisions.

**Key Decisions**:
- Nominatim OpenStreetMap API (free, CORS-enabled)
- react-leaflet useMapEvents hook
- Client-side LRU cache (100 entries)
- Debounced API calls (1-second delay)
- Modal confirmation pattern

---

## Phase 1: Design & Contracts (Complete ✅)

**Outputs**:
- [data-model.md](./data-model.md) - Types, cache, data flow
- [contracts/README.md](./contracts/README.md) - Nominatim API docs
- [quickstart.md](./quickstart.md) - Developer guide

**No database changes** ✅

---

## Next Steps

Run `/speckit.tasks` to generate implementation task breakdown.

**Current Status**: Ready for task generation and implementation.
