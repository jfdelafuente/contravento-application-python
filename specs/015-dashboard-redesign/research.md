# Research & Technical Decisions: Dashboard Redesign

**Feature**: 015-dashboard-redesign
**Phase**: 0 - Research & Technology Selection
**Date**: 2026-01-20

## Summary

Esta feature es **exclusivamente frontend**, consumiendo APIs REST que ya están implementadas en el backend. No se requieren cambios en Python/FastAPI. Las decisiones técnicas se enfocan en patrones React, optimización de rendimiento, y estrategias de carga de datos.

---

## Decision 1: CSS Strategy - Tailwind CSS v4 with @tailwindcss/vite

**Decision**: Adoptar **Tailwind CSS v4 con @tailwindcss/vite** para componentes nuevos de Feature 015, manteniendo CSS Modules en componentes existentes

**Rationale**:

1. **Requisito del usuario**: Migración explícita a Tailwind CSS como estrategia de styling preferida
2. **Coexistencia gradual**: Feature 015 (~15 componentes nuevos) usa Tailwind, componentes existentes (~70) mantienen CSS Modules sin cambios
3. **Compatibilidad con Design System**: CSS Custom Properties (`--color-primary`, `--space-4`) se mapean a Tailwind via `@theme` directive
4. **Tailwind v4 benefits**: CSS-first config (@theme), JIT mode nativo, bundle size optimizado (<100KB gzipped con purga), HMR mejorado
5. **Developer Experience**: Utility-first approach acelera desarrollo, clsx + tailwind-merge para manejo de clases condicionales
6. **Modern tooling**: @tailwindcss/vite plugin integrado nativamente en Vite 5.0.8 (upgrade a 5.2.0+ recomendado)

**Alternatives Considered**:

- **CSS Modules (continuar 100%)**: Rechazado porque usuario requiere Tailwind explícitamente
- **Tailwind v3**: Rechazado porque v4 tiene mejoras significativas (CSS-first config, mejor performance)
- **Styled Components / Emotion**: Rechazado por runtime CSS-in-JS overhead (peor performance)
- **Migración total a Tailwind**: Rechazado por riesgo innecesario (70 componentes funcionando no requieren cambios)

**Implementation Strategy**:

**Setup** (ver detalles completos en [tailwind-setup.md](tailwind-setup.md)):

```bash
# Instalación
npm install -D tailwindcss@4.1.18 @tailwindcss/vite@4.1.18
npm install clsx tailwind-merge
```

**Vite Configuration**:

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': '/src' },
  },
});
```

**CSS Entry Point**:

```css
/* frontend/src/index.css */
@import "tailwindcss";

/* Mapear CSS Custom Properties existentes a Tailwind Theme */
@theme {
  --color-primary: #6B8E23;
  --color-secondary: #8B4513;
  --color-success: #28a745;
  --color-danger: #dc3545;

  --spacing-1: 0.25rem;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  --font-family-sans: 'Inter', -apple-system, sans-serif;
  --font-family-serif: 'Merriweather', 'Georgia', serif;
}

@source "src/**/*.{js,ts,jsx,tsx}";
```

**Component Pattern (Tailwind - NEW)**:

```typescript
// frontend/src/components/dashboard/DashboardHeader.tsx
import { cn } from '@/lib/cn';

export const DashboardHeader: React.FC = () => {
  return (
    <header className={cn(
      'sticky top-0 z-50',
      'bg-white px-6 py-4',
      'shadow-sm border-b border-gray-200'
    )}>
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <h1 className="text-2xl font-serif text-gray-800">ContraVento</h1>
      </div>
    </header>
  );
};
```

**Helper Utility (cn function)**:

```typescript
// frontend/src/lib/cn.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
```

**Coexistence with CSS Modules (EXISTING components unchanged)**:

```typescript
// frontend/src/components/profile/ProfileCard.tsx (NO CHANGES)
import styles from './ProfileCard.module.css';

