<!--
Sync Impact Report - Constitution Update
===========================================
Version Change: Initial → 1.0.0
Modification Type: MINOR (New constitution created)
Date: 2025-12-23

Principles Added:
- I. Code Quality & Maintainability
- II. Testing Standards (Non-Negotiable)
- III. User Experience Consistency
- IV. Performance Requirements

Added Sections:
- Security & Data Protection
- Development Workflow
- Governance

Templates Status:
- ✅ plan-template.md: Reviewed - Constitution Check section ready for these principles
- ✅ spec-template.md: Reviewed - Requirements and Success Criteria align with principles
- ✅ tasks-template.md: Reviewed - Test-first workflow and task categorization compatible
- ✅ commands/*.md: Reviewed - No agent-specific references found

Follow-up TODOs: None
-->

# ContraVento Constitution

## Core Principles

### I. Code Quality & Maintainability

Code MUST be written to last and evolve with the platform. Quality is non-negotiable because ContraVento serves a growing community of cyclists who depend on data integrity and reliable functionality.

**Rules**:
- All code MUST follow PEP 8 style guidelines for Python
- Functions and classes MUST have clear, single responsibilities (Single Responsibility Principle)
- Complex logic MUST include explanatory comments describing the "why", not the "what"
- Magic numbers and hardcoded values MUST be replaced with named constants
- Code duplication MUST be eliminated through appropriate abstractions
- All public APIs MUST have complete docstrings following Google/NumPy style
- Type hints MUST be used for all function signatures
- Linting (flake8/ruff) and formatting (black) MUST pass with zero warnings before commits

**Rationale**: As ContraVento grows to support thousands of cyclists and their travel data, maintainability directly impacts our ability to add features, fix bugs, and onboard new developers. Poor code quality creates technical debt that slows development and increases risk of data loss or corruption.

### II. Testing Standards (Non-Negotiable)

Testing is MANDATORY and MUST follow Test-Driven Development (TDD) principles. No production code may be written without corresponding tests.

**Rules**:
- **TDD Workflow STRICTLY ENFORCED**: Write test → Test fails (Red) → Implement → Test passes (Green) → Refactor
- Every feature MUST have tests written and approved by stakeholders BEFORE implementation begins
- **Unit Tests REQUIRED**: All business logic, models, and services MUST have unit tests with ≥90% coverage
- **Integration Tests REQUIRED** for:
  - API endpoints and contracts
  - Database operations and migrations
  - Third-party integrations (GPS processing, map services, authentication)
  - File upload/download functionality (GPX files, images)
- **Contract Tests REQUIRED** for all public APIs to ensure backward compatibility
- Edge cases and error conditions MUST be tested explicitly
- Tests MUST be independent, repeatable, and fast (unit tests <100ms each)
- All tests MUST pass before any PR can be merged
- pytest framework MUST be used with appropriate fixtures and parametrization

**Rationale**: ContraVento handles precious user data (travel journals, GPS tracks, photos). A single bug could lose someone's record of their cross-country journey. TDD ensures features work correctly from day one and prevents regressions as the platform evolves.

### III. User Experience Consistency

The platform MUST provide a seamless, predictable experience across all features and devices. Every interaction should feel cohesive and aligned with ContraVento's identity as a cyclist-focused community.

**Rules**:
- All user-facing text MUST be in Spanish (primary) with internationalization support for future languages
- Error messages MUST be clear, actionable, and user-friendly (no stack traces or technical jargon to users)
- API responses MUST follow consistent JSON structure:
  ```json
  {
    "success": true/false,
    "data": {...},
    "error": {"code": "ERR_CODE", "message": "User-friendly message"}
  }
  ```
- HTTP status codes MUST be used correctly (200 success, 400 client errors, 500 server errors)
- Validation errors MUST return field-specific messages
- Loading states, empty states, and error states MUST be explicitly designed and implemented
- All interactive elements MUST provide visual feedback (hover, active, disabled states)
- Images MUST include alt text for accessibility
- Forms MUST validate input client-side and server-side with consistent error messaging
- Date/time formats MUST be localized and timezone-aware
- Distance and elevation MUST be displayed in metric units (km, meters) with configurable imperial conversion

**Rationale**: Cyclists using ContraVento come from diverse backgrounds but share a passion for documenting and sharing their journeys. Consistency builds trust and reduces cognitive load, allowing users to focus on what matters—their cycling adventures.

### IV. Performance Requirements

ContraVento MUST be fast and responsive to handle real-world usage patterns, including cyclists in remote areas with limited connectivity uploading GPX files and photos from their trips.

**Rules**:
- API endpoints MUST respond within:
  - **Simple queries** (user profile, trip list): <200ms p95
  - **Complex queries** (feed generation, search): <500ms p95
  - **File uploads** (GPX processing): <2s for files up to 10MB
- Database queries MUST be optimized with appropriate indexes
- N+1 query problems MUST be eliminated using eager loading/joins
- Large data sets MUST be paginated (max 50 items per page for trips, 100 for feed)
- Images MUST be automatically resized/optimized on upload (max 2MB per image)
- GPX file processing MUST be asynchronous for files >1MB
- Static assets MUST be cacheable with appropriate headers
- Database connections MUST use connection pooling
- Memory usage MUST stay below 512MB for typical API server instance
- All performance-critical code paths MUST be profiled and benchmarked
- Background jobs (image processing, GPX analysis) MUST use task queues (Celery/RQ)

**Rationale**: Performance directly impacts user satisfaction. Slow load times frustrate cyclists trying to share their experiences, and poor performance under load risks platform stability as the community grows. ContraVento must handle peaks when cyclists return from weekend trips and upload content simultaneously.

## Security & Data Protection

User data security is paramount. ContraVento stores personal travel histories, location data, and user-generated content that must be protected.

**Rules**:
- All passwords MUST be hashed using bcrypt with appropriate salt rounds (≥12)
- Authentication MUST use secure session management or JWT tokens with appropriate expiration
- SQL injection MUST be prevented through parameterized queries/ORM usage only
- All file uploads MUST be validated (type, size, content) and sanitized
- User input MUST be sanitized to prevent XSS attacks
- API endpoints MUST enforce authentication and authorization checks
- Sensitive data (API keys, database credentials) MUST be stored in environment variables, never in code
- HTTPS MUST be enforced for all production traffic
- User privacy settings MUST be respected (private trips, visibility controls)
- GDPR compliance MUST be maintained (data export, deletion requests)
- Security vulnerabilities MUST be patched within 48 hours of discovery
- Dependencies MUST be regularly updated and scanned for known vulnerabilities

## Development Workflow

Consistent workflow ensures code quality and team collaboration.

**Rules**:
- All work MUST happen on feature branches named `###-feature-description`
- Commits MUST have clear, descriptive messages following conventional commit format
- Pull requests MUST include:
  - Description of changes and rationale
  - Link to related feature specification
  - Test coverage summary
  - Screenshots/demos for UI changes
- Code reviews MUST verify:
  - All tests pass
  - Code follows quality standards
  - No security vulnerabilities introduced
  - Documentation updated if needed
- CI/CD pipeline MUST run all tests and linting before merge
- Breaking changes MUST be documented and communicated
- Database migrations MUST be reversible and tested
- No direct commits to main/master branch

## Governance

This constitution defines the quality bar for ContraVento development and supersedes all other practices.

**Amendment Process**:
- Proposed amendments MUST be documented with rationale and impact analysis
- Amendments require team review and approval
- Version number MUST be incremented according to semantic versioning:
  - **MAJOR**: Breaking changes to principles or governance
  - **MINOR**: New principles or sections added
  - **PATCH**: Clarifications, wording improvements, non-semantic changes
- Migration plan MUST be provided for amendments affecting existing code

**Compliance**:
- All pull requests MUST be verified against this constitution
- Violations MUST be justified in the Complexity Tracking section of implementation plans
- Constitution check is a REQUIRED gate before implementation can proceed
- Unjustified complexity or violations MUST be rejected

**Template Synchronization**:
- Changes to principles MUST be reflected in `.specify/templates/plan-template.md`, `spec-template.md`, and `tasks-template.md`
- Command workflows MUST remain aligned with constitutional requirements

**Version**: 1.0.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-23
