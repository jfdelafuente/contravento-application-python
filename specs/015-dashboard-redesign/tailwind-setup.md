# Tailwind CSS v4 Setup Guide - Dashboard Redesign

**Feature**: 015-dashboard-redesign
**Date**: 2026-01-20
**Tailwind Version**: 4.1.18
**Plugin Version**: @tailwindcss/vite 4.1.18

---

## Overview

Esta guía consolida los resultados de 27 investigaciones específicas (T001-T027) sobre la integración de Tailwind CSS v4 en el proyecto ContraVento. Sirve como referencia única durante la implementación del Dashboard Redesign.

**Enfoque de Migración**: Gradual
- **Componentes nuevos** (Feature 015): Tailwind CSS v4
- **Componentes existentes** (~70): CSS Modules (sin cambios)
- **Coexistencia**: Ambos sistemas funcionan en paralelo

---

## Setup Checklist

### 1. Instalación de Dependencias (T001, T009)

```bash
cd frontend

# Tailwind CSS v4 con plugin Vite
npm install -D tailwindcss@4.1.18 @tailwindcss/vite@4.1.18

# Utilidades para manejo de clases
npm install clsx tailwind-merge
```

**Nota**: Vite 5.0.8 actual funciona, pero considera actualizar a 5.2.0+ para compatibilidad óptima con Tailwind v4.

**Verificar instalación**:
```bash
npm list tailwindcss @tailwindcss/vite
# Debe mostrar: tailwindcss@4.1.18, @tailwindcss/vite@4.1.18
```

---

### 2. Configuración de Vite (T002)

**Archivo**: `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), // Plugin Tailwind v4
  ],
  resolve: {
    alias: {
      '@': '/src', // Path alias para imports
    },
  },
});
```

**Validación**:
```bash
npm run dev
# Debe iniciar sin errores, HMR funcional
```

---

### 3. Archivo CSS de Entrada (T003)

**Archivo**: `frontend/src/index.css`

```css
/* Tailwind v4 - Directiva @import */
@import "tailwindcss";

/* Design System - Variables CSS existentes (compatibilidad) */
/* Estas variables se mapean a Tailwind con @theme (ver sección 4) */
:root {
  /* Colores */
  --color-primary: #6B8E23;
  --color-secondary: #8B4513;
  --color-success: #28a745;
  --color-error: #dc3545;
  --color-white: #ffffff;
  --color-black: #000000;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;

  /* Espaciado */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* Bordes */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  /* Tipografía */
  --font-family-sans: 'Inter', 'Segoe UI', sans-serif;
  --font-family-serif: 'Merriweather', 'Georgia', serif;
}
```

**Importar en `main.tsx`**:
```typescript
import './index.css'; // Ya existe, verificar que esté presente
```

---

### 4. Configuración de Theme con @theme (T005, T027)

**Archivo**: `frontend/src/index.css` (añadir después de @import)

```css
@import "tailwindcss";

/* Mapeo de CSS Custom Properties a Tailwind Theme */
@theme {
  /* Colores - Usar variables existentes */
  --color-primary: #6B8E23;
  --color-secondary: #8B4513;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-800: #1f2937;

  /* Espaciado - Mantener nomenclatura existente */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;

  /* Radios de borde */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  /* Tipografía - Merriweather para títulos */
  --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-serif: 'Merriweather', 'Georgia', serif;
}

/* Tipografía - Cargar fuentes */
@font-face {
  font-family: 'Merriweather';
  src: url('/fonts/Merriweather-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Merriweather';
  src: url('/fonts/Merriweather-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
```

**Uso en componentes**:
```tsx
<h1 className="font-serif text-3xl text-gray-800">Dashboard</h1>
<p className="text-primary">Bienvenido</p>
<div className="p-4 rounded-md bg-gray-50">...</div>
```

---

### 5. TypeScript Configuration (T004)

