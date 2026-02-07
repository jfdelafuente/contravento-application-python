# Accessibility Testing

Accessibility (a11y) testing guide for WCAG 2.1 AA compliance.

**Extracted from**: `frontend/TESTING_GUIDE.md` (Phase 3 consolidation)

---

## Table of Contents

- [Overview](#overview)
- [WCAG 2.1 AA Requirements](#wcag-21-aa-requirements)
- [Automated Testing](#automated-testing)
- [Manual Testing](#manual-testing)
- [Screen Reader Testing](#screen-reader-testing)
- [Common Issues](#common-issues)

---

## Overview

ContraVento aims for **WCAG 2.1 Level AA** compliance to ensure the application is accessible to users with disabilities.

**Target Compliance**: WCAG 2.1 AA
**Test Tools**:
- axe-core (automated)
- Screen readers (NVDA, VoiceOver, JAWS)
- Keyboard navigation testing

---

## WCAG 2.1 AA Requirements

### 1. Perceivable

**Text Alternatives (1.1)**:
- ✅ All images have `alt` attributes
- ✅ Decorative images use `alt=""` or `role="presentation"`
- ✅ Form inputs have associated labels

**Color Contrast (1.4.3)**:
- ✅ Normal text: 4.5:1 contrast ratio
- ✅ Large text (18pt+): 3:1 contrast ratio
- ✅ Interactive elements: Sufficient contrast

**Resize Text (1.4.4)**:
- ✅ Text can scale to 200% without loss of functionality
- ✅ No horizontal scrolling at 200% zoom

### 2. Operable

**Keyboard Accessible (2.1)**:
- ✅ All functionality available via keyboard
- ✅ No keyboard traps
- ✅ Logical tab order

**Focus Visible (2.4.7)**:
- ✅ Visible focus indicator on all interactive elements
- ✅ Focus indicator has 3:1 contrast ratio

**Headings and Labels (2.4.6)**:
- ✅ Descriptive page titles
- ✅ Logical heading hierarchy (h1 → h2 → h3)
- ✅ Clear form labels

### 3. Understandable

**Language (3.1.1)**:
- ✅ Page language declared (`<html lang="es">`)

**Error Identification (3.3.1)**:
- ✅ Form errors clearly identified
- ✅ Error messages in text, not just color

**Labels or Instructions (3.3.2)**:
- ✅ Required fields indicated
- ✅ Input format explained (e.g., "DD/MM/AAAA")

### 4. Robust

**Parsing (4.1.1)**:
- ✅ Valid HTML (no duplicate IDs)
- ✅ Proper nesting of elements

**Name, Role, Value (4.1.2)**:
- ✅ ARIA roles used correctly
- ✅ Interactive elements have accessible names

---

## Automated Testing

### axe-core Integration

**Install**:
```bash
npm install --save-dev @axe-core/playwright
```

**Test Example**:
```typescript
// tests/a11y/homepage.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage should not have accessibility violations', async ({ page }) => {
  await page.goto('http://localhost:5173');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

**Run accessibility tests**:
```bash
npx playwright test tests/a11y/
```

---

### Pa11y for CI

**Install**:
```bash
npm install --save-dev pa11y
```

**Configuration** (`pa11y.config.js`):
```javascript
module.exports = {
  standard: 'WCAG2AA',
  runners: [
    'axe',
    'htmlcs'
  ],
  ignore: [
    'notice',  // Ignore notices, focus on warnings and errors
  ]
};
```

**Run**:
```bash
npx pa11y http://localhost:5173
```

---

## Manual Testing

### Keyboard Navigation Checklist

**Test all interactive elements**:
- [ ] Tab through all form fields in logical order
- [ ] Shift+Tab works (reverse navigation)
- [ ] Enter/Space activates buttons
- [ ] Escape closes modals/dialogs
- [ ] Arrow keys work in dropdowns/menus
- [ ] No keyboard traps (can always tab away)

**Example Test**:
```typescript
test('trip form is keyboard navigable', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Tab through form
  await page.keyboard.press('Tab'); // Title
  await expect(page.locator('input[name="title"]')).toBeFocused();

  await page.keyboard.press('Tab'); // Description
  await expect(page.locator('textarea[name="description"]')).toBeFocused();

  // Submit with Enter
  await page.keyboard.press('Tab'); // Submit button
  await page.keyboard.press('Enter');
});
```

---

### Color Contrast Testing

**Tools**:
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools Accessibility Panel

**Manual Check**:
1. Open Chrome DevTools → Accessibility
2. Select element
3. Check "Contrast" section
4. Verify ratio ≥ 4.5:1 (normal text) or ≥ 3:1 (large text)

**Example CSS**:
```css
/* Good contrast (7.4:1) */
.button-primary {
  background: #0066CC; /* Blue */
  color: #FFFFFF;      /* White */
}

/* Bad contrast (2.1:1) - WCAG AA FAIL */
.button-bad {
  background: #CCCCCC; /* Light gray */
  color: #FFFFFF;      /* White */
}
```

---

### Focus Indicator Testing

**Requirements**:
- Visible focus outline on all interactive elements
- Minimum 3:1 contrast ratio against background
- Not removed with `outline: none` without replacement

**Example CSS**:
```css
/* Good: Custom focus indicator with sufficient contrast */
button:focus-visible {
  outline: 3px solid #0066CC;
  outline-offset: 2px;
}

/* Bad: No focus indicator */
button:focus {
  outline: none; /* WCAG AA FAIL */
}
```

---

## Screen Reader Testing

### Test with NVDA (Windows)

**Install**: [NVDA Download](https://www.nvaccess.org/download/)

**Basic Commands**:
- `Insert + Down Arrow` - Read next item
- `Insert + Up Arrow` - Read previous item
- `H` - Navigate by headings
- `K` - Navigate by links
- `F` - Navigate by form fields
- `Tab` - Navigate interactive elements

**Test Checklist**:
- [ ] Page title announced correctly
- [ ] Headings read in logical order (h1 → h2 → h3)
- [ ] Form labels associated with inputs
- [ ] Error messages announced
- [ ] Dynamic content updates announced (aria-live regions)
- [ ] All interactive elements have accessible names

---

### Test with VoiceOver (macOS)

**Enable**: System Preferences → Accessibility → VoiceOver

**Basic Commands**:
- `Cmd + F5` - Toggle VoiceOver
- `Ctrl + Option + Right Arrow` - Next item
- `Ctrl + Option + Left Arrow` - Previous item
- `Ctrl + Option + Cmd + H` - Next heading
- `Ctrl + Option + Space` - Activate element

**Test Script Example**:
```
1. Navigate to homepage
2. VoiceOver announces: "ContraVento - Plataforma ciclista"
3. Tab to login button
4. VoiceOver announces: "Iniciar sesión, button"
5. Activate button
6. VoiceOver announces: "Email, edit text"
7. Type email
8. Tab to password field
9. VoiceOver announces: "Contraseña, secure edit text"
```

---

## Common Issues

### Issue: Images without alt text

**Problem**:
```html
<img src="/photo.jpg" />
```

**Solution**:
```html
<!-- Informative image -->
<img src="/photo.jpg" alt="Vista del valle desde el Mirador" />

<!-- Decorative image -->
<img src="/icon-decorative.svg" alt="" role="presentation" />
```

---

### Issue: Form inputs without labels

**Problem**:
```html
<input type="text" name="username" placeholder="Username" />
```

**Solution**:
```html
<!-- Visible label -->
<label for="username">Username</label>
<input type="text" id="username" name="username" />

<!-- Or aria-label for icon-only inputs -->
<input
  type="search"
  name="query"
  aria-label="Buscar viajes"
  placeholder="Buscar..."
/>
```

---

### Issue: Missing ARIA landmarks

**Problem**:
```html
<div>
  <div>Navigation</div>
  <div>Main content</div>
  <div>Footer</div>
</div>
```

**Solution**:
```html
<header>
  <nav aria-label="Navegación principal">
    ...
  </nav>
</header>

<main>
  <h1>Contenido principal</h1>
  ...
</main>

<footer>
  ...
</footer>
```

---

### Issue: Color-only error indication

**Problem**:
```html
<input type="email" style="border-color: red;" />
<!-- Error only indicated by red border -->
```

**Solution**:
```html
<div>
  <label for="email">Email</label>
  <input
    type="email"
    id="email"
    aria-invalid="true"
    aria-describedby="email-error"
  />
  <div id="email-error" role="alert">
    El email es inválido
  </div>
</div>
```

---

### Issue: Non-descriptive link text

**Problem**:
```html
<a href="/trips/123">Click here</a>
```

**Solution**:
```html
<a href="/trips/123">Ver detalles del viaje "Camino de Santiago"</a>

<!-- Or provide context -->
<div aria-label="Viaje: Camino de Santiago">
  <h3>Camino de Santiago</h3>
  <a href="/trips/123">Ver detalles</a>
</div>
```

---

## Related Documentation

- **[E2E Tests](e2e-tests.md)** - Playwright E2E testing
- **[Component Tests](component-tests.md)** - Component testing
- **[Manual QA](../manual-qa/)** - Manual testing procedures

---

**Last Updated**: 2026-02-06 (Extracted from frontend/TESTING_GUIDE.md)
**WCAG Level**: 2.1 AA
**Tools**: axe-core, Pa11y, NVDA, VoiceOver
