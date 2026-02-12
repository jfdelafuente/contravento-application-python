# Sistema de Diseño - ContraVento
## Estética Rústica de Viajes

**Última actualización**: 2026-01-09
**Versión**: 1.0.0
**Tema**: Rustic Travel Aesthetic (Estética Rústica de Viajes)

---

## Filosofía de Diseño

ContraVento utiliza una estética **rústica y moderna** inspirada en diarios de viaje, que evoca:
- Aventura al aire libre y ciclismo
- Calidez y naturaleza
- Elegancia clásica con toques contemporáneos
- Materiales naturales (madera, cuero, papel envejecido)

---

## Paleta de Colores

### Colores Primarios

```css
/* Verde Oliva - Color principal de marca */
--color-primary: #6B8E23;        /* Olive green */
--color-primary-light: #8FBC8F;  /* Light sea green */
--color-primary-dark: #556B2F;   /* Dark olive green */
```

### Colores Secundarios

```css
/* Marrón Silla - Acento */
--color-secondary: #8B4513;      /* Saddle brown */
--color-secondary-light: #A0522D; /* Sienna */
--color-secondary-dark: #654321;  /* Dark brown */
```

### Tonos Tierra

```css
/* Camel/Tan - Acentos y bordes */
--color-earth: #C19A6B;          /* Camel/tan */
--color-earth-light: #D2B48C;    /* Tan */
--color-earth-dark: #8B7355;     /* Burlywood dark */
```

### Tonos Crema

```css
/* Crema - Fondos */
--color-cream: #FFF8DC;          /* Cornsilk */
--color-cream-light: #FFFAF0;    /* Floral white */
--color-cream-dark: #F5DEB3;     /* Wheat */
```

### Verdes Naturales

```css
/* Bosque y Musgo */
--color-forest: #2F4F2F;         /* Dark slate gray green */
--color-moss: #8A9A5B;           /* Moss green */
```

### Neutrales

```css
/* Escala de grises con tono cálido */
--color-white: #FFFFFF;
--color-off-white: #FAFAF8;
--color-gray-100: #F5F5F0;
--color-gray-200: #E8E8E0;
--color-gray-300: #D1D1C7;
--color-gray-400: #A8A89E;
--color-gray-500: #6B6B61;
--color-gray-600: #4A4A42;
--color-gray-700: #2C2C26;
--color-gray-800: #1A1A16;
--color-black: #0F0F0D;
```

### Colores Semánticos

```css
/* Estados de la aplicación */
--color-success: #6B8E23;        /* Olive green */
--color-success-light: #E8F5E9;
--color-warning: #D4A574;        /* Tan/amber */
--color-warning-light: #FFF4E6;
--color-error: #A0522D;          /* Sienna */
--color-error-light: #FFE8E8;
```

---

## Tipografía

### Fuentes

```css
/* Fuentes de Google Fonts */
--font-serif: 'Merriweather', 'Georgia', 'Times New Roman', serif;
--font-sans: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
--font-display: 'Playfair Display', 'Georgia', serif;
```

**Importación en HTML**:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:wght@400;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
```

### Jerarquía Tipográfica

| Uso | Fuente | Tamaño | Peso |
|-----|--------|--------|------|
| **Títulos principales** (h1) | Playfair Display | 3rem (48px) | 700 |
| **Títulos secundarios** (h2) | Merriweather | 2.25rem (36px) | 700 |
| **Subtítulos** (h3) | Merriweather | 1.875rem (30px) | 700 |
| **Encabezados** (h4-h6) | Merriweather | Variable | 700 |
| **Cuerpo de texto** | Inter | 1rem (16px) | 400 |
| **Etiquetas/Labels** | Inter | 0.875rem (14px) | 600 |

### Tamaños de Texto

```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */
```

---

## Espaciado

Sistema de espaciado consistente basado en múltiplos de 4px:

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

---

## Bordes y Radios

```css
--radius-sm: 0.25rem;  /* 4px - botones pequeños */
--radius-md: 0.5rem;   /* 8px - elementos estándar */
--radius-lg: 0.75rem;  /* 12px - tarjetas pequeñas */
--radius-xl: 1rem;     /* 16px - tarjetas medianas */
--radius-2xl: 1.5rem;  /* 24px - tarjetas grandes */
--radius-full: 9999px; /* badges circulares */
```

**Grosor de bordes**: Usar `2px` para bordes principales (consistencia visual)

---

## Sombras

Sombras suaves y orgánicas con tonos cálidos:

```css
/* Color base de sombra: rgba(75, 70, 60, ...) */
--shadow-sm: 0 2px 4px rgba(75, 70, 60, 0.08);
--shadow-md: 0 4px 12px rgba(75, 70, 60, 0.12);
--shadow-lg: 0 8px 24px rgba(75, 70, 60, 0.15);
--shadow-xl: 0 16px 40px rgba(75, 70, 60, 0.2);
```

---

## Transiciones

```css
--transition-fast: 150ms ease-in-out;
--transition-base: 250ms ease-in-out;
--transition-slow: 350ms ease-in-out;
```

---

## Patrones de Diseño

### 1. Gradientes

**Gradiente diagonal de encabezado**:
```css
background: linear-gradient(135deg,
  var(--color-primary) 0%,
  var(--color-forest) 100%
);
```

**Gradiente de fondo de página**:
```css
background: linear-gradient(135deg,
  var(--color-cream) 0%,
  var(--color-cream-light) 50%,
  var(--color-gray-100) 100%
);
```

**Gradiente de botón**:
```css
background: linear-gradient(135deg,
  var(--color-primary) 0%,
  var(--color-primary-dark) 100%
);
```

### 2. Texturas

**Overlay de textura diagonal**:
```css
.page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(139, 115, 85, 0.02) 10px,
      rgba(139, 115, 85, 0.02) 20px
    );
  pointer-events: none;
}
```

### 3. Clip-path Diagonal

**Acento diagonal en encabezados**:
```css
.header::after {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 0;
  right: 0;
  height: 30px;
  background: var(--color-white);
  clip-path: polygon(0 50%, 100% 0, 100% 100%, 0% 100%);
}
```

### 4. Efectos Hover

**Elevación de botones**:
```css
.button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
  background: linear-gradient(135deg,
    var(--color-primary-dark) 0%,
    var(--color-forest) 100%
  );
}
```

**Desplazamiento horizontal de items**:
```css
.info-item:hover {
  background: var(--color-cream-light);
  border-color: var(--color-earth);
  transform: translateX(4px);
}
```

---

## Animaciones

### SlideUp
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Uso */
animation: slideUp 0.6s ease-out;
```

