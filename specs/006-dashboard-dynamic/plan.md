# Feature 006: Dashboard Dinámico - Plan de Implementación

**Versión**: 1.0.0
**Feature**: 006-dashboard-dynamic
**Fecha**: 2026-01-09

---

## 1. Resumen del Plan

Transformar el dashboard placeholder en un dashboard funcional con:
- **Stats Cards**: Mostrar métricas clave (viajes, km, países, seguidores)
- **Recent Trips**: Lista de viajes recientes con fotos
- **Quick Actions**: Accesos rápidos a funcionalidades
- **Welcome Banner**: Saludo personalizado

**Estrategia**: Desarrollo incremental por fases, reutilizando APIs backend ya implementadas.

---

## 2. Arquitectura de Componentes

### 2.1. Component Hierarchy

```
DashboardPage
├── WelcomeBanner
│   ├── UserAvatar
│   └── VerifiedBadge
├── StatsSection
│   ├── StatsCard (x4)
│   │   ├── StatIcon
│   │   ├── StatValue
│   │   └── StatLabel
│   └── SkeletonLoader (loading state)
├── RecentTripsSection
│   ├── SectionHeader
│   ├── RecentTripCard (x3-5)
│   │   ├── TripImage (lazy loaded)
│   │   ├── TripInfo
│   │   └── TagBadges
│   ├── EmptyState (no trips)
│   └── SkeletonLoader
└── QuickActionsSection
    └── QuickActionButton (x4)
```

### 2.2. Data Flow

```
┌─────────────────┐
│  DashboardPage  │
└────────┬────────┘
         │
         ├── useStats() hook
         │   └── GET /api/stats/me
         │
         ├── useRecentTrips() hook
         │   └── GET /api/users/{username}/trips
         │
         └── useAuth() context
             └── Current user data
```

---

## 3. Servicios y API Integration

### 3.1. Stats Service

**Archivo**: `frontend/src/services/statsService.ts`

```typescript
import api from './api';
import { UserStats } from '../types/stats';

/**
 * Fetch current user's statistics
 */
export const getMyStats = async (): Promise<UserStats> => {
  const response = await api.get<UserStats>('/stats/me');
  return response.data;
};

/**
 * Format large numbers with commas
 */
export const formatStatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-ES').format(value);
};

/**
 * Format distance with units
 */
export const formatDistance = (km: number): string => {
  if (km >= 1000) {
    return `${(km / 1000).toFixed(1)} mil km`;
  }
  return `${formatStatNumber(km)} km`;
};
```

**API Endpoint**: `GET /api/stats/me`

**Response Shape**:
```json
{
  "trip_count": 12,
  "total_distance_km": 1234.5,
  "countries_visited": ["Spain", "France", "Portugal"],
  "follower_count": 42,
  "following_count": 38,
  "longest_trip_km": 450.2,
  "photo_count": 156
}
```

---

### 3.2. Trips Service

**Archivo**: `frontend/src/services/tripsService.ts`

```typescript
import api from './api';
import { Trip, TripsListResponse } from '../types/trip';

/**
 * Fetch user's recent published trips
 */
export const getRecentTrips = async (
  username: string,
  limit: number = 5
): Promise<Trip[]> => {
  const response = await api.get<TripsListResponse>(
    `/users/${username}/trips`,
    {
      params: {
        status: 'PUBLISHED',
        limit,
        offset: 0,
      },
    }
  );
  return response.data.trips;
};

/**
 * Format trip date for display
 */
export const formatTripDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-ES', {
    month: 'short',
    year: 'numeric',
  }).format(date);
};
```

**API Endpoint**: `GET /api/users/{username}/trips?status=PUBLISHED&limit=5`

**Response Shape**:
```json
{
  "trips": [
    {
      "id": "uuid",
      "title": "Ruta Pirineos",
      "start_date": "2024-06-01",
      "end_date": "2024-06-05",
      "distance_km": 320.5,
      "tags": ["bikepacking", "montaña"],
      "photo_url": "/storage/trip_photos/.../photo.jpg",
      "photo_count": 12,
      "status": "PUBLISHED"
    }
  ],
  "total": 12,
  "limit": 5,
  "offset": 0
}
```

---

## 4. Types Definitions

### 4.1. Stats Types

**Archivo**: `frontend/src/types/stats.ts`

```typescript
/**
 * User statistics from backend
 */
export interface UserStats {
  trip_count: number;
  total_distance_km: number;
  countries_visited: string[];
  follower_count: number;
  following_count: number;
  longest_trip_km: number;
  photo_count: number;
}

/**
 * Individual stat card data
 */
export interface StatCardData {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  color?: string; // For icon color theming
}
```

---

