# Frontend Architecture - ContraVento

Frontend architecture documentation for the ContraVento React application.

**Last Updated**: 2026-02-07
**Stack**: React 18 + TypeScript 5 + Vite

---

## Quick Navigation

| Topic | Documentation | Status |
|-------|--------------|--------|
| **Design System** | [design-system.md](design-system.md) | ✅ Complete |
| **Component Patterns** | 📋 Planned | ⏳ Future |
| **State Management** | 📋 Planned | ⏳ Future |
| **Routing** | 📋 Planned | ⏳ Future |

---

## Available Documentation

### 🎨 Design System

**File**: [design-system.md](design-system.md)

Component library, styling guidelines, and design patterns for the frontend.

**Topics**:
- Component structure and organization
- Styling conventions (CSS modules, Tailwind)
- Design tokens (colors, typography, spacing)
- Reusable UI components
- Theming and accessibility

**Use Cases**:
- Building new UI components
- Maintaining consistent design
- Understanding component architecture

---

## Planned Documentation

The following documentation is planned for future phases:

### Component Patterns (Planned)

- Container/Presentational component split
- Custom hooks patterns (useTripList, useTripForm, useTripPhotos)
- Form management with React Hook Form
- Photo upload with react-dropzone
- Modal dialogs and confirmations

### State Management (Planned)

- React Context for global state
- Local state management patterns
- Form state with React Hook Form
- Cache strategies
- Optimistic updates

### Routing (Planned)

- React Router 6 patterns
- Route protection (authentication)
- Nested routes
- Route parameters and query strings
- Programmatic navigation

---

## Related Documentation

- **[Backend Architecture](../backend/README.md)** - Backend architecture overview
- **[API Reference](../../api/README.md)** - API consumed by frontend
- **[User Guides](../../user-guides/README.md)** - End-user flows
- **[Testing](../../testing/frontend/)** - Frontend testing strategies

---

## Technology Stack

**Core**:
- React 18.3.1
- TypeScript 5.x
- Vite 6.0.11

**Routing & Forms**:
- React Router 6.x
- React Hook Form 7.70.x
- Zod (validation)

**UI & Styling**:
- Tailwind CSS 3.x (utility-first)
- CSS Modules (scoped styles)
- react-dropzone (file uploads)
- yet-another-react-lightbox (photo galleries)

**Maps & GPS**:
- react-leaflet 4.2.x
- Leaflet.js 1.9.x
- Recharts 3.7.x (elevation profiles)

**HTTP & State**:
- Axios 1.x (API client)
- React Context (global state)

**Security**:
- Cloudflare Turnstile (CAPTCHA)
- HttpOnly cookies (authentication)

---

## Architecture Principles

1. **Component-Based**: Reusable, testable components
2. **Type Safety**: TypeScript for all code
3. **Performance**: Code splitting, lazy loading
4. **Accessibility**: WCAG 2.1 AA compliance
5. **Responsive**: Mobile-first design
6. **Developer Experience**: Fast HMR, clear error messages

---

## Contributing

To add frontend architecture documentation:

1. Create markdown file in `docs/architecture/frontend/`
2. Follow naming convention: `topic-name.md` (lowercase, hyphens)
3. Include:
   - **Overview**: What the pattern/system does
   - **Implementation**: How it's implemented
   - **Examples**: Code examples
   - **Best Practices**: Dos and don'ts
   - **Related Files**: Links to source code
4. Update this README.md with link
5. Cross-reference from related docs

See [docs/CONTRIBUTING.md](../../CONTRIBUTING.md) for complete guidelines.

---

**Total Files**: 1 (design-system)
**Coverage**: Design system complete, patterns planned for future
**Maintenance**: Update when architecture changes
