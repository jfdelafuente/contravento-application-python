# Contributing to ContraVento Documentation

Welcome! This guide explains how to maintain and improve ContraVento's documentation.

**Documentation Hub**: [docs/README.md](README.md)

---

## 📋 Quick Reference

### When to Add Documentation

| Scenario | Where to Add | Type |
|----------|-------------|------|
| New deployment mode | `docs/deployment/modes/` | Mode guide |
| New API endpoint | `docs/api/endpoints/` | API reference |
| New feature (user-facing) | `docs/user-guides/` | User guide |
| New feature (technical) | `docs/features/` | Feature deep-dive |
| Architectural decision | `docs/architecture/` | Architecture doc |
| Troubleshooting solution | `docs/development/troubleshooting/` | Troubleshooting guide |
| Testing strategy | `docs/testing/` | Testing doc |

### When to Update Documentation

- ✅ **API changes**: Update endpoint docs + OpenAPI contracts
- ✅ **New environment variable**: Update deployment guides
- ✅ **Architecture changes**: Update architecture docs
- ✅ **Breaking changes**: Update migration guides + CHANGELOG
- ✅ **Bug fixes**: Update troubleshooting guides if applicable

---

## 📁 Documentation Structure

```
docs/
├── README.md                    # 📌 Master navigation hub (NEVER delete)
├── CONTRIBUTING.md              # 📌 This file
│
├── deployment/                  # ✅ Complete (Feature 016)
│   ├── README.md               # Deployment hub
│   ├── modes/                  # 9 deployment modes
│   ├── guides/                 # Cross-cutting guides
│   └── archive/                # Old deployment docs
│
├── user-guides/                 # ✅ Complete (Phase 4)
│   ├── README.md               # User guides hub
│   ├── getting-started.md      # Onboarding
│   ├── trips/                  # Trip management guides
│   ├── social/                 # Social features guides
│   └── maps/                   # GPS & maps guides
│
├── api/                         # ✅ Complete (Phase 2)
│   ├── README.md               # API hub
│   ├── authentication.md       # Auth guide
│   ├── endpoints/              # Endpoint documentation
│   ├── contracts/              # OpenAPI YAML schemas
│   ├── postman/                # Postman collections
│   └── testing/                # API testing guides
│
├── architecture/                # ✅ Complete (Phase 5)
│   ├── README.md               # Architecture hub
│   ├── backend/                # Backend architecture
│   ├── frontend/               # Frontend architecture
│   ├── integrations/           # External integrations
│   └── data-model/             # Database schemas
│
├── testing/                     # ✅ Complete (Phase 3)
│   ├── README.md               # Testing hub
│   ├── backend/                # Backend testing
│   ├── frontend/               # Frontend testing
│   ├── manual-qa/              # Manual testing guides
│   └── ci-cd/                  # CI/CD documentation
│
├── development/                 # ✅ Complete (Phase 6)
│   ├── README.md               # Development hub
│   ├── getting-started.md      # Onboarding for developers
│   ├── tdd-workflow.md         # TDD process
│   ├── code-quality.md         # Linting, formatting
│   ├── scripts/                # Utility scripts catalog
│   └── troubleshooting/        # Common issues
│
├── features/                    # 🔄 Partial (30%)
│   ├── README.md               # Features index
│   └── [feature-name].md       # Feature deep-dives
│
├── operations/                  # 🔄 Minimal (10%)
│   └── README.md               # Operations hub (structure only)
│
└── archive/                     # ✅ Complete (Phase 7)
    ├── README.md               # Archive index
    ├── deployment/             # Old deployment docs
    ├── development-notes/      # SESSION_*, PHASE_* files
    ├── test-results/           # Historical test reports
    └── superseded/             # Superseded specs
```

---

## ✍️ Writing Guidelines

### Markdown Style

**Headers**:
```markdown
# Top Level (Page Title)
## Category
### Subsection
#### Detail
```