### 4.2. Trip Types

**Archivo**: `frontend/src/types/trip.ts`

```typescript
/**
 * Trip from backend API
 */
export interface Trip {
  id: string;
  title: string;
  description?: string;
  start_date: string; // ISO date
  end_date?: string;
  distance_km: number;
  difficulty?: 'easy' | 'moderate' | 'hard';
  status: 'DRAFT' | 'PUBLISHED';
  tags: string[];
  photo_url?: string; // Main photo
  photo_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Trips list response
 */
export interface TripsListResponse {
  trips: Trip[];
  total: number;
  limit: number;
  offset: number;
}
```

---

## 5. Custom Hooks

### 5.1. useStats Hook

**Archivo**: `frontend/src/hooks/useStats.ts`

```typescript
import { useState, useEffect } from 'react';
import { getMyStats } from '../services/statsService';
import { UserStats } from '../types/stats';

export const useStats = () => {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getMyStats();
        setStats(data);
      } catch (err) {
        setError('Error al cargar estadísticas');
        console.error('Stats fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
};
```

---

### 5.2. useRecentTrips Hook

**Archivo**: `frontend/src/hooks/useRecentTrips.ts`

```typescript
import { useState, useEffect } from 'react';
import { getRecentTrips } from '../services/tripsService';
import { Trip } from '../types/trip';

export const useRecentTrips = (username: string, limit: number = 5) => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getRecentTrips(username, limit);
        setTrips(data);
      } catch (err) {
        setError('Error al cargar viajes');
        console.error('Trips fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchTrips();
    }
  }, [username, limit]);

  return { trips, loading, error };
};
```

---

## 6. Component Specifications

### 6.1. StatsCard Component

**Archivo**: `frontend/src/components/dashboard/StatsCard.tsx`

```typescript
import React from 'react';
import './StatsCard.css';

export interface StatsCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  loading?: boolean;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  label,
  value,
  icon,
  subtitle,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="stats-card skeleton">
        <div className="skeleton-icon" />
        <div className="skeleton-value" />
        <div className="skeleton-label" />
      </div>
    );
  }

  return (
    <div className="stats-card">
      <div className="stats-icon">{icon}</div>
      <div className="stats-content">
        <div className="stats-value">{value}</div>
        <div className="stats-label">{label}</div>
        {subtitle && <div className="stats-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
};
```

**Estilos**: `StatsCard.css`
- Card blanco con borde `color-earth-light`
- Icon circular con background `color-primary-light`
- Value grande con `font-display` y `text-4xl`
- Hover effect: `translateY(-2px)` + `shadow-lg`
- Grid responsive: 2x2 desktop, 1 columna mobile

---

### 6.2. RecentTripCard Component

**Archivo**: `frontend/src/components/dashboard/RecentTripCard.tsx`

```typescript
import React from 'react';
import { Link } from 'react-router-dom';
import { Trip } from '../../types/trip';
import { formatTripDate, formatDistance } from '../../services/tripsService';
import './RecentTripCard.css';

export interface RecentTripCardProps {
  trip: Trip;
}

export const RecentTripCard: React.FC<RecentTripCardProps> = ({ trip }) => {
  return (
    <Link to={`/trips/${trip.id}`} className="recent-trip-card">
      <div className="trip-image-container">
        {trip.photo_url ? (
          <img
            src={trip.photo_url}
            alt={trip.title}
            loading="lazy"
            className="trip-image"
          />
        ) : (
          <div className="trip-image-placeholder">
            <span className="placeholder-icon">🚴</span>
          </div>
        )}
        <div className="trip-photo-count">{trip.photo_count} fotos</div>
      </div>

      <div className="trip-info">
        <h3 className="trip-title">{trip.title}</h3>
        <div className="trip-meta">
          <span className="trip-date">{formatTripDate(trip.start_date)}</span>
          <span className="trip-distance">
            {formatDistance(trip.distance_km)}
          </span>
        </div>
        {trip.tags.length > 0 && (
          <div className="trip-tags">
            {trip.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="trip-tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
};
```

**Estilos**: `RecentTripCard.css`
- Card horizontal con imagen a la izquierda
- Imagen 200x150px con object-fit cover
- Placeholder con gradiente `color-primary` → `color-forest`
- Tags con background `color-cream` y border `color-earth-light`
- Hover: `translateY(-2px)` + sombra

---

### 6.3. QuickActionButton Component

**Archivo**: `frontend/src/components/dashboard/QuickActionButton.tsx`

