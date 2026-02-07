# Superseded Documentation Archive

Documentation that has been replaced by newer versions, consolidated docs, or is no longer relevant.

**Archived**: 2026-02-07 (Phase 7 of Documentation Consolidation)

---

## Contents

This archive contains feature specifications and documentation that have been superseded:

- **Minimal Specs**: Features with incomplete specifications
- **Consolidated Docs**: Documentation replaced by consolidated versions
- **Obsolete Features**: Features no longer in active development

**Total Specs**: 1
**Reason**: Minimal/incomplete specification

---

## Archived Specs

### 012-typescript-code-quality/

**TypeScript Code Quality** - Minimal specification for frontend code quality

**Contents**:
- [`issue.md`](012-typescript-code-quality/issue.md) - Original GitHub issue describing the feature

**Date Archived**: 2026-02-07
**Reason**: Minimal spec (only issue.md, no plan/tasks/implementation)

**Status**: Feature was minimal and never fully developed beyond initial issue

**Related Active Documentation**:
- Frontend code quality is now covered in:
  - [Frontend README](../../../frontend/README.md)
  - [Frontend Testing Guide](../../../frontend/TESTING_GUIDE.md)
  - TypeScript configuration: `frontend/tsconfig.json`
  - ESLint configuration: `frontend/.eslintrc.js`

---

## Why Archive Superseded Docs?

**Clean Specs Folder**:
- Active specs only (plan.md, tasks.md, spec.md)
- No minimal/incomplete specs cluttering workspace
- Clear signal: "If it's in specs/, it's active"

**Preserve History**:
- Original issue preserved for reference
- Context for why feature was minimal
- Audit trail for feature decisions

**Redirect to Current Docs**:
- Point users to current, maintained documentation
- Avoid confusion from outdated specs
- Single source of truth for features

---

## Accessing Superseded Docs

### Browse Archived Specs

Navigate to subdirectories:
- [012-typescript-code-quality/](012-typescript-code-quality/) - TypeScript code quality (minimal spec)

### Search Archived Specs

```bash
# Search for specific keyword in superseded docs
grep -r "typescript" docs/archive/superseded/

# Find all issue files
find docs/archive/superseded/ -name "issue.md"
```

### View in Git History

```bash
# See when spec was archived
git log --follow docs/archive/superseded/012-typescript-code-quality/

# View original location
git log --all --full-history -- specs/012-typescript-code-quality/
```

---

## Active Frontend Quality Documentation

**Instead of archived 012-typescript-code-quality, see**:

1. **[Frontend README](../../../frontend/README.md)** - Frontend architecture and setup
   - TypeScript configuration
   - Project structure
   - Development workflow

2. **[Frontend Testing Guide](../../../frontend/TESTING_GUIDE.md)** - Testing strategies
   - Unit tests with Vitest
   - E2E tests with Playwright
   - Accessibility testing
   - Code quality standards

3. **Configuration Files**:
   - `frontend/tsconfig.json` - TypeScript compiler options
   - `frontend/.eslintrc.js` - ESLint rules
   - `frontend/vite.config.ts` - Vite build configuration

4. **Package Scripts** (`frontend/package.json`):
   - `npm run lint` - ESLint checks
   - `npm run type-check` - TypeScript type checking
   - `npm run test` - Run test suite

---

## Archive Index

| Spec | Files | Reason | Active Alternative |
|------|-------|--------|-------------------|
| 012-typescript-code-quality | 1 | Minimal spec | Frontend README, TESTING_GUIDE |
| **TOTAL** | **1** | **Superseded specs** | **Active frontend docs** |

---

## Related Documentation

- **[Archive Home](../README.md)** - Main archive index
- **[Development Notes Archive](../development-notes/README.md)** - Implementation notes
- **[Test Results Archive](../test-results/README.md)** - Historical test reports
- **[Active Specs](../../../specs/)** - Current feature specifications

---

**Last Updated**: 2026-02-07
**Archive Policy**: Preserve superseded specs for historical reference
**Specs Archived**: 1 minimal specification
