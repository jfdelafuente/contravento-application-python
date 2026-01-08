# Documentation Archive

This directory contains historical documentation from previous versions of ContraVento.

## Purpose

Documents are moved here when they:
- Describe deprecated features or approaches
- Are superseded by newer documentation
- No longer reflect current implementation
- Are kept for historical reference only

## Guidelines

### When to Archive

Archive documentation when:
- ✅ Feature has been removed or completely redesigned
- ✅ Document references scripts/tools no longer in use
- ✅ Approach has been replaced by a better solution
- ✅ Document contradicts current best practices

### When NOT to Archive

Keep documents active when:
- ❌ Just needs minor updates to fix references
- ❌ Still relevant but slightly outdated
- ❌ Describes optional features still supported
- ❌ Used by any current deployment/environment

### Archive Format

When archiving a document:

1. **Move file** to this directory
2. **Rename** with version prefix: `v0.1.0-ORIGINAL_NAME.md`
3. **Add header** explaining why it was archived:
   ```markdown
   # [ARCHIVED - v0.1.0] Original Document Title

   **Archived on**: YYYY-MM-DD
   **Reason**: Brief explanation
   **Replaced by**: Link to new document (if applicable)

   ---

   [Original content below...]
   ```
4. **Update references** in active docs to point to replacement

## Current Archive Status

**Last updated**: 2026-01-08
**Archived documents**: 2

### Archived Files

| File | Version | Archived Date | Reason | Replaced By |
|------|---------|---------------|--------|-------------|
| `v0.1.0-DEPLOYMENT.md` | v0.1.0 | 2026-01-08 | Consolidated with DOCKER_DEPLOYMENT.md | [DEPLOYMENT.md](../DEPLOYMENT.md) |
| `v0.1.0-DOCKER_DEPLOYMENT.md` | v0.1.0 | 2026-01-08 | Consolidated with DEPLOYMENT.md | [DEPLOYMENT.md](../DEPLOYMENT.md) |

---

**Note**: Before archiving any document, ensure it's truly obsolete and not just in need of updates. When in doubt, update rather than archive.