```typescript
import React from 'react';
import './QuickActionButton.css';

export interface QuickActionButtonProps {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export const QuickActionButton: React.FC<QuickActionButtonProps> = ({
  label,
  icon,
  onClick,
  variant = 'primary',
}) => {
  return (
    <button
      className={`quick-action-button quick-action-${variant}`}
      onClick={onClick}
      type="button"
    >
      <div className="action-icon">{icon}</div>
      <div className="action-label">{label}</div>
    </button>
  );
};
```

**Estilos**: `QuickActionButton.css`
- Botón grande con padding `space-8`
- Primary: gradient `color-primary` → `color-primary-dark`
- Secondary: background `color-cream` + border `color-earth`
- Icon circular arriba, label abajo (columna)
- Hover: `translateY(-3px)` + `shadow-lg`

---

### 6.4. WelcomeBanner Component

**Archivo**: `frontend/src/components/dashboard/WelcomeBanner.tsx`

```typescript
import React, { useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './WelcomeBanner.css';

export const WelcomeBanner: React.FC = () => {
  const { user } = useAuth();

  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Buenos días';
    if (hour < 20) return 'Buenas tardes';
    return 'Buenas noches';
  }, []);

  if (!user) return null;

  const initials = user.username.slice(0, 2).toUpperCase();

  return (
    <div className="welcome-banner">
      <div className="welcome-avatar">{initials}</div>
      <div className="welcome-content">
        <h2 className="welcome-greeting">{greeting},</h2>
        <div className="welcome-user">
          <span className="welcome-username">{user.username}</span>
          {user.is_verified && (
            <span className="verified-badge" title="Usuario verificado">
              ✓
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
```

**Estilos**: `WelcomeBanner.css`
- Banner horizontal con avatar circular a la izquierda
- Avatar con gradient `color-primary` → `color-forest`
- Greeting con `font-serif` y `text-2xl`
- Username con `font-display` y `text-4xl`
- Verified badge con background `color-success-light`
- Animación `slideDown` de entrada

---

## 7. DashboardPage Refactor

**Archivo**: `frontend/src/pages/DashboardPage.tsx` (actualizar)

```typescript
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useStats } from '../hooks/useStats';
import { useRecentTrips } from '../hooks/useRecentTrips';
import { WelcomeBanner } from '../components/dashboard/WelcomeBanner';
import { StatsCard } from '../components/dashboard/StatsCard';
import { RecentTripCard } from '../components/dashboard/RecentTripCard';
import { QuickActionButton } from '../components/dashboard/QuickActionButton';
import { UserMenu } from '../components/auth/UserMenu';
import './DashboardPage.css';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { stats, loading: statsLoading, error: statsError } = useStats();
  const { trips, loading: tripsLoading, error: tripsError } = useRecentTrips(
    user?.username || '',
    5
  );

  // Quick actions
  const handleCreateTrip = () => navigate('/trips/new');
  const handleViewProfile = () => navigate('/profile');
  const handleExplore = () => navigate('/explore');
  const handleEditProfile = () => navigate('/profile/edit');

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Dashboard</h1>
          <UserMenu />
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          {/* Welcome Banner */}
          <WelcomeBanner />

          {/* Stats Cards */}
          <section className="stats-section">
            <h2 className="section-title">Tus Estadísticas</h2>
            <div className="stats-grid">
              <StatsCard
                label="Viajes Publicados"
                value={stats?.trip_count || 0}
                icon={<span>🚴</span>}
                loading={statsLoading}
              />
              <StatsCard
                label="Kilómetros Totales"
                value={`${stats?.total_distance_km.toFixed(0) || 0} km`}
                icon={<span>📏</span>}
                loading={statsLoading}
              />
              <StatsCard
                label="Países Visitados"
                value={stats?.countries_visited.length || 0}
                icon={<span>🌍</span>}
                subtitle={stats?.countries_visited.join(', ')}
                loading={statsLoading}
              />
              <StatsCard
                label="Seguidores"
                value={stats?.follower_count || 0}
                icon={<span>👥</span>}
                loading={statsLoading}
              />
            </div>
            {statsError && (
              <div className="error-message">{statsError}</div>
            )}
          </section>

          {/* Recent Trips */}
          <section className="recent-trips-section">
            <div className="section-header">
              <h2 className="section-title">Viajes Recientes</h2>
              <button
                className="view-all-button"
                onClick={() => navigate('/trips')}
              >
                Ver todos →
              </button>
            </div>

            {tripsLoading && (
              <div className="trips-loading">Cargando viajes...</div>
            )}

            {!tripsLoading && trips.length === 0 && (
              <div className="empty-state">
                <p>Aún no has publicado viajes</p>
                <button
                  className="create-trip-button"
                  onClick={handleCreateTrip}
                >
                  Crear tu primer viaje
                </button>
              </div>
            )}

            {!tripsLoading && trips.length > 0 && (
              <div className="trips-grid">
                {trips.map((trip) => (
                  <RecentTripCard key={trip.id} trip={trip} />
                ))}
              </div>
            )}

            {tripsError && (
              <div className="error-message">{tripsError}</div>
            )}
          </section>

          {/* Quick Actions */}
          <section className="quick-actions-section">
            <h2 className="section-title">Acciones Rápidas</h2>
            <div className="actions-grid">
              <QuickActionButton
                label="Crear Viaje"
                icon={<span>➕</span>}
                onClick={handleCreateTrip}
                variant="primary"
              />
              <QuickActionButton
                label="Ver Perfil"
                icon={<span>👤</span>}
                onClick={handleViewProfile}
                variant="secondary"
              />
              <QuickActionButton
                label="Explorar"
                icon={<span>🔍</span>}
                onClick={handleExplore}
                variant="secondary"
              />
              <QuickActionButton
                label="Editar Perfil"
                icon={<span>⚙️</span>}
                onClick={handleEditProfile}
                variant="secondary"
              />
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};
```