export const ProfileCard: React.FC = () => {
  return (
    <div className={styles.profileCard}>
      {/* CSS Modules - sin cambios */}
    </div>
  );
};
```

**Migration Rules**:

1. ❌ **NO migrar** componentes existentes (Features 001-014) - innecesario y riesgoso
2. ✅ **USAR Tailwind** para todos los componentes nuevos (Feature 015)
3. ✅ **Permitir híbridos** solo si pragmático (evitar idealmente)
4. ✅ **Mantener CSS variables** - design system permanece consistente

**Reference Documentation**: Ver [tailwind-setup.md](tailwind-setup.md) para:
- Setup checklist completo (instalación, config, TypeScript)
- Patrones de componentes (sticky header, grid responsivo, dropdowns)
- Accessibility (focus states, screen reader utilities)
- Testing (Playwright selectores semánticos, Vitest config)
- Performance (bundle analysis, JIT mode, HMR)
- Troubleshooting (7 problemas comunes con soluciones)

---

## Decision 2: Layout Strategy - CSS Grid with Responsive Breakpoints

**Decision**: Usar **CSS Grid** para layout de 3 columnas con media queries para responsive

**Rationale**:

1. **Native browser support**: CSS Grid tiene soporte en Chrome 90+, Firefox 88+, Safari 14+ (target platform)
2. **Declarative layout**: Grid permite definir layout completo sin JavaScript
3. **Performance**: Sin re-renders JavaScript durante resize
4. **Accessibility**: Grid mantiene orden semántico HTML independiente del orden visual

**Alternatives Considered**:

- **Flexbox**: Rechazado porque Grid es superior para layouts 2D (filas + columnas)
- **react-grid-layout**: Rechazado porque es overkill (no necesitamos drag-and-drop)
- **Manual positioning**: Rechazado por ser difícil de mantener y no responsive

**Implementation**:

```typescript
// frontend/src/utils/constants.ts
export const BREAKPOINTS = {
  MOBILE: 320,
  TABLET: 768,
  DESKTOP: 1024,
  WIDE: 1440,
} as const;
```

```css
/* frontend/src/components/dashboard/DashboardLayout.css */
.dashboard-layout {
  display: grid;
  grid-template-columns: 1fr; /* Mobile: 1 column */
  gap: var(--space-6);
  padding: var(--space-4);
}

@media (min-width: 768px) {
  .dashboard-layout {
    grid-template-columns: 2fr 1fr; /* Tablet: 2 columns */
  }
}

@media (min-width: 1024px) {
  .dashboard-layout {
    grid-template-columns: 3fr 5fr 2fr; /* Desktop: 30% 50% 20% */
  }
}
```

---

## Decision 3: Data Fetching - React Query (TanStack Query) vs Custom Hooks

**Decision**: Usar **Custom Hooks con Axios** (sin react-query)

**Rationale**:

1. **Simplicidad**: Dashboard no requiere cache complejo, optimistic updates o sincronización server
2. **Zero dependencies**: Axios ya está instalado (1.6.5), evita añadir react-query (~40KB)
3. **Control total**: Custom hooks permiten lógica específica (debounce search, pagination feed)
4. **Consistencia**: Otros features (trips, profile) usan custom hooks + Axios

**Alternatives Considered**:

- **React Query (TanStack Query)**: Rechazado por overhead innecesario para este caso de uso
- **SWR**: Rechazado por misma razón que React Query
- **Redux Toolkit Query**: Rechazado porque no usamos Redux en el proyecto

**Implementation**:

```typescript
// frontend/src/hooks/useDashboardStats.ts
import { useState, useEffect } from 'react';
import { getDashboardStats } from '../services/dashboardService';
import type { DashboardStats } from '../types/dashboard';

export const useDashboardStats = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const data = await getDashboardStats();
        setStats(data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Error al cargar estadísticas');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, isLoading, error };
};
```

---

## Decision 4: Search Debouncing - lodash.debounce vs Custom Implementation

**Decision**: Usar **lodash.debounce** (ya instalado en proyecto)

**Rationale**:

1. **Already installed**: `lodash.debounce@4.0.8` ya está en package.json
2. **Battle-tested**: Maneja edge cases (trailing, leading, maxWait)
3. **TypeScript support**: `@types/lodash.debounce` ya instalado
4. **Zero bundle impact**: Solo importamos la función específica (~2KB)

**Alternatives Considered**:

- **Custom debounce**: Rechazado porque lodash.debounce ya cubre todos los casos
- **use-debounce hook**: Rechazado por añadir dependencia innecesaria

**Implementation**:

```typescript
// frontend/src/hooks/useGlobalSearch.ts
import { useState, useCallback } from 'react';
import debounce from 'lodash.debounce';
import { searchGlobal } from '../services/dashboardService';