**Archivo**: `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**No requiere tipos adicionales** - Tailwind v4 no usa typescript para config.

---

### 6. Utilidad cn() para Manejo de Clases (T010, T026)

**Archivo**: `frontend/src/lib/cn.ts` (crear directorio lib/)

```typescript
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combina clases de Tailwind evitando conflictos
 *
 * @example
 * cn('px-2 py-1', condition && 'bg-primary')
 * cn('px-2', { 'bg-primary': isActive })
 *
 * @param inputs - Clases CSS (strings, objetos, arrays)
 * @returns String de clases combinadas y optimizadas
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
```

**Uso en componentes**:
```tsx
import { cn } from '@/lib/cn';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  isActive?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isActive = false,
  children
}) => {
  return (
    <button
      className={cn(
        // Clases base
        'rounded-md font-medium transition-colors',

        // Variantes
        {
          'bg-primary text-white hover:bg-primary/90': variant === 'primary',
          'bg-gray-100 text-gray-800 hover:bg-gray-200': variant === 'secondary',
        },

        // Tamaños
        {
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-base': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
        },

        // Estados condicionales
        isActive && 'ring-2 ring-primary ring-offset-2'
      )}
    >
      {children}
    </button>
  );
};
```

---

### 7. Contenido para Purga de Clases (T016)

**Archivo**: `frontend/src/index.css` (añadir a @theme)

```css
@theme {
  /* ... colores, espaciado, etc ... */
}

/* Content paths para purga de clases no usadas */
@source "src/**/*.{js,ts,jsx,tsx}";
```

**Alternativa** (si @source no funciona en v4.1.18):
Crear `frontend/tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
};

export default config;
```

---

### 8. Breakpoints Personalizados (T013)

**Archivo**: `frontend/src/index.css` (dentro de @theme)

```css
@theme {
  /* Breakpoints responsive */
  --breakpoint-sm: 320px;   /* Mobile small */
  --breakpoint-md: 768px;   /* Tablet */
  --breakpoint-lg: 1024px;  /* Desktop */
  --breakpoint-xl: 1280px;  /* Desktop large */
}
```

**Uso en componentes**:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Mobile: 1 columna, Tablet: 2 columnas, Desktop: 3 columnas */}
</div>

<h1 className="text-2xl md:text-3xl lg:text-4xl">
  {/* Tamaño de texto responsivo */}
</h1>

<div className="p-4 md:p-6 lg:p-8">
  {/* Padding responsivo */}
</div>
```

---

## Patrones de Componentes

### Sticky Header (T007)

```tsx
// frontend/src/components/dashboard/DashboardHeader.tsx
import { cn } from '@/lib/cn';

export const DashboardHeader: React.FC = () => {
  return (
    <header
      className={cn(
        // Sticky positioning
        'sticky top-0 z-50',

        // Estilo base
        'bg-white px-6 py-4',

        // Sombra sutil
        'shadow-sm border-b border-gray-200',

        // Hardware acceleration
        'will-change-transform'
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <h1 className="text-2xl font-serif text-gray-800">ContraVento</h1>
        {/* Search, notifications, etc. */}
      </div>
    </header>
  );
};
```

---

### Grid Responsivo 3 Columnas (T008, T014, T015)

```tsx
// frontend/src/components/dashboard/DashboardLayout.tsx
export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div
      className={cn(
        // Grid responsivo: 1→2→3 columnas
        'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',

        // Gap responsivo
        'gap-4 md:gap-6',

        // Padding responsivo
        'p-4 md:p-6 lg:p-8',

        // Contenedor máximo
        'max-w-7xl mx-auto'
      )}
    >
      {children}
    </div>
  );
};
```

---

### Dropdown con Posicionamiento Absoluto (T011, T012)

```tsx
// frontend/src/components/dashboard/NotificationPanel.tsx
import { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/cn';

export const NotificationPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Cerrar al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Botón trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'relative p-2 rounded-full hover:bg-gray-100 transition-colors',
          // Indicador de notificaciones no leídas
          'after:absolute after:top-0 after:right-0',
          'after:w-2 after:h-2 after:bg-danger after:rounded-full'
        )}
        aria-label="Notificaciones"
        aria-expanded={isOpen}
      >
        <BellIcon className="w-6 h-6 text-gray-600" />
      </button>

      {/* Dropdown panel */}
      {isOpen && (
        <div
          className={cn(
            // Posicionamiento absoluto
            'absolute right-0 mt-2',

            // Dimensiones
            'w-80 max-h-96 overflow-y-auto',

            // Estilo
            'bg-white rounded-lg shadow-lg border border-gray-200',

            // Z-index
            'z-50',

            // Animación entrada
            'animate-in fade-in slide-in-from-top-2 duration-200'
          )}
          role="menu"
          aria-label="Panel de notificaciones"
        >
          <div className="p-4">
            <h3 className="font-semibold text-gray-800 mb-2">Notificaciones</h3>
            {/* Lista de notificaciones */}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

### Autocomplete Search con Debounce (T012)

```tsx
// frontend/src/components/dashboard/GlobalSearch.tsx
import { useState, useEffect } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { cn } from '@/lib/cn';