---

## 8. Estilos CSS

### 8.1. DashboardPage.css (expand)

```css
/* Stats Section */
.stats-section {
  margin-bottom: var(--space-10);
}

.section-title {
  margin: 0 0 var(--space-6) 0;
  font-family: var(--font-serif);
  font-size: var(--text-3xl);
  color: var(--color-forest);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-6);
}

/* Recent Trips Section */
.recent-trips-section {
  margin-bottom: var(--space-10);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.view-all-button {
  background: none;
  border: none;
  color: var(--color-primary);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: 600;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.view-all-button:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.trips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
}

.empty-state {
  text-align: center;
  padding: var(--space-12);
  background: var(--color-cream);
  border: 2px dashed var(--color-earth-light);
  border-radius: var(--radius-2xl);
}

.empty-state p {
  margin: 0 0 var(--space-4) 0;
  font-family: var(--font-sans);
  font-size: var(--text-lg);
  color: var(--color-gray-600);
}

.create-trip-button {
  padding: var(--space-4) var(--space-8);
  background: linear-gradient(135deg,
    var(--color-primary) 0%,
    var(--color-primary-dark) 100%
  );
  color: var(--color-cream);
  border: 2px solid var(--color-primary-dark);
  border-radius: var(--radius-lg);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-base);
}

.create-trip-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Quick Actions Section */
.quick-actions-section {
  margin-bottom: var(--space-10);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-6);
}

/* Error Messages */
.error-message {
  padding: var(--space-4);
  background: var(--color-error-light);
  border: 2px solid var(--color-error);
  border-radius: var(--radius-lg);
  color: var(--color-secondary-dark);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  margin-top: var(--space-4);
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .trips-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }
}
```

---

## 9. Testing Strategy

### 9.1. Manual Testing Checklist

**Stats Cards**:
- [ ] Stats cargan correctamente desde API
- [ ] Loading skeleton se muestra mientras carga
- [ ] Error message si falla la API
- [ ] Números formateados correctamente (1,234)
- [ ] Responsive en mobile/tablet/desktop

**Recent Trips**:
- [ ] Viajes recientes se muestran correctamente
- [ ] Imágenes cargan con lazy loading
- [ ] Empty state si no hay viajes
- [ ] Link a detalle de viaje funciona
- [ ] Tags se renderizan correctamente

**Quick Actions**:
- [ ] Botones navegan a rutas correctas
- [ ] Hover effects funcionan
- [ ] Responsive en mobile

**Welcome Banner**:
- [ ] Saludo cambia según hora del día
- [ ] Avatar muestra iniciales correctas
- [ ] Badge verificado se muestra si corresponde

### 9.2. Performance Testing

- [ ] Dashboard carga en < 1s con caché
- [ ] No layout shift durante carga
- [ ] Imágenes lazy loaded
- [ ] No memory leaks en hooks

---

## 10. Deployment Checklist

- [ ] Todos los componentes implementados
- [ ] Estilos consistentes con diseño rústico
- [ ] Responsive testing completo
- [ ] Error handling robusto
- [ ] Loading states funcionando
- [ ] API integration validada
- [ ] Types correctamente definidos
- [ ] Manual testing completado
- [ ] Code review aprobado
- [ ] Merge a main

---

## 11. Future Enhancements (Out of Scope)

- Activity feed con timeline de eventos
- Gráficos de progreso (charts.js)
- Comparación de stats con otros usuarios
- Badges/achievements interactivos
- Personalización del dashboard (drag & drop widgets)

---

**Próximo paso**: Crear rama `006-dashboard-dynamic` e iniciar implementación.

**Última actualización**: 2026-01-09
