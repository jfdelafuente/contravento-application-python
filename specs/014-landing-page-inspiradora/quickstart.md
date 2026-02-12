# Quickstart Guide: Landing Page Inspiradora

**Feature**: Landing Page Inspiradora (Feature 014)
**Branch**: `014-landing-page-inspiradora`
**Date**: 2026-01-16

## Overview

This guide provides integration scenarios for testing the Landing Page feature after implementation.

## Prerequisites

- Frontend development server running (`npm run dev`)
- Backend server running (for authentication context)
- Test user accounts available (testuser, admin)

## Integration Scenarios

### Scenario 1: Anonymous Visitor Journey

**Test Case**: New visitor discovers ContraVento and registers

**Steps**:

1. **Navigate to landing page**:
   ```bash
   # Open browser to root URL
   http://localhost:5173/
   ```

2. **Verify hero section loads**:
   - [ ] Hero image displays (cinematographic cycling photo)
   - [ ] Headline "El camino es el destino" is visible
   - [ ] Subheadline explains platform philosophy
   - [ ] CTA button "Formar parte del viaje" is prominent

3. **Scroll through sections**:
   - [ ] Manifesto section shows 4 pillars in correct order
   - [ ] Value Pillars grid shows 3 columns (desktop) or stacked (mobile)
   - [ ] How It Works shows 4 numbered steps
   - [ ] Final CTA section with register button
   - [ ] Footer with social links, legal, contact

4. **Click CTA to register**:
   ```
   Click "Formar parte del viaje" button
   → Should redirect to /register
   ```

5. **Complete registration**:
   - Fill registration form
   - Submit
   - Verify email
   - Login

6. **Verify post-registration behavior**:
   ```
   Navigate to http://localhost:5173/
   → Should auto-redirect to /dashboard (user is authenticated)
   ```

**Expected Results**:
- Landing page loads in < 3s on 3G
- All sections render correctly
- CTA redirects to /register
- Authenticated users skip landing page

---

### Scenario 2: Authenticated User Auto-Redirect

**Test Case**: Logged-in user navigating to root URL

**Steps**:

1. **Login as existing user**:
   ```bash
   # Navigate to login page
   http://localhost:5173/login

   # Login credentials
   Username: testuser
   Password: TestPass123!
   ```

2. **Navigate to root URL**:
   ```bash
   http://localhost:5173/
   ```

3. **Verify immediate redirect**:
   - [ ] Landing page should NOT render
   - [ ] Browser redirects to /dashboard
   - [ ] No flash of landing page content (FOUC)

**Expected Results**:
- Redirect happens in < 500ms
- No visible landing page content
- Dashboard loads normally

