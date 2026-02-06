# Documentation Archive - ContraVento

This directory contains archived documentation from previous versions of ContraVento.

**Purpose**: Preserve historical documentation while maintaining clean, current docs structure.

---

## Archival Policy

### What Gets Archived

Documentation is archived when it meets ANY of these criteria:

1. **Superseded**: Replaced by newer, consolidated documentation
2. **Obsolete**: No longer relevant to current codebase
3. **Development Notes**: Session summaries, phase plans, implementation notes (not user-facing)
4. **Test Results**: Historical test reports, completed testing artifacts

### What Does NOT Get Archived

- **Active Specifications**: specs/ folder contains active feature designs
- **Current Documentation**: docs/ contains current, maintained documentation
- **Code**: Source code is never archived (use git history)

---

## Archive Structure

```
archive/
├── README.md (this file)
├── development-notes/      # SESSION_*.md, PHASE*.md, implementation summaries
├── test-results/           # Historical test reports, QA results
├── superseded/             # Old docs replaced by new structure
└── deployment/             # Old deployment docs (pre-Feature-016)
    ├── v0.3.0-QUICK_START.md
    ├── v0.3.0-DEPLOYMENT.md
    └── v0.3.0-ENVIRONMENTS.md
```

---

## Archive Contents

### Deployment Documentation (v0.3.0)

Archived on **2026-01-28** as part of Feature 016 (Deployment Documentation Consolidation).

| Archived File | Replaced By | Reason |
|---------------|-------------|--------|
| [v0.3.0-QUICK_START.md](deployment/v0.3.0-QUICK_START.md) | [docs/deployment/README.md](../deployment/README.md) | Superseded by unified deployment docs |
| [v0.3.0-DEPLOYMENT.md](deployment/v0.3.0-DEPLOYMENT.md) | [docs/deployment/modes/](../deployment/modes/) | Split into 9 mode-specific docs |
| [v0.3.0-ENVIRONMENTS.md](deployment/v0.3.0-ENVIRONMENTS.md) | [docs/deployment/guides/environment-variables.md](../deployment/guides/environment-variables.md) | Superseded by environment variables guide |

**Redirects**: Original files replaced with redirect documents pointing to new locations.

---

### Development Notes (Planned - Phase 7)

Session notes and phase plans from active feature development.

**To be archived from specs/**:

| Source | Reason for Archival |
|--------|-------------------|
| `specs/004-social-network/SESSION_*.md` (9 files) | Development session notes (historical) |
| `specs/006-dashboard-dynamic/MVP_SUMMARY.md` | Implementation summary (historical) |
| `specs/008-travel-diary-frontend/PHASE9_SUMMARY.md` | Phase completion notes (historical) |
| `specs/009-gps-coordinates/PHASE3_PLAN.md` | Superseded by tasks.md |
| `specs/014-landing-page/SESSION_SUMMARY.md` | Session notes (historical) |
| `specs/017-gps-trip-wizard/FASE2_DISEÑO_MOCKUP.md` | Design phase notes (historical) |

**Destination**: `archive/development-notes/`

**Note**: Will be archived in Phase 7 (Week 7) of consolidation plan.

---

### Test Results (Planned - Phase 7)

Historical test reports and QA results.

**To be archived from specs/**:

| Source | Reason for Archival |
|--------|-------------------|
| `specs/004-social-network/TEST_RESULTS_*.md` | Completed test reports |
| `specs/004-social-network/TESTING_MANUAL_*.md` | Historical manual testing guides |
| `specs/013-public-trips-feed/TESTING_RESULTS.md` | Completed E2E test results |

**Destination**: `archive/test-results/`

**Note**: Will be archived in Phase 7 (Week 7) of consolidation plan.

---

### Superseded Documentation (Planned - Phase 7)

Documentation replaced by newer versions or consolidation.

**Candidates**:
- `specs/012-typescript-code-quality/` (minimal spec, likely obsolete)
- `specs/011-frontend-deployment/` (if redundant with docs/deployment/)

**Destination**: `archive/superseded/`

**Note**: Will be evaluated in Phase 7 (Week 7) of consolidation plan.

---

## How to Find Archived Documentation

### Search by Topic

Use git grep to search across all archives:

```bash
# Search for specific topic
git grep -i "deployment" docs/archive/

# Search in specific archive folder
git grep -i "session" docs/archive/development-notes/
```

### Browse Git History

For deleted/moved files:

```bash
# Find when file was deleted/moved
git log --all --full-history -- path/to/file.md

# View file at specific commit
git show <commit-hash>:path/to/file.md
```

---

## Accessing Archived Documentation

Archived files are preserved in their **original format** without modifications.

### Deployment Archive (v0.3.0)

**Online**:
- Navigate to `docs/archive/deployment/` in your IDE or GitHub
- Files are markdown and fully readable

**Local**:
```bash
cd docs/archive/deployment
less v0.3.0-QUICK_START.md
```

### Development Notes Archive (Planned)

**Online**:
- Navigate to `docs/archive/development-notes/` in your IDE or GitHub

**Local**:
```bash
cd docs/archive/development-notes
ls -la  # List all archived session notes
```

---

## Migration Timeline

| Archive Category | Migration Date | Status |
|-----------------|----------------|--------|
| **Deployment Docs** (v0.3.0) | 2026-01-28 | ✅ Complete (Feature 016 Phase 4) |
| **Development Notes** | TBD (Week 7) | ⏳ Planned (Consolidation Plan Phase 7) |
| **Test Results** | TBD (Week 7) | ⏳ Planned (Consolidation Plan Phase 7) |
| **Superseded Docs** | TBD (Week 7) | ⏳ Planned (Consolidation Plan Phase 7) |

---

## Archival Process

When archiving documentation:

1. **Copy** original file to `docs/archive/<category>/` with version prefix (e.g., `v0.3.0-FILE.md`)
2. **Preserve** original formatting (no edits)
3. **Add entry** to this README.md explaining what was archived and why
4. **Update references** in current documentation pointing to archived files
5. **Create redirect** (optional) in original location pointing to new documentation

**Important**: Never delete old docs - always archive them for historical reference.

---

## Related Documentation

- **[Current Documentation Hub](../README.md)** - Master navigation for all current docs
- **[Deployment Documentation](../deployment/README.md)** - Active deployment docs
- **[MIGRATION_PLAN.md](../deployment/MIGRATION_PLAN.md)** - Feature 016 migration plan

---

**Last Updated**: 2026-02-06
**Archival Policy**: Preserve, don't delete
**Contact**: For questions about archived docs, see CONTRIBUTING.md (to be created)
