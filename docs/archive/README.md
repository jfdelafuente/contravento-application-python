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

### Development Notes (✅ Archived - Phase 7)

Session notes and phase plans from feature development.

**Archived on 2026-02-07**:

| Source | Destination | Files |
|--------|-------------|-------|
| `specs/004-social-network/` | [`development-notes/004-social-network/`](development-notes/004-social-network/) | 3 files |
| `specs/006-dashboard-dynamic/` | [`development-notes/006-dashboard-dynamic/`](development-notes/006-dashboard-dynamic/) | 2 files |
| `specs/008-travel-diary-frontend/` | [`development-notes/008-travel-diary-frontend/`](development-notes/008-travel-diary-frontend/) | 1 file |
| `specs/009-gps-coordinates/` | [`development-notes/009-gps-coordinates/`](development-notes/009-gps-coordinates/) | 2 files |
| `specs/014-landing-page-inspiradora/` | [`development-notes/014-landing-page-inspiradora/`](development-notes/014-landing-page-inspiradora/) | 2 files |
| `specs/017-gps-trip-wizard/` | [`development-notes/017-gps-trip-wizard/`](development-notes/017-gps-trip-wizard/) | 1 file |

**Total Files Archived**: 11 development notes from 6 features

**See**: [development-notes/README.md](development-notes/README.md) for complete index

---

### Test Results (✅ Archived - Phase 7)

Historical test reports and QA results.

**Archived on 2026-02-07** (Phase 7 Initial + Cleanup Continuation):

| Source | Destination | Files | Phase |
|--------|-------------|-------|-------|
| `specs/003-gps-routes/` | [`test-results/003-gps-routes/`](test-results/003-gps-routes/) | 1 file | Cleanup |
| `specs/004-social-network/` | [`test-results/004-social-network/`](test-results/004-social-network/) | 13 files | Initial + Cleanup |
| `specs/006-dashboard-dynamic/` | [`test-results/006-dashboard-dynamic/`](test-results/006-dashboard-dynamic/) | 1 file | Cleanup |
| `specs/007-profile-management/` | [`test-results/007-profile-management/`](test-results/007-profile-management/) | 6 files | Cleanup |
| `specs/008-travel-diary-frontend/` | [`test-results/008-travel-diary-frontend/`](test-results/008-travel-diary-frontend/) | 2 files | Cleanup |
| `specs/010-reverse-geocoding/` | [`test-results/010-reverse-geocoding/`](test-results/010-reverse-geocoding/) | 1 file | Cleanup |
| `specs/013-public-trips-feed/` | [`test-results/013-public-trips-feed/`](test-results/013-public-trips-feed/) | 2 files | Initial + Cleanup |
| `specs/017-gps-trip-wizard/` | [`test-results/017-gps-trip-wizard/`](test-results/017-gps-trip-wizard/) | 1 file | Cleanup |

**Total Files Archived**: 29 test result documents from 10 features (3 initial + 26 additional)

**Test Coverage**: GPS routes, social network, dashboard, profile management, travel diary frontend, reverse geocoding, public trips feed, GPX trip wizard

**See**: [`test-results/README.md`](test-results/README.md) for complete index with test coverage details

---

### Superseded Documentation (✅ Archived - Phase 7)

Documentation replaced by newer versions or consolidation.

**Archived on 2026-02-07**:

| Source | Destination | Reason |
|--------|-------------|--------|
| `specs/012-typescript-code-quality/` | [`superseded/012-typescript-code-quality/`](superseded/012-typescript-code-quality/) | Minimal spec (only issue.md) |

**Total Specs Archived**: 1 minimal specification

**Not Archived**:
- `specs/011-frontend-deployment/` - Active spec with plan.md, tasks.md (NOT redundant)

**See**: [superseded/README.md](superseded/README.md) for complete index

---

### Moved to Active Documentation (✅ Phase 7 Cleanup)

Some files were moved to active documentation instead of archiving:

**Moved on 2026-02-07**:

| Source                                               | Destination                            | Reason                        |
|------------------------------------------------------|----------------------------------------|-------------------------------|
| `specs/008-travel-diary-frontend/TROUBLESHOOTING.md` | [travel-diary-troubleshooting.md][tdt] | Active troubleshooting guide  |

[tdt]: ../development/troubleshooting/travel-diary-troubleshooting.md

**Total Files Moved**: 1 troubleshooting guide

**See**: [docs/development/troubleshooting/README.md](../development/troubleshooting/README.md) for troubleshooting index

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
| **Development Notes** | 2026-02-07 | ✅ Complete (11 files from 6 features) |
| **Test Results** | 2026-02-07 | ✅ Complete (29 files from 10 features) |
| **Superseded Docs** | 2026-02-07 | ✅ Complete (1 minimal spec) |

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

**Last Updated**: 2026-02-07
**Archival Policy**: Preserve, don't delete
**Total Files Archived**: 44 documents (3 deployment + 11 development notes + 29 test results + 1 superseded spec)
**Consolidation Plan**: Phase 7 (Archive and Cleanup) - ✅ Complete