export const GlobalSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounce 300ms para evitar búsquedas excesivas
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      performSearch(debouncedQuery);
    } else {
      setResults([]);
    }
  }, [debouncedQuery]);

  const performSearch = async (searchQuery: string) => {
    setIsSearching(true);
    try {
      const data = await searchGlobal(searchQuery);
      setResults(data);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="relative">
      {/* Input con ícono */}
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="search"
          placeholder="Buscar rutas, usuarios, pueblos..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className={cn(
            'w-full pl-10 pr-4 py-2',
            'border border-gray-300 rounded-lg',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'text-gray-800 placeholder-gray-400'
          )}
          aria-label="Búsqueda global"
          aria-autocomplete="list"
          aria-controls="search-results"
        />
      </div>

      {/* Resultados dropdown */}
      {query.length >= 2 && (
        <div
          id="search-results"
          role="listbox"
          className={cn(
            'absolute top-full left-0 right-0 mt-2',
            'bg-white rounded-lg shadow-lg border border-gray-200',
            'max-h-80 overflow-y-auto',
            'z-50'
          )}
        >
          {isSearching ? (
            <div className="p-4 text-center text-gray-500">Buscando...</div>
          ) : results.length > 0 ? (
            results.map((result) => (
              <SearchResultItem key={result.id} result={result} />
            ))
          ) : (
            <div className="p-4 text-center text-gray-500">
              No se encontraron resultados
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

---

### Skeleton Loader (T025)

```tsx
// frontend/src/components/common/SkeletonLoader.tsx
import { cn } from '@/lib/cn';

interface SkeletonProps {
  variant?: 'text' | 'rect' | 'circle';
  width?: string;
  height?: string;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className,
}) => {
  return (
    <div
      className={cn(
        // Animación de pulso
        'animate-pulse bg-gray-200',

        // Variantes
        {
          'h-4 rounded': variant === 'text',
          'rounded-md': variant === 'rect',
          'rounded-full': variant === 'circle',
        },

        className
      )}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
};

// Skeleton para StatsCard
export const StatsCardSkeleton: React.FC = () => {
  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <Skeleton variant="text" width="60%" className="mb-2" />
      <Skeleton variant="text" width="40%" height="2rem" className="mb-4" />
      <Skeleton variant="rect" width="100%" height="60px" />
    </div>
  );
};
```

---

## Accessibility (WCAG 2.1 AA)

### Focus States (T019)

```tsx
// Botones con focus visible
<button
  className={cn(
    'px-4 py-2 bg-primary text-white rounded-md',

    // Focus ring (solo con teclado)
    'focus-visible:outline-none',
    'focus-visible:ring-2 focus-visible:ring-blue-500',
    'focus-visible:ring-offset-2',

    // Hover
    'hover:bg-primary/90 transition-colors'
  )}
>
  Acción
</button>

// Inputs con focus
<input
  className={cn(
    'px-3 py-2 border border-gray-300 rounded-md',

    // Focus
    'focus:outline-none focus:ring-2 focus:ring-primary',
    'focus:border-transparent'
  )}
/>

// Links con focus
<a
  href="/trips"
  className={cn(
    'text-primary underline',

    // Focus
    'focus-visible:outline-none',
    'focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary',
    'focus-visible:rounded-sm'
  )}
>
  Ver viajes
</a>
```

---

### Screen Reader Only Utility (T020)

```tsx
// frontend/src/lib/cn.ts (añadir clase sr-only)
// En index.css con @layer utilities:

@layer utilities {
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
}

// Uso en componentes:
<button aria-label="Cerrar notificación">
  <span className="sr-only">Cerrar notificación</span>
  <XIcon className="w-5 h-5" aria-hidden="true" />
</button>

<h2>
  <span className="sr-only">Estadísticas del usuario</span>
  <span aria-hidden="true">📊</span> Estadísticas
</h2>
```

---

## Testing

### Playwright - Selectores Semánticos (T023)

**❌ NO USAR**: Selectores basados en clases Tailwind (inestables)
```typescript
// MAL - Las clases Tailwind pueden cambiar
await page.locator('.bg-blue-500.text-white').click();
await page.locator('.grid-cols-3').first().click();
```

**✅ USAR**: Selectores basados en roles y accesibilidad
```typescript
// BIEN - Selectores estables basados en semántica
await page.getByRole('button', { name: 'Publicar viaje' }).click();
await page.getByRole('heading', { name: 'Dashboard' }).isVisible();
await page.getByLabel('Búsqueda global').fill('bikepacking');
await page.getByText('156 km recorridos').isVisible();

// Selectores por data-testid (cuando role no es suficiente)
<div data-testid="stats-card-distance">...</div>
await page.getByTestId('stats-card-distance').isVisible();
```

**Ejemplo completo** (dashboard-navigation.spec.ts):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.getByLabel('Usuario').fill('testuser');
    await page.getByLabel('Contraseña').fill('TestPass123!');
    await page.getByRole('button', { name: 'Iniciar sesión' }).click();
    await page.waitForURL('**/dashboard');
  });

  test('header remains sticky on scroll', async ({ page }) => {
    const header = page.getByRole('banner'); // <header> tiene role="banner"

    // Posición inicial
    const initialBox = await header.boundingBox();
    expect(initialBox).not.toBeNull();

    // Scroll hacia abajo
    await page.evaluate(() => window.scrollTo(0, 1000));

    // Header sigue visible en top
    const scrolledBox = await header.boundingBox();
    expect(scrolledBox?.y).toBe(0);
  });

  test('global search shows results', async ({ page }) => {
    const searchInput = page.getByLabel('Búsqueda global');

    await searchInput.fill('bikepacking');
    await page.waitForTimeout(400); // Esperar debounce

    const resultsDropdown = page.getByRole('listbox', { name: /resultados/i });
    await expect(resultsDropdown).toBeVisible();

    const firstResult = page.getByRole('option').first();
    await expect(firstResult).toBeVisible();
  });
});
```

---

### Vitest - Configuración (T022)

**Archivo**: `frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    css: true, // Procesar CSS (incluye Tailwind)
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

