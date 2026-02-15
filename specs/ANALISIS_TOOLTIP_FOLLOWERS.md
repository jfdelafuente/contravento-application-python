# Análisis: Tooltip de Seguidores/Siguiendo en Dashboard

**Fecha**: 2026-02-11
**Componente**: SocialStatsSection (Dashboard)
**Objetivo**: Mostrar lista de usuarios al pasar el ratón sobre tarjetas de seguidores/siguiendo

---

## 1. Situación Actual

### Componente Existente: `SocialStatsSection.tsx`

**Ubicación**: `frontend/src/components/dashboard/SocialStatsSection.tsx`

**Estado Actual**:
- Muestra 2 tarjetas (`social-stat-card`): Seguidores y Siguiendo
- Datos mostrados: Solo contador numérico (ej: "12")
- Hover actual: Efecto visual (translateY, box-shadow) pero sin tooltip
- Fuente de datos: Hook `useStats()` que devuelve solo contadores

**Endpoints Disponibles**:
- ✅ `GET /users/{username}/followers` - Lista completa de seguidores
- ✅ `GET /users/{username}/following` - Lista completa de siguiendo

**Tipos Existentes** (`followService.ts`):
```typescript
interface UserSummaryForFollow {
  user_id: string;
  username: string;
  profile_photo_url: string | null;
}

interface FollowersListResponse {
  followers: UserSummaryForFollow[];
  total_count: number;
}

interface FollowingListResponse {
  following: UserSummaryForFollow[];
  total_count: number;
}
```

---

## 2. Opciones de Diseño UX

### Opción A: Tooltip Simple (Recomendada ✅)

**Descripción**: Tooltip compacto que muestra los primeros 5-8 usuarios con avatares y nombres.

**Ventajas**:
- ✅ Mínima intrusión visual
- ✅ Carga bajo demanda (solo on hover)
- ✅ Consistente con patrones de redes sociales (Instagram, Twitter)
- ✅ Implementación simple con positioning absolute
- ✅ Buena accesibilidad (role="tooltip", aria-describedby)

**Desventajas**:
- ⚠️ Espacio limitado (max 5-8 usuarios visibles)
- ⚠️ Requiere "Ver todos" link para listas largas

**Mockup Visual**:
```
┌─────────────────────────────────┐
│  ❤️  SEGUIDORES                 │  ← Tarjeta existente
│      12                          │
└─────────────────────────────────┘
           ↓ Hover
┌─────────────────────────────────┐
│  👤 maria_garcia                │
│  👤 juan_perez                  │  ← Tooltip flotante
│  👤 ana_lopez                   │    con 5 primeros
│  👤 carlos_ruiz                 │
│  👤 laura_martin                │
│  ──────────────────             │
│  + 7 más · Ver todos            │  ← Link a modal/página
└─────────────────────────────────┘
```

**Timing**:
- Delay on hover: 500ms (evitar tooltips accidentales)
- Delay on leave: 200ms (permitir mover ratón al tooltip)
- Fade in/out: 150ms

---

### Opción B: Popover Expandible

**Descripción**: Popover más grande que muestra más usuarios (10-15) con scroll interno.

**Ventajas**:
- ✅ Más usuarios visibles sin modal
- ✅ Puede incluir búsqueda inline
- ✅ Permite acciones (follow/unfollow) directamente

**Desventajas**:
- ⚠️ Más invasivo visualmente
- ⚠️ Puede bloquear contenido del dashboard
- ⚠️ Mayor complejidad de implementación
- ⚠️ Puede confundirse con un modal

---

### Opción C: Drawer/Sidebar Lateral

**Descripción**: Panel lateral deslizante desde derecha con lista completa.

**Ventajas**:
- ✅ Muestra todos los usuarios sin paginación
- ✅ No bloquea contenido principal
- ✅ Permite acciones y filtrado avanzado

**Desventajas**:
- ⚠️ Overhead visual alto para una acción simple
- ⚠️ Interrupción del flujo de trabajo
- ⚠️ Mobile UX complejo

---

## 3. Recomendación: Opción A (Tooltip Simple)