**Code Blocks**:
```markdown
```bash
# Always specify language
./run-local-dev.sh
\```
```

**Links**:
```markdown
# Internal (relative from current file)
[Getting Started](../development/getting-started.md)

# External (absolute URL)
[FastAPI](https://fastapi.tiangolo.com/)

# Anchor links (same page)
[Commands](#commands)
```

**Lists**:
```markdown
- Use hyphens for unordered lists
- Keep consistent indentation

1. Use numbers for ordered lists
2. Auto-numbering is fine (all `1.`)
```

### Spanish vs English

**Spanish for**:
- User-facing text in app
- User guides (end-user documentation)
- Error messages shown to users

**English for**:
- Technical documentation (API, architecture, deployment)
- Code comments and variable names
- Git commit messages
- This documentation (developer-facing)

### Code Examples

**Always provide**:
1. **Working example** (tested, copy-pasteable)
2. **Expected output** (if applicable)
3. **Context** (when to use it)

**Example**:
```markdown
### Create Admin User

```bash
cd backend
poetry run python scripts/user-mgmt/create_admin.py
\```

**Expected Output**:
```
Admin user created successfully!
Username: admin
Email: admin@contravento.com
Role: ADMIN
\```

**When to Use**: First-time setup or when you need admin access.
```

---

## 🔄 Update Workflow

### 1. Identify Documentation to Update

**Trigger**: Code change → Check impact on docs

| Code Change | Docs to Update |
|-------------|----------------|
| New API endpoint | `docs/api/endpoints/`, `docs/api/contracts/` |
| New environment variable | `docs/deployment/guides/environment-variables.md` |
| New deployment mode | `docs/deployment/modes/`, `docs/deployment/README.md` |
| Architecture change | `docs/architecture/` |
| New script | `docs/development/scripts/overview.md` |
| Bug fix (common issue) | `docs/development/troubleshooting/` |

### 2. Update Relevant Files

**Example: Adding New API Endpoint**

1. **Create endpoint doc** (`docs/api/endpoints/photos.md`):
   ```markdown
   # Photos API

   Manage trip photos.

   ## Endpoints

   ### Upload Photo
   \`POST /trips/{trip_id}/photos\`
   ```

2. **Update OpenAPI contract** (`docs/api/contracts/photos-api.yaml`):
   ```yaml
   paths:
     /trips/{trip_id}/photos:
       post:
         summary: Upload trip photo
   ```

3. **Update API README** (`docs/api/README.md`):
   ```markdown
   - [Photos](endpoints/photos.md)
   ```

4. **Test the docs**:
   ```bash
   # Verify links work
   # Copy/paste code examples
   # Check formatting renders correctly
   ```

### 3. Submit Changes

```bash
# Stage changes
git add docs/

# Commit with descriptive message
git commit -m "docs: add Photos API endpoint documentation

- Created docs/api/endpoints/photos.md
- Added OpenAPI contract for photos
- Updated API README with photos link"

# Push
git push origin develop
```

---

## 🏗️ Adding New Documentation

### New Deployment Mode

1. **Create mode file**: `docs/deployment/modes/new-mode.md`
   ```markdown
   # New Mode Deployment

   **Purpose**: [What is this mode for?]
   **Environment**: [Where does it run?]
   **Database**: [SQLite or PostgreSQL?]

   ## Quick Start

   \`\`\`bash
   ./deploy.sh new-mode
   \`\`\`

   ## Environment Variables

   | Variable | Value | Required |
   |----------|-------|----------|
   | DATABASE_URL | ... | Yes |
   ```

2. **Update deployment README**: Add to mode table + decision tree

3. **Update CLAUDE.md**: Add to Local Development Options (if applicable)

### New User Guide

1. **Create guide**: `docs/user-guides/category/guide-name.md`

2. **Add screenshots**: Use `docs/user-guides/images/` folder

3. **Update user-guides README**: Add link in appropriate category

4. **Cross-reference**: Link from related guides