**Archivo**: `frontend/tests/setup.ts`

```typescript
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

**Ejemplo de test**:
```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';

describe('DashboardHeader', () => {
  it('should render with sticky positioning', () => {
    render(<DashboardHeader />);

    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();

    // Verificar que tiene clases Tailwind aplicadas
    expect(header).toHaveClass('sticky', 'top-0', 'z-50');
  });

  it('should display search input', () => {
    render(<DashboardHeader />);

    const searchInput = screen.getByLabelText(/búsqueda/i);
    expect(searchInput).toBeInTheDocument();
  });
});
```

---

## Performance

### Bundle Size Analysis (T017)

```bash
# Construir producción
cd frontend
npm run build

# Analizar bundle con vite-bundle-visualizer
npx vite-bundle-visualizer

# Abre http://localhost:8888 con treemap interactivo
# Buscar: tailwindcss debe ser <50KB gzipped
```

**Objetivo**: Bundle CSS total <100KB gzipped (con purga de clases no usadas).

---

### JIT Mode (T018)

Tailwind v4 tiene JIT (Just-In-Time) **activado por defecto**.

**Ventajas**:
- Genera clases on-demand (solo las que usas)
- Build time más rápido
- Clases arbitrarias: `w-[147px]`, `top-[117px]`
- Variantes arbitrarias: `[&:nth-child(3)]:bg-primary`

**Ejemplo**:
```tsx
<div className="w-[147px] h-[64px] bg-[#6B8E23]">
  {/* Valores arbitrarios - generados dinámicamente */}
</div>

<div className="[&>li]:p-4 [&>li:hover]:bg-gray-100">
  {/* Selectores arbitrarios */}
  <ul>
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</div>
```

---

### HMR (Hot Module Replacement) (T024)

Tailwind v4 con @tailwindcss/vite tiene HMR optimizado:

**Comportamiento**:
- Cambios en clases → actualización instantánea (sin page reload)
- Cambios en @theme → reconstrucción CSS rápida
- Sin necesidad de configuración adicional

**Verificar HMR funciona**:
```bash
npm run dev

# En componente, cambiar:
<div className="bg-blue-500"> → <div className="bg-red-500">
# Debe actualizarse sin reload completo
```

---

## Coexistencia con CSS Modules (T006)

**Estrategia**: Ambos sistemas coexisten sin conflictos.

**Componentes Nuevos** (Feature 015):
```tsx
// frontend/src/components/dashboard/DashboardHeader.tsx
import { cn } from '@/lib/cn';

export const DashboardHeader: React.FC = () => {
  return (
    <header className={cn('sticky top-0 z-50 bg-white px-6 py-4')}>
      {/* Tailwind puro */}
    </header>
  );
};
```

**Componentes Existentes** (Features 001-014):
```tsx
// frontend/src/components/profile/ProfileCard.tsx
import styles from './ProfileCard.module.css';