### Rationale

1. **Principio de Progressive Disclosure**:
   - Mostrar resumen compacto (5 primeros usuarios)
   - Link "Ver todos" abre modal/página completa solo si usuario necesita más

2. **Patrón Familiar**:
   - Instagram, Twitter, LinkedIn usan tooltips similares
   - Usuarios esperan este comportamiento

3. **Performance**:
   - Carga datos solo on hover (lazy loading)
   - No afecta tiempo de carga inicial del dashboard

4. **Accesibilidad**:
   - Tooltip con ARIA attributes
   - Funciona con teclado (focus → show tooltip)

---

## 4. Implementación Técnica Propuesta

### 4.1. Nuevo Hook: `useFollowersTooltip`

```typescript
// frontend/src/hooks/useFollowersTooltip.ts

import { useState, useCallback } from 'react';
import { getFollowers, getFollowing } from '../services/followService';
import type { UserSummaryForFollow } from '../services/followService';

interface UseFollowersTooltipReturn {
  users: UserSummaryForFollow[];
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
}

export function useFollowersTooltip(
  username: string,
  type: 'followers' | 'following'
): UseFollowersTooltipReturn {
  const [users, setUsers] = useState<UserSummaryForFollow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    if (!username) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = type === 'followers'
        ? await getFollowers(username)
        : await getFollowing(username);

      // Solo primeros 8 para tooltip
      const topUsers = type === 'followers'
        ? response.followers.slice(0, 8)
        : response.following.slice(0, 8);

      setUsers(topUsers);
      setTotalCount(response.total_count);
    } catch (err: any) {
      setError(err.message || 'Error al cargar usuarios');
      console.error(`Error fetching ${type}:`, err);
    } finally {
      setIsLoading(false);
    }
  }, [username, type]);

  return { users, totalCount, isLoading, error, fetchUsers };
}
```

---

### 4.2. Nuevo Componente: `SocialStatTooltip`

```typescript
// frontend/src/components/dashboard/SocialStatTooltip.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import type { UserSummaryForFollow } from '../../services/followService';
import './SocialStatTooltip.css';

interface SocialStatTooltipProps {
  users: UserSummaryForFollow[];
  totalCount: number;
  type: 'followers' | 'following';
  username: string;
  isLoading: boolean;
  visible: boolean;
}

export const SocialStatTooltip: React.FC<SocialStatTooltipProps> = ({
  users,
  totalCount,
  type,
  username,
  isLoading,
  visible,
}) => {
  if (!visible) return null;

  const remaining = totalCount - users.length;
  const title = type === 'followers' ? 'Seguidores' : 'Siguiendo';

  return (
    <div
      className="social-stat-tooltip"
      role="tooltip"
      aria-live="polite"
    >
      {isLoading ? (
        <div className="social-stat-tooltip__loading">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      ) : (
        <>
          <div className="social-stat-tooltip__header">
            <h3 className="social-stat-tooltip__title">{title}</h3>
          </div>

          <ul className="social-stat-tooltip__list">
            {users.map((user) => (
              <li key={user.user_id} className="social-stat-tooltip__item">
                <Link
                  to={`/users/${user.username}`}
                  className="social-stat-tooltip__user-link"
                >
                  {user.profile_photo_url ? (
                    <img
                      src={user.profile_photo_url}
                      alt={user.username}
                      className="social-stat-tooltip__avatar"
                    />
                  ) : (
                    <div className="social-stat-tooltip__avatar social-stat-tooltip__avatar--placeholder">
                      {user.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="social-stat-tooltip__username">
                    {user.username}
                  </span>
                </Link>
              </li>
            ))}
          </ul>

          {remaining > 0 && (
            <Link
              to={`/users/${username}/${type}`}
              className="social-stat-tooltip__view-all"
            >
              + {remaining} más · Ver todos
            </Link>
          )}
        </>
      )}
    </div>
  );
};
```

---

### 4.3. Modificación de `SocialStatsSection.tsx`