### SlideDown
```css
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Uso */
animation: slideDown 0.3s ease-out;
```

### Spin (para loaders)
```css
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Uso */
animation: spin 1s linear infinite;
```

---

## Componentes

### Botones

**Primario (Principal)**:
```css
.button-primary {
  padding: var(--space-5) var(--space-8);
  background: linear-gradient(135deg,
    var(--color-primary) 0%,
    var(--color-primary-dark) 100%
  );
  color: var(--color-cream);
  border: 2px solid var(--color-primary-dark);
  border-radius: var(--radius-lg);
  font-family: var(--font-sans);
  font-size: var(--text-lg);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
}
```

**Secundario**:
```css
.button-secondary {
  background: var(--color-white);
  color: var(--color-secondary);
  border: 2px solid var(--color-secondary);
}

.button-secondary:hover {
  background: var(--color-secondary);
  color: var(--color-cream);
}
```

### Inputs

```css
.input {
  width: 100%;
  padding: var(--space-4) var(--space-5);
  border: 2px solid var(--color-earth-light);
  border-radius: var(--radius-lg);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-gray-700);
  background: var(--color-white);
  transition: all var(--transition-base);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--color-cream);
  box-shadow: 0 0 0 3px rgba(107, 142, 35, 0.1);
}

.input::placeholder {
  color: var(--color-gray-400);
}
```

### Labels

```css
.label {
  display: block;
  margin-bottom: var(--space-2);
  font-family: var(--font-sans);
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--color-forest);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### Tarjetas (Cards)

```css
.card {
  background: var(--color-white);
  padding: var(--space-8);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  border: 2px solid var(--color-earth-light);
  animation: slideUp 0.6s ease-out;
}
```

### Badges

**Verificado**:
```css
.verified-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-primary-dark);
  background: var(--color-success-light);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 600;
  border: 1px solid var(--color-primary);
}
```

**No verificado**:
```css
.unverified-badge {
  color: var(--color-secondary);
  background: var(--color-warning-light);
  border: 1px solid var(--color-warning);
}
```

### Banners (Mensajes)

**Éxito**:
```css
.success-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  background: var(--color-success-light);
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-lg);
  color: var(--color-forest);
  animation: slideDown 0.3s ease-out;
}
```

**Error**:
```css
.error-banner {
  background: var(--color-error-light);
  border: 2px solid var(--color-error);
  color: var(--color-secondary-dark);
}
```

**Advertencia**:
```css
.warning-banner {
  background: var(--color-warning-light);
  border: 2px solid var(--color-warning);
  color: var(--color-secondary);
}
```

---

## Layout de Páginas

### Estructura Base

```css
.page {
  min-height: 100vh;
  background: linear-gradient(135deg,
    var(--color-cream) 0%,
    var(--color-cream-light) 50%,
    var(--color-gray-100) 100%
  );
  position: relative;
}

.page::before {
  /* Textura diagonal (ver patrón arriba) */
}
```

### Header

```css
.header {
  background: linear-gradient(135deg,
    var(--color-primary) 0%,
    var(--color-forest) 100%
  );
  color: var(--color-cream);
  padding: var(--space-8) var(--space-8);
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 1;
}

.header h1 {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--color-cream);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
```

### Contenedor Centrado

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-10) var(--space-8);
}
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile */
@media (max-width: 640px) { }

/* Tablet */
@media (max-width: 768px) { }

/* Desktop pequeño */
@media (max-width: 1024px) { }
```

### Patrones Responsive

**Reducir padding en móvil**:
```css
@media (max-width: 640px) {
  .container {
    padding: var(--space-6) var(--space-4);
  }
}
```