export const ProfileCard: React.FC = () => {
  return (
    <div className={styles.profileCard}>
      {/* CSS Modules sin cambios */}
    </div>
  );
};
```

**Componentes Híbridos** (si es necesario):
```tsx
import { cn } from '@/lib/cn';
import styles from './HybridComponent.module.css';

export const HybridComponent: React.FC = () => {
  return (
    <div className={cn(styles.legacy, 'flex items-center gap-4')}>
      {/* Combina CSS Modules + Tailwind */}
    </div>
  );
};
```

**Reglas**:
1. ❌ NO migrar componentes existentes (innecesario)
2. ✅ USAR Tailwind para componentes nuevos (Feature 015)
3. ✅ Permitir híbridos solo si es pragmático (evitar idealmente)

---

## Dark Mode (T021)

**Configuración** (opcional - no es requisito P1):

```css
/* frontend/src/index.css */
@theme {
  /* Soporte dark mode con media query */
  @media (prefers-color-scheme: dark) {
    --color-bg: #1f2937;
    --color-text: #f9fafb;
    --color-primary: #86a654;
  }
}
```

**Uso en componentes**:
```tsx
<div className="bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100">
  {/* Cambia automáticamente con preferencias del sistema */}
</div>
```

**Toggle manual** (si se implementa):
```tsx
// Añadir clase 'dark' al <html>
<html className={isDarkMode ? 'dark' : ''}>
```

---

## Quick Reference - Clases Comunes

### Layout
```tsx
// Flexbox
<div className="flex items-center justify-between gap-4">

// Grid responsivo
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

// Centrado
<div className="flex items-center justify-center min-h-screen">

// Sticky
<header className="sticky top-0 z-50">

// Absolute positioning
<div className="absolute top-4 right-4">
```

### Spacing
```tsx
// Padding
<div className="p-4 px-6 py-2">

// Margin
<div className="m-4 mx-auto my-8">

// Gap (flexbox/grid)
<div className="flex gap-4">
```

### Typography
```tsx
// Tamaños
<h1 className="text-4xl font-bold">
<p className="text-base leading-relaxed">

// Fuente serif
<h2 className="font-serif text-2xl">

// Colores
<p className="text-gray-800 dark:text-gray-100">
```

### Colores de Fondo
```tsx
<div className="bg-white border border-gray-200">
<div className="bg-primary text-white">
<div className="bg-gray-50 hover:bg-gray-100">
```

### Bordes y Sombras
```tsx
<div className="rounded-lg border border-gray-300 shadow-md">
<div className="rounded-full shadow-lg">
```

### Transiciones
```tsx
<button className="transition-colors duration-200 hover:bg-primary/90">
<div className="transition-all duration-300 ease-in-out">
```

### Estados Interactivos
```tsx
<button className="hover:bg-gray-100 active:bg-gray-200 disabled:opacity-50">
<input className="focus:ring-2 focus:ring-primary focus:border-transparent">
```

### Responsive
```tsx
<div className="hidden md:block"> {/* Oculto en mobile, visible en tablet+ */}
<div className="block md:hidden"> {/* Visible solo en mobile */}
<div className="text-sm md:text-base lg:text-lg"> {/* Tamaño responsivo */}
```

---

## Troubleshooting

### 1. Clases Tailwind no se aplican

**Síntoma**: Clases en componentes no tienen efecto visual.

**Soluciones**:
```bash
# Verificar que @tailwindcss/vite está en plugins
cat vite.config.ts | grep tailwindcss

# Verificar que index.css tiene @import "tailwindcss"
cat src/index.css | grep tailwindcss

# Verificar que main.tsx importa index.css
cat src/main.tsx | grep index.css

# Reiniciar dev server
npm run dev
```

---

### 2. Clases personalizadas no funcionan

**Síntoma**: Clases definidas en @theme no se reconocen.

**Solución**:
```css
/* Verificar sintaxis @theme en index.css */
@theme {
  --color-primary: #6B8E23; /* ✅ BIEN */
  color-primary: #6B8E23;   /* ❌ MAL - falta -- */
}

/* Uso correcto */
<div className="text-primary"> /* Usa --color-primary */
```

---

### 3. HMR no funciona

**Síntoma**: Cambios en clases requieren reload manual.

**Solución**:
```bash
# Verificar versión Vite
npm list vite
# Si <5.2.0, actualizar:
npm install -D vite@latest