**Code Reference**: [LandingPage.tsx:771-783](../specs/014-landing-page-inspiradora/plan.md#scenario-2-authenticated-user--auto-redirect)

---

### Scenario 3: Responsive Design Testing

**Test Case**: Landing page adapts to different screen sizes

**Devices to Test**:

| Device Type | Viewport Size | Expected Layout |
|-------------|---------------|-----------------|
| Mobile (iPhone SE) | 375×667 | Single column, stacked |
| Tablet (iPad) | 768×1024 | 2 columns, medium spacing |
| Desktop (Laptop) | 1440×900 | 3 columns, full layout |
| Desktop (4K) | 3840×2160 | Max-width container |

**Steps**:

1. **Mobile Testing** (< 768px):
   ```bash
   # Chrome DevTools: Toggle device toolbar
   # Select iPhone SE preset
   ```
   - [ ] Hero image scales correctly
   - [ ] Value Pillars stack vertically (1 column)
   - [ ] How It Works steps stack vertically
   - [ ] CTA button is touch-friendly (min 44px height)
   - [ ] Text is readable without zooming

2. **Tablet Testing** (768-1024px):
   - [ ] Hero section maintains aspect ratio
   - [ ] Value Pillars show 2 columns
   - [ ] How It Works shows 2 steps per row
   - [ ] Footer stacks to 2 columns

3. **Desktop Testing** (> 1024px):
   - [ ] Hero section full-width with overlay
   - [ ] Value Pillars show 3 columns
   - [ ] How It Works shows 4 steps horizontally
   - [ ] Footer shows 4 columns

**Expected Results**:
- No horizontal scroll on any device
- Text remains readable at all breakpoints
- Touch targets ≥ 44×44px on mobile
- Images scale without distortion

---

### Scenario 4: SEO and Meta Tags Validation

**Test Case**: Search engines can index landing page correctly

**Steps**:

1. **View page source**:
   ```bash
   # Right-click on landing page → View Page Source
   # OR curl and inspect HTML
   curl http://localhost:5173/ | grep -i "meta"
   ```

2. **Verify meta tags present**:
   - [ ] `<title>ContraVento - Pedalear para Conectar</title>`
   - [ ] `<meta name="description" content="Una plataforma para ciclistas que pedalean para conectar...">`
   - [ ] `<meta property="og:title" content="ContraVento - Pedalear para Conectar">`
   - [ ] `<meta property="og:description" content="...">`
   - [ ] `<meta property="og:image" content="...hero.jpg">`
   - [ ] `<meta property="og:type" content="website">`
   - [ ] `<meta name="twitter:card" content="summary_large_image">`

3. **Test Open Graph preview**:
   ```bash
   # Use Facebook Sharing Debugger
   https://developers.facebook.com/tools/debug/

   # Enter URL: https://contravento.com/
   # Verify image, title, description appear
   ```

4. **Verify semantic HTML**:
   - [ ] Proper heading hierarchy (h1 → h2 → h3)
   - [ ] Semantic elements (`<section>`, `<footer>`, `<nav>`)
   - [ ] Alt text on all images

**Expected Results**:
- All meta tags present in HTML source
- Open Graph preview shows hero image
- No heading hierarchy violations
- Images have descriptive alt text

---

### Scenario 5: Performance Validation

**Test Case**: Landing page meets Core Web Vitals targets

**Steps**:

1. **Run Lighthouse audit**:
   ```bash
   # Chrome DevTools → Lighthouse tab
   # Select: Performance, Accessibility, Best Practices, SEO
   # Device: Mobile
   # Run audit
   ```

2. **Verify Core Web Vitals**:
   - [ ] Largest Contentful Paint (LCP) < 2.5s ✅
   - [ ] First Input Delay (FID) < 100ms ✅
   - [ ] Cumulative Layout Shift (CLS) < 0.1 ✅

3. **Check performance metrics**:
   - [ ] Performance Score ≥ 90
   - [ ] Accessibility Score ≥ 90
   - [ ] Best Practices Score ≥ 90
   - [ ] SEO Score ≥ 90

4. **Analyze bundle size**:
   ```bash
   # Build for production
   cd frontend
   npm run build

   # Check dist folder size
   du -sh dist/
   # Should be < 2MB total
   ```

5. **Test on slow network**:
   ```bash
   # Chrome DevTools → Network tab
   # Throttling: Fast 3G
   # Reload page
   # Verify load time < 3s
   ```

**Expected Results**:
- All Core Web Vitals in "Good" range
- Lighthouse scores ≥ 90 across all categories
- Production bundle < 500KB (initial load)
- Total page weight < 2MB

---

### Scenario 6: Accessibility Testing

**Test Case**: Landing page is accessible to all users

**Steps**:

1. **Keyboard navigation**:
   - [ ] Tab through all interactive elements
   - [ ] Focus indicators visible on all focusable elements
   - [ ] CTA buttons activatable with Enter key
   - [ ] Footer links accessible via keyboard

2. **Screen reader testing** (NVDA/JAWS):
   ```bash
   # Windows: Download NVDA (free)
   # Mac: Use VoiceOver (built-in)
   ```
   - [ ] Page structure announced correctly
   - [ ] Headings read in order
   - [ ] Alt text on images descriptive
   - [ ] Links have clear context

3. **Color contrast validation**:
   ```bash
   # Use aXe DevTools browser extension
   # Or WebAIM Contrast Checker
   https://webaim.org/resources/contrastchecker/
   ```
   - [ ] Terracota CTA on white: ≥ 4.5:1 ✅
   - [ ] Verde Bosque titles on crema: ≥ 4.5:1 ✅
   - [ ] Gris Carbón text on crema: ≥ 4.5:1 ✅

4. **ARIA attributes**:
   - [ ] Landmarks used correctly (`<main>`, `<nav>`, `<footer>`)
   - [ ] ARIA labels on icon-only elements
   - [ ] Semantic HTML preferred over ARIA

**Expected Results**:
- All interactive elements keyboard accessible
- Screen reader announces content logically
- Color contrast meets WCAG AA (4.5:1)
- Zero critical accessibility violations

---

### Scenario 7: Cross-Browser Compatibility

**Test Case**: Landing page works on all target browsers

**Browsers to Test**:

| Browser | Version | Expected Result |
|---------|---------|-----------------|
| Chrome | Latest 2 | Full support ✅ |
| Firefox | Latest 2 | Full support ✅ |
| Safari (macOS) | Latest 2 | Full support ✅ |
| Edge | Latest 2 | Full support ✅ |
| Safari (iOS) | Latest | Mobile support ✅ |
| Chrome (Android) | Latest | Mobile support ✅ |

**Steps**:

1. **Test on each browser**:
   - [ ] Hero image displays correctly
   - [ ] Fonts load (Playfair Display)
   - [ ] Responsive breakpoints work
   - [ ] CTA buttons clickable
   - [ ] No console errors

2. **Verify fallbacks**:
   - [ ] WebP images with JPG fallback
   - [ ] Google Fonts with system serif fallback
   - [ ] CSS Grid with flexbox fallback (if needed)

**Expected Results**:
- Consistent rendering across browsers
- No broken layouts
- Fonts load correctly or fallback gracefully
- Zero JavaScript errors

---

### Scenario 8: PublicFeedPage Relocation

**Test Case**: PublicFeedPage accessible at new route

**Steps**:

1. **Verify new route**:
   ```bash
   http://localhost:5173/trips/public
   ```
   - [ ] PublicFeedPage loads correctly
   - [ ] Trip cards display
   - [ ] Pagination works

2. **Check for broken links**:
   ```bash
   # Search for internal references to root route
   cd frontend/src
   grep -r "to=\"/\"" components/ pages/
   # Update any PublicFeedPage links to /trips/public
   ```

3. **Update PublicHeader** (if exists):
   ```typescript
   // Check if PublicHeader links to feed
   // Update link from "/" to "/trips/public"
   <Link to="/trips/public">Explorar Viajes</Link>
   ```

**Expected Results**:
- PublicFeedPage works at /trips/public
- No broken links to old root route
- Navigation updated to new route

---

## Manual Testing Checklist

Before marking feature complete, verify:

### Functional Requirements

- [ ] FR-001: Landing page accessible at / without auth
- [ ] FR-002: Hero image 1920×1080+, optimized
- [ ] FR-003: Headline uses Playfair Display serif
- [ ] FR-004: Manifesto shows 4 pillars in order
- [ ] FR-005: Value Pillars shows 3 columns
- [ ] FR-006: How It Works shows 4 steps
- [ ] FR-007: CTA visible in hero + final section
- [ ] FR-008: CTA uses terracota #D35400, contrast ≥4.5:1
- [ ] FR-009: Footer has social, legal, contact links
- [ ] FR-010: Responsive at 768px, 1024px breakpoints
- [ ] FR-011: Color palette matches spec
- [ ] FR-012: Tone is inspirador, ético, pausado
- [ ] FR-013: CTA redirects to /register
- [ ] FR-014: Authenticated users redirect to /dashboard
- [ ] FR-015: Images use WebP + JPG fallback
- [ ] FR-016: Loads in < 3s on 3G
- [ ] FR-017: SEO meta tags present

### Success Criteria

- [ ] SC-001: Visitors understand value prop in < 10s
- [ ] SC-002: Conversion rate increase (track post-launch)
- [ ] SC-003: 80%+ visitors scroll past hero
- [ ] SC-004: Avg time on page ≥ 30s
- [ ] SC-005: Core Web Vitals "Good" (LCP, FID, CLS)
- [ ] SC-006: 90%+ mobile visitors don't zoom
- [ ] SC-007: Color contrast ≥ 4.5:1 (WCAG AA)
- [ ] SC-008: CTA clicked by 15%+ visitors (track)
- [ ] SC-009: 50+ registrations week 1 (track)
- [ ] SC-010: 70% complete first trip in 2 weeks (track)

---

## Troubleshooting

### Issue: Hero image not loading

**Symptoms**: Broken image icon, console error 404

**Solution**:
```bash
# Verify images exist
ls frontend/src/assets/images/landing/
# Should see: hero.jpg, hero.webp, hero-mobile.jpg, hero-mobile.webp

# Check import path in HeroSection.tsx
# Ensure path matches: /assets/images/landing/hero.jpg
```

---

### Issue: Fonts not loading (Playfair Display)

**Symptoms**: Fallback serif font used (Georgia, Times New Roman)

**Solution**:
```html
<!-- Add to index.html <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
```

---

### Issue: Authenticated user sees landing page briefly

**Symptoms**: FOUC (Flash of Unstyled Content), landing page flickers before redirect

**Solution**:
```typescript
// In LandingPage.tsx, add loading state
const { user, isLoading } = useAuth();

if (isLoading) {
  return <div className="loading">Cargando...</div>;
}

if (user) {
  navigate('/dashboard', { replace: true });
  return null; // Prevent render
}
```

---

### Issue: Lighthouse performance score < 90

**Common Causes**:
- Hero image too large (> 200KB WebP)
- Fonts not preloaded
- JavaScript bundle too large

**Solutions**:
```bash
# Optimize hero image
npx @squoosh/cli --webp auto frontend/src/assets/images/landing/hero.jpg

# Preload critical fonts in index.html
<link rel="preload" href="https://fonts.gstatic.com/..." as="font" crossorigin>

# Analyze bundle size
npm run build
npx vite-bundle-visualizer
```

---

## Analytics Tracking

To measure Success Criteria, configure event tracking:

```typescript
// Add to LandingPage.tsx (if analytics configured)
import { trackEvent } from '../utils/analytics';

// Track scroll depth
const handleScroll = () => {
  const scrollPercentage = (window.scrollY / document.body.scrollHeight) * 100;
  if (scrollPercentage > 75) {
    trackEvent('landing_page_scroll', { depth: '75%' });
  }
};

// Track CTA clicks
const handleCTAClick = () => {
  trackEvent('landing_page_cta_click', { location: 'hero' });
};
```

**Events to Track**:
- `landing_page_view`: Page view
- `landing_page_scroll`: Scroll depth (25%, 50%, 75%, 100%)
- `landing_page_cta_click`: CTA button clicks (location: hero/final)
- `landing_page_exit`: Exit without clicking CTA

---

## Post-Launch Monitoring

**Week 1 Goals**:
- 500+ unique visitors
- 15% CTA click-through rate
- 50+ new registrations
- < 5% bounce rate on hero

**Dashboards**:
- Google Analytics: Traffic, bounce rate, session duration
- Lighthouse CI: Performance trends
- Sentry: Error tracking
- Hotjar/LogRocket: Session recordings (optional)

---

## Next Steps After Testing

1. **Create PR** with:
   - Screenshots of all sections (mobile + desktop)
   - Lighthouse report (all scores ≥ 90)
   - Test coverage report (≥ 90%)
   - Cross-browser test results

2. **Code review checklist**:
   - All tests passing
   - No console errors/warnings
   - TypeScript type checking passes
   - ESLint zero warnings
   - Accessibility audit clean

3. **Deploy to staging**:
   ```bash
   ./deploy.sh staging
   # Test on staging URL before production
   ```

4. **Production deployment**:
   ```bash
   ./deploy.sh prod
   # Monitor analytics and error logs
   ```

5. **Post-launch tasks**:
   - Monitor Lighthouse scores daily (first week)
   - Track conversion metrics
   - Collect user feedback
   - A/B test CTA copy (future)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-16
**Maintained By**: ContraVento Development Team
