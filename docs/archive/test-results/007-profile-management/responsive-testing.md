# T073: Responsive Testing - Profile Management

## Objetivo

Verificar que la página de edición de perfil (ProfileEditPage) y todos sus componentes funcionen correctamente en diferentes tamaños de pantalla: desktop, tablet, y mobile.

## Dispositivos y Breakpoints de Prueba

### 1. Desktop (≥ 968px)
- **Resolución típica**: 1920x1080, 1440x900, 1366x768
- **Navegadores**: Chrome, Firefox, Edge, Safari
- **Características esperadas**:
  - Layout de 2 columnas para Basic Info + Photo Upload
  - Full width para Password Change y Privacy Settings
  - Espaciado completo (padding: var(--space-8))
  - Títulos en tamaño var(--text-3xl)
  - Botones con max-width: 300px centrados

### 2. Tablet (768px - 968px)
- **Resolución típica**: iPad (768x1024), iPad Air (820x1180)
- **Navegadores**: Chrome, Safari, Firefox
- **Características esperadas**:
  - Layout de 1 columna para todas las secciones
  - Padding reducido (var(--space-6))
  - Títulos en tamaño var(--text-2xl)
  - Header flexible con gap: var(--space-4)

### 3. Mobile (480px - 768px)
- **Resolución típica**: iPhone 12/13 (390x844), Samsung Galaxy S21 (360x800)
- **Navegadores**: Chrome Mobile, Safari iOS, Firefox Mobile
- **Características esperadas**:
  - Layout de 1 columna
  - Padding mínimo (var(--space-4) a var(--space-2))
  - Width 95% en wrapper
  - Títulos en tamaño var(--text-2xl)
  - Botones de foto en columna (vertical stack)

### 4. Small Mobile (<480px)
- **Resolución típica**: iPhone SE (375x667), Android pequeños (360x640)
- **Características esperadas**:
  - Width 100% en wrapper
  - Padding muy reducido (var(--space-3))
  - Títulos en tamaño var(--text-xl)
  - Font-size reducido a var(--text-sm) en inputs

---

## Checklist de Pruebas por Componente

### ProfileEditPage (Contenedor Principal)

#### Desktop (≥968px)
- [ ] El contenedor principal tiene `max-width: 1200px` centrado
- [ ] El header muestra título y botón "Cancelar" en la misma línea
- [ ] El padding del page es `var(--space-6) var(--space-4)`
- [ ] El wrapper de contenido usa `width: 100%` con `padding: var(--space-8)`
- [ ] Primera fila (Basic Info + Photo) se muestra en 2 columnas iguales
- [ ] Segunda fila (Password) ocupa el ancho completo
- [ ] Tercera fila (Privacy) ocupa el ancho completo
- [ ] Gap entre secciones es `var(--space-6)`

#### Tablet (768px-968px)
- [ ] Todas las filas cambian a 1 columna (grid-template-columns: 1fr)
- [ ] El contenedor principal mantiene `max-width: 1200px` pero usa todo el ancho disponible
- [ ] Padding y espaciado se mantienen legibles

#### Mobile (<768px)
- [ ] El header cambia a `flex-direction: column` con alineación `flex-start`
- [ ] Título reduce a `var(--text-2xl)`
- [ ] El wrapper cambia a `width: 95%`
- [ ] Padding del page reduce a `var(--space-4) var(--space-2)`
- [ ] Padding del wrapper reduce a `var(--space-6) 0`
- [ ] Section content reduce padding a `var(--space-4)`
- [ ] Section actions reduce padding a `var(--space-3) var(--space-4)`

#### Small Mobile (<480px)
- [ ] Título reduce a `var(--text-xl)`
- [ ] Wrapper cambia a `width: 100%`
- [ ] Section content reduce padding a `var(--space-3)`

---

### BasicInfoSection

#### Desktop
- [ ] Padding del section: `var(--space-6)`
- [ ] Título en `var(--text-2xl)`
- [ ] Form groups con `margin-bottom: var(--space-6)`
- [ ] Inputs con padding completo `var(--space-3) var(--space-4)`
- [ ] Font-size de inputs: `var(--text-base)`
- [ ] Character counter visible y alineado a la derecha

#### Tablet (768px)
- [ ] Padding reduce a `var(--space-5)`
- [ ] Título reduce a `var(--text-xl)`
- [ ] Form groups con `margin-bottom: var(--space-5)`
- [ ] Inputs mantienen tamaño legible

#### Mobile (<768px)
- [ ] Padding reduce a `var(--space-5)` (igual que tablet)
- [ ] Inputs se ajustan al ancho disponible sin overflow

