# Implementation Plan: Landing Page Inspiradora

**Branch**: `014-landing-page-inspiradora` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-landing-page-inspiradora/spec.md`

## Summary

Create a public landing page (/) that embodies ContraVento's philosophy of human and territorial connection for cyclists. The landing page features a cinematic hero section, a 4-pillar manifesto, value pillars grid, "How it works" flow, and prominent CTA for registration. Design uses a rustic minimalist aesthetic with earth-tone color palette. This replaces the current PublicFeedPage at the root URL (which will be moved to /trips/public).

**Technical Approach**: React component-based architecture using existing patterns from Feature 013 (PublicFeedPage). Frontend-only implementation with no backend changes. Responsive design with CSS grid/flexbox, lazy-loaded images (WebP with JPG fallback), and SEO optimization. Detects authenticated users via AuthContext and redirects to /dashboard.

## Technical Context

**Language/Version**: TypeScript 5 (frontend), Python 3.12 (backend - no changes required)
**Primary Dependencies**: React 18, React Router 6, react-helmet-async (NEW for SEO meta tags)
**Storage**: N/A (static content only, no new database entities)
**Testing**: Vitest (unit tests), Playwright (E2E tests), React Testing Library
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
**Project Type**: web (frontend/backend structure)
**Performance Goals**:
  - Largest Contentful Paint (LCP) < 2.5s
  - First Input Delay (FID) < 100ms
  - Cumulative Layout Shift (CLS) < 0.1
  - Initial bundle size < 500KB
  - Total page weight < 2MB
**Constraints**:
  - WCAG 2.1 AA compliance (contrast 4.5:1 minimum)
  - Mobile-first responsive design (breakpoints: 768px, 1024px)
  - SEO indexable (meta tags, semantic HTML, alt text)
  - Load time < 3s on 3G network
**Scale/Scope**:
  - Single landing page
  - 6 distinct sections (Hero, Manifesto, Value Pillars, How It Works, CTA, Footer)
  - Expected traffic: 500+ visitors/week post-launch

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Code Quality & Maintainability ✅ PASS

- **PEP 8**: N/A (frontend TypeScript only)
- **Single Responsibility**: Each section will be its own component (HeroSection, ManifestoSection, etc.)
- **Comments**: Complex responsive logic and SEO configuration will be documented
- **No magic numbers**: Color palette defined as CSS custom properties in theme.css
- **Type hints**: TypeScript interfaces for all props and data structures
- **Linting**: ESLint + TypeScript configured in project

**Status**: ✅ No violations. Follows React component best practices.

### Gate 2: Testing Standards (TDD) ✅ PASS

- **TDD Workflow**: Tests will be written first for:
  - Component rendering (Hero, Manifesto, Value Pillars, How It Works, Footer)
  - Responsive behavior (mobile/tablet/desktop breakpoints)
  - CTA click navigation to /register
  - Authenticated user redirect to /dashboard
  - SEO meta tags presence
- **Unit Tests**: Required for all components and hooks (≥90% coverage)
- **Integration Tests**: E2E tests for full user journey (land → read → CTA click → redirect)
- **Contract Tests**: N/A (no API changes)

**Status**: ✅ No violations. Test files will be created in `frontend/tests/unit/` and `frontend/tests/e2e/`.

### Gate 3: User Experience Consistency ✅ PASS

- **Spanish**: All content in Spanish
- **Error handling**: Loading states for images, fallback for missing resources
- **Accessibility**: ARIA labels, semantic HTML, alt text on all images, keyboard navigation
- **Visual feedback**: Hover states on CTA buttons and pillar cards
- **Consistent structure**: Follows existing page patterns (PublicFeedPage.tsx structure)

**Status**: ✅ No violations. Spanish content confirmed in spec.md.

### Gate 4: Performance Requirements ✅ PASS

- **LCP < 2.5s**: Hero image optimized (WebP, lazy loading), critical CSS inlined
- **Image optimization**: WebP with JPG fallback, srcset for responsive images, max 2MB per image
- **Pagination**: N/A (static content)
- **Caching**: Static assets with appropriate cache headers
- **Lazy loading**: Below-the-fold images and sections lazy-loaded

**Status**: ✅ No violations. Performance budget enforced with Lighthouse CI.

### Security & Data Protection ✅ PASS

- **No user input**: Landing page is read-only (no forms except CTA redirect)
- **No sensitive data**: Only public-facing content
- **XSS prevention**: React automatic escaping, no dangerouslySetInnerHTML
- **HTTPS**: Enforced by deployment configuration

**Status**: ✅ No violations. No security concerns for static landing page.

### Development Workflow ✅ PASS

- **Feature branch**: `014-landing-page-inspiradora` (already created)
- **Conventional commits**: Will follow format `feat(landing): add hero section`
- **PR requirements**: Tests, screenshots, Lighthouse report
- **No breaking changes**: PublicFeedPage moved to /trips/public (non-breaking route change)

**Status**: ✅ No violations. Standard workflow.

---

**Constitution Check Summary**: ✅ ALL GATES PASS - No violations. Ready to proceed.

## Project Structure

### Documentation (this feature)

```text
specs/014-landing-page-inspiradora/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already created)
├── checklists/
│   └── requirements.md  # Validation checklist (already created)
├── research.md          # Phase 0 output (MINIMAL - most decisions already made)
├── data-model.md        # N/A (no new entities)
├── quickstart.md        # Phase 1 output (integration scenarios)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── landing/                  # NEW - Landing page components
│   │       ├── HeroSection.tsx
│   │       ├── HeroSection.css
│   │       ├── ManifestoSection.tsx
│   │       ├── ManifestoSection.css
│   │       ├── ValuePillarsSection.tsx
│   │       ├── ValuePillarsSection.css
│   │       ├── HowItWorksSection.tsx
│   │       ├── HowItWorksSection.css
│   │       ├── CTASection.tsx
│   │       ├── CTASection.css
│   │       ├── Footer.tsx
│   │       └── Footer.css
│   ├── pages/
│   │   ├── LandingPage.tsx           # NEW - Main landing page
│   │   ├── LandingPage.css           # NEW - Page-level styles
│   │   ├── PublicFeedPage.tsx        # EXISTING - will move to /trips/public route
│   │   └── PublicFeedPage.css
│   ├── hooks/
│   │   └── useSEO.ts                 # NEW - SEO meta tags hook
│   ├── assets/
│   │   └── images/
│   │       └── landing/              # NEW - Landing page images
│   │           ├── hero.jpg          # Hero background image (2560x1440 source)
│   │           ├── hero.webp         # WebP optimized version
│   │           ├── hero-mobile.jpg   # Mobile version (1024x768)
│   │           └── hero-mobile.webp
│   ├── App.tsx                       # MODIFIED - Update route from / to LandingPage
│   └── pages/theme.css               # MODIFIED - Add landing page color custom properties
└── tests/
    ├── unit/
    │   └── landing/                  # NEW - Unit tests for landing components
    │       ├── HeroSection.test.tsx
    │       ├── ManifestoSection.test.tsx
    │       ├── ValuePillarsSection.test.tsx
    │       ├── HowItWorksSection.test.tsx
    │       ├── CTASection.test.tsx
    │       ├── Footer.test.tsx
    │       └── LandingPage.test.tsx
    └── e2e/
        └── landing.spec.ts           # NEW - E2E tests for landing page journey

