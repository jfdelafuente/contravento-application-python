# Feature 006: Dashboard Dinámico

**Versión**: 1.0.0
**Estado**: Planning
**Prioridad**: Alta
**Estimación**: 2-3 días

---

## 1. Resumen Ejecutivo

Evolucionar el dashboard placeholder actual en un dashboard dinámico y funcional que muestre estadísticas del usuario, viajes recientes, actividad, y acciones rápidas. El dashboard será el hub central de la aplicación donde los usuarios ven su progreso y acceden a funcionalidades clave.

**Problema que resuelve**: El dashboard actual es un placeholder sin información útil. Los usuarios necesitan ver sus estadísticas, viajes recientes, y tener acceso rápido a acciones comunes.

**Valor para el usuario**: Dashboard informativo y accionable que incentiva el uso de la plataforma y facilita la navegación.

---

## 2. Requisitos Funcionales

### FR-001: Stats Cards
**Descripción**: Mostrar tarjetas con estadísticas clave del usuario
**Prioridad**: Alta

**Criterios de aceptación**:
- Display de 4 stats cards principales:
  - Total de viajes publicados
  - Kilómetros totales recorridos
  - Países visitados (con badges)
  - Seguidores actuales
- Cada card con icono representativo
- Números grandes y legibles con formato (1,234 km)
- Loading skeleton mientras carga data
- Error state si falla la carga
- Responsive grid (2x2 en desktop, 1 columna en mobile)

**API necesaria**:
- `GET /api/stats/me` - Ya implementada en backend

---

### FR-002: Recent Trips Section
**Descripción**: Lista de viajes recientes del usuario con fotos
**Prioridad**: Alta

**Criterios de aceptación**:
- Mostrar últimos 3-5 viajes publicados
- Card de viaje con:
  - Foto principal (o placeholder si no hay)
  - Título del viaje
  - Fecha de inicio
  - Distancia en km
  - Tags principales (max 3)
  - Link a detalle de viaje
- Botón "Ver todos los viajes"
- Empty state si no hay viajes: "Aún no has publicado viajes"
- Skeleton loader mientras carga

**API necesaria**:
- `GET /api/users/{username}/trips?status=PUBLISHED&limit=5` - Ya implementada

---

### FR-003: Activity Feed
**Descripción**: Timeline de actividades recientes
**Prioridad**: Media

**Criterios de aceptación**:
- Lista de últimas 5-10 actividades:
  - "Publicaste el viaje 'X'" (con link)
  - "Subiste 3 fotos a 'Y'" (con link)
  - "Te siguió @username" (con link a perfil)
  - "Lograste el badge 'Z'"
- Cada actividad con icono y timestamp relativo ("hace 2 horas")
- Ordenadas por fecha descendente
- Empty state: "No hay actividad reciente"
- Límite de 10 items con "Ver más"

**API necesaria**:
- Nueva: `GET /api/activity/me?limit=10` - A implementar en backend

---

### FR-004: Quick Actions
**Descripción**: Botones de acceso rápido a funcionalidades clave
**Prioridad**: Alta

**Criterios de aceptación**:
- 3-4 botones destacados:
  - "Crear Viaje" → Navega a /trips/new (placeholder)
  - "Ver Perfil" → Navega a /profile
  - "Explorar Viajes" → Navega a /explore (placeholder)
  - "Editar Perfil" → Navega a /profile/edit (placeholder)
- Botones con iconos claros
- Diseño consistente con estética rústica
- Responsive (2x2 grid en mobile)

**API necesaria**: Ninguna (solo navegación)

---

### FR-005: Welcome Banner
**Descripción**: Banner de bienvenida personalizado
**Prioridad**: Baja

**Criterios de aceptación**:
- Mensaje personalizado: "¡Bienvenido de vuelta, {username}!"
- Avatar del usuario (o inicial)
- Badge de verificado si corresponde
- Horario contextual: "Buenos días", "Buenas tardes", "Buenas noches"
- Animación de entrada (slideDown)

**API necesaria**: Ninguna (usa datos de AuthContext)

---

## 3. Requisitos No Funcionales

### NFR-001: Performance
- Carga inicial del dashboard < 1s (con stats cached)
- Loading skeletons para evitar layout shift
- Lazy loading de imágenes de viajes
- Caché de stats por 5 minutos

### NFR-002: Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px
- Grid adaptativo para stats cards
- Imágenes responsive con srcset

### NFR-003: Accesibilidad
- Semantic HTML (section, article, h2-h6)
- ARIA labels para stats cards
- Focus states visibles
- Color contrast WCAG AA

### NFR-004: Diseño
- Consistente con sistema de diseño rústico
- Paleta de colores tierra
- Tipografía: Playfair Display (headings), Inter (body)
- Animaciones sutiles (slideUp, fadeIn)

---

## 4. Componentes a Crear

### 4.1. StatsCard Component
```typescript
interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  loading?: boolean;
  error?: string;
}
```

**Responsabilidades**:
- Renderizar stat individual con icono
- Skeleton loader
- Error state
- Formateo de números (1,234)

---