#### Small Mobile (<480px)
- [ ] Padding reduce a `var(--space-4)`
- [ ] Inputs reducen font-size a `var(--text-sm)`
- [ ] Select y textarea también reducen a `var(--text-sm)`
- [ ] Labels se mantienen legibles

---

### PhotoUploadSection

#### Desktop
- [ ] Photo preview/placeholder: 200px x 200px circular
- [ ] Placeholder icon: 64px x 64px
- [ ] Botones "Cambiar foto" y "Eliminar foto" en fila horizontal
- [ ] Gap entre botones: `var(--space-4)`
- [ ] Botones con padding `var(--space-3) var(--space-6)`

#### Mobile (<640px)
- [ ] Photo preview/placeholder reduce a 160px x 160px
- [ ] Placeholder icon reduce a 48px x 48px
- [ ] Botones cambian a `flex-direction: column`
- [ ] Gap entre botones reduce a `var(--space-3)`
- [ ] Botones ocupan `width: 100%` y se centran
- [ ] Section padding reduce a `var(--space-4)`

#### Verificaciones Adicionales
- [ ] Progress bar se ajusta al 100% del ancho en todos los tamaños
- [ ] Error messages no causan overflow horizontal
- [ ] Help text se mantiene centrado y legible

---

### PasswordChangeSection

#### Desktop
- [ ] Section padding: `var(--space-6)`
- [ ] Password toggle button alineado correctamente a la derecha
- [ ] Password strength bar ocupa 100% del ancho disponible
- [ ] Requirements list con gap: `var(--space-2)`
- [ ] Requirements container con padding `var(--space-4)`

#### Mobile (<640px)
- [ ] Section padding reduce a `var(--space-4)`
- [ ] Requirements padding reduce a `var(--space-3)`
- [ ] Requirements list font-size reduce a `var(--text-xs)`
- [ ] Password toggle button se mantiene visible y clickeable

#### Verificaciones Adicionales
- [ ] Password toggle no interfiere con el texto del input
- [ ] Strength bar (weak/medium/strong) se visualiza correctamente
- [ ] Checkmarks (✓) y círculos (○) se muestran correctamente
- [ ] No hay overflow horizontal en los labels largos

---

### PrivacySettingsSection

#### Desktop
- [ ] Radio groups se muestran correctamente con iconos SVG
- [ ] Íconos SVG tienen tamaño apropiado (definido en `.radio-icon`)
- [ ] Espaciado entre radio options es adecuado
- [ ] Descriptions (radio-help) se leen sin truncamiento

#### Mobile
- [ ] Radio options apilan verticalmente sin problemas
- [ ] Íconos SVG mantienen proporciones
- [ ] Radio labels y descriptions se ajustan al ancho
- [ ] No hay overflow horizontal

#### Verificaciones Adicionales
- [ ] Radio buttons son fáciles de clickear en móvil (área táctil ≥44x44px)
- [ ] Focus states son visibles en todos los tamaños
- [ ] Error messages no causan layout shift

---

## Procedimiento de Prueba

### 1. Prueba con Chrome DevTools

```bash
# Abrir Chrome DevTools
F12 o Ctrl+Shift+I (Windows/Linux)
Cmd+Opt+I (Mac)

# Activar "Device Toolbar"
Ctrl+Shift+M (Windows/Linux)
Cmd+Shift+M (Mac)

# Dispositivos a probar:
- iPhone SE (375x667) - Small Mobile
- iPhone 12 Pro (390x844) - Mobile
- iPad Air (820x1180) - Tablet
- Desktop (1920x1080) - Desktop

# Para cada dispositivo:
1. Navegar a http://localhost:5173/profile/edit
2. Verificar layout (columnas, espaciado, padding)
3. Verificar font sizes (títulos, labels, inputs)
4. Verificar que no hay overflow horizontal (scroll horizontal)
5. Verificar que todos los botones son clickeables
6. Verificar que todos los inputs son editables
7. Verificar que los mensajes de error se muestran correctamente
```

### 2. Prueba con Firefox Responsive Design Mode

```bash
# Abrir Responsive Design Mode
Ctrl+Shift+M (Windows/Linux)
Cmd+Opt+M (Mac)

# Presets a probar:
- iPhone 12/13 (390x844)
- Galaxy S20 (360x800)
- iPad (768x1024)
- Desktop (1920x1080)

# Repetir checklist anterior
```

### 3. Prueba en Dispositivos Reales (Opcional pero Recomendado)