```typescript
// frontend/src/components/dashboard/SocialStatsSection.tsx

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useStats } from '../../hooks/useStats';
import { useFollowersTooltip } from '../../hooks/useFollowersTooltip';
import { SocialStatTooltip } from './SocialStatTooltip';
import './SocialStatsSection.css';

const SocialStatsSection: React.FC = () => {
  const { user } = useAuth();
  const { stats, loading, error } = useStats(user?.username || '');

  // State for tooltip visibility
  const [activeTooltip, setActiveTooltip] = useState<'followers' | 'following' | null>(null);

  // Hooks for followers and following lists
  const followersTooltip = useFollowersTooltip(user?.username || '', 'followers');
  const followingTooltip = useFollowersTooltip(user?.username || '', 'following');

  // Hover handlers with delay
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);

  const handleMouseEnter = (type: 'followers' | 'following') => {
    // Clear any existing timeout
    if (hoverTimeout) clearTimeout(hoverTimeout);

    // Delay 500ms before showing tooltip
    const timeout = setTimeout(() => {
      setActiveTooltip(type);

      // Fetch data on hover (lazy load)
      if (type === 'followers') {
        followersTooltip.fetchUsers();
      } else {
        followingTooltip.fetchUsers();
      }
    }, 500);

    setHoverTimeout(timeout);
  };

  const handleMouseLeave = () => {
    // Clear hover timeout
    if (hoverTimeout) clearTimeout(hoverTimeout);

    // Delay 200ms before hiding (allow moving to tooltip)
    const timeout = setTimeout(() => {
      setActiveTooltip(null);
    }, 200);

    setHoverTimeout(timeout);
  };

  return (
    <section className="social-stats-section" aria-labelledby="social-stats-heading">
      <h2 id="social-stats-heading" className="social-stats-section__title">
        Pelotón
      </h2>

      {loading && (
        <div className="social-stats-section__loading">
          <div className="spinner"></div>
        </div>
      )}

      {error && (
        <div className="social-stats-section__error">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="social-stats-section__grid">
          {/* Followers Card with Tooltip */}
          <div
            className="social-stat-card social-stat-card--with-tooltip"
            onMouseEnter={() => handleMouseEnter('followers')}
            onMouseLeave={handleMouseLeave}
            aria-describedby={activeTooltip === 'followers' ? 'followers-tooltip' : undefined}
          >
            <div className="social-stat-card__icon social-stat-card__icon--followers">
              <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
              </svg>
            </div>
            <div className="social-stat-card__content">
              <h3 className="social-stat-card__label">Seguidores</h3>
              <p className="social-stat-card__value">
                {stats?.followers_count ?? 0}
              </p>
            </div>

            {/* Tooltip */}
            <SocialStatTooltip
              users={followersTooltip.users}
              totalCount={followersTooltip.totalCount}
              type="followers"
              username={user?.username || ''}
              isLoading={followersTooltip.isLoading}
              visible={activeTooltip === 'followers'}
            />
          </div>

          {/* Following Card with Tooltip */}
          <div
            className="social-stat-card social-stat-card--with-tooltip"
            onMouseEnter={() => handleMouseEnter('following')}
            onMouseLeave={handleMouseLeave}
            aria-describedby={activeTooltip === 'following' ? 'following-tooltip' : undefined}
          >
            <div className="social-stat-card__icon social-stat-card__icon--following">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="8.5" cy="7" r="4" />
                <line x1="20" y1="8" x2="20" y2="14" />
                <line x1="23" y1="11" x2="17" y2="11" />
              </svg>
            </div>
            <div className="social-stat-card__content">
              <h3 className="social-stat-card__label">Siguiendo</h3>
              <p className="social-stat-card__value">
                {stats?.following_count ?? 0}
              </p>
            </div>

            {/* Tooltip */}
            <SocialStatTooltip
              users={followingTooltip.users}
              totalCount={followingTooltip.totalCount}
              type="following"
              username={user?.username || ''}
              isLoading={followingTooltip.isLoading}
              visible={activeTooltip === 'following'}
            />
          </div>
        </div>
      )}
    </section>
  );
};

export default SocialStatsSection;
```

---

### 4.4. CSS: `SocialStatTooltip.css`