### New Troubleshooting Guide

1. **Add to category**:
   - Common issues → `docs/development/troubleshooting/common-issues.md`
   - Database issues → `docs/development/troubleshooting/database-issues.md`
   - Feature-specific → Create new file

2. **Format**:
   ```markdown
   ### Issue Title

   **Symptoms**:
   - Error message or behavior

   **Cause**:
   - Root cause explanation

   **Solution**:
   \`\`\`bash
   # Step-by-step fix
   command1
   command2
   \`\`\`

   **Prevention**:
   - How to avoid in future
   ```

3. **Update troubleshooting README**: Add to index

---

## 🗂️ Archiving Documentation

### When to Archive

Archive documentation when it meets **ANY** of:

1. **Superseded**: Replaced by newer, consolidated documentation
2. **Obsolete**: No longer relevant to current codebase
3. **Development Notes**: Session summaries, phase plans (not user-facing)
4. **Test Results**: Historical test reports, completed testing artifacts

### How to Archive

1. **Move file** (preserves git history):
   ```bash
   git mv specs/feature/TESTING_GUIDE.md docs/archive/test-results/feature/
   ```

2. **Update archive README**:
   ```markdown
   ### Feature Name

   - [TESTING_GUIDE.md](feature/TESTING_GUIDE.md) - Description

   **Date Archived**: YYYY-MM-DD
   **Reason**: Consolidated in docs/testing/manual-qa/feature-testing.md
   ```

3. **Create redirect** (optional) in original location:
   ```markdown
   # TESTING_GUIDE.md (Archived)

   This file has been archived.

   **New Location**: [docs/archive/test-results/feature/TESTING_GUIDE.md](../../docs/archive/test-results/feature/TESTING_GUIDE.md)

   **Superseded By**: [docs/testing/manual-qa/feature-testing.md](../../docs/testing/manual-qa/feature-testing.md)
   ```

4. **Commit**:
   ```bash
   git add -A
   git commit -m "docs: archive feature testing guide

   Moved specs/feature/TESTING_GUIDE.md to docs/archive/test-results/feature/
   Reason: Consolidated in docs/testing/manual-qa/feature-testing.md"
   ```

**Important**: **NEVER delete** old documentation. Always archive for historical reference.

---

## ✅ Quality Checklist

Before committing documentation changes:

### Content Quality

- [ ] **Accurate**: All information is current and correct
- [ ] **Complete**: Covers all necessary information
- [ ] **Clear**: Easy to understand for target audience
- [ ] **Tested**: All code examples work as shown
- [ ] **Screenshots**: Images are current (if applicable)

### Technical Quality

- [ ] **Links work**: All internal and external links are valid
- [ ] **Formatting**: Markdown renders correctly
- [ ] **Structure**: Headers follow hierarchy (H1 → H2 → H3)
- [ ] **Code blocks**: Language specified (```bash, ```python, etc.)

### Navigation

- [ ] **Indexed**: Added to parent README.md
- [ ] **Cross-referenced**: Linked from related documents
- [ ] **Discoverable**: Can be found via search or decision tree

### Maintenance

- [ ] **Date updated**: "Last Updated" field current
- [ ] **Status noted**: ✅ Complete, 🔄 In Progress, ⏳ Planned
- [ ] **Ownership**: Clear who maintains this doc

---

## 🔍 Finding Documentation to Update

### Search for References

```bash
# Find all references to a file
grep -r "filename.md" docs/

# Find all references to a topic
grep -r "keyword" docs/

# Find all broken links (markdown-link-check)
npx markdown-link-check docs/**/*.md
```

### Common Update Scenarios

**Scenario**: New environment variable added to `.env.example`

**Docs to Update**:
1. `docs/deployment/guides/environment-variables.md`
2. Relevant mode guide (e.g., `docs/deployment/modes/staging.md`)
3. `CLAUDE.md` (if critical for AI guidance)

**Scenario**: New testing pattern introduced