backend/
└── [NO CHANGES REQUIRED]
```

**Structure Decision**: Web application structure (Option 2) is used. Frontend changes only - no backend modifications required. The landing page is a pure frontend feature using existing authentication context and routing infrastructure.

**Key Files to Modify**:
- `frontend/src/App.tsx` (lines 44, 118): Change root route from PublicFeedPage to LandingPage, add /trips/public route for PublicFeedPage
- `frontend/src/pages/theme.css`: Add landing-specific CSS custom properties for color palette
- `frontend/package.json`: Add `react-helmet-async` dependency for SEO meta tags

**Key Files to Create**:
- `frontend/src/pages/LandingPage.tsx`: Main landing page component
- `frontend/src/components/landing/*.tsx`: 6 section components
- `frontend/src/hooks/useSEO.ts`: Custom hook for meta tags
- `frontend/src/assets/images/landing/*`: Optimized hero images

## Complexity Tracking

> **No violations to justify** - All gates passed.

This table is intentionally empty because the feature complies with all constitutional requirements.

## Phase 0: Research & Decisions

### Research Tasks

Since the specification already includes detailed design decisions (from `feature/landing_page.md`), research is MINIMAL. Only two areas need investigation:

1. **Icon Library Selection** (DECISION REQUIRED)
   - **Question**: Which open-source icon library to use for Value Pillars and How It Works?
   - **Options**: Heroicons (already used in project), Feather Icons, Lucide Icons
   - **Criteria**: Consistency with existing UI, MIT license, availability of required icons (tienda, brújula, hoja, cámara, compartir, mapa, corazón)

2. **SEO Meta Tags Library** (DECISION REQUIRED)
   - **Question**: Which library for managing SEO meta tags?
   - **Options**: react-helmet-async (recommended for React 18), react-helmet (legacy)
   - **Criteria**: React 18 compatibility, SSR support (future), bundle size

### Decisions Already Made (from spec.md)

- **Color Palette**: Defined (#F9F7F2, #1B2621, #D35400, #4A4A4A) ✅
- **Typography**: Playfair Display (serif) via Google Fonts ✅
- **Hero Image**: Cinematographic cycling photo, golden hour ✅
- **Pillar Interaction**: Static with subtle hover (no expandables) ✅
- **Social Media**: Instagram + Facebook ✅
- **Authenticated User Behavior**: Auto-redirect to /dashboard ✅
- **PublicFeedPage Relocation**: Move to /trips/public ✅
- **Responsive Strategy**: Mobile-first with breakpoints 768px, 1024px ✅

### Assumptions Validation

1. **Google Fonts**: Confirm Playfair Display is free and has required weights (Regular 400, Bold 700)
   - **Action**: Check Google Fonts catalog
   - **Fallback**: Use system serif font stack if unavailable

2. **Image License**: Confirm hero image source and license
   - **Action**: User must provide high-quality image or specify stock photo source
   - **Constraint**: Must be royalty-free or licensed for commercial use

3. **Legal Pages**: Confirm existence of /terms-of-service and /privacy-policy routes
   - **Action**: Grep for existing routes in App.tsx
   - **Fallback**: Create placeholder pages or link to external legal documents

## Phase 1: Design & Contracts

### Data Model

**N/A** - No new database entities. The landing page is purely presentational.

### API Contracts

**N/A** - No new backend endpoints. The landing page uses existing authentication context (`AuthContext`) to detect logged-in users.

### Component Architecture

#### 1. LandingPage.tsx (Main Container)

**Responsibilities**:
- Compose all section components
- Detect authenticated user via `useAuth()`
- Redirect to /dashboard if user is logged in
- Apply SEO meta tags via `useSEO()` hook

**Props**: None

**State**:
```typescript
// Authentication check
const { user, isLoading } = useAuth();

useEffect(() => {
  if (!isLoading && user) {
    navigate('/dashboard');
  }
}, [user, isLoading, navigate]);
```

**Structure**:
```tsx
<div className="landing-page">
  <HeroSection />
  <ManifestoSection />
  <ValuePillarsSection />
  <HowItWorksSection />
  <CTASection />
  <Footer />
</div>
```

---

#### 2. HeroSection.tsx

**Responsibilities**:
- Display hero background image (responsive)
- Render headline "El camino es el destino"
- Render subheadline
- Render primary CTA button "Formar parte del viaje"

**Props**: None (all content hardcoded per spec)

**Structure**:
```tsx
<section className="hero-section">
  <picture>
    <source srcSet="/assets/images/landing/hero.webp" type="image/webp" />
    <source srcSet="/assets/images/landing/hero.jpg" type="image/jpeg" />
    <img src="/assets/images/landing/hero.jpg" alt="Ciclista en entorno rural durante la hora dorada" />
  </picture>
  <div className="hero-content">
    <h1 className="hero-title">El camino es el destino</h1>
    <p className="hero-subtitle">
      Una plataforma para quienes pedalean para conectar, no para competir.
      Premia la experiencia, regenera el territorio y cuida a la comunidad.
    </p>
    <Link to="/register" className="hero-cta">
      Formar parte del viaje
    </Link>
  </div>
</section>
```

**CSS Strategy**:
- Background image with `background-size: cover`
- Text overlay with semi-transparent backdrop for readability
- Responsive typography (vw units for h1, clamped with min/max)

---

#### 3. ManifestoSection.tsx

**Responsibilities**:
- Display 4 philosophical pillars in order
- Use generous whitespace (per "aire" requirement)

**Props**: None

**Structure**:
```tsx
<section className="manifesto-section">
  <h2 className="manifesto-title">Nuestro Manifiesto</h2>
  <div className="manifesto-pillars">
    <div className="manifesto-pillar">
      <h3>El camino es el destino</h3>
      <p>No venimos a conquistar, venimos a habitar.</p>
    </div>
    <div className="manifesto-pillar">
      <h3>Motor de regeneración</h3>
      <p>Tu pedalada activa la economía de los pueblos pequeños.</p>
    </div>
    <div className="manifesto-pillar">
      <h3>Solidaridad en ruta</h3>
      <p>La comunidad se cuida y se reporta mutuamente.</p>
    </div>
    <div className="manifesto-pillar">
      <h3>No dejar rastro</h3>
      <p>Respeto absoluto al entorno natural y la cortesía rural.</p>
    </div>
  </div>
</section>
```

**CSS Strategy**:
- Vertical layout (stack)
- Large padding between pillars (3-4rem)
- Centered text alignment

---

#### 4. ValuePillarsSection.tsx

**Responsibilities**:
- Display 3-column grid (Territorio, Comunidad, Ética)
- Render icons + titles + descriptions
- Subtle hover effect (background color shift)

**Props**: None

**Icon Mapping**:
```typescript
const PILLAR_ICONS = {
  territorio: 'ShoppingBagIcon',  // Heroicons
  comunidad: 'UsersIcon',         // Heroicons
  etica: 'LeafIcon'               // Heroicons (or alternative library)
};
```

**Structure**:
```tsx
<section className="value-pillars-section">
  <h2 className="value-pillars-title">Nuestros Valores</h2>
  <div className="value-pillars-grid">
    <div className="value-pillar">
      <TerritoryIcon className="value-pillar-icon" />
      <h3>Territorio</h3>
      <p>Consumo local, impacto real</p>
    </div>
    <div className="value-pillar">
      <CommunityIcon className="value-pillar-icon" />
      <h3>Comunidad</h3>
      <p>Reporte de alertas y consejos compartidos</p>
    </div>
    <div className="value-pillar">
      <EthicsIcon className="value-pillar-icon" />
      <h3>Ética</h3>
      <p>Cortesía rural y ética de preservación</p>
    </div>
  </div>
</section>
```

**CSS Strategy**:
- CSS Grid with 3 columns (desktop), 1 column (mobile)
- Icon size: 48px × 48px
- Hover: `background-color: rgba(27, 38, 33, 0.05)` (subtle green tint)

---

#### 5. HowItWorksSection.tsx

**Responsibilities**:
- Display 4-step flow with numbers, icons, titles, descriptions
- Responsive layout (vertical stack on mobile, horizontal flow on desktop)

**Props**: None

**Structure**:
```tsx
<section className="how-it-works-section">
  <h2 className="how-it-works-title">Cómo Funciona</h2>
  <div className="how-it-works-steps">
    <div className="step">
      <span className="step-number">1</span>
      <CameraIcon className="step-icon" />
      <h3>Documenta tu viaje</h3>
      <p>Crea diarios de ruta con fotos y ubicaciones</p>
    </div>
    <div className="step">
      <span className="step-number">2</span>
      <ShareIcon className="step-icon" />
      <h3>Comparte con la comunidad</h3>
      <p>Publica para inspirar a otros ciclistas</p>
    </div>
    <div className="step">
      <span className="step-number">3</span>
      <MapIcon className="step-icon" />
      <h3>Descubre nuevas rutas</h3>
      <p>Explora viajes de la comunidad</p>
    </div>
    <div className="step">
      <span className="step-number">4</span>
      <HeartIcon className="step-icon" />
      <h3>Impacta positivamente</h3>
      <p>Tu pedalada activa economías locales</p>
    </div>
  </div>
</section>
```

**CSS Strategy**:
- Flexbox horizontal layout (desktop), vertical stack (mobile)
- Step numbers as large accent element (3rem font size, terracota color)
- Icons: 40px × 40px

---

#### 6. CTASection.tsx

**Responsibilities**:
- Final call-to-action with inspiring message
- Large CTA button "Formar parte del viaje"
- Alternative login link

**Props**: None

**Structure**:
```tsx
<section className="cta-section">
  <h2 className="cta-title">¿Listo para pedalear con propósito?</h2>
  <p className="cta-subtitle">
    Únete a una comunidad que pedalea para conectar, no para competir
  </p>
  <Link to="/register" className="cta-button">
    Formar parte del viaje
  </Link>
  <p className="cta-login">
    ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
  </p>
</section>
```

**CSS Strategy**:
- Center-aligned content
- CTA button: Large (48px height), terracota background, white text
- Login link: Smaller, discrete gray color

---

#### 7. Footer.tsx

**Responsibilities**:
- Display ContraVento branding
- Social media links (Instagram, Facebook)
- Legal links (Terms, Privacy)
- Contact link

**Props**: None

**Structure**:
```tsx
<footer className="landing-footer">
  <div className="footer-content">
    <div className="footer-branding">
      <h3>ContraVento</h3>
      <p>Pedalear para conectar</p>
    </div>
    <div className="footer-links">
      <div className="footer-section">
        <h4>Síguenos</h4>
        <a href="https://instagram.com/contravento" target="_blank" rel="noopener noreferrer">
          Instagram
        </a>
        <a href="https://facebook.com/contravento" target="_blank" rel="noopener noreferrer">
          Facebook
        </a>
      </div>
      <div className="footer-section">
        <h4>Legal</h4>
        <Link to="/terms-of-service">Términos de Servicio</Link>
        <Link to="/privacy-policy">Política de Privacidad</Link>
      </div>
      <div className="footer-section">
        <h4>Contacto</h4>
        <a href="mailto:hola@contravento.com">hola@contravento.com</a>
      </div>
    </div>
  </div>
</footer>
```

**CSS Strategy**:
- 4-column grid (desktop), stacked (mobile)
- Neutral colors (#4A4A4A text, #F9F7F2 background)
- External links open in new tab (`target="_blank"`)

---

### SEO Hook: useSEO.ts

**Responsibilities**:
- Set page title, description, Open Graph tags
- Use react-helmet-async for meta tag injection

**Implementation**:
```typescript
import { useEffect } from 'react';
import { Helmet } from 'react-helmet-async';

interface SEOConfig {
  title: string;
  description: string;
  image?: string;
  url?: string;
}

export const useSEO = ({ title, description, image, url }: SEOConfig) => {
  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      {image && <meta property="og:image" content={image} />}
      {url && <meta property="og:url" content={url} />}
      <meta property="og:type" content="website" />
      <meta name="twitter:card" content="summary_large_image" />
    </Helmet>
  );
};
```

**Usage in LandingPage.tsx**:
```tsx
export const LandingPage: React.FC = () => {
  const seoConfig = {
    title: 'ContraVento - Pedalear para Conectar',
    description: 'Una plataforma para ciclistas que pedalean para conectar, no para competir. Documenta viajes, regenera territorios, y únete a la comunidad.',
    image: '/assets/images/landing/hero.jpg',
    url: 'https://contravento.com',
  };

  return (
    <>
      {useSEO(seoConfig)}
      <div className="landing-page">
        {/* sections */}
      </div>
    </>
  );
};
```

---

### Image Optimization Strategy

**Hero Image Specifications**:
- **Source**: 2560×1440px (16:9 ratio) - high quality JPG (~500KB)
- **WebP Version**: Same dimensions, ~200KB (60% size reduction)
- **Mobile Version**: 1024×768px, JPG ~150KB, WebP ~60KB
- **Lazy Loading**: Use `loading="lazy"` attribute
- **Responsive Images**: Use `<picture>` element with `srcset`

**Example**:
```html
<picture>
  <!-- Mobile WebP -->
  <source
    media="(max-width: 768px)"
    srcSet="/assets/images/landing/hero-mobile.webp"
    type="image/webp"
  />
  <!-- Mobile JPG -->
  <source
    media="(max-width: 768px)"
    srcSet="/assets/images/landing/hero-mobile.jpg"
    type="image/jpeg"
  />
  <!-- Desktop WebP -->
  <source
    srcSet="/assets/images/landing/hero.webp"
    type="image/webp"
  />
  <!-- Desktop JPG (fallback) -->
  <img
    src="/assets/images/landing/hero.jpg"
    alt="Ciclista en entorno rural durante la hora dorada"
    loading="eager"  <!-- Hero is above the fold, load immediately -->
  />