# Limpiar cache
rm -rf node_modules/.vite
npm run dev
```

---

### 4. Bundle CSS demasiado grande

**Síntoma**: CSS de producción >200KB gzipped.

**Solución**:
```bash
# Verificar que purga está activa
cat src/index.css | grep @source

# Si no existe, añadir:
@source "src/**/*.{js,ts,jsx,tsx}";

# Reconstruir
npm run build
npm run preview
```

---

### 5. Conflictos CSS Modules + Tailwind

**Síntoma**: Estilos se sobreescriben entre CSS Modules y Tailwind.

**Solución**:
```tsx
// Usar cn() para combinar sin conflictos
import { cn } from '@/lib/cn';
import styles from './Component.module.css';

<div className={cn(styles.legacy, 'flex items-center')}>
  {/* twMerge resuelve conflictos */}
</div>
```

---

### 6. Tests fallan con clases Tailwind

**Síntoma**: Vitest/Playwright no reconocen clases.

**Solución Vitest**:
```typescript
// Verificar vitest.config.ts tiene css: true
export default defineConfig({
  test: {
    css: true, // Procesar Tailwind
  },
});
```

**Solución Playwright**:
```typescript
// NO usar clases como selectores
await page.locator('.bg-primary').click(); // ❌ MAL

// Usar roles/labels
await page.getByRole('button', { name: 'Publicar' }).click(); // ✅ BIEN
```

---

### 7. Fuente Merriweather no carga

**Síntoma**: Títulos no muestran fuente serif.

**Solución**:
```bash
# Verificar que fuentes existen
ls public/fonts/Merriweather-*.woff2

# Si no existen, descargar de Google Fonts
# Añadir a index.css:
@font-face {
  font-family: 'Merriweather';
  src: url('/fonts/Merriweather-Regular.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}

# Uso:
<h1 className="font-serif">Título</h1>
```

---

## Referencias Cruzadas

**Investigaciones específicas** (T001-T027):
- **T001**: Comando instalación npm
- **T002**: Configuración vite.config.ts
- **T003**: Archivo CSS entrada (@import)
- **T004**: TypeScript config
- **T005**: Mapeo CSS variables → @theme
- **T006**: Coexistencia CSS Modules
- **T007**: Sticky header clases
- **T008**: Grid 3 columnas responsivo
- **T009**: clsx + tailwind-merge
- **T010**: Función cn() helper
- **T011**: Dropdown positioning
- **T012**: Autocomplete styling
- **T013**: Breakpoints personalizados
- **T014**: Padding responsivo
- **T015**: Text size responsivo
- **T016**: Content paths purga
- **T017**: Bundle size analysis
- **T018**: JIT mode
- **T019**: Focus states accesibles
- **T020**: Screen reader utility
- **T021**: Dark mode config
- **T022**: Vitest config
- **T023**: Playwright selectors
- **T024**: HMR support
- **T025**: Skeleton loader
- **T026**: Clases condicionales pattern
- **T027**: Fuente Merriweather

**Documentos relacionados**:
- [spec.md](spec.md): User Stories y requisitos funcionales
- [plan.md](plan.md): Plan de implementación (actualizar con Tailwind)
- [research.md](research.md): Decisiones tecnológicas (actualizar Decision 1)
- [data-model.md](data-model.md): TypeScript interfaces (sin cambios)
- [quickstart.md](quickstart.md): Workflow desarrollo (actualizar templates)
- [contracts/](contracts/): API endpoints (sin cambios)

---

## Checklist de Implementación

Antes de empezar a codificar componentes:

- [ ] **T001-T004**: Setup básico completado (npm install, vite config, CSS entry, TS config)
- [ ] **T005**: CSS variables mapeadas a @theme
- [ ] **T009-T010**: Utilidades clsx + tailwind-merge instaladas, cn() creada
- [ ] **T016**: Content paths configurados (@source)
- [ ] **T019-T020**: Utilidades accessibility creadas (focus states, sr-only)
- [ ] **T022**: Vitest configurado con css: true
- [ ] **T027**: Fuentes Merriweather cargadas
- [ ] **Verificación**: `npm run dev` funciona sin errores
- [ ] **Verificación**: HMR funciona cambiando clases en componente test
- [ ] **Verificación**: `npm run build` genera bundle <100KB CSS gzipped

**Siguiente paso**: Generar tasks.md con `/speckit.tasks` para secuencia de implementación detallada.

---

**Guía completa** - 27 investigaciones consolidadas ✅