export const useGlobalSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const debouncedSearch = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const data = await searchGlobal(searchQuery);
        setResults(data);
      } catch (error) {
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300), // 300ms debounce
    []
  );

  const handleSearchChange = (value: string) => {
    setQuery(value);
    debouncedSearch(value);
  };

  return { query, results, isSearching, handleSearchChange };
};
```

---

## Decision 5: Feed Virtualization - react-window vs react-virtualized

**Decision**: Usar **react-window** solo si feed excede 100 items

**Rationale**:

1. **Conditional need**: La mayoría de usuarios tendrán <50 items en feed (spec SC-003)
2. **Lightweight**: react-window es 1/3 del tamaño de react-virtualized (~10KB vs ~30KB)
3. **Simple API**: react-window es más fácil de integrar que react-virtualized
4. **Performance**: Virtualización solo aporta beneficio con listas >100 items

**Alternatives Considered**:

- **react-virtualized**: Rechazado por ser más pesado y complejo
- **No virtualization**: Aceptable para listas <100 items
- **Manual implementation**: Rechazado por complejidad innecesaria

**Implementation Strategy**:

```typescript
// frontend/src/components/dashboard/ActivityFeed.tsx
import { FixedSizeList as List } from 'react-window';

export const ActivityFeed: React.FC<Props> = ({ items }) => {
  // Only virtualize if >100 items
  if (items.length > 100) {
    return (
      <List
        height={600}
        itemCount={items.length}
        itemSize={120}
        width="100%"
      >
        {({ index, style }) => (
          <div style={style}>
            <ActivityFeedItem item={items[index]} />
          </div>
        )}
      </List>
    );
  }

  // Regular rendering for <100 items
  return (
    <div className="activity-feed">
      {items.map(item => (
        <ActivityFeedItem key={item.id} item={item} />
      ))}
    </div>
  );
};
```

**Note**: Instalar react-window solo si testing confirma necesidad (P3 optimization)

---

## Decision 6: Responsive Detection - useMediaQuery Hook vs CSS-only

**Decision**: Usar **hook personalizado `useResponsiveLayout`** para lógica condicional

**Rationale**:

1. **Conditional rendering**: Algunos componentes necesitan cambiar estructura, no solo CSS
2. **JavaScript control**: Layout de 3 → 2 → 1 columnas requiere cambiar orden de componentes
3. **Accessibility**: Orden de tab navigation difiere entre mobile y desktop
4. **Zero dependencies**: Custom hook usando `window.matchMedia()`

**Alternatives Considered**:

- **CSS-only**: Rechazado porque no permite conditional rendering
- **react-responsive**: Rechazado por añadir dependencia innecesaria (~3KB)

**Implementation**:

```typescript
// frontend/src/hooks/useResponsiveLayout.ts
import { useState, useEffect } from 'react';
import { BREAKPOINTS } from '../utils/constants';

type Layout = 'mobile' | 'tablet' | 'desktop' | 'wide';

export const useResponsiveLayout = (): Layout => {
  const [layout, setLayout] = useState<Layout>('desktop');

  useEffect(() => {
    const mediaQueries = [
      { query: window.matchMedia(`(min-width: ${BREAKPOINTS.WIDE}px)`), layout: 'wide' as Layout },
      { query: window.matchMedia(`(min-width: ${BREAKPOINTS.DESKTOP}px)`), layout: 'desktop' as Layout },
      { query: window.matchMedia(`(min-width: ${BREAKPOINTS.TABLET}px)`), layout: 'tablet' as Layout },
      { query: window.matchMedia(`(max-width: ${BREAKPOINTS.TABLET - 1}px)`), layout: 'mobile' as Layout },
    ];

    const updateLayout = () => {
      for (const { query, layout } of mediaQueries) {
        if (query.matches) {
          setLayout(layout);
          break;
        }
      }
    };

    updateLayout();
    mediaQueries.forEach(({ query }) => query.addEventListener('change', updateLayout));

    return () => {
      mediaQueries.forEach(({ query }) => query.removeEventListener('change', updateLayout));
    };
  }, []);

  return layout;
};
```

---

## Decision 7: Sticky Header Implementation - CSS position:sticky vs JavaScript

**Decision**: Usar **CSS `position: sticky`** nativo

**Rationale**:

1. **Native performance**: Browser maneja scroll events eficientemente
2. **Zero JavaScript**: No requiere listeners ni state management
3. **Smooth**: Hardware-accelerated en navegadores modernos
4. **Accessible**: Mantiene keyboard navigation funcionando

**Alternatives Considered**:

- **Intersection Observer**: Rechazado por ser más complejo innecesariamente
- **Scroll event listener**: Rechazado por peor performance (throttling required)
- **react-sticky**: Rechazado por añadir dependencia innecesaria

**Implementation**:

```css
/* frontend/src/components/dashboard/DashboardHeader.css */
.dashboard-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-white);
  box-shadow: var(--shadow-sm);

  /* Evita layout shift durante scroll */
  will-change: transform;
  transform: translateZ(0);
}
```

---

## Decision 8: Loading States - Skeleton vs Spinner

**Decision**: Usar **Skeleton Loaders** (ya implementado en `SkeletonLoader.tsx`)

**Rationale**:

1. **Better UX**: Skeleton muestra estructura de contenido, reduciendo perceived load time
2. **Consistency**: Ya usado en DashboardPage existente (Feature 006)
3. **Accessibility**: Skeleton incluye `aria-busy="true"` y `role="status"`
4. **Zero dependencies**: Componente ya existe y está probado

**Alternatives Considered**:

- **Spinners**: Rechazado por peor UX (no muestra estructura esperada)
- **Progress bars**: Rechazado porque no sabemos duración exacta de carga

**Implementation**:

```typescript
// frontend/src/components/dashboard/StatsOverview.tsx
import SkeletonLoader from '../common/SkeletonLoader';