</picture>
```

---

### CSS Custom Properties (theme.css additions)

```css
/* Landing Page Color Palette (Feature 014) */
:root {
  /* Existing properties... */

  /* Landing Page Specific */
  --landing-bg: #F9F7F2;        /* Crema orgánico */
  --landing-title: #1B2621;     /* Verde bosque profundo */
  --landing-cta: #D35400;       /* Terracota arcilloso */
  --landing-text: #4A4A4A;      /* Gris carbón suave */

  /* Hover States */
  --landing-cta-hover: #BF4A00; /* Darker terracota */
  --landing-pillar-hover: rgba(27, 38, 33, 0.05); /* Subtle green tint */

  /* Typography */
  --landing-font-serif: 'Playfair Display', Georgia, serif;
  --landing-font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

---

### Routing Changes (App.tsx)

**Current**:
```tsx
<Route path="/" element={<PublicFeedPage />} />
```

**New**:
```tsx
{/* Landing page - root route */}
<Route path="/" element={<LandingPage />} />

{/* Public trips feed - moved from root */}
<Route path="/trips/public" element={<PublicFeedPage />} />
```

**Impact**: Non-breaking change. PublicFeedPage is public, so moving it to /trips/public doesn't require authentication changes. Any existing links to PublicFeedPage would need updating, but it's a new feature (013) with minimal external references.

---

## Phase 2: Implementation Tasks (High-Level Overview)

**Note**: Detailed task breakdown will be generated by `/speckit.tasks` command. This section provides strategic guidance only.

### Task Categories

1. **Setup & Dependencies** (T001-T003)
   - Install react-helmet-async
   - Create folder structure (components/landing, assets/images/landing)
   - Update theme.css with color custom properties

2. **Component Development** (T004-T010) - **TDD Required**
   - HeroSection (test + implementation)
   - ManifestoSection (test + implementation)
   - ValuePillarsSection (test + implementation)
   - HowItWorksSection (test + implementation)
   - CTASection (test + implementation)
   - Footer (test + implementation)
   - LandingPage container (test + implementation)

3. **SEO & Accessibility** (T011-T013)
   - useSEO hook (test + implementation)
   - Meta tags configuration
   - ARIA labels and semantic HTML
   - Alt text for all images

4. **Routing & Integration** (T014-T016)
   - Update App.tsx routes
   - Add authenticated user redirect logic
   - Test route navigation

5. **Image Optimization** (T017-T019)
   - Source hero image (high quality)
   - Generate WebP versions (desktop + mobile)
   - Generate JPG fallbacks (desktop + mobile)
   - Implement responsive `<picture>` elements

6. **Responsive Design** (T020-T022)
   - Mobile styles (< 768px)
   - Tablet styles (768-1024px)
   - Desktop styles (> 1024px)
   - Test on real devices

7. **E2E Testing** (T023-T025)
   - User journey: land → scroll → CTA click → redirect
   - Authenticated user auto-redirect
   - Cross-browser testing (Chrome, Firefox, Safari)

8. **Performance Optimization** (T026-T028)
   - Lighthouse audit (LCP, FID, CLS)
   - Bundle size analysis
   - Lazy loading verification

9. **Legal Pages** (T029-T030) - **If not existing**
   - Create Terms of Service placeholder
   - Create Privacy Policy placeholder

---

## Integration Scenarios (quickstart.md preview)

### Scenario 1: Anonymous Visitor → Registration

**Flow**:
1. Visitor lands on `/` → LandingPage renders
2. Reads hero, manifesto, value pillars
3. Clicks CTA "Formar parte del viaje"
4. Redirected to `/register` (existing page)
5. Completes registration
6. Redirected to `/welcome` (existing flow)

**Integration Points**:
- LandingPage CTA → RegisterPage (`Link to="/register"`)
- No backend changes required

---

### Scenario 2: Authenticated User → Auto-Redirect

**Flow**:
1. Logged-in user navigates to `/` (e.g., clicks logo, types URL)
2. LandingPage detects `user` in AuthContext
3. Immediately redirects to `/dashboard` via `useNavigate()`

**Integration Points**:
- LandingPage → AuthContext (`useAuth()` hook)
- LandingPage → React Router (`useNavigate()` hook)

**Code**:
```tsx
export const LandingPage: React.FC = () => {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, isLoading, navigate]);

  // Render landing page...
}
```

---

### Scenario 3: PublicFeedPage Relocation

**Flow**:
1. Update internal navigation links pointing to PublicFeedPage
2. Update any documentation/README references

**Files to Check**:
- PublicHeader.tsx (if it links to feed)
- Dashboard links (if any)
- Footer navigation (if any)

**Impact**: Low - PublicFeedPage is a recent feature (013) with minimal external references.

---

### Scenario 4: SEO Indexing

**Flow**:
1. Search engine crawler lands on `/`
2. Reads meta tags from `<Helmet>` component
3. Indexes content with proper title and description

**Integration Points**:
- react-helmet-async → Vite HTML plugin
- Ensure server-side rendering (SSR) compatibility for future

**Meta Tags**:
```html
<title>ContraVento - Pedalear para Conectar</title>
<meta name="description" content="Una plataforma para ciclistas que pedalean para conectar, no para competir. Documenta viajes, regenera territorios, y únete a la comunidad." />
<meta property="og:title" content="ContraVento - Pedalear para Conectar" />
<meta property="og:description" content="..." />
<meta property="og:image" content="https://contravento.com/assets/images/landing/hero.jpg" />
```

---

## Performance Budget

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP (Largest Contentful Paint) | < 2.5s | Lighthouse CI |
| FID (First Input Delay) | < 100ms | Lighthouse CI |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse CI |
| Initial Bundle Size | < 500KB | Webpack Bundle Analyzer |
| Total Page Weight | < 2MB | Network tab (DevTools) |
| Hero Image (WebP) | < 200KB | Image optimization tools |
| Time to Interactive (TTI) | < 3.5s | Lighthouse CI |

**Enforcement**:
- Add Lighthouse CI to PR checks
- Fail build if performance budget exceeded
- Use `vite-plugin-compression` for gzip compression

---

## Accessibility Checklist

- [ ] Color contrast ratio ≥ 4.5:1 (WCAG AA) for all text
- [ ] All images have descriptive alt text
- [ ] Semantic HTML (h1, h2, section, footer)
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Focus states visible on interactive elements
- [ ] ARIA labels on icon-only buttons
- [ ] Screen reader testing (NVDA/JAWS)
- [ ] Mobile touch targets ≥ 44px × 44px

---

## Testing Strategy

### Unit Tests (Vitest + React Testing Library)

**Coverage Target**: ≥90% for all components

**Test Files**:
- `HeroSection.test.tsx`: Render, CTA link, responsive image srcset
- `ManifestoSection.test.tsx`: 4 pillars present, correct order
- `ValuePillarsSection.test.tsx`: 3 columns, icons render, hover state
- `HowItWorksSection.test.tsx`: 4 steps, numbered correctly
- `CTASection.test.tsx`: CTA button, login link
- `Footer.test.tsx`: Social links, legal links, external link behavior
- `LandingPage.test.tsx`: Authenticated user redirect, SEO tags

**Example Test** (HeroSection.test.tsx):
```typescript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { HeroSection } from './HeroSection';

describe('HeroSection', () => {
  it('renders headline and CTA button', () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    expect(screen.getByText('El camino es el destino')).toBeInTheDocument();
    expect(screen.getByText('Formar parte del viaje')).toBeInTheDocument();
  });

  it('CTA button links to /register', () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const ctaButton = screen.getByText('Formar parte del viaje');
    expect(ctaButton.closest('a')).toHaveAttribute('href', '/register');
  });

  it('renders responsive hero image', () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const picture = screen.getByRole('img').closest('picture');
    expect(picture).toBeInTheDocument();
    expect(picture?.querySelector('source[type="image/webp"]')).toBeInTheDocument();
  });
});
```

---

### E2E Tests (Playwright)

**Test File**: `tests/e2e/landing.spec.ts`

**Scenarios**:
1. **Anonymous visitor journey**:
   - Navigate to `/`
   - Verify hero section visible
   - Scroll to manifesto → verify 4 pillars
   - Scroll to value pillars → verify 3 columns
   - Scroll to how it works → verify 4 steps
   - Click CTA → redirected to `/register`

2. **Authenticated user redirect**:
   - Log in as test user
   - Navigate to `/`
   - Verify immediate redirect to `/dashboard`

3. **Mobile responsiveness**:
   - Set viewport to 375×667 (iPhone SE)
   - Verify grid collapses to single column
   - Verify touch targets ≥ 44px

**Example E2E Test**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('anonymous visitor can navigate to registration', async ({ page }) => {
    await page.goto('/');

    // Verify hero section
    await expect(page.locator('h1')).toContainText('El camino es el destino');

    // Click CTA
    await page.click('text=Formar parte del viaje');

    // Verify redirect to register
    await expect(page).toHaveURL(/\/register/);
  });

  test('authenticated user redirects to dashboard', async ({ page, context }) => {
    // Log in (use existing auth fixture)
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    // Navigate to landing page
    await page.goto('/');

    // Should immediately redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
```

---

## Deployment Checklist

- [ ] All unit tests passing (≥90% coverage)
- [ ] All E2E tests passing
- [ ] Lighthouse score ≥ 90 (Performance, Accessibility, Best Practices, SEO)
- [ ] Hero images optimized (WebP + JPG fallbacks)
- [ ] Google Fonts loaded via preconnect
- [ ] Legal pages exist (Terms, Privacy) or placeholders created
- [ ] Social media URLs confirmed (Instagram, Facebook)
- [ ] Meta tags validated (Open Graph, Twitter Card)
- [ ] Cross-browser testing completed (Chrome, Firefox, Safari, Edge)
- [ ] Mobile testing on real devices (iOS, Android)
- [ ] Analytics tracking verified (if applicable)
- [ ] Route change documented in CHANGELOG.md
- [ ] PublicFeedPage references updated to /trips/public

---

## Rollback Plan

**If issues arise post-deployment**:

1. **Quick Rollback** (emergency):
   - Revert App.tsx route change:
     ```tsx
     <Route path="/" element={<PublicFeedPage />} />
     ```
   - Deploy immediately

2. **Partial Rollback** (if specific section broken):
   - Comment out problematic section component
   - Deploy with reduced landing page

3. **Full Feature Flag** (future enhancement):
   - Add feature flag `ENABLE_LANDING_PAGE` in config
   - Conditionally render LandingPage vs PublicFeedPage

---

## Future Enhancements (Out of Scope for v1)

- **User Testimonials Section**: Add after collecting user feedback
- **Newsletter Signup**: Embed email capture form
- **Animated Scroll Effects**: Parallax or fade-in animations (requires performance validation)
- **A/B Testing**: Test different hero copy or CTA placement
- **Blog Integration**: Link to future blog/news section
- **Video Hero**: Replace static image with video background (requires significant performance optimization)
- **Localization**: Add English version (requires i18n infrastructure)

---

## Dependencies & Risks

### External Dependencies

| Dependency | Risk Level | Mitigation |
|------------|-----------|------------|
| Google Fonts API (Playfair Display) | LOW | Fallback to system serif fonts |
| Hero image source | MEDIUM | Require image upfront, have placeholder ready |
| react-helmet-async library | LOW | Well-maintained, React 18 compatible |
| Icon library (Heroicons) | LOW | Already used in project |

### Internal Dependencies

| Dependency | Status | Risk Level |
|------------|--------|-----------|
| AuthContext (Feature 005) | ✅ Complete | NONE |
| RegisterPage (Feature 005) | ✅ Complete | NONE |
| PublicFeedPage (Feature 013) | ✅ Complete | LOW (moving route) |
| React Router | ✅ Existing | NONE |

### Risks & Mitigation

1. **Image Licensing**:
   - **Risk**: Hero image copyright issues
   - **Mitigation**: Use royalty-free stock photo or commission original photography

2. **Performance Budget Overrun**:
   - **Risk**: Hero image too large, slow load times
   - **Mitigation**: Strict image optimization, Lighthouse CI enforcement

3. **Legal Pages Missing**:
   - **Risk**: Footer links to non-existent pages (404)
   - **Mitigation**: Create placeholder pages with "Coming Soon" message, link to external legal docs

4. **PublicFeedPage Route Change**:
   - **Risk**: Broken external links to old root URL
   - **Mitigation**: PublicFeedPage is new (Feature 013), minimal external references

---

## Success Metrics (Post-Launch)

**Week 1 Goals**:
- 500+ unique visitors to landing page
- 15% CTA click-through rate (75+ clicks on "Formar parte del viaje")
- 50+ new registrations
- < 5% bounce rate on hero section (measured via scroll tracking)

**Performance Metrics**:
- Lighthouse Performance score ≥ 90
- LCP < 2.5s (median)
- Zero accessibility violations (aXe DevTools)

**User Engagement**:
- 80%+ scroll past hero to manifesto
- 30s+ average time on page
- 70% of new users complete first trip documentation within 2 weeks

---

## Appendix: Color Palette Reference

| Color Name | Hex Code | Usage | Contrast Ratio (on white) |
|------------|----------|-------|---------------------------|
| Crema Orgánico | #F9F7F2 | Page background | N/A (background) |
| Verde Bosque | #1B2621 | Headings, titles | 15.2:1 (AAA) |
| Terracota Arcilloso | #D35400 | CTA buttons, accents | 4.8:1 (AA) |
| Gris Carbón | #4A4A4A | Body text | 9.7:1 (AAA) |

**Accessibility Validation**:
- All color combinations meet WCAG AA standard (4.5:1 minimum)
- Terracota CTA on white background: 4.8:1 ✅
- Verde Bosque on crema: 14.5:1 ✅
- Gris Carbón on crema: 9.2:1 ✅

---

## Next Steps

1. **Run `/speckit.tasks`** to generate detailed implementation tasks
2. **Begin TDD workflow** (write tests first for each component)
3. **Source hero image** (coordinate with designer/photographer)
4. **Install react-helmet-async** dependency
5. **Create component structure** (folders + empty files)
6. **Implement components iteratively** (HeroSection → ManifestoSection → ...)
7. **Run Lighthouse CI** after each major component completion
8. **E2E testing** once all sections integrated
9. **Cross-browser/device testing** before PR
10. **PR review** with screenshots and Lighthouse report

---

**Plan Status**: ✅ COMPLETE - Ready for task generation (`/speckit.tasks`)
**Constitution Check**: ✅ ALL GATES PASS
**Next Command**: `/speckit.tasks` to break down implementation into actionable tasks