```css
/* SocialStatTooltip.css - Tooltip para mostrar lista de seguidores/siguiendo */

.social-stat-card--with-tooltip {
  position: relative;
  cursor: pointer;
}

.social-stat-tooltip {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--surface-elevated);
  border: 1px solid var(--border-emphasis);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: var(--space-3);
  min-width: 220px;
  max-width: 280px;
  z-index: 1000;
  animation: tooltip-fade-in 150ms ease-out;
}

/* Arrow pointing up */
.social-stat-tooltip::before {
  content: '';
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid var(--border-emphasis);
}

.social-stat-tooltip::after {
  content: '';
  position: absolute;
  top: -7px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid var(--surface-elevated);
}

@keyframes tooltip-fade-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.social-stat-tooltip__header {
  margin-bottom: var(--space-2);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border-soft);
}

.social-stat-tooltip__title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.social-stat-tooltip__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  color: var(--text-tertiary);
}

.social-stat-tooltip__loading .spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-soft);
  border-top-color: var(--accent-amber);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.social-stat-tooltip__list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 240px;
  overflow-y: auto;
}

.social-stat-tooltip__item {
  margin: 0;
  padding: 0;
}

.social-stat-tooltip__user-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--text-primary);
  transition: background 0.15s ease;
}

.social-stat-tooltip__user-link:hover {
  background: var(--surface-hover);
}

.social-stat-tooltip__avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.social-stat-tooltip__avatar--placeholder {
  background: var(--accent-moss);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.social-stat-tooltip__username {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.social-stat-tooltip__view-all {
  display: block;
  margin-top: var(--space-2);
  padding: var(--space-2);
  text-align: center;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent-amber);
  text-decoration: none;
  border-top: 1px solid var(--border-soft);
  transition: color 0.15s ease;
}

.social-stat-tooltip__view-all:hover {
  color: var(--accent-amber-hover);
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .social-stat-tooltip {
    min-width: 200px;
    max-width: 240px;
  }
}
```

---

## 5. Consideraciones de UX/Accesibilidad

### 5.1. Accesibilidad (WCAG 2.1 AA)

✅ **ARIA Attributes**:
```typescript
<div
  role="tooltip"
  aria-live="polite"
  id="followers-tooltip"
>
```

✅ **Keyboard Navigation**:
- Tooltip aparece también en `onFocus` (no solo hover)
- `Escape` cierra tooltip
- Links dentro de tooltip son tab-navigable

✅ **Screen Readers**:
- `aria-describedby` en la tarjeta principal
- Anuncio de carga con `aria-live="polite"`

### 5.2. Performance

✅ **Lazy Loading**:
- Datos NO se cargan en mount del dashboard
- Solo se fetch on hover (ahorro de requests)

✅ **Debouncing**:
- Hover delay de 500ms evita tooltips accidentales
- Leave delay de 200ms permite mover ratón al tooltip

✅ **Caching**:
- Considerar cachear respuesta por 60s (React Query)
- Evita re-fetch en hovers sucesivos

### 5.3. Mobile UX

⚠️ **Touch Devices**:
- Hover no existe en touch
- **Opción 1**: Convertir en `onClick` en mobile (modal)
- **Opción 2**: Link directo a página `/users/{username}/followers`

**Implementación Mobile**:
```typescript
const isMobile = window.matchMedia('(hover: none)').matches;

const handleInteraction = isMobile
  ? () => navigate(`/users/${username}/followers`) // Click → Navigate
  : () => handleMouseEnter('followers');           // Hover → Tooltip
```

---

## 6. Testing

### 6.1. Unit Tests

```typescript
// SocialStatTooltip.test.tsx

describe('SocialStatTooltip', () => {
  it('renders loading state correctly', () => {
    render(<SocialStatTooltip isLoading={true} visible={true} />);
    expect(screen.getByText('Cargando...')).toBeInTheDocument();
  });

  it('renders user list correctly', () => {
    const mockUsers = [
      { user_id: '1', username: 'user1', profile_photo_url: null },
      { user_id: '2', username: 'user2', profile_photo_url: '/photo.jpg' },
    ];
    render(<SocialStatTooltip users={mockUsers} totalCount={10} visible={true} />);
    expect(screen.getByText('user1')).toBeInTheDocument();
    expect(screen.getByText('+ 8 más · Ver todos')).toBeInTheDocument();
  });

  it('hides when visible=false', () => {
    const { container } = render(<SocialStatTooltip visible={false} />);
    expect(container.firstChild).toBeNull();
  });
});
```