**Docs to Update**:
1. `docs/testing/README.md`
2. Specific guide (e.g., `docs/testing/backend/unit-tests.md`)
3. `CLAUDE.md` → Testing Patterns section

**Scenario**: Troubleshooting new common issue

**Docs to Update**:
1. `docs/development/troubleshooting/common-issues.md`
2. `docs/development/troubleshooting/README.md` (index)

---

## 📊 Documentation Metrics

### Consolidation Goals (Achieved)

- **Baseline**: 300+ markdown files (scattered, duplicated)
- **Target**: ~150 well-organized files (50% reduction)
- **Actual**: 120 markdown files in `docs/` (60% reduction) ✅

### Quality Metrics

**Link Validity**:
- **Target**: 95% links valid
- **Current**: 90% (2 planned links in operations/)

**Discoverability**:
- **Target**: Find docs in <30 seconds
- **Method**: Decision tree + search

**Coverage**:
- Deployment: ✅ 97%
- User Guides: ✅ 100%
- API: ✅ 100%
- Architecture: ✅ 90%
- Testing: ✅ 100%
- Development: ✅ 100%
- Features: 🔄 30%
- Operations: 🔄 10%
- Archive: ✅ 100%

---

## 🚨 Common Mistakes to Avoid

1. **Don't duplicate**: Check if docs already exist before creating new ones
2. **Don't skip indexing**: Always update parent README.md
3. **Don't hardcode URLs**: Use relative paths for internal links
4. **Don't mix audiences**: Keep user guides separate from technical docs
5. **Don't forget screenshots**: Visual aids help user guides significantly
6. **Don't skip testing**: Always test code examples before committing
7. **Don't create orphans**: Ensure new docs are linked from at least one place
8. **Don't delete**: Archive instead of deleting old documentation
9. **Don't skip dates**: Always update "Last Updated" field
10. **Don't ignore linter**: Fix markdown warnings before committing

---

## 📞 Getting Help

### Documentation Questions

- **Structure questions**: Review [docs/README.md](README.md) decision tree
- **Style questions**: See [Writing Guidelines](#writing-guidelines)
- **Archival questions**: See [docs/archive/README.md](archive/README.md)

### Review Process

1. **Self-review**: Use [Quality Checklist](#quality-checklist)
2. **Peer review**: Ask teammate to review docs
3. **Test docs**: Follow your own instructions to verify accuracy

---

## 📈 Future Improvements

**Planned Enhancements**:

1. **Automated link checking**: CI/CD validation of all markdown links
2. **Screenshot automation**: Automated screenshot generation for user guides
3. **Versioning**: Document version-specific features (v1.0, v2.0)
4. **Search optimization**: Add tags/keywords for better search
5. **Diagrams**: Architecture diagrams using Mermaid or PlantUML
6. **API changelog**: Automated API changelog from OpenAPI diffs
7. **Internationalization**: Spanish translations for user guides

---

## 🎯 Documentation Philosophy

### Principles

1. **User-Centric**: Write for the reader, not for yourself
2. **Actionable**: Provide clear next steps, not just theory
3. **Accurate**: Wrong docs are worse than no docs
4. **Discoverable**: If docs can't be found, they don't exist
5. **Maintainable**: Keep docs up-to-date or archive them
6. **Comprehensive**: Cover the "why" and "how", not just "what"

### Target Audiences

| Audience | Primary Docs | Secondary Docs |
|----------|-------------|----------------|
| **End Users** | user-guides/ | features/ |
| **API Consumers** | api/ | architecture/ |
| **New Developers** | development/, deployment/ | testing/, architecture/ |
| **DevOps** | deployment/, operations/ | architecture/ |
| **QA Engineers** | testing/, deployment/ | user-guides/ |

---

**Last Updated**: 2026-02-07
**Consolidation Plan**: Phase 8 (Validation & Polish) - ✅ Complete
**Total Documentation Files**: 120+ markdown files in docs/