#### iOS (iPhone/iPad)
```bash
# Requisitos:
- Asegurar que el frontend esté accesible en la red local
- Usar la IP local en lugar de localhost

# En el terminal del frontend:
npm run dev -- --host

# Acceder desde el dispositivo iOS:
http://[TU_IP_LOCAL]:5173/profile/edit

# Ejemplo:
http://192.168.1.100:5173/profile/edit
```

#### Android
```bash
# Similar a iOS:
npm run dev -- --host

# Acceder desde el dispositivo Android:
http://[TU_IP_LOCAL]:5173/profile/edit
```

### 4. Prueba de Rotación de Pantalla

- [ ] En tablet, rotar de portrait a landscape y verificar layout
- [ ] En móvil, rotar de portrait a landscape y verificar layout
- [ ] Verificar que no hay contenido cortado después de rotación

---

## Problemas Comunes y Soluciones

### 1. Overflow Horizontal en Mobile

**Síntoma**: Aparece scroll horizontal en móvil

**Causas posibles**:
- Padding/margin excesivos
- Width fijos en píxeles en lugar de porcentajes
- `max-width` muy grandes
- Imágenes sin `max-width: 100%`

**Solución**:
```css
/* Añadir en el componente afectado */
* {
  box-sizing: border-box;
}

.container {
  max-width: 100%;
  overflow-x: hidden;
}
```

### 2. Botones Pequeños en Mobile

**Síntoma**: Botones difíciles de clickear en pantalla táctil

**Solución**: Asegurar que los botones tengan al menos 44x44px de área táctil
```css
@media (max-width: 640px) {
  .btn {
    min-height: 44px;
    padding: var(--space-3) var(--space-4);
  }
}
```

### 3. Texto Truncado

**Síntoma**: Texto cortado o con puntos suspensivos no deseados

**Solución**:
```css
.text-container {
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
```

### 4. Layout Roto en Tablet

**Síntoma**: Layout no cambia correctamente en breakpoint 968px

**Verificación**: Revisar que los media queries estén en el orden correcto (mobile-first)

---

## Métricas de Éxito

### Funcionalidad
- [ ] **100%** de los componentes se renderizan correctamente en todos los tamaños
- [ ] **0** errores de overflow horizontal
- [ ] **100%** de los botones son clickeables en móvil (área táctil ≥44x44px)
- [ ] **100%** de los inputs son editables en todos los dispositivos

### Usabilidad
- [ ] Tiempo de carga < 3s en conexión 3G simulada
- [ ] Font-sizes legibles (≥14px body text en móvil)
- [ ] Contraste de color ≥4.5:1 (WCAG AA)
- [ ] Espaciado táctil entre elementos ≥8px

### Performance
- [ ] Lighthouse Mobile Score ≥ 90
- [ ] Lighthouse Desktop Score ≥ 95
- [ ] First Contentful Paint < 2s
- [ ] Cumulative Layout Shift (CLS) < 0.1

---

## Resultado de Pruebas

### Desktop (≥968px) - 1920x1080
**Fecha**: _____________________
**Navegador**: Chrome/Firefox/Safari/Edge

- [ ] Layout 2 columnas funciona correctamente
- [ ] Espaciado y padding apropiados
- [ ] Botones centrados con max-width
- [ ] No hay overflow

**Notas**: ___________________________________________

---

### Tablet (768px-968px) - iPad Air
**Fecha**: _____________________
**Navegador**: Chrome/Safari

- [ ] Layout 1 columna funciona correctamente
- [ ] Espaciado reducido apropiadamente
- [ ] Botones y campos editables
- [ ] No hay overflow

**Notas**: ___________________________________________

---

### Mobile (480px-768px) - iPhone 12 Pro
**Fecha**: _____________________
**Navegador**: Safari iOS/Chrome Mobile

- [ ] Layout 1 columna funciona correctamente
- [ ] Header apila verticalmente
- [ ] Botones de foto apilan verticalmente
- [ ] Font-sizes legibles
- [ ] No hay overflow

**Notas**: ___________________________________________

---

### Small Mobile (<480px) - iPhone SE
**Fecha**: _____________________
**Navegador**: Safari iOS

- [ ] Layout funciona con width: 100%
- [ ] Padding mínimo pero legible
- [ ] Font-sizes reducidos pero legibles
- [ ] No hay overflow

**Notas**: ___________________________________________

---

## Breakpoints Implementados

### ProfileEditPage.css