**Cambiar dirección de flex**:
```css
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
    text-align: center;
  }
}
```

---

## Estados de Componentes

### Botones

```css
/* Normal */
.button { }

/* Hover */
.button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* Active */
.button:active:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Disabled */
.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--color-gray-400);
  border-color: var(--color-gray-500);
}
```

### Inputs

```css
/* Error */
.input.error {
  border-color: var(--color-error);
  background: var(--color-error-light);
}

/* Success */
.input.success {
  border-color: var(--color-primary);
  background: var(--color-success-light);
}
```

---

## Iconografía

- **Tamaño estándar**: 1.5rem (24px)
- **Tamaño pequeño**: 1.25rem (20px)
- **Tamaño grande**: 3rem+ (48px+)
- **Color**: Heredar del padre o usar colores semánticos

---

## Scrollbar Personalizada

```css
::-webkit-scrollbar {
  width: 12px;
}

::-webkit-scrollbar-track {
  background: var(--color-cream-dark);
}

::-webkit-scrollbar-thumb {
  background: var(--color-earth);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-earth-dark);
}
```

---

## Accesibilidad

### Contraste de Color

Todos los textos cumplen con WCAG AA:
- **Texto normal**: Ratio mínimo 4.5:1
- **Texto grande**: Ratio mínimo 3:1

### Focus States

```css
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Checkboxes Personalizados

```css
input[type="checkbox"] {
  accent-color: var(--color-primary);
}
```

---

## Archivos del Sistema de Diseño

### Ubicación de Archivos

```
frontend/
├── index.html                         # Importación de Google Fonts
├── src/
│   ├── styles/
│   │   ├── theme.css                  # Variables CSS y estilos globales
│   │   └── global.css                 # Reset y estilos base
│   ├── pages/
│   │   ├── LoginPage.css
│   │   ├── RegisterPage.css
│   │   ├── WelcomePage.css
│   │   ├── ProfilePage.css
│   │   ├── DashboardPage.css
│   │   ├── ForgotPasswordPage.css
│   │   ├── ResetPasswordPage.css
│   │   └── VerifyEmailPage.css
│   └── components/
│       └── auth/
│           ├── LoginForm.css
│           └── RegisterForm.css
```

---

## Guías de Uso

### Cuándo Usar Cada Fuente

| Elemento | Fuente |
|----------|--------|
| Títulos de página (h1) | Playfair Display |
| Subtítulos (h2-h6) | Merriweather |
| Texto de cuerpo, párrafos | Inter |
| Labels de formulario | Inter (uppercase, bold) |
| Botones | Inter (uppercase, bold) |

### Cuándo Usar Cada Color

| Elemento | Color |
|----------|-------|
| Fondos de página | cream + gradient |
| Headers | primary → forest gradient |
| Texto principal | gray-700 / forest |
| Texto secundario | gray-600 |
| Bordes principales | earth-light |
| Bordes hover | earth |
| Botones primarios | primary gradient |
| Éxito | success + success-light |
| Error | error + error-light |
| Advertencia | warning + warning-light |

### Jerarquía Visual

1. **Primero**: Títulos grandes (Playfair Display)
2. **Segundo**: Cards elevadas con sombras
3. **Tercero**: Botones con gradientes
4. **Cuarto**: Contenido de texto (Inter)

---

## Checklist de Implementación

Al crear un nuevo componente o página:

- [ ] Usar variables CSS de `theme.css`
- [ ] Aplicar gradiente diagonal en headers
- [ ] Añadir textura de fondo en páginas completas
- [ ] Usar Playfair Display para h1
- [ ] Usar Merriweather para h2-h6
- [ ] Usar Inter para texto de cuerpo
- [ ] Bordes de 2px con colores tierra
- [ ] Border radius consistente (lg o 2xl)
- [ ] Sombras orgánicas (shadow-md o shadow-xl)
- [ ] Animación slideUp en cards
- [ ] Animación slideDown en banners
- [ ] Efectos hover con translateY
- [ ] Estados disabled con opacity 0.5
- [ ] Responsive en mobile (640px)
- [ ] Focus states accesibles

---

## Notas de Mantenimiento

### Versión 1.0.0 (2026-01-09)
- Implementación inicial del sistema de diseño rústico
- Aplicado a todas las páginas de autenticación
- Aplicado a páginas de perfil y dashboard

### Próximas Mejoras
- [ ] Dark mode con paleta rústica nocturna
- [ ] Micro-interacciones adicionales
- [ ] Variantes de cards (outline, ghost)
- [ ] Sistema de grid para layouts complejos
- [ ] Componentes de navegación (navbar, sidebar)

---

## Inspiración y Referencias

- **Diarios de viaje vintage**: Tipografía serif, tonos crema
- **Material natural**: Colores tierra, texturas orgánicas
- **Ciclismo outdoor**: Verde oliva, marrones naturales
- **Modernidad**: Gradientes suaves, animaciones fluidas

---

**Mantenido por**: Equipo de ContraVento
**Contacto**: Para preguntas sobre el sistema de diseño, consultar este documento primero.