export const StatsOverview: React.FC = () => {
  const { stats, isLoading, error } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="stats-overview" aria-busy="true">
        <SkeletonLoader variant="text" width="60%" height="1.5rem" />
        <SkeletonLoader variant="rectangle" width="100%" height="120px" />
      </div>
    );
  }

  // ... render stats
};
```

---

## Decision 9: Date Formatting - date-fns vs Intl API

**Decision**: Usar **date-fns** (ya instalado en proyecto)

**Rationale**:

1. **Already installed**: `date-fns@3.0.0` ya está en package.json
2. **Spanish localization**: `date-fns/locale/es` disponible
3. **Relative time**: `formatDistanceToNow` para "hace 5 minutos" en feed
4. **Tree-shakeable**: Solo importamos funciones necesarias

**Alternatives Considered**:

- **Intl.DateTimeFormat**: Rechazado por ser más verboso y difícil configurar relative time
- **moment.js**: Rechazado por ser pesado (~70KB) y deprecated
- **day.js**: Rechazado porque date-fns ya está instalado

**Implementation**:

```typescript
// frontend/src/utils/dateHelpers.ts
import { format, formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export const formatFeedTimestamp = (dateString: string): string => {
  const date = new Date(dateString);
  return formatDistanceToNow(date, { addSuffix: true, locale: es });
  // Output: "hace 5 minutos", "hace 2 horas", "hace 3 días"
};

export const formatStatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return format(date, 'dd/MM/yyyy', { locale: es });
  // Output: "20/01/2026"
};
```

---

## Decision 10: Error Handling Strategy - Toast Notifications vs Inline Errors

**Decision**: Usar **react-hot-toast** (ya instalado) para errores de acciones + inline errors para secciones

**Rationale**:

1. **Already installed**: `react-hot-toast@2.6.0` ya está en package.json
2. **Action errors**: Toast para errores de acciones (search failed, mark notification read failed)
3. **Section errors**: Inline errors para secciones que no cargan (stats, feed)
4. **UX consistency**: Ya usado en feature 004 (social network)

**Alternatives Considered**:

- **Only inline errors**: Rechazado porque acciones necesitan feedback temporal
- **Modal errors**: Rechazado por ser demasiado intrusivo
- **react-toastify**: Rechazado porque react-hot-toast ya está instalado

**Implementation**:

```typescript
// frontend/src/hooks/useGlobalSearch.ts
import toast from 'react-hot-toast';