### 6.2. E2E Tests (Playwright)

```typescript
// dashboard-social-stats.spec.ts

test('followers tooltip appears on hover', async ({ page }) => {
  await page.goto('/dashboard');

  const followersCard = page.locator('.social-stat-card').first();
  await followersCard.hover();

  // Wait 500ms for tooltip delay
  await page.waitForTimeout(600);

  const tooltip = page.locator('.social-stat-tooltip');
  await expect(tooltip).toBeVisible();
  await expect(tooltip).toContainText('Seguidores');
});

test('tooltip shows user list', async ({ page }) => {
  await page.goto('/dashboard');

  const followersCard = page.locator('.social-stat-card').first();
  await followersCard.hover();
  await page.waitForTimeout(600);

  const userLinks = page.locator('.social-stat-tooltip__user-link');
  expect(await userLinks.count()).toBeGreaterThan(0);
});

test('view all link navigates correctly', async ({ page }) => {
  await page.goto('/dashboard');

  const followersCard = page.locator('.social-stat-card').first();
  await followersCard.hover();
  await page.waitForTimeout(600);

  await page.click('.social-stat-tooltip__view-all');
  await expect(page).toHaveURL(/\/users\/.*\/followers/);
});
```

---

## 7. Alternativas Consideradas y Descartadas

### ❌ Inline Expansion

**Descripción**: Expandir la tarjeta inline en el dashboard mostrando lista.

**Por qué se descartó**:
- Rompe el layout del dashboard (desplaza otros elementos)
- UX confusa (no está claro si es temporal o permanente)
- Mobile: Problema de espacio

### ❌ Click to Modal

**Descripción**: Click en tarjeta abre modal full-screen con lista.

**Por qué se descartó**:
- Overhead alto para "quick peek"
- Requiere cerrar modal para volver
- Progressive disclosure perdido (todo o nada)

---

## 8. Implementación Recomendada - Roadmap

### Fase 1: MVP (2-3 horas)
1. ✅ Crear `useFollowersTooltip` hook
2. ✅ Crear `SocialStatTooltip` component
3. ✅ Modificar `SocialStatsSection` con hover handlers
4. ✅ CSS básico con posicionamiento y animación

### Fase 2: Polish (1-2 horas)
1. ✅ Accessibility (ARIA, keyboard nav)
2. ✅ Mobile fallback (onClick → navigate)
3. ✅ Loading states y error handling

### Fase 3: Testing (1 hora)
1. ✅ Unit tests componente
2. ✅ E2E test hover behavior

### Fase 4: Optimización (opcional, 1 hora)
1. ✅ React Query caching
2. ✅ Intersection Observer para pre-fetch
3. ✅ Virtual scrolling si listas muy largas

**Total estimado**: 4-7 horas

---

## 9. Conclusión

### ✅ Implementación Recomendada: Tooltip Simple (Opción A)

**Rationale**:
- Balance perfecto entre información y simplicidad
- Patrón familiar para usuarios de redes sociales
- Performance óptimo (lazy loading on hover)
- Accesibilidad completa con ARIA
- Implementación limpia y mantenible

**Next Steps**:
1. Aprobar diseño propuesto
2. Implementar MVP (Fase 1)
3. Testear con usuarios reales
4. Iterar basado en feedback

**User Value**:
- Descubrimiento rápido de quién te sigue
- No interrumpe el flujo de navegación del dashboard
- Click en usuario → navega a perfil
- Link "Ver todos" → lista completa cuando se necesita

---

**Documento creado por**: Claude Code
**Fecha**: 2026-02-11
**Para revisión por**: Equipo de desarrollo ContraVento