```css
/* Tablet: 968px */
@media (max-width: 968px) {
  .profile-edit-row {
    grid-template-columns: 1fr; /* 2 columnas → 1 columna */
  }
}

/* Mobile: 768px */
@media (max-width: 768px) {
  .profile-edit-page {
    padding: var(--space-4) var(--space-2);
  }

  .profile-edit-header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: flex-start;
  }

  .profile-edit-title {
    font-size: var(--text-2xl);
  }

  .profile-edit-content-wrapper {
    width: 95%;
    padding: var(--space-6) 0;
  }

  .section-content {
    padding: var(--space-4);
  }

  .section-actions {
    padding: var(--space-3) var(--space-4);
  }
}

/* Small Mobile: 480px */
@media (max-width: 480px) {
  .profile-edit-title {
    font-size: var(--text-xl);
  }

  .profile-edit-content-wrapper {
    width: 100%;
  }

  .section-content {
    padding: var(--space-3);
  }
}
```

### BasicInfoSection.css

```css
/* Tablet: 768px */
@media (max-width: 768px) {
  .basic-info-section {
    padding: var(--space-5);
  }

  .section-title {
    font-size: var(--text-xl);
  }

  .form-group {
    margin-bottom: var(--space-5);
  }
}

/* Small Mobile: 480px */
@media (max-width: 480px) {
  .basic-info-section {
    padding: var(--space-4);
  }

  .form-input,
  .form-select,
  .form-textarea {
    font-size: var(--text-sm);
  }
}
```

### PhotoUploadSection.css

```css
/* Mobile: 640px */
@media (max-width: 640px) {
  .photo-preview,
  .photo-preview-placeholder {
    width: 160px;
    height: 160px;
  }

  .photo-placeholder-icon {
    width: 48px;
    height: 48px;
  }

  .photo-actions {
    flex-direction: column;
    gap: var(--space-3);
  }

  .btn-change-photo,
  .btn-remove-photo {
    width: 100%;
    justify-content: center;
  }

  .photo-upload-section {
    padding: var(--space-4);
  }
}
```

### PasswordChangeSection.css

```css
/* Mobile: 640px */
@media (max-width: 640px) {
  .password-change-section {
    padding: var(--space-4);
  }

  .password-requirements {
    padding: var(--space-3);
  }

  .requirements-list {
    font-size: var(--text-xs);
  }
}
```

---

## Herramientas de Testing

### Chrome DevTools
- **Device Toolbar**: Simular diferentes dispositivos
- **Network Throttling**: Simular conexiones 3G/4G
- **Lighthouse**: Auditoría de performance y accesibilidad

### Firefox Developer Tools
- **Responsive Design Mode**: Simular breakpoints
- **Screenshot**: Capturar pantallas de diferentes tamaños

### Navegadores para Pruebas
- Chrome (Desktop/Mobile)
- Firefox (Desktop/Mobile)
- Safari (Desktop/iOS)
- Edge (Desktop)

### Herramientas Online
- **BrowserStack**: Pruebas en dispositivos reales remotos
- **LambdaTest**: Testing cross-browser
- **Responsively App**: Visualizar múltiples breakpoints simultáneamente

---

## Comandos Útiles

### Iniciar Frontend con Host Exposed

```bash
cd frontend
npm run dev -- --host

# Output esperado:
# ➜  Local:   http://localhost:5173/
# ➜  Network: http://192.168.1.100:5173/
```

### Lighthouse CI (Performance Testing)

```bash
# Instalar Lighthouse CI
npm install -g @lhci/cli

# Ejecutar audit
lhci autorun --collect.url=http://localhost:5173/profile/edit
```

### Simular 3G en Chrome DevTools

```javascript
// Network Panel → Online → Slow 3G
// Throttling: Download: 400 Kbps, Upload: 400 Kbps, Latency: 400ms
```

---

## Referencias

- [MDN - Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Web.dev - Responsive Web Design Basics](https://web.dev/responsive-web-design-basics/)
- [WCAG 2.1 - Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [Chrome DevTools - Device Mode](https://developer.chrome.com/docs/devtools/device-mode/)

---

## Checklist Final

- [ ] Todas las pruebas de desktop completadas
- [ ] Todas las pruebas de tablet completadas
- [ ] Todas las pruebas de mobile completadas
- [ ] Todas las pruebas de small mobile completadas
- [ ] Lighthouse Mobile Score ≥ 90
- [ ] Lighthouse Desktop Score ≥ 95
- [ ] No hay overflow horizontal en ningún tamaño
- [ ] Todos los botones son clickeables (área táctil ≥44x44px)
- [ ] Todos los inputs son editables
- [ ] Rotación de pantalla funciona correctamente
- [ ] Documentación actualizada con resultados

---

**Última actualización**: 2026-01-10
**Responsable**: Claude Code
**Estado**: ✅ Documento de testing creado - Pendiente ejecución de pruebas