### 4.2. RecentTripCard Component
```typescript
interface RecentTripCardProps {
  trip: {
    id: string;
    title: string;
    start_date: string;
    distance_km: number;
    tags: string[];
    photo_url?: string;
  };
}
```

**Responsabilidades**:
- Card de viaje reciente
- Lazy load de imagen
- Link a detalle
- Tags badges

---

### 4.3. ActivityItem Component
```typescript
interface ActivityItemProps {
  type: 'trip_published' | 'photo_uploaded' | 'new_follower' | 'badge_earned';
  message: string;
  timestamp: string;
  link?: string;
}
```

**Responsabilidades**:
- Renderizar actividad con icono
- Timestamp relativo ("hace 2 horas")
- Link opcional

---

### 4.4. QuickActionButton Component
```typescript
interface QuickActionButtonProps {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}
```

**Responsabilidades**:
- Botón de acción rápida
- Icono + label
- Navegación

---

## 5. Estructura de Archivos

```
frontend/src/
├── components/
│   ├── dashboard/
│   │   ├── StatsCard.tsx
│   │   ├── StatsCard.css
│   │   ├── RecentTripCard.tsx
│   │   ├── RecentTripCard.css
│   │   ├── ActivityItem.tsx
│   │   ├── ActivityItem.css
│   │   ├── QuickActionButton.tsx
│   │   └── QuickActionButton.css
│   └── common/
│       ├── SkeletonLoader.tsx
│       └── SkeletonLoader.css
├── pages/
│   ├── DashboardPage.tsx (refactor)
│   └── DashboardPage.css (expand)
├── services/
│   ├── statsService.ts (new)
│   ├── tripsService.ts (new)
│   └── activityService.ts (new)
├── types/
│   ├── stats.ts (new)
│   ├── trip.ts (new)
│   └── activity.ts (new)
└── utils/
    └── formatters.ts (new - numbers, dates)
```

---

## 6. API Integration

### Backend APIs Disponibles (ya implementadas)
- `GET /api/stats/me` - Estadísticas del usuario
- `GET /api/users/{username}/trips?status=PUBLISHED&limit=5` - Viajes recientes
- `GET /api/profile/me` - Perfil del usuario (para welcome banner)

### Backend APIs a Implementar (si es necesario)
- `GET /api/activity/me?limit=10` - Feed de actividades (opcional para MVP)

---

## 7. Success Criteria

### SC-001: Funcionalidad
- ✅ Stats cards muestran datos correctos del backend
- ✅ Viajes recientes se cargan y renderizan correctamente
- ✅ Quick actions navegan a rutas correctas
- ✅ Loading y error states funcionan

### SC-002: Performance
- ✅ Carga inicial < 1s con caché
- ✅ No layout shift (skeletons)
- ✅ Imágenes lazy loaded

### SC-003: UX
- ✅ Dashboard es informativo y accionable
- ✅ Diseño consistente con estética rústica
- ✅ Responsive en todos los breakpoints
- ✅ Accesible (WCAG AA)

---

## 8. Fases de Implementación

### Phase 1: Stats Cards (Día 1 AM)
1. Crear `StatsCard` component
2. Crear `statsService.ts`
3. Integrar stats en `DashboardPage`
4. Loading y error states

### Phase 2: Recent Trips (Día 1 PM)
1. Crear `RecentTripCard` component
2. Crear `tripsService.ts`
3. Integrar trips en `DashboardPage`
4. Empty state si no hay viajes

### Phase 3: Quick Actions (Día 2 AM)
1. Crear `QuickActionButton` component
2. Definir actions con iconos
3. Integrar en `DashboardPage`
4. Navegación funcional

### Phase 4: Welcome Banner (Día 2 PM)
1. Crear `WelcomeBanner` component
2. Lógica de horario contextual
3. Integrar avatar y badge verificado
4. Animación de entrada

### Phase 5: Polish & Testing (Día 3)
1. Activity Feed (opcional)
2. Responsive testing
3. Accessibility audit
4. Performance optimization
5. Documentation

---

## 9. Out of Scope (para features futuras)

- Feed de actividad social (likes, comments)
- Achievements/badges interactivos
- Gráficos de progreso (charts)
- Filtros avanzados de viajes
- Comparación de stats con otros usuarios
- Notificaciones en tiempo real

---

## 10. Preguntas Abiertas

1. ¿Implementamos activity feed en esta feature o lo dejamos para Feature 007?
   - **Recomendación**: Dejarlo para después, enfocarnos en stats + trips + actions

2. ¿Necesitamos badges/achievements visuales ahora?
   - **Recomendación**: Solo mostrar conteo en stats, UI detallada después

3. ¿Creamos la página de "Crear Viaje" ahora o placeholder?
   - **Recomendación**: Placeholder (Feature 008 es Travel Diary Frontend)

---

## 11. Referencias

- **Backend Stats API**: `backend/src/api/stats.py`
- **Backend Trips API**: `backend/src/api/trips.py`
- **Design System**: `frontend/docs/DESIGN_SYSTEM.md`
- **Navigation Flows**: `specs/005-frontend-user-profile/NAVIGATION_FLOWS.md`

---

**Última actualización**: 2026-01-09
**Siguiente paso**: Crear `plan.md` con arquitectura detallada