export const useGlobalSearch = () => {
  const debouncedSearch = useCallback(
    debounce(async (searchQuery: string) => {
      try {
        const data = await searchGlobal(searchQuery);
        setResults(data);
      } catch (error: any) {
        toast.error('Error en la búsqueda. Intenta de nuevo.');
        setResults([]);
      }
    }, 300),
    []
  );

  return { query, results, isSearching, handleSearchChange };
};
```

```typescript
// frontend/src/components/dashboard/StatsOverview.tsx
export const StatsOverview: React.FC = () => {
  const { stats, isLoading, error } = useDashboardStats();

  if (error) {
    return (
      <div className="stats-overview stats-overview--error" role="alert">
        <p className="error-message">{error}</p>
        <button onClick={refetch}>Reintentar</button>
      </div>
    );
  }

  // ... render stats
};
```

---

## Technology Stack Summary

| Category | Technology | Version | Reason |
|----------|-----------|---------|---------|
| **Language** | TypeScript | 5.2+ | Type safety, better IDE support |
| **Framework** | React | 18.2 | Already installed, component-based |
| **Routing** | React Router | 6.21 | Already installed, declarative routing |
| **HTTP Client** | Axios | 1.6 | Already installed, interceptors support |
| **Styling (NEW)** | Tailwind CSS + @tailwindcss/vite | 4.1.18 | User requirement, utility-first, JIT mode, CSS-first config |
| **Styling (EXISTING)** | CSS Modules | Native | Keep for 70+ existing components (no migration) |
| **Class Utilities** | clsx + tailwind-merge | Latest | Conditional classes, conflict resolution |
| **State Management** | React Hooks | Native | Simple state needs, no Redux required |
| **Form Handling** | N/A | - | Dashboard has minimal forms (search only) |
| **Date Formatting** | date-fns | 3.0 | Already installed, tree-shakeable |
| **Search Debounce** | lodash.debounce | 4.0.8 | Already installed, battle-tested |
| **Notifications** | react-hot-toast | 2.6.0 | Already installed, lightweight |
| **Testing (Unit)** | Vitest | 1.6 | Already installed, fast |
| **Testing (E2E)** | Playwright | 1.40 | Already installed, cross-browser |
| **Virtualization** | react-window | TBD | Install only if needed (>100 items) |

---

## Performance Optimizations

### Lazy Loading Strategy

```typescript
// frontend/src/pages/DashboardPage.tsx
import React, { lazy, Suspense } from 'react';

// P1 components - load immediately
import DashboardHeader from '../components/dashboard/DashboardHeader';
import StatsOverview from '../components/dashboard/StatsOverview';
import ActivityFeed from '../components/dashboard/ActivityFeed';

// P3 components - lazy load
const ActiveChallenges = lazy(() => import('../components/dashboard/ActiveChallenges'));
const NotificationPanel = lazy(() => import('../components/dashboard/NotificationPanel'));

export const DashboardPage: React.FC = () => {
  return (
    <div>
      <DashboardHeader />
      <StatsOverview />
      <ActivityFeed />

      <Suspense fallback={<SkeletonLoader />}>
        <ActiveChallenges />
      </Suspense>

      <Suspense fallback={<SkeletonLoader />}>
        <NotificationPanel />
      </Suspense>
    </div>
  );
};
```

### Image Optimization

```typescript
// Use native lazy loading for feed images
<img
  src={item.imageUrl}
  alt={item.title}
  loading="lazy"
  decoding="async"
  width="400"
  height="300"
/>
```

### Bundle Size Monitoring

```json
// frontend/package.json
{
  "scripts": {
    "build": "tsc && vite build",
    "analyze": "vite-bundle-analyzer"
  }
}
```

---

## API Contracts (to be consumed)

Los siguientes endpoints deben estar disponibles en el backend (Python/FastAPI):

1. `GET /api/v1/dashboard/stats` - Estadísticas personales
2. `GET /api/v1/dashboard/feed?page=1&limit=50` - Feed de actividad
3. `GET /api/v1/dashboard/suggested-routes?limit=5` - Rutas sugeridas
4. `GET /api/v1/dashboard/challenges` - Desafíos activos
5. `GET /api/v1/dashboard/notifications?unread=true` - Notificaciones
6. `GET /api/v1/dashboard/search?q={query}&types=users,routes,towns` - Búsqueda global

**Contracts detallados en**: `specs/015-dashboard-redesign/contracts/*.yaml` (Phase 1)

---

## Next Steps (Phase 1: Design)

1. ✅ Generate `data-model.md` with TypeScript interfaces for all entities
2. ✅ Create API contracts in `contracts/` directory (OpenAPI YAML)
3. ✅ Write `quickstart.md` with development workflow
4. ✅ Update agent context with new technologies (none - all existing)

---

**Research complete** - Ready to proceed to Phase 1 (Design)
